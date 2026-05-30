from app.db.models import Topic


def match_topic(topics: list[Topic], query: str, topic_hint: str | None = None) -> Topic | None:
    hint = (topic_hint or "").lower().strip()
    lowered_query = query.lower()

    if hint:
        for topic in topics:
            values = [topic.name, *topic.aliases]
            if any(hint == value.lower() or hint in value.lower() for value in values):
                return topic

    for topic in topics:
        if any(alias.lower() in lowered_query for alias in topic.aliases):
            return topic

    for topic in topics:
        if topic.name.lower() in lowered_query:
            return topic

    return None
