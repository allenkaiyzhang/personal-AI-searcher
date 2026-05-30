from app.config import get_settings
from app.db.models import Evidence, Insight, TimelineEvent, Topic
from app.db.repository import Repository
from app.pipeline.answer_generator import generate_answer
from app.pipeline.content_extractor import extract_content
from app.pipeline.evidence_extractor import extract_evidence
from app.pipeline.fetcher import fetch_page
from app.pipeline.insight_updater import update_insight_decision
from app.pipeline.query_planner import plan_queries
from app.pipeline.query_rewriter import QueryRewriter
from app.pipeline.timeline_builder import build_timeline_events
from app.pipeline.topic_matcher import match_topic
from app.providers.base import SearchProvider, SearchResult
from app.schemas import ResearchRequest, ResearchResponse, RewrittenQuery
from app.utils.normalize import normalize_url


class ResearchPipeline:
    def __init__(self, repository: Repository, search_provider: SearchProvider) -> None:
        self.repository = repository
        self.search_provider = search_provider

    async def run(self, request: ResearchRequest) -> ResearchResponse:
        topics = self.repository.list_topics()
        topic = match_topic(topics, request.query, request.topic_hint)
        old_insight, old_evidence, old_timeline = self._load_memory(topic, request.use_memory)

        search_results, rewritten_queries = await self._search(
            request.query,
            topic,
            request.max_results,
            request.rewrite_query,
        )
        evidence_items = await self._collect_evidence(topic, search_results, old_evidence)

        saved_evidence: list[Evidence] = []
        timeline_updates: list[TimelineEvent] = []
        if request.update_memory and topic is not None and evidence_items:
            saved_evidence = self.repository.save_evidence(evidence_items)
            new_evidence = [item for item in saved_evidence if item.novelty == "new"]
            timeline_updates = self.repository.save_timeline_events(build_timeline_events(new_evidence))
        else:
            new_evidence = [item for item in evidence_items if item.novelty == "new"]

        view_changed, new_view, confidence = update_insight_decision(topic, old_insight, len(new_evidence))
        if request.update_memory and topic is not None and view_changed and new_view is not None:
            self.repository.create_insight(topic.id, new_view, confidence)

        answer = generate_answer(topic, old_insight, saved_evidence or evidence_items, timeline_updates, confidence)
        if request.update_memory:
            self.repository.create_research_run(request.query, topic.id if topic else None, answer, confidence)

        return ResearchResponse(
            matched_topic=topic.name if topic else None,
            old_view=old_insight.current_view if old_insight else None,
            answer=answer,
            view_changed=view_changed,
            timeline_updates=timeline_updates,
            new_evidence=saved_evidence if request.update_memory else [],
            confidence=confidence,
            rewritten_queries=rewritten_queries,
        )

    def _load_memory(
        self,
        topic: Topic | None,
        use_memory: bool,
    ) -> tuple[Insight | None, list[Evidence], list[TimelineEvent]]:
        if topic is None or not use_memory:
            return None, [], []
        return (
            self.repository.latest_insight(topic.id),
            self.repository.recent_evidence(topic.id),
            self.repository.recent_timeline(topic.id),
        )

    async def _search(
        self,
        query: str,
        topic: Topic | None,
        max_results: int,
        rewrite_query: bool,
    ) -> tuple[list[SearchResult], list[RewrittenQuery]]:
        results: list[SearchResult] = []
        seen_urls: set[str] = set()
        rewritten_queries = await self._plan_search_queries(query, topic, rewrite_query)

        for planned_query in rewritten_queries:
            try:
                query_results = await self.search_provider.search(
                    planned_query.query,
                    max_results=max_results,
                    market=planned_query.market,
                )
            except Exception:
                continue
            for result in query_results:
                normalized_url = normalize_url(result.url)
                if not normalized_url or normalized_url in seen_urls:
                    continue
                seen_urls.add(normalized_url)
                results.append(SearchResult(title=result.title, url=normalized_url, snippet=result.snippet))
                if len(results) >= max_results:
                    return results, rewritten_queries
        return results, rewritten_queries

    async def _plan_search_queries(
        self,
        query: str,
        topic: Topic | None,
        rewrite_query: bool,
    ) -> list[RewrittenQuery]:
        settings = get_settings()
        if rewrite_query and settings.enable_query_rewrite:
            rewritten = await QueryRewriter(settings).rewrite(query)
            if not self._is_original_query_only(query, rewritten):
                return rewritten

        return [
            RewrittenQuery(query=planned_query, market=None, language=None, reason="rule-based query planner")
            for planned_query in plan_queries(query, topic)
        ]

    @staticmethod
    def _is_original_query_only(query: str, rewritten_queries: list[RewrittenQuery]) -> bool:
        return len(rewritten_queries) == 1 and rewritten_queries[0].query.strip() == query.strip()

    async def _collect_evidence(
        self,
        topic: Topic | None,
        search_results: list[SearchResult],
        old_evidence: list[Evidence],
    ) -> list[Evidence]:
        if topic is None:
            return []

        existing_claims = [item.claim for item in old_evidence]
        evidence_items: list[Evidence] = []
        for result in search_results:
            html = await fetch_page(result.url)
            content = extract_content(html, fallback=result.snippet)
            if not content:
                continue
            evidence = extract_evidence(topic, result, content, existing_claims)
            evidence_items.append(evidence)
            existing_claims.append(evidence.claim)
        return evidence_items
