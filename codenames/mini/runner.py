from __future__ import annotations

import logging

from codenames.duet.board import DuetBoard
from codenames.duet.score import GameResult
from codenames.generic.exceptions import InvalidGuess
from codenames.generic.move import GivenGuess
from codenames.generic.player import Operative, PlayerRole, Spymaster
from codenames.generic.runner import (
    SEPARATOR,
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from codenames.mini.state import MiniGameState

log = logging.getLogger(__name__)


class MiniGameRunner:
    def __init__(self, players: TeamPlayers, state: MiniGameState | None = None, board: DuetBoard | None = None):
        self.players = players
        if (not state and not board) or (state and board):
            raise ValueError("Exactly one of state or board must be provided.")
        self.state = state or MiniGameState.from_board(board=board)  # type: ignore[arg-type]
        self.clue_given_subscribers: list[ClueGivenSubscriber] = []
        self.guess_given_subscribers: list[GuessGivenSubscriber] = []

    @property
    def spymaster(self) -> Spymaster:
        return self.players.spymaster

    @property
    def operative(self) -> Operative:
        return self.players.operative

    @property
    def current_role(self) -> PlayerRole:
        return self.state.current_player_role

    def run_game(self) -> GameResult:
        self._notify_game_starts()
        result = self._run_rounds()
        suffix = "win!" if result.win else "lose!"
        log.info(f"{SEPARATOR}{result.reason}, you {suffix}")
        return result

    def _notify_game_starts(self):
        self.spymaster.on_game_start(board=self.state.board)
        self.operative.on_game_start(board=self.state.board.censored)

    def _run_rounds(self) -> GameResult:
        while not self.state.is_game_over:
            self._run_turn()
        return self.state.game_result  # type: ignore

    def _run_turn(self):
        if not self.state.is_sudden_death:
            self._get_clue_from(spymaster=self.spymaster)
        while not self.state.is_game_over and self.current_role == PlayerRole.OPERATIVE:
            self._get_guess_from(operative=self.operative)

    def _get_clue_from(self, spymaster: Spymaster):
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
            except InvalidGuess:
                continue
            for subscriber in self.guess_given_subscribers:
                subscriber(operative, guess)
            return given_guess
