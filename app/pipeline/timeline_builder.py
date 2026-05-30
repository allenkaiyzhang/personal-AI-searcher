from app.db.models import Evidence, TimelineEvent


def build_timeline_events(evidence_items: list[Evidence]) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []
    for evidence in evidence_items:
        if evidence.novelty != "new":
            continue
        event_date = evidence.published_at or evidence.retrieved_at
        events.append(
            TimelineEvent(
                topic_id=evidence.topic_id,
                event_date=event_date,
                title=evidence.claim,
                description=evidence.summary[:500],
                importance=evidence.confidence,
                evidence_id=evidence.id,
            )
        )
    return events
