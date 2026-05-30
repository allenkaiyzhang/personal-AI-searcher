from urllib.parse import urlparse, urlunparse


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")
