import logging
from functools import cached_property
from typing import Callable, List, Optional, Tuple

from codenames.game.board import Board
from codenames.game.color import TeamColor
from codenames.game.exceptions import InvalidGuess
from codenames.game.move import GivenGuess, Guess, Hint
from codenames.game.player import GamePlayers, Guesser, Hinter, Team
from codenames.game.state import GameState, new_game_state
from codenames.game.winner import Winner
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)
SEPARATOR = "\n-----\n"
HintGivenSubscriber = Callable[[Hinter, Hint], None]
GuessGivenSubscriber = Callable[[Guesser, Guess], None]


class GameRunner:
    def __init__(self, players: GamePlayers, state: Optional[GameState] = None, board: Optional[Board] = None):
        self.players = players
        if (not state and not board) or (state and board):
            raise ValueError("Exactly one of state or board must be provided.")
        self.state = state or new_game_state(board=board)
        self.hint_given_subscribers: List[HintGivenSubscriber] = []
        self.guess_given_subscribers: List[GuessGivenSubscriber] = []

    @cached_property
    def hinters(self) -> Tuple[Hinter, Hinter]:
        return self.players.hinters

    @cached_property
    def guessers(self) -> Tuple[Guesser, Guesser]:
        return self.players.guessers

    @cached_property
    def blue_team(self) -> Team:
        return self.players.blue_team

    @cached_property
    def red_team(self) -> Team:
        return self.players.red_team

    @property
    def winner(self) -> Optional[Winner]:
        return self.state.winner

    def run_game(self) -> Winner:
        self._notify_game_starts()
        winner = self._run_rounds()
        log.info(f"{SEPARATOR}{winner.reason.value}, {wrap(winner.team_color)} team wins!")
        return winner

    def _notify_game_starts(self):
        censored_board = self.state.board.censured
        for hinter in self.hinters:
            hinter.on_game_start(board=self.state.board)
        for guesser in self.guessers:
            guesser.on_game_start(board=censored_board)

    def _run_rounds(self) -> Winner:
        while not self.state.is_game_over:
            current_team = self.blue_team if self.state.current_team_color == TeamColor.BLUE else self.red_team
            self._run_team_turn(team=current_team)
        return self.winner  # type: ignore

    def _run_team_turn(self, team: Team):
        self._get_hint_from(hinter=team.hinter)
        while self.state.left_guesses > 0:
            self._get_guess_from(guesser=team.guesser)

    def _get_hint_from(self, hinter: Hinter):
        log.info(f"{SEPARATOR}{wrap(self.state.current_team_color)} turn.")
        hint = hinter.pick_hint(game_state=self.state.hinter_state)
        for subscriber in self.hint_given_subscribers:
            subscriber(hinter, hint)
        given_hint = self.state.process_hint(hint)
        if given_hint is None:
            return
        for player in self.players:
            player.on_hint_given(given_hint=given_hint)

    def _get_guess_from(self, guesser: Guesser):
        given_guess = self._get_guess_until_valid(guesser)
        if given_guess is None:
            return
        for player in self.players:
            player.on_guess_given(given_guess=given_guess)

    def _get_guess_until_valid(self, guesser: Guesser) -> Optional[GivenGuess]:
        while True:
            guess = guesser.guess(game_state=self.state.guesser_state)
            try:
                given_guess = self.state.process_guess(guess)
                for subscriber in self.guess_given_subscribers:
                    subscriber(guesser, guess)
                return given_guess
            except InvalidGuess:
                pass
