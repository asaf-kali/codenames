import json
import math
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Iterable, List, Optional, Set, Tuple, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import validator

from codenames.game.exceptions import CardNotFoundError
from codenames.utils import wrap

if TYPE_CHECKING:
    from beautifultable import BeautifulTable
WordGroup = Tuple[str, ...]


def canonical_format(word: str) -> str:
    return word.replace("_", " ").strip().lower()


def get_cached_properties_names(cls: type) -> Set[str]:
    return {k for k, v in cls.__dict__.items() if isinstance(v, cached_property)}


class BaseModel(PydanticBaseModel):
    class Config:
        keep_untouched = (cached_property,)

    @classmethod
    def from_json(cls, s: str) -> "BaseModel":
        data = json.loads(s)
        return cls(**data)

    def dict(self, *args, **kwargs) -> dict:
        result = super().dict(*args, **kwargs)
        cached_properties = get_cached_properties_names(self.__class__)
        include = kwargs.get("include", None) or set()
        for k in cached_properties:
            if k not in include:
                result.pop(k, None)
        return result


class CardColor(str, Enum):
    BLUE = "Blue"
    RED = "Red"
    GRAY = "Gray"
    BLACK = "Black"

    def __str__(self):
        return self.value

    @property
    def as_team_color(self) -> "TeamColor":
        if self == CardColor.RED:
            return TeamColor.RED
        if self == CardColor.BLUE:
            return TeamColor.BLUE
        raise ValueError(f"No such team color: {self.value}.")

    @property
    def opponent(self) -> "CardColor":
        return self.as_team_color.opponent.as_card_color

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]


CARD_COLOR_TO_EMOJI = {
    CardColor.RED: "🟥",
    CardColor.BLUE: "🟦",
    CardColor.GRAY: "⬜",
    CardColor.BLACK: "💀",
}


class TeamColor(str, Enum):
    BLUE = "Blue"
    RED = "Red"

    def __str__(self):
        return self.value

    @property
    def opponent(self) -> "TeamColor":
        return TeamColor.BLUE if self == TeamColor.RED else TeamColor.RED

    @property
    def as_card_color(self) -> CardColor:
        return CardColor.BLUE if self == TeamColor.BLUE else CardColor.RED


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
    def censored(self) -> "Card":
        if self.revealed:
            return self
        return Card(word=self.word, color=None, revealed=self.revealed)

    @cached_property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


Cards = Tuple[Card, ...]
LTR = "\u200E"


def two_integer_factors(n: int) -> Tuple[int, int]:
    x = math.floor(math.sqrt(n))
    if x == 0:
        return 0, 0
    while n % x != 0:
        x -= 1
    return n // x, x


class Board(BaseModel):
    cards: List[Card]

    @validator("cards")
    def convert_cards(cls, cards: Iterable[Card]):
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
    def censured(self) -> "Board":
        return Board(cards=[card.censored for card in self.cards])

    @property
    def as_table(self) -> "BeautifulTable":
        from beautifultable import BeautifulTable

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
        for i, row in enumerate(table.rows):
            for j, card in enumerate(row):
                row[j] = LTR + str(card)
        return str(table)

    def cards_for_color(self, card_color: CardColor) -> Cards:
        return tuple(card for card in self.cards if card.color == card_color)

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


class Hint(BaseModel):
    word: str
    card_amount: int
    for_words: Optional[WordGroup] = None

    def __str__(self) -> str:
        result = f"Said {wrap(self.word)} {wrap(self.card_amount)}"
        if self.for_words:
            result += f" for: {self.for_words}"
        return result


class GivenHint(BaseModel):
    word: str
    card_amount: int
    team_color: TeamColor

    def __str__(self) -> str:
        return f"{self.word}, {self.card_amount}"

    @cached_property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


class Guess(BaseModel):
    card_index: int


class GivenGuess(BaseModel):
    given_hint: GivenHint
    guessed_card: Card

    def __str__(self) -> str:
        result = "Correct!" if self.correct else "Wrong!"
        return f"'{self.guessed_card}', {result}"

    @property
    def correct(self) -> bool:
        return self.team.as_card_color == self.guessed_card.color

    def dict(self, *args, **kwargs) -> dict:
        result = super().dict(*args, **kwargs)
        result["correct"] = self.correct
        return result

    @cached_property
    def team(self) -> TeamColor:
        return self.given_hint.team_color
