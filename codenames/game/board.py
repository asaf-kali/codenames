from __future__ import annotations

import math
from functools import cached_property
from typing import TYPE_CHECKING, Iterable, List, Tuple, Union

from pydantic import validator

from codenames.game.base import BaseModel, WordGroup, canonical_format
from codenames.game.card import Card, Cards
from codenames.game.color import CardColor
from codenames.game.exceptions import CardNotFoundError

if TYPE_CHECKING:
    from beautifultable import BeautifulTable

LTR = "\u200E"


class Board(BaseModel):
    cards: List[Card]

    @validator("cards")
    def convert_cards(cls, cards: Iterable[Card]):  # pylint: disable=no-self-argument
        return list(cards)

    def __getitem__(self, item: Union[int, str]) -> Card:
        if isinstance(item, str):
            item = self.find_card_index(item)
        if not isinstance(item, int):
            raise IndexError(f"Illegal index type for card: {item}")
        if item < 0 or item >= self.size:
            raise IndexError(f"Card index out of bounds: {item}")
        return self.cards[item]

    def __iter__(self):
        return iter(self.cards)

    def __len__(self) -> int:
        return self.size

    def __str__(self) -> str:
        return self.printable_string

    @property
    def size(self) -> int:
        return len(self.cards)

    @cached_property
    def all_words(self) -> WordGroup:
        return tuple(card.formatted_word for card in self.cards)

    @property
    def all_colors(self) -> Tuple[CardColor, ...]:
        return tuple(card.color for card in self.cards)  # type: ignore

    @property
    def all_reveals(self) -> Tuple[bool, ...]:
        return tuple(card.revealed for card in self.cards)

    @property
    def revealed_card_indexes(self) -> Tuple[int, ...]:
        return tuple(i for i, card in enumerate(self.cards) if card.revealed)

    @property
    def unrevealed_cards(self) -> Cards:
        return tuple(card for card in self.cards if not card.revealed)

    @property
    def revealed_cards(self) -> Cards:
        return tuple(card for card in self.cards if card.revealed)

    @cached_property
    def red_cards(self) -> Cards:
        return self.cards_for_color(CardColor.RED)

    @cached_property
    def blue_cards(self) -> Cards:
        return self.cards_for_color(CardColor.BLUE)

    @property
    def censured(self) -> Board:
        return Board(cards=[card.censored for card in self.cards])

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

    def cards_for_color(self, card_color: CardColor) -> Cards:
        return tuple(card for card in self.cards if card.color == card_color)

    def revealed_cards_for_color(self, card_color: CardColor) -> Cards:
        return tuple(card for card in self.cards if card.color == card_color and card.revealed)

    def unrevealed_cards_for_color(self, card_color: CardColor) -> Cards:
        return tuple(card for card in self.cards if card.color == card_color and not card.revealed)

    def find_card_index(self, word: str) -> int:
        formatted_word = canonical_format(word)
        if formatted_word not in self.all_words:
            raise CardNotFoundError(word)
        return self.all_words.index(formatted_word)

    def reset_state(self):
        for card in self.cards:
            card.revealed = False


def two_integer_factors(n: int) -> Tuple[int, int]:
    x = math.floor(math.sqrt(n))
    if x == 0:
        return 0, 0
    while n % x != 0:
        x -= 1
    return n // x, x
