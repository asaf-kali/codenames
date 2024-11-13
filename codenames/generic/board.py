from __future__ import annotations

import math
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Collection, Generic, Iterator, Union

from pydantic import BaseModel, field_validator

from codenames.generic.card import C, Card, Cards, canonical_format
from codenames.generic.exceptions import CardNotFoundError

if TYPE_CHECKING:
    from beautifultable import BeautifulTable

LTR = "\u200E"

WordGroup = tuple[str, ...]


class Board(BaseModel, Generic[C], ABC):
    language: str
    cards: list[Card[C]]

    @field_validator("cards")
    @classmethod
    def convert_cards(cls, v: Any) -> list[Card[C]]:
        return list(v)

    def __getitem__(self, item: Union[int, str]) -> Card:
        if isinstance(item, str):
            item = self.find_card_index(item)
        if not isinstance(item, int):
            raise IndexError(f"Illegal index type for card: {item}")
        if item < 0 or item >= self.size:
            raise IndexError(f"Card index out of bounds: {item}")
        return self.cards[item]

    def __iter__(self) -> Iterator[Card[C]]:  # type: ignore
        return iter(self.cards)

    def __len__(self) -> int:
        return self.size

    def __str__(self) -> str:
        return self.printable_string

    @property
    def size(self) -> int:
        return len(self.cards)

    @property
    def is_clean(self) -> bool:
        return all(not card.revealed for card in self.cards)

    @property
    def all_words(self) -> WordGroup:
        return tuple(card.formatted_word for card in self.cards)

    @property
    def all_reveals(self) -> tuple[bool, ...]:
        return tuple(card.revealed for card in self.cards)

    @property
    def revealed_card_indexes(self) -> tuple[int, ...]:
        return tuple(i for i, card in enumerate(self.cards) if card.revealed)

    @property
    def unrevealed_cards(self) -> Cards[C]:
        return tuple(card for card in self.cards if not card.revealed)

    @property
    def revealed_cards(self) -> Cards[C]:
        return tuple(card for card in self.cards if card.revealed)

    @property
    def censored(self) -> Board[C]:
        return self.__class__(language=self.language, cards=[card.censored for card in self.cards])

    @property
    def as_table(self) -> BeautifulTable:
        from beautifultable import (  # pylint: disable=import-outside-toplevel
            BeautifulTable,
        )

        table = BeautifulTable()
        cols, rows = two_integer_factors(self.size)
        for i in range(rows):
            start_index, end_index = i * cols, (i + 1) * cols
            row = self.cards[start_index:end_index]
            table.rows.append(row)
        return table

    @property
    def printable_string(self) -> str:
        table = self.as_table
        for row in table.rows:
            for i, card in enumerate(row):
                row[i] = LTR + str(card)
        return str(table)

    def cards_for_color(self, card_color: str) -> Cards[C]:
        return tuple(card for card in self.cards if card.color == card_color)

    def revealed_cards_for_color(self, card_color: str) -> Cards[C]:
        return tuple(card for card in self.cards if card.color == card_color and card.revealed)

    def unrevealed_cards_for_color(self, card_color: str) -> Cards[C]:
        return tuple(card for card in self.cards if card.color == card_color and not card.revealed)

    def find_card_index(self, word: str) -> int:
        formatted_word = canonical_format(word)
        try:
            return self.all_words.index(formatted_word)
        except ValueError as e:
            raise CardNotFoundError(word) from e

    def reset_state(self):
        for card in self.cards:
            card.revealed = False


@dataclass
class Vocabulary:
    language: str
    words: Collection[str]


def two_integer_factors(n: int) -> tuple[int, int]:
    x = math.floor(math.sqrt(n))
    if x == 0:
        return 0, 0
    while n % x != 0:
        x -= 1
    return n // x, x
