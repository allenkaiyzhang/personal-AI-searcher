from pathlib import Path

from app.providers.bing_html import BingHtmlSearchProvider


def test_bing_parser_extracts_and_deduplicates_results() -> None:
    html = Path("tests/fixtures/bing_sample.html").read_text(encoding="utf-8")

    results = BingHtmlSearchProvider.parse_results(html, max_results=5)

    assert len(results) == 2
    assert results[0].title == "DRAM market update"
    assert results[0].url == "https://example.com/report"
    assert results[0].snippet == "Pricing has continued to improve in recent months."
    assert results[1].title == "HBM demand rises"


def test_bing_parser_respects_max_results() -> None:
    html = Path("tests/fixtures/bing_sample.html").read_text(encoding="utf-8")

    results = BingHtmlSearchProvider.parse_results(html, max_results=1)

    assert len(results) == 1
    assert results[0].title == "DRAM market update"
