from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.schemas import RewrittenQuery


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a search query planner. Convert the user's input into 1-3 high-quality web search queries. "
    "Do not answer the question. Do not invent facts. Output valid JSON only."
)


class QueryRewriter:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def rewrite(self, query: str, market: str | None = None) -> list[RewrittenQuery]:
        fallback = self._fallback(query, market)
        if not fallback:
            return []
        if not self.settings.enable_query_rewrite:
            return fallback
        if not self.settings.deepseek_api_key:
            logger.warning("Query rewrite requested but DEEPSEEK_API_KEY is not configured")
            return fallback

        try:
            rewritten = await self._call_deepseek(query.strip(), market)
        except Exception as exc:
            logger.warning("Query rewrite failed; falling back to original query: %s", exc)
            return fallback

        return rewritten or fallback

    def _fallback(self, query: str, market: str | None) -> list[RewrittenQuery]:
        stripped = query.strip()
        if not stripped:
            return []
        return [RewrittenQuery(query=stripped, market=market, language=None, reason="original query")]

    async def _call_deepseek(self, query: str, market: str | None) -> list[RewrittenQuery]:
        url = f"{self.settings.deepseek_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.deepseek_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": self._user_prompt(query, market)},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 500,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return self._parse_queries(parsed, fallback_market=market)

    @staticmethod
    def _user_prompt(query: str, market: str | None) -> str:
        schema = {
            "queries": [
                {
                    "query": "...",
                    "market": "en-US|zh-CN|ja-JP|null",
                    "language": "en|zh|ja|null",
                    "reason": "...",
                }
            ]
        }
        return (
            f"Original query: {query}\n"
            f"Requested market: {market or 'null'}\n"
            "Output schema:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )

    @staticmethod
    def _parse_queries(payload: dict[str, Any], fallback_market: str | None) -> list[RewrittenQuery]:
        raw_queries = payload.get("queries", [])
        if not isinstance(raw_queries, list):
            return []

        results: list[RewrittenQuery] = []
        seen: set[str] = set()
        for item in raw_queries:
            if not isinstance(item, dict):
                continue
            query = str(item.get("query", "")).strip()
            if not query:
                continue
            key = query.casefold()
            if key in seen:
                continue
            seen.add(key)
            market = item.get("market", fallback_market)
            language = item.get("language")
            reason = item.get("reason")
            results.append(
                RewrittenQuery(
                    query=query,
                    market=market if isinstance(market, str) else None,
                    language=language if isinstance(language, str) else None,
                    reason=reason if isinstance(reason, str) else None,
                )
            )
            if len(results) >= 3:
                break
        return results
