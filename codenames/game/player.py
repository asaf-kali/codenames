from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

from codenames.game import (
    Board,
    CardColor,
    GivenGuess,
    GivenHint,
    Guess,
    Hint,
    TeamColor,
)

if TYPE_CHECKING:
    from codenames.game import GuesserGameState, HinterGameState


class PlayerRole(str, Enum):
    HINTER = "Hinter"
    GUESSER = "Guesser"

    @property
    def other(self) -> "PlayerRole":
        if self == PlayerRole.HINTER:
            return PlayerRole.GUESSER
        return PlayerRole.HINTER


class Player:
    def __init__(self, name: str):
        self.name: str = name
        self.team_color: Optional[TeamColor] = None

    def __str__(self):
        team = ""
        if self.team_color:
            team = f" {self.team_color}"
        return f"{self.name} -{team} {self.role.value}"

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

    def pick_hint(self, game_state: "HinterGameState") -> Hint:
        raise NotImplementedError()


class Guesser(Player):
    @property
    def role(self) -> PlayerRole:
        return PlayerRole.GUESSER

    def guess(self, game_state: "GuesserGameState") -> Guess:
        raise NotImplementedError()


@dataclass(frozen=True)
class Team:
    hinter: Hinter
    guesser: Guesser
    team_color: TeamColor

    def __iter__(self):
        return iter([self.hinter, self.guesser])
