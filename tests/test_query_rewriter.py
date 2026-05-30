import json

import pytest

from app.config import Settings
from app.pipeline.query_rewriter import QueryRewriter


def test_query_rewriter_returns_original_when_disabled() -> None:
    settings = Settings(enable_query_rewrite=False, deepseek_api_key="test-key")
    rewriter = QueryRewriter(settings)

    result = rewriter._fallback("How to speak VAT in CHinese", "en-US")

    assert result[0].query == "How to speak VAT in CHinese"
    assert result[0].market == "en-US"


@pytest.mark.asyncio
async def test_query_rewriter_rewrite_returns_original_when_disabled() -> None:
    settings = Settings(enable_query_rewrite=False, deepseek_api_key="test-key")
    rewriter = QueryRewriter(settings)

    result = await rewriter.rewrite("How to speak VAT in CHinese", "en-US")

    assert [item.query for item in result] == ["How to speak VAT in CHinese"]


@pytest.mark.asyncio
async def test_query_rewriter_returns_original_without_api_key() -> None:
    settings = Settings(enable_query_rewrite=True, deepseek_api_key=None)
    rewriter = QueryRewriter(settings)

    result = await rewriter.rewrite("How to speak VAT in CHinese", "en-US")

    assert [item.query for item in result] == ["How to speak VAT in CHinese"]


@pytest.mark.asyncio
async def test_query_rewriter_parses_valid_json(monkeypatch) -> None:
    payload = {
        "queries": [
            {
                "query": "VAT Chinese translation",
                "market": "en-US",
                "language": "en",
                "reason": "Clarifies VAT translation intent.",
            },
            {
                "query": "增值税 英文 VAT 中文怎么说",
                "market": "zh-CN",
                "language": "zh",
                "reason": "Adds Chinese phrasing.",
            },
        ]
    }

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": json.dumps(payload)}}]}

    class FakeClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, url: str, headers: dict, json: dict) -> FakeResponse:
            assert url == "https://api.deepseek.com/chat/completions"
            assert headers["Authorization"] == "Bearer test-key"
            assert json["response_format"] == {"type": "json_object"}
            return FakeResponse()

    monkeypatch.setattr("app.pipeline.query_rewriter.httpx.AsyncClient", FakeClient)
    settings = Settings(enable_query_rewrite=True, deepseek_api_key="test-key")
    rewriter = QueryRewriter(settings)

    result = await rewriter.rewrite("How to speak VAT in CHinese", "en-US")

    assert [item.query for item in result] == [
        "VAT Chinese translation",
        "增值税 英文 VAT 中文怎么说",
    ]
    assert result[0].market == "en-US"
    assert result[1].language == "zh"


@pytest.mark.asyncio
async def test_query_rewriter_falls_back_on_invalid_json(monkeypatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "not json"}}]}

    class FakeClient:
        def __init__(self, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> None:
            return None

        async def post(self, url: str, headers: dict, json: dict) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("app.pipeline.query_rewriter.httpx.AsyncClient", FakeClient)
    settings = Settings(enable_query_rewrite=True, deepseek_api_key="test-key")
    rewriter = QueryRewriter(settings)

    result = await rewriter.rewrite("How to speak VAT in CHinese", "en-US")

    assert [item.query for item in result] == ["How to speak VAT in CHinese"]
