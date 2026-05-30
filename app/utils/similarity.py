import difflib

from app.utils.normalize import normalize_text


def similarity_score(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalize_text(left).lower(), normalize_text(right).lower()).ratio()


def is_similar(left: str, right: str, threshold: float = 0.82) -> bool:
    return similarity_score(left, right) >= threshold
