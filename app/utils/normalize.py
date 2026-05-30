import base64
from urllib.parse import parse_qs, urlparse, urlunparse


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def extract_bing_redirect_url(url: str) -> str:
    parsed = urlparse(url)
    if "bing.com" not in parsed.netloc.lower() or not parsed.path.startswith("/ck/a"):
        return url

    values = parse_qs(parsed.query).get("u")
    if not values:
        return url

    raw = values[0]
    if raw.startswith("a1"):
        raw = raw[2:]
    raw += "=" * (-len(raw) % 4)

    try:
        decoded = base64.urlsafe_b64decode(raw).decode("utf-8")
    except Exception:
        return url

    if decoded.startswith(("http://", "https://")):
        return decoded
    return url


def normalize_url(url: str) -> str:
    cleaned_url = extract_bing_redirect_url(url.strip())
    parsed = urlparse(cleaned_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme, netloc, path, "", parsed.query, ""))


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")
