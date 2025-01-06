from __future__ import annotations

import logging

from pydantic import BaseModel

from codenames.generic.board import Board, WordGroup
from codenames.generic.card import CardColor
from codenames.generic.move import Clue, GivenClue, GivenGuess
from codenames.generic.team import Team

log = logging.getLogger(__name__)


class PlayerState[C: CardColor, T: Team](BaseModel):
    """
    Represents all the information that is available to any player
    """

    board: Board[C]
    current_team: T
    given_clues: list[GivenClue[T]] = []
    given_guesses: list[GivenGuess[C, T]] = []

    @property
    def given_clue_words(self) -> WordGroup:
        return tuple(clue.formatted_word for clue in self.given_clues)

    @property
    def illegal_clue_words(self) -> WordGroup:
        return *self.board.all_words, *self.given_clue_words


class SpymasterState[C: CardColor, T: Team](PlayerState[C, T]):
    """
    Represents all the information that is available to a Spymaster.
    """

    clues: list[Clue] = []


class OperativeState[C: CardColor, T: Team](PlayerState[C, T]):
    """
    Represents all the information that is available to an Operative.
    """

    @property
    def current_clue(self) -> GivenClue[T]:
        return self.given_clues[-1]

    @property
    def turn_guesses(self) -> list[GivenGuess[C, T]]:
        return [guess for guess in self.given_guesses if guess.for_clue == self.current_clue]


class TeamScore(BaseModel):
    total: int
    revealed: int

    @staticmethod
    def new(total: int) -> TeamScore:
        return TeamScore(total=total, revealed=0)

    @property
    def unrevealed(self) -> int:
        return self.total - self.revealed
