from __future__ import annotations

from dataclasses import dataclass
from typing import Collection, Iterator

from codenames.classic.color import ClassicTeam
from codenames.generic.player import Operative, Player, PlayerRole, Spymaster


@dataclass(frozen=True)
class TeamPlayers:
    spymaster: Spymaster
    operative: Operative

    def __post_init__(self):
        if self.spymaster.team != self.operative.team:
            raise ValueError("Spymaster and Operative must be on the same team")


@dataclass(frozen=True)
class GamePlayers:
    blue_team: TeamPlayers
    red_team: TeamPlayers

    @staticmethod
    def from_collection(players: Collection[Player]) -> GamePlayers:
        if len(players) != 4:
            raise ValueError("There must be exactly 4 players")
        blue_team = find_team(players, team=ClassicTeam.BLUE)
        red_team = find_team(players, team=ClassicTeam.RED)
        return GamePlayers(blue_team=blue_team, red_team=red_team)

    @property
    def spymasters(self) -> tuple[Spymaster, Spymaster]:
        return self.blue_team.spymaster, self.red_team.spymaster

    @property
    def operatives(self) -> tuple[Operative, Operative]:
        return self.blue_team.operative, self.red_team.operative

    @property
    def all(self) -> tuple[Spymaster, Operative, Spymaster, Operative]:
        return self.blue_team.spymaster, self.blue_team.operative, self.red_team.spymaster, self.red_team.operative

    def __iter__(self) -> Iterator[Player]:
        return iter(self.all)

    def get_player(self, team: ClassicTeam, role: PlayerRole) -> Player:
        team_players = self.blue_team if team == ClassicTeam.BLUE else self.red_team
        if role == PlayerRole.SPYMASTER:
            return team_players.spymaster
        return team_players.operative


def find_team(players: Collection[Player], team: ClassicTeam) -> TeamPlayers:
    spymaster = operative = None
    for player in players:
        if player.team == team:
            if isinstance(player, Spymaster):
                spymaster = player
            elif isinstance(player, Operative):
                operative = player
            else:
                raise ValueError(f"Player {player} is not a Spymaster or Operative")
    if spymaster is None:
        raise ValueError(f"No Spymaster found for team {team}")
    if operative is None:
        raise ValueError(f"No Operative found for team {team}")
    return TeamPlayers(spymaster=spymaster, operative=operative)
