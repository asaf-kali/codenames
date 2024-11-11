from __future__ import annotations

from abc import ABC
from enum import StrEnum
from typing import TYPE_CHECKING, Generic, TypeVar

from codenames.utils.formatting import camel_case_split

if TYPE_CHECKING:
    from codenames.generic.board import Board
    from codenames.generic.move import Clue, GivenClue, GivenGuess, Guess
    from codenames.generic.state import OperativeState, SpymasterState


class Team(StrEnum):
    @property
    def as_card_color(self) -> str:
        raise NotImplementedError


T = TypeVar("T", bound=Team)


class PlayerRole(StrEnum):
    SPYMASTER = "SPYMASTER"
    OPERATIVE = "OPERATIVE"

    @property
    def other(self) -> PlayerRole:
        return PlayerRole.SPYMASTER if self == PlayerRole.OPERATIVE else PlayerRole.OPERATIVE


class Player(Generic[T], ABC):
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

    def on_game_start(self, board: Board):
        pass

    def on_clue_given(self, given_clue: GivenClue):
        pass

    def on_guess_given(self, given_guess: GivenGuess):
        pass


class Spymaster(Player[T], ABC):
    def give_clue(self, game_state: SpymasterState) -> Clue:
        raise NotImplementedError()


class Operative(Player[T], ABC):
    def guess(self, game_state: OperativeState) -> Guess:
        raise NotImplementedError()
