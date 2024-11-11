from __future__ import annotations

from abc import ABC
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, computed_field


class CardColor(StrEnum):

    @property
    def emoji(self) -> str:
        raise NotImplementedError


C = TypeVar("C", bound=CardColor)


class Card(BaseModel, Generic[C], ABC):
    word: str
    color: C | None  # None for operatives.
    revealed: bool = False

    def __str__(self) -> str:
        result = self.word
        if self.color:
            result = f"{self.color.emoji} {self.word}"
        # result += " V" if self.revealed else " X"
        return result

    def __hash__(self):
        return hash(f"{self.word}{self.color}{self.revealed}")

    @property
    def censored(self) -> Card[C]:
        if self.revealed:
            return self
        return self.__class__(word=self.word, color=None, revealed=self.revealed)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


Cards = tuple[Card[C], ...]


def canonical_format(word: str) -> str:
    return word.replace("_", " ").strip().lower()
