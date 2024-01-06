from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Collection, Iterator, Tuple

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
    def __init__(self, name: str, team_color: TeamColor):
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
        return self.team_color.as_card_color

    def on_game_start(self, board: Board):
        pass

    def on_hint_given(self, given_hint: GivenHint):
        pass

    def on_guess_given(self, given_guess: GivenGuess):
        pass


class Hinter(Player, ABC):
    @property
    def role(self) -> PlayerRole:
        return PlayerRole.HINTER

    def pick_hint(self, game_state: HinterGameState) -> Hint:
        raise NotImplementedError()


class Guesser(Player, ABC):
    @property
    def role(self) -> PlayerRole:
        return PlayerRole.GUESSER

    def guess(self, game_state: GuesserGameState) -> Guess:
        raise NotImplementedError()


@dataclass(frozen=True)
class Team:
    hinter: Hinter
    guesser: Guesser

    def __post_init__(self):
        if self.hinter.team_color != self.guesser.team_color:
            raise ValueError(f"Team hinter {self.hinter} and guesser {self.guesser} must have the same team color")


@dataclass(frozen=True)
class GamePlayers:
    blue_team: Team
    red_team: Team

    @staticmethod
    def from_collection(players: Collection[Player]) -> GamePlayers:
        if len(players) != 4:
            raise ValueError("There must be exactly 4 players")
        blue_team = find_team(players, team_color=TeamColor.BLUE)
        red_team = find_team(players, team_color=TeamColor.RED)
        return GamePlayers(blue_team=blue_team, red_team=red_team)

    @property
    def hinters(self) -> Tuple[Hinter, Hinter]:
        return self.blue_team.hinter, self.red_team.hinter

    @property
    def guessers(self) -> Tuple[Guesser, Guesser]:
        return self.blue_team.guesser, self.red_team.guesser

    @property
    def all(self) -> Tuple[Hinter, Guesser, Hinter, Guesser]:
        return self.blue_team.hinter, self.blue_team.guesser, self.red_team.hinter, self.red_team.guesser

    def __iter__(self) -> Iterator[Player]:
        return iter(self.all)

    def get_player(self, team_color: TeamColor, role: PlayerRole) -> Player:
        team = self.blue_team if team_color == TeamColor.BLUE else self.red_team
        if role == PlayerRole.HINTER:
            return team.hinter
        return team.guesser


def find_team(players: Collection[Player], team_color: TeamColor) -> Team:
    hinter = guesser = None
    for player in players:
        if player.team_color == team_color:
            if isinstance(player, Hinter):
                hinter = player
            elif isinstance(player, Guesser):
                guesser = player
            else:
                raise ValueError(f"Player {player} is not a Hinter or Guesser")
    if hinter is None:
        raise ValueError(f"No Hinter found for team {team_color}")
    if guesser is None:
        raise ValueError(f"No Guesser found for team {team_color}")
    return Team(hinter=hinter, guesser=guesser)
