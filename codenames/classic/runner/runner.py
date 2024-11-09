from __future__ import annotations

import logging
from typing import Callable

from codenames.classic.board import ClassicBoard
from codenames.classic.builder import generate_board
from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.runner.models import GamePlayers, TeamPlayers
from codenames.classic.score import Score, TeamScore
from codenames.classic.state import ClassicGameState
from codenames.classic.winner import Winner
from codenames.generic.exceptions import InvalidGuess
from codenames.generic.move import Clue, GivenGuess, Guess
from codenames.generic.player import Operative, PlayerRole, Spymaster
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)
SEPARATOR = "\n-----\n"
ClueGivenSubscriber = Callable[[Spymaster, Clue], None]
GuessGivenSubscriber = Callable[[Operative, Guess], None]


class ClassicGameRunner:
    def __init__(self, players: GamePlayers, state: ClassicGameState | None = None, board: ClassicBoard | None = None):
        self.players = players
        if (not state and not board) or (state and board):
            raise ValueError("Exactly one of state or board must be provided.")
        self.state = state or new_game_state(board=board)
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


def new_game_state(board: ClassicBoard | None = None, language: str | None = None) -> ClassicGameState:
    if board is None and language is None:
        raise ValueError("Either board or language must be provided.")
    if board is None:
        board = generate_board(language=language)  # type: ignore[arg-type]
    if not board.is_clean:
        raise ValueError("Board must be clean.")
    first_team = _determine_first_team(board)
    score = build_score(board)
    return ClassicGameState(
        board=board,
        score=score,
        current_team=first_team,
        current_player_role=PlayerRole.SPYMASTER,
    )


def build_score(board: ClassicBoard) -> Score:
    blue_score = TeamScore(total=len(board.blue_cards), revealed=len(board.revealed_cards_for_color(ClassicColor.BLUE)))
    red_score = TeamScore(total=len(board.red_cards), revealed=len(board.revealed_cards_for_color(ClassicColor.RED)))
    score = Score(blue=blue_score, red=red_score)
    return score


def _determine_first_team(board: ClassicBoard) -> ClassicTeam:
    if len(board.blue_cards) >= len(board.red_cards):
        return ClassicTeam.BLUE
    return ClassicTeam.RED
