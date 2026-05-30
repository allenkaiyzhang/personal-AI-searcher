from bs4 import BeautifulSoup

from app.utils.normalize import normalize_text


def extract_content(html: str | None, fallback: str = "") -> str:
    if not html:
        return fallback

    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("script, style, header, footer, nav"):
        node.decompose()

    text = normalize_text(soup.get_text(" ", strip=True))
    return text if len(text) >= 120 else fallback
