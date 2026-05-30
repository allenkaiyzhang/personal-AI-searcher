from app.db.models import Evidence, Insight, TimelineEvent, Topic


DISCLAIMER = "This report is generated using rule-based summarization and should not be considered a factual conclusion."


def generate_answer(
    topic: Topic | None,
    old_insight: Insight | None,
    evidence_items: list[Evidence],
    timeline_updates: list[TimelineEvent],
    confidence: str,
) -> str:
    topic_name = topic.name if topic else "None"
    old_view = old_insight.current_view if old_insight else "No previous insight."

    evidence_lines = "\n".join(
        f"- {item.claim} ({item.novelty}, confidence={item.confidence:.2f})" for item in evidence_items
    ) or "- No new evidence collected."
    timeline_lines = "\n".join(
        f"- {item.event_date.date()}: {item.title}" for item in timeline_updates
    ) or "- No timeline updates."
    source_lines = "\n".join(
        f"- [{item.source_title}]({item.source_url})" for item in evidence_items
    ) or "- No sources."

    return (
        "# Research Report\n\n"
        f"## Matched Topic\n{topic_name}\n\n"
        f"## Old View\n{old_view}\n\n"
        f"## New Evidence\n{evidence_lines}\n\n"
        f"## Timeline Updates\n{timeline_lines}\n\n"
        f"## Sources\n{source_lines}\n\n"
        f"## Confidence\n{confidence}\n\n"
        f"{DISCLAIMER}"
    )
