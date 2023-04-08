from __future__ import annotations

from functools import cached_property
from typing import Optional, Tuple

from codenames.game.base import BaseModel, canonical_format
from codenames.game.color import CardColor


class Card(BaseModel):
    word: str
    color: Optional[CardColor]  # None for guessers.
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
    def censored(self) -> Card:
        if self.revealed:
            return self
        return Card(word=self.word, color=None, revealed=self.revealed)

    @cached_property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


Cards = Tuple[Card, ...]
