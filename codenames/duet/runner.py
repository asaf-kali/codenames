from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterator

from codenames.duet.board import DuetBoard
from codenames.duet.player import DuetPlayer
from codenames.duet.score import GameResult
from codenames.duet.state import DuetGameState, DuetSide
from codenames.generic.exceptions import InvalidGuess
from codenames.generic.move import GivenGuess
from codenames.generic.player import Operative, PlayerRole, Spymaster
from codenames.generic.runner import (
    SEPARATOR,
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)


@dataclass
class DuetGamePlayers:
    player_a: DuetPlayer
    player_b: DuetPlayer

    @property
    def team_a(self) -> TeamPlayers:
        return TeamPlayers(spymaster=self.player_a, operative=self.player_b)

    @property
    def team_b(self) -> TeamPlayers:
        return TeamPlayers(spymaster=self.player_b, operative=self.player_a)

    def __iter__(self) -> Iterator[DuetPlayer]:
        return iter([self.player_a, self.player_b])


class DuetGameRunner:
    def __init__(self, players: DuetGamePlayers, state: DuetGameState | None = None, board: DuetBoard | None = None):
        self.players = players
        if (not state and not board) or (state and board):
            raise ValueError("Exactly one of state or board must be provided.")
        self.state = state or DuetGameState.from_board(board=board)  # type: ignore[arg-type]
        self.clue_given_subscribers: list[ClueGivenSubscriber] = []
        self.guess_given_subscribers: list[GuessGivenSubscriber] = []

    @property
    def current_team(self) -> TeamPlayers:
        if self.state.current_playing_side == DuetSide.SIDE_A:
            return self.players.team_a
        return self.players.team_b

    @property
    def current_role(self) -> PlayerRole:
        return self.state.current_side_state.current_player_role

    def run_game(self) -> GameResult:
        self._notify_game_starts()
        result = self._run_rounds()
        suffix = "win!" if result.win else "lose!"
        log.info(f"{SEPARATOR}{result.reason}, you {suffix}")
        return result

    def _notify_game_starts(self):
        self.players.player_a.on_game_start(board=self.state.side_a.board)
        self.players.player_a.on_game_start(board=self.state.side_b.board.censored)
        self.players.player_b.on_game_start(board=self.state.side_b.board)
        self.players.player_b.on_game_start(board=self.state.side_a.board.censored)

    def _run_rounds(self) -> GameResult:
        while not self.state.is_game_over:
            self._run_side_turn()
        return self.state.game_result  # type: ignore

    def _run_side_turn(self):
        side_turn = self.state.current_playing_side
        log.info(f"{SEPARATOR}{wrap(side_turn)} turn.")
        team = self.current_team
        if not self.state.is_sudden_death:
            self._get_clue_from(spymaster=team.spymaster)
        while not self.state.is_game_over and self.current_role == PlayerRole.OPERATIVE:
            self._get_guess_from(operative=team.operative)
            # In sudden death, we get one guess per operative turn
            if self.state.is_sudden_death:
                break

    def _get_clue_from(self, spymaster: Spymaster):
        state, dual_state = self.state.current_side_state, self.state.current_dual_state
        spymaster_state = state.get_spymaster_state(dual_state=dual_state)
        clue = spymaster.give_clue(game_state=spymaster_state)
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
        state, dual_state = self.state.current_side_state, self.state.current_dual_state
        operative_state = state.get_operative_state(dual_state=dual_state)
        while True:
            guess = operative.guess(game_state=operative_state)
            try:
                given_guess = self.state.process_guess(guess=guess)
            except InvalidGuess:
                continue
            for subscriber in self.guess_given_subscribers:
                subscriber(operative, guess)
            return given_guess
