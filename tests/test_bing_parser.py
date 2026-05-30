import base64
from pathlib import Path

from app.providers.bing_html import BingHtmlSearchProvider
from app.utils.normalize import extract_bing_redirect_url


def _bing_ck_url(target_url: str) -> str:
    encoded = base64.urlsafe_b64encode(target_url.encode("utf-8")).decode("ascii").rstrip("=")
    return f"https://www.bing.com/ck/a?foo=bar&u=a1{encoded}&ntb=1"


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


def test_extract_bing_redirect_url_decodes_bing_ck_url() -> None:
    target_url = "https://www.investopedia.com/terms/v/valueaddedtax.asp"
    bing_url = _bing_ck_url(target_url)

    assert extract_bing_redirect_url(bing_url) == target_url


def test_bing_parser_returns_decoded_urls() -> None:
    target_url = "https://www.investopedia.com/terms/v/valueaddedtax.asp"
    html = f"""
    <html>
      <body>
        <li class="b_algo">
          <h2><a href="{_bing_ck_url(target_url)}">Value-Added Tax Definition</a></h2>
          <div class="b_caption"><p>VAT definition and explanation.</p></div>
        </li>
      </body>
    </html>
    """

    results = BingHtmlSearchProvider.parse_results(html, max_results=5)

    assert len(results) == 1
    assert results[0].url == target_url
    assert "bing.com/ck/a" not in results[0].url
