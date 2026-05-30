from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models


class Repository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_topic(self, name: str, aliases: list[str], description: str | None) -> models.Topic:
        topic = models.Topic(name=name, aliases=aliases, description=description)
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def list_topics(self) -> list[models.Topic]:
        return list(self.db.scalars(select(models.Topic).order_by(models.Topic.created_at.desc())))

    def get_topic(self, topic_id: int) -> models.Topic | None:
        return self.db.get(models.Topic, topic_id)

    def latest_insight(self, topic_id: int) -> models.Insight | None:
        stmt = (
            select(models.Insight)
            .where(models.Insight.topic_id == topic_id)
            .order_by(models.Insight.updated_at.desc(), models.Insight.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def recent_evidence(self, topic_id: int, limit: int = 20) -> list[models.Evidence]:
        stmt = (
            select(models.Evidence)
            .where(models.Evidence.topic_id == topic_id)
            .order_by(models.Evidence.retrieved_at.desc(), models.Evidence.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def recent_timeline(self, topic_id: int, limit: int = 20) -> list[models.TimelineEvent]:
        stmt = (
            select(models.TimelineEvent)
            .where(models.TimelineEvent.topic_id == topic_id)
            .order_by(models.TimelineEvent.event_date.desc(), models.TimelineEvent.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def save_evidence(self, evidence: Sequence[models.Evidence]) -> list[models.Evidence]:
        self.db.add_all(evidence)
        self.db.commit()
        for item in evidence:
            self.db.refresh(item)
        return list(evidence)

    def save_timeline_events(self, events: Sequence[models.TimelineEvent]) -> list[models.TimelineEvent]:
        self.db.add_all(events)
        self.db.commit()
        for item in events:
            self.db.refresh(item)
        return list(events)

    def create_insight(self, topic_id: int, current_view: str, confidence: str) -> models.Insight:
        insight = models.Insight(topic_id=topic_id, current_view=current_view, confidence=confidence)
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def create_research_run(
        self,
        query: str,
        topic_id: int | None,
        answer: str,
        confidence: str,
    ) -> models.ResearchRun:
        run = models.ResearchRun(query=query, topic_id=topic_id, answer=answer, confidence=confidence)
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run
