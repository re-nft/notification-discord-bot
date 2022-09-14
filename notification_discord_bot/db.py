import json
from abc import ABC
from dataclasses import asdict, dataclass
from os.path import exists

from notification_discord_bot.constants import DB_PATH


def get_collection(collection_name: str):
    with open(DB_PATH, "r") as f:
        d = json.load(f)
        coll = d.get(collection_name)
    return coll


def document_matches_builder(**kwargs):
    def document_matches(doc):
        return all(v == doc.get(k) for k, v in kwargs.items())

    return document_matches


@dataclass
class Model(ABC):
    @property
    @classmethod
    def unique_index(cls) -> set[str]:
        raise NotImplementedError()

    @property
    @classmethod
    def collection_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def assert_kwargs_are_unique(cls, **kwargs):
        if not cls.unique_index == set(kwargs.keys()):
            raise AssertionError(
                "Keyword arguments don't uniquely identify the document."
            )

    @classmethod
    def filter(cls, **kwargs): # -> list[Self] awaiting 3.11 for typing
        coll = get_collection(cls.collection_name)  # type: ignore
        return [cls(**doc) for doc in coll if document_matches_builder(**kwargs)(doc)]

    @classmethod
    def get_or_none(cls, **kwargs): # -> Optional[Self] awaiting 3.11 for typing
        cls.assert_kwargs_are_unique(**kwargs)
        l = cls.filter(**kwargs)
        if len(l) == 0:
            return None
        if len(l) > 1:
            raise AssertionError("There is more than 1 document matching the query.")
        return l[0]

    @classmethod
    def update_or_create(cls, defaults=None, **kwargs):
        cls.assert_kwargs_are_unique(**kwargs)
        coll = get_collection(cls.collection_name)
        existing_doc = cls.get_or_none(**kwargs)
        if defaults is None:
            defaults = {}
        if existing_doc is not None:
            new_doc = asdict(existing_doc)
            for (key, value) in defaults.items():
                new_doc[key] = value
            coll = [doc for doc in coll if not document_matches_builder(**kwargs)(doc)]
        else:
            new_doc = asdict(cls(**kwargs, **defaults))
        coll.append(new_doc)
        with open(DB_PATH, "r") as f:
            d = json.load(f)
            d[cls.collection_name] = coll

        with open(DB_PATH, "w") as f:
            json.dump(d, f, ensure_ascii=False, indent=4)


def is_initialized() -> bool:
    return exists(DB_PATH)


def initialize():
    with open(DB_PATH, "w") as f:
        # pylint: disable=unused-import
        from notification_discord_bot import models

        all_models = Model.__subclasses__()
        d = {model.collection_name: [] for model in all_models}
        json.dump(d, f, ensure_ascii=False, indent=4)


def seed():
    if not is_initialized():
        initialize()
    from notification_discord_bot.seed import seed_renft

    seed_renft()
