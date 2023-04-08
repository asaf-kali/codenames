from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from codenames.game.base import BaseModel, WordGroup, canonical_format
from codenames.game.card import Card
from codenames.game.color import TeamColor
from codenames.utils.formatting import wrap

PASS_GUESS = -1
QUIT_GAME = -2


class Hint(BaseModel):
    word: str
    card_amount: int
    for_words: Optional[WordGroup] = None

    def __str__(self) -> str:
        result = f"{wrap(self.word)} {wrap(self.card_amount)}"
        if self.for_words:
            result += f" for: {self.for_words}"
        return result


class GivenHint(BaseModel):
    word: str
    card_amount: int
    team_color: TeamColor

    def __str__(self) -> str:
        return f"{wrap(self.word)} {wrap(self.card_amount)}"

    def __hash__(self) -> int:
        return self.hash

    @cached_property
    def hash(self) -> int:
        return hash(f"{self.formatted_word}{self.card_amount}{self.team_color}")

    @cached_property
    def formatted_word(self) -> str:
        return canonical_format(self.word)


class Guess(BaseModel):
    card_index: int


class GivenGuess(BaseModel):
    given_hint: GivenHint
    guessed_card: Card

    def __str__(self) -> str:
        result = "correct!" if self.correct else "wrong!"
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


@dataclass
class Move:
    @property
    def team_color(self) -> TeamColor:
        raise NotImplementedError()


@dataclass
class HintMove(Move):
    given_hint: GivenHint

    @property
    def team_color(self) -> TeamColor:
        return self.given_hint.team_color


@dataclass
class GuessMove(Move):
    given_guess: GivenGuess

    @property
    def team_color(self) -> TeamColor:
        return self.given_guess.team


@dataclass
class PassMove(Move):
    team: TeamColor

    @property
    def team_color(self) -> TeamColor:
        return self.team
