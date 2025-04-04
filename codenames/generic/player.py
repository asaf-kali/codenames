from __future__ import annotations

import abc
from enum import StrEnum
from typing import TYPE_CHECKING

from codenames.generic.card import CardColor
from codenames.generic.state import OperativeState, SpymasterState
from codenames.generic.team import Team
from codenames.utils.formatting import camel_case_split

if TYPE_CHECKING:
    from codenames.generic.board import Board
    from codenames.generic.move import Clue, GivenClue, GivenGuess, Guess


class PlayerRole(StrEnum):
    SPYMASTER = "SPYMASTER"
    OPERATIVE = "OPERATIVE"

    @property
    def other(self) -> PlayerRole:
        return PlayerRole.SPYMASTER if self == PlayerRole.OPERATIVE else PlayerRole.OPERATIVE


class Player[C: CardColor, T: Team]:
    def __init__(self, name: str, team: T):
        self.name = name
        self.team = team

    def __str__(self):
        return f"{self.name} | {self.team.title()} {self.clazz}"

    @property
    def clazz(self) -> str:
        class_name = self.__class__.__name__
        split = camel_case_split(class_name)
        clazz = " ".join(split)
        return clazz

    @property
    def is_human(self) -> bool:
        return False

    def on_game_start(self, board: Board[C]):
        pass

    def on_clue_given(self, given_clue: GivenClue[T]):
        pass

    def on_guess_given(self, given_guess: GivenGuess[C, T]):
        pass


class Spymaster[C: CardColor, T: Team, S: SpymasterState](Player[C, T], abc.ABC):
    @abc.abstractmethod
    def give_clue(self, game_state: S) -> Clue:
        raise NotImplementedError


class Operative[C: CardColor, T: Team, S: OperativeState](Player[C, T], abc.ABC):
    @abc.abstractmethod
    def guess(self, game_state: S) -> Guess:
        raise NotImplementedError
