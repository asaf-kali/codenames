from __future__ import annotations

import abc

from pydantic import BaseModel

from codenames.generic.board import WordGroup
from codenames.generic.card import Card, CardColor, canonical_format
from codenames.generic.team import Team
from codenames.utils.formatting import wrap

PASS_GUESS = -1
QUIT_GAME = -2


class Clue(BaseModel):
    word: str
    card_amount: int
    for_words: WordGroup | None = None

    def __str__(self) -> str:
        result = f"{wrap(self.word)} {wrap(self.card_amount)}"
        if self.for_words:
            result += f" for: {self.for_words}"
        return result


class GivenClue[T: Team](BaseModel, abc.ABC):
    word: str
    card_amount: int
    team: T

    def __str__(self) -> str:
        return f"{wrap(self.word)} {wrap(self.card_amount)}"

    def __hash__(self) -> int:
        return self.hash

    @property
    def hash(self) -> int:
        return hash(f"{self.formatted_word}{self.card_amount}")

    @property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


class Guess(BaseModel):
    card_index: int


class GivenGuess[C: CardColor, T: Team](BaseModel, abc.ABC):
    guessed_card: Card[C]
    for_clue: GivenClue[T]

    def __str__(self) -> str:
        result = "correct!" if self.correct else "wrong!"
        return f"'{self.guessed_card}', {result}"

    @property
    def correct(self) -> bool:
        card_color = self.guessed_card.color
        if not card_color:
            msg = f"Card {self.guessed_card} has no color set"
            raise ValueError(msg)
        return self.for_clue.team.as_card_color == card_color

    @property
    def team(self) -> T:
        return self.for_clue.team
