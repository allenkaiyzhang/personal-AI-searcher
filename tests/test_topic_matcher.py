from app.db.models import Topic
from app.pipeline.topic_matcher import match_topic


def test_topic_matcher_prefers_topic_hint_alias() -> None:
    dram = Topic(id=1, name="DRAM Market", aliases=["DRAM", "HBM"], description=None)
    nand = Topic(id=2, name="NAND Market", aliases=["NAND"], description=None)

    matched = match_topic([nand, dram], "memory pricing", topic_hint="HBM")

    assert matched is dram


def test_topic_matcher_uses_alias_before_name() -> None:
    dram = Topic(id=1, name="DRAM Market", aliases=["DRAM", "HBM"], description=None)

    matched = match_topic([dram], "Is Micron benefiting from DRAM pricing?")

    assert matched is dram


def test_topic_matcher_returns_none_without_match() -> None:
    dram = Topic(id=1, name="DRAM Market", aliases=["DRAM", "HBM"], description=None)

    matched = match_topic([dram], "foundry equipment lead times")

    assert matched is None
