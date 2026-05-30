from app.db.models import Insight, Topic


UPDATED_VIEW = "New evidence has been collected and the topic requires review."


def update_insight_decision(
    topic: Topic | None,
    old_insight: Insight | None,
    new_evidence_count: int,
) -> tuple[bool, str | None, str]:
    if topic is None:
        return False, old_insight.current_view if old_insight else None, "low"
    if new_evidence_count >= 2:
        return True, UPDATED_VIEW, "medium"
    if old_insight is not None:
        return False, old_insight.current_view, old_insight.confidence
    return False, None, "low"
