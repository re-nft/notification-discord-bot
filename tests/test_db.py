from dataclasses import dataclass
import pytest
from notification_discord_bot import db
from notification_discord_bot.constants import DB_PATH
import json


@dataclass
class DummyModel(db.Model):
    a: str
    b: str
    c: str
    unique_index = {"a", "b"}
    collection_name = "test-collection"


def setup_function():
    if not db.is_initialized():
        db.initialize()
    with open(DB_PATH, "r") as f:
        d = json.load(f)
        d[DummyModel.collection_name] = []

    with open(DB_PATH, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)


def teardown_function():
    with open(DB_PATH, "r") as f:
        d = json.load(f)
        del d[DummyModel.collection_name]

    with open(DB_PATH, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)


def test_uniqueness():
    with pytest.raises(AssertionError):
        DummyModel.get_or_none(a="a", b="b", c="c")
    with pytest.raises(AssertionError):
        DummyModel.update_or_create(a="a", b="b", c="c")


def test_get_none():
    out = DummyModel.get_or_none(a="a", b="b")
    assert out is None


def test_create_and_get():
    DummyModel.update_or_create(a="a", b="b", defaults={"c": "c"})
    out = DummyModel.get_or_none(a="a", b="b")
    assert out == DummyModel(a="a", b="b", c="c")


def test_update():
    DummyModel.update_or_create(a="a", b="b", defaults={"c": "c"})
    DummyModel.update_or_create(a="a", b="b", defaults={"c": "d"})
    out = DummyModel.get_or_none(a="a", b="b")
    assert out == DummyModel(a="a", b="b", c="d")


def test_filter():
    DummyModel.update_or_create(a="a", b="b", defaults={"c": "c"})
    DummyModel.update_or_create(a="a", b="e", defaults={"c": "f"})
    first = DummyModel(a="a", b="b", c="c")
    second = DummyModel(a="a", b="e", c="f")

    out = DummyModel.get_or_none(a="a", b="b")
    assert out == first

    out = DummyModel.get_or_none(a="a", b="e")
    assert out == second

    out = DummyModel.filter(a="a")
    assert out == [first, second]
