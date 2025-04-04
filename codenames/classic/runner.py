from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Collection, Iterator

from codenames.classic.board import ClassicBoard
from codenames.classic.state import ClassicGameState
from codenames.classic.team import ClassicTeam
from codenames.classic.winner import Winner
from codenames.generic.exceptions import InvalidGuess
from codenames.generic.move import GivenGuess
from codenames.generic.player import Operative, Player, PlayerRole, Spymaster
from codenames.generic.runner import (
    SEPARATOR,
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClassicGamePlayers:
    blue_team: TeamPlayers
    red_team: TeamPlayers

    @staticmethod
    def from_collection(*players: Player) -> ClassicGamePlayers:
        if len(players) != 4:
            raise ValueError("There must be exactly 4 players")
        blue_team = find_team(players, team=ClassicTeam.BLUE)
        red_team = find_team(players, team=ClassicTeam.RED)
        return ClassicGamePlayers(blue_team=blue_team, red_team=red_team)

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


class ClassicGameRunner:
    def __init__(
        self,
        players: ClassicGamePlayers,
        state: ClassicGameState | None = None,
        board: ClassicBoard | None = None,
    ):
        self.players = players
        if not state:
            if not board:
                raise ValueError("Exactly one of state or board must be provided.")
            state = ClassicGameState.from_board(board=board)
        self.state = state
        self.clue_given_subscribers: list[ClueGivenSubscriber] = []
        self.guess_given_subscribers: list[GuessGivenSubscriber] = []

    @property
    def spymasters(self) -> tuple[Spymaster, Spymaster]:
        return self.players.spymasters

    @property
    def operatives(self) -> tuple[Operative, Operative]:
        return self.players.operatives

    @property
    def blue_team(self) -> TeamPlayers:
        return self.players.blue_team

    @property
    def red_team(self) -> TeamPlayers:
        return self.players.red_team

    @property
    def winner(self) -> Winner | None:
        return self.state.winner

    def run_game(self) -> Winner:
        self._notify_game_starts()
        winner = self._run_rounds()
        log.info(f"{SEPARATOR}{winner.reason.value}, {wrap(winner.team)} team wins!")
        return winner

    def _notify_game_starts(self):
        censored_board = self.state.board.censored
        for spymaster in self.spymasters:
            spymaster.on_game_start(board=self.state.board)
        for operative in self.operatives:
            operative.on_game_start(board=censored_board)

    def _run_rounds(self) -> Winner:
        while not self.state.is_game_over:
            current_team = self.blue_team if self.state.current_team == ClassicTeam.BLUE else self.red_team
            self._run_team_turn(team=current_team)
        return self.winner  # type: ignore

    def _run_team_turn(self, team: TeamPlayers):
        self._get_clue_from(spymaster=team.spymaster)
        while self.state.left_guesses > 0:
            self._get_guess_from(operative=team.operative)

    def _get_clue_from(self, spymaster: Spymaster):
        log.info(f"{SEPARATOR}{wrap(self.state.current_team)} turn.")
        clue = spymaster.give_clue(game_state=self.state.spymaster_state)
        for subscriber in self.clue_given_subscribers:
            subscriber(spymaster, clue)
        given_clue = self.state.process_clue(clue=clue)
        if given_clue is None:
            return
        for player in self.players:
            player.on_clue_given(given_clue=given_clue)

    def _get_guess_from(self, operative: Operative):
        given_guess = self._get_guess_until_valid(operative)
        if given_guess is None:
            return
        for player in self.players:
            player.on_guess_given(given_guess=given_guess)

    def _get_guess_until_valid(self, operative: Operative) -> GivenGuess | None:
        while True:
            guess = operative.guess(game_state=self.state.operative_state)
            try:
                given_guess = self.state.process_guess(guess=guess)
                for subscriber in self.guess_given_subscribers:
                    subscriber(operative, guess)
                return given_guess
            except InvalidGuess:
                pass


def find_team(players: Collection[Player], team: ClassicTeam) -> TeamPlayers:
    spymaster = operative = None
    for player in players:
        if player.team == team:
            if isinstance(player, Spymaster):
                spymaster = player
            elif isinstance(player, Operative):
                operative = player
            else:
                msg = f"Player {player} is not a Spymaster or Operative"
                raise ValueError(msg)
    if spymaster is None:
        msg = f"No Spymaster found for team {team}"
        raise ValueError(msg)
    if operative is None:
        msg = f"No Operative found for team {team}"
        raise ValueError(msg)
    return TeamPlayers(spymaster=spymaster, operative=operative)
