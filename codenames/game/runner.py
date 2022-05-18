from functools import cached_property
from typing import Callable, List, Optional, Tuple

from codenames.game import (
    Board,
    GameState,
    GivenGuess,
    Guess,
    Guesser,
    Hint,
    Hinter,
    InvalidGuess,
    Player,
    Team,
    TeamColor,
    Winner,
    build_game_state,
    log,
)
from codenames.utils import wrap

SEPARATOR = "\n-----\n"


class GameRunner:
    def __init__(
        self,
        blue_hinter: Hinter,
        red_hinter: Hinter,
        blue_guesser: Guesser,
        red_guesser: Guesser,
        state: Optional[GameState] = None,
    ):
        self.blue_hinter = blue_hinter
        self.red_hinter = red_hinter
        self.blue_guesser = blue_guesser
        self.red_guesser = red_guesser
        self.state: GameState = state  # type: ignore
        self.hint_given_subscribers: List[Callable[[Hinter, Hint], None]] = []
        self.guess_given_subscribers: List[Callable[[Guesser, Guess], None]] = []
        self._set_player_team_colors()

    @staticmethod
    def from_teams(blue_team: Team, red_team: Team):
        return GameRunner(
            blue_hinter=blue_team.hinter,
            red_hinter=red_team.hinter,
            blue_guesser=blue_team.guesser,
            red_guesser=red_team.guesser,
        )

    @cached_property
    def hinters(self) -> Tuple[Hinter, Hinter]:
        return self.blue_hinter, self.red_hinter

    @cached_property
    def guessers(self) -> Tuple[Guesser, Guesser]:
        return self.blue_guesser, self.red_guesser

    @cached_property
    def players(self) -> Tuple[Player, ...]:
        return *self.hinters, *self.guessers

    @cached_property
    def blue_team(self) -> Team:
        return Team(hinter=self.blue_hinter, guesser=self.blue_guesser, team_color=TeamColor.BLUE)

    @cached_property
    def red_team(self) -> Team:
        return Team(hinter=self.red_hinter, guesser=self.red_guesser, team_color=TeamColor.RED)

    @property
    def winner(self) -> Optional[Winner]:
        return self.state.winner

    def run_game(self, language: str, board: Board) -> Winner:
        if self.state is None:
            self.state = build_game_state(language=language, board=board)
        self._notify_game_starts()
        winner = self._run_rounds()
        log.info(f"{SEPARATOR}{winner.reason.value}, {wrap(winner.team_color)} team wins!")
        return winner

    def _set_player_team_colors(self):
        for player in self.red_team:
            player.team_color = TeamColor.RED
        for player in self.blue_team:
            player.team_color = TeamColor.BLUE

    def _notify_game_starts(self):
        censored_board = self.state.board.censured
        for hinter in self.hinters:
            hinter.on_game_start(language=self.state.language, board=self.state.board)
        for guesser in self.guessers:
            guesser.on_game_start(language=self.state.language, board=censored_board)

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
