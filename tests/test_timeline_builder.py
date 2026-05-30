from datetime import datetime, timezone

from app.db.models import Evidence
from app.pipeline.timeline_builder import build_timeline_events


def test_timeline_builder_creates_event_for_new_evidence() -> None:
    retrieved_at = datetime(2026, 5, 30, tzinfo=timezone.utc)
    evidence = Evidence(
        id=42,
        topic_id=1,
        claim="DRAM prices rise",
        summary="A market report says DRAM prices are rising.",
        excerpt="A market report says DRAM prices are rising.",
        source_title="DRAM prices rise",
        source_url="https://example.com/dram",
        source_domain="example.com",
        published_at=None,
        retrieved_at=retrieved_at,
        confidence=0.8,
        novelty="new",
    )

    events = build_timeline_events([evidence])

    assert len(events) == 1
    assert events[0].topic_id == 1
    assert events[0].event_date == retrieved_at
    assert events[0].title == "DRAM prices rise"
    assert events[0].evidence_id == 42


def test_timeline_builder_skips_repeated_evidence() -> None:
    evidence = Evidence(
        id=42,
        topic_id=1,
        claim="DRAM prices rise",
        summary="Repeated report.",
        excerpt="Repeated report.",
        source_title="DRAM prices rise",
        source_url="https://example.com/dram",
        source_domain="example.com",
        published_at=None,
        retrieved_at=datetime(2026, 5, 30, tzinfo=timezone.utc),
        confidence=0.8,
        novelty="repeated",
    )

    assert build_timeline_events([evidence]) == []
