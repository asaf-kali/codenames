from __future__ import annotations

import math
import random
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from pydantic import validator

from codenames.game.base import BaseModel, WordGroup, canonical_format
from codenames.game.card import Card, Cards
from codenames.game.color import CardColor, TeamColor
from codenames.game.exceptions import CardNotFoundError

if TYPE_CHECKING:
    from beautifultable import BeautifulTable

LTR = "\u200E"


class Board(BaseModel):
    language: str
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

    def __iter__(self) -> Iterator[Card]:  # type: ignore
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

    @cached_property
    def gray_cards(self) -> Cards:
        return self.cards_for_color(CardColor.GRAY)

    @cached_property
    def black_cards(self) -> Cards:
        return self.cards_for_color(CardColor.BLACK)

    @property
    def censured(self) -> Board:
        return Board(language=self.language, cards=[card.censored for card in self.cards])

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

    @staticmethod
    def from_vocabulary(
        language: str,
        vocabulary: List[str],
        board_size: int = 25,
        black_amount: int = 1,
        seed: Optional[int] = None,
        first_team: Optional[TeamColor] = None,
    ) -> Board:
        if seed:
            random.seed(seed)

        first_team = first_team or random.choice(list(TeamColor))
        red_amount = blue_amount = board_size // 3
        if first_team == TeamColor.RED:
            red_amount += 1
        else:
            blue_amount += 1
        gray_amount = board_size - red_amount - blue_amount - black_amount

        words_list, red_words = _extract_random_subset(vocabulary, red_amount)
        words_list, blue_words = _extract_random_subset(words_list, blue_amount)
        words_list, gray_words = _extract_random_subset(words_list, gray_amount)
        words_list, black_words = _extract_random_subset(words_list, black_amount)

        red_cards = [Card(word=word, color=CardColor.RED) for word in red_words]
        blue_cards = [Card(word=word, color=CardColor.BLUE) for word in blue_words]
        gray_cards = [Card(word=word, color=CardColor.GRAY) for word in gray_words]
        black_cards = [Card(word=word, color=CardColor.BLACK) for word in black_words]

        all_cards = red_cards + blue_cards + gray_cards + black_cards
        random.shuffle(all_cards)
        return Board(language=language, cards=all_cards)

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


def _extract_random_subset(elements: Sequence, subset_size: int) -> Tuple[tuple, tuple]:
    sample = tuple(random.sample(elements, k=subset_size))
    remaining = tuple(e for e in elements if e not in sample)
    return remaining, sample
