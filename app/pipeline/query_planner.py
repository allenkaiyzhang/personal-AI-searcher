from app.db.models import Topic


def plan_queries(query: str, topic: Topic | None) -> list[str]:
    queries = [query.strip()]
    if topic is not None:
        aliases = " ".join(topic.aliases[:3])
        if aliases:
            queries.append(f"{query} {aliases}")
        queries.append(f"{topic.name} latest recent update")

    deduped: list[str] = []
    for item in queries:
        if item and item not in deduped:
            deduped.append(item)
    return deduped[:3]
