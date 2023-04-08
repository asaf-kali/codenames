from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from codenames.game.color import CardColor, TeamColor
from codenames.utils.formatting import camel_case_split

if TYPE_CHECKING:
    from codenames.game.board import Board
    from codenames.game.move import GivenGuess, GivenHint, Guess, Hint
    from codenames.game.state import GuesserGameState, HinterGameState


class PlayerRole(str, Enum):
    HINTER = "HINTER"
    GUESSER = "GUESSER"

    def __str__(self) -> str:
        return self.value.title()

    @property
    def other(self) -> PlayerRole:
        if self == PlayerRole.HINTER:
            return PlayerRole.GUESSER
        return PlayerRole.HINTER


class Player:
    def __init__(self, name: str, team_color: Optional[TeamColor] = None):
        self.name = name
        self.team_color = team_color

    def __str__(self):
        team = str(self.team_color) if self.team_color else None
        role = str(self.role)
        class_name = self.clazz
        if role.lower() in class_name.lower():
            role = None
        parts = [part for part in (team, role, class_name) if part is not None]
        description = " ".join(parts)
        return f"{self.name} | {description}"

    @property
    def clazz(self) -> str:
        class_name = self.__class__.__name__
        split = camel_case_split(class_name)
        clazz = " ".join(split)
        return clazz

    @property
    def role(self) -> PlayerRole:
        raise NotImplementedError()

    @property
    def is_human(self) -> bool:
        return False

    @property
    def team_card_color(self) -> CardColor:
        if self.team_color is None:
            raise ValueError("Team color not set")
        return self.team_color.as_card_color

    def on_game_start(self, language: str, board: Board):
        pass

    def on_hint_given(self, given_hint: GivenHint):
        pass

    def on_guess_given(self, given_guess: GivenGuess):
        pass


class Hinter(Player):
    @property
    def role(self) -> PlayerRole:
        return PlayerRole.HINTER

    def pick_hint(self, game_state: HinterGameState) -> Hint:
        raise NotImplementedError()


class Guesser(Player):
    @property
    def role(self) -> PlayerRole:
        return PlayerRole.GUESSER

    def guess(self, game_state: GuesserGameState) -> Guess:
        raise NotImplementedError()


@dataclass(frozen=True)
class Team:
    hinter: Hinter
    guesser: Guesser
    team_color: TeamColor

    @property
    def players(self) -> Tuple[Hinter, Guesser]:
        return self.hinter, self.guesser

    def __iter__(self):
        return iter(self.players)
