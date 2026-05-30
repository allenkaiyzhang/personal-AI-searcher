from datetime import datetime, timezone

from app.db.models import Evidence, Topic
from app.providers.base import SearchResult
from app.utils.normalize import domain_from_url
from app.utils.similarity import is_similar


def confidence_from_content(content: str) -> float:
    length = len(content)
    if length >= 3000:
        return 1.0
    return round(0.5 + min(length, 3000) / 3000 * 0.5, 2)


def extract_evidence(
    topic: Topic,
    result: SearchResult,
    content: str,
    existing_claims: list[str],
) -> Evidence:
    novelty = "repeated" if any(is_similar(result.title, claim) for claim in existing_claims) else "new"
    now = datetime.now(timezone.utc)
    summary = content[:500]
    excerpt = content[:500]
    return Evidence(
        topic_id=topic.id,
        claim=result.title,
        summary=summary,
        excerpt=excerpt,
        source_title=result.title,
        source_url=result.url,
        source_domain=domain_from_url(result.url),
        published_at=None,
        retrieved_at=now,
        confidence=confidence_from_content(content),
        novelty=novelty,
    )
