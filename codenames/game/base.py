from __future__ import annotations

import json
from functools import cached_property
from typing import Set, Tuple

from pydantic import BaseModel as PydanticBaseModel

WordGroup = Tuple[str, ...]


class BaseModel(PydanticBaseModel):
    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def from_json(cls, string: str) -> BaseModel:
        data = json.loads(string)
        return cls(**data)

    def dict(self, *args, **kwargs) -> dict:
        result = super().dict(*args, **kwargs)
        cached_properties = get_cached_properties_names(self.__class__)
        include = kwargs.get("include", None) or set()
        for prop in cached_properties:
            if prop not in include:
                result.pop(prop, None)
        return result


def get_cached_properties_names(cls: type) -> Set[str]:
    return {k for k, v in cls.__dict__.items() if isinstance(v, cached_property)}


def canonical_format(word: str) -> str:
    return word.replace("_", " ").strip().lower()
