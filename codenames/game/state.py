from __future__ import annotations

import logging
from functools import cached_property
from typing import Dict, List, Optional

from codenames.game.base import BaseModel, WordGroup, canonical_format
from codenames.game.board import Board
from codenames.game.card import Card
from codenames.game.color import CardColor, TeamColor
from codenames.game.exceptions import (
    CardNotFoundError,
    GameIsOver,
    InvalidGuess,
    InvalidHint,
    InvalidTurn,
)
from codenames.game.move import (
    PASS_GUESS,
    QUIT_GAME,
    GivenGuess,
    GivenHint,
    Guess,
    GuessMove,
    Hint,
    HintMove,
    Move,
    PassMove,
)
from codenames.game.player import PlayerRole
from codenames.game.score import Score, TeamScore
from codenames.game.winner import Winner, WinningReason
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)


class BaseGameState(BaseModel):
    board: Board
    score: Score
    current_team_color: TeamColor
    current_player_role: PlayerRole = PlayerRole.HINTER
    given_hints: List[GivenHint] = []
    given_guesses: List[GivenGuess] = []

    class Config:
        abstract = True

    @property
    def given_hint_words(self) -> WordGroup:
        return tuple(hint.formatted_word for hint in self.given_hints)

    @property
    def illegal_hint_words(self) -> WordGroup:
        return *self.board.all_words, *self.given_hint_words

    @property
    def moves(self) -> List[Move]:
        return get_moves(
            given_hints=self.given_hints, given_guesses=self.given_guesses, current_turn=self.current_player_role
        )


class GameState(BaseGameState):
    """
    Game state is a mutable object that represents the current state of the game.
    """

    left_guesses: int = 0
    winner: Optional[Winner] = None
    raw_hints: List[Hint] = []

    @property
    def hinter_state(self) -> HinterGameState:
        return HinterGameState(
            board=self.board,
            score=self.score,
            current_team_color=self.current_team_color,
            current_player_role=self.current_player_role,
            given_hints=self.given_hints,
            given_guesses=self.given_guesses,
        )

    @property
    def guesser_state(self) -> GuesserGameState:
        return GuesserGameState(
            board=self.board.censured,
            score=self.score,
            current_team_color=self.current_team_color,
            current_player_role=self.current_player_role,
            given_hints=self.given_hints,
            given_guesses=self.given_guesses,
            left_guesses=self.left_guesses,
        )

    @property
    def last_given_hint(self) -> GivenHint:
        return self.given_hints[-1]

    @property
    def is_game_over(self) -> bool:
        return self.winner is not None

    def process_hint(self, hint: Hint) -> Optional[GivenHint]:
        if self.is_game_over:
            raise GameIsOver()
        if self.current_player_role != PlayerRole.HINTER:
            raise InvalidTurn("It's not the Hinter's turn now!")
        self.raw_hints.append(hint)
        if hint.card_amount == QUIT_GAME:
            log.info("Hinter quit the game")
            self._team_quit()
            return None
        formatted_hint_word = canonical_format(hint.word)
        if formatted_hint_word in self.illegal_hint_words:
            raise InvalidHint("Hint word is on board or was already used!")
        given_hint = GivenHint(
            word=formatted_hint_word, card_amount=hint.card_amount, team_color=self.current_team_color
        )
        log.info(f"Hinter: {wrap(hint.word)} {hint.card_amount} card(s)")
        self.given_hints.append(given_hint)
        self.left_guesses = given_hint.card_amount + 1
        self.current_player_role = PlayerRole.GUESSER
        return given_hint

    def process_guess(self, guess: Guess) -> Optional[GivenGuess]:
        if self.is_game_over:
            raise GameIsOver()
        if self.current_player_role != PlayerRole.GUESSER:
            raise InvalidTurn("It's not the Guesser's turn now!")
        if guess.card_index == PASS_GUESS:
            log.info("Guesser passed the turn")
            self._end_turn()
            return None
        if guess.card_index == QUIT_GAME:
            log.info("Guesser quit the game")
            self._team_quit()
            return None
        guessed_card = self._reveal_guessed_card(guess)
        given_guess = GivenGuess(given_hint=self.last_given_hint, guessed_card=guessed_card)
        log.info(f"Guesser: {given_guess}")
        self.given_guesses.append(given_guess)
        self._update_score(given_guess)
        if self.is_game_over:
            log.info("Winner found, turn is over")
            self._end_turn()
            return given_guess
        if not given_guess.correct:
            log.info("Guesser wrong, turn is over")
            self._end_turn()
            return given_guess
        self.left_guesses -= 1
        if self.left_guesses > 0:
            return given_guess
        log.info("Turn is over")
        self._end_turn()
        return given_guess

    def _reveal_guessed_card(self, guess: Guess) -> Card:
        try:
            guessed_card = self.board[guess.card_index]
        except (IndexError, CardNotFoundError) as e:
            raise InvalidGuess("Given card index is out of range!") from e
        if guessed_card.revealed:
            raise InvalidGuess("Given card is already revealed!")
        guessed_card.revealed = True
        return guessed_card

    def _end_turn(self, switch_role: bool = True):
        self.left_guesses = 0
        self.current_team_color = self.current_team_color.opponent
        if switch_role:
            self.current_player_role = self.current_player_role.other

    def _team_quit(self):
        winner_color = self.current_team_color.opponent
        self.winner = Winner(team_color=winner_color, reason=WinningReason.OPPONENT_QUIT)
        self._end_turn()

    def _update_score(self, given_guess: GivenGuess):
        card_color = given_guess.guessed_card.color
        if card_color == CardColor.GRAY:
            return
        if card_color == CardColor.BLACK:
            winner_color = given_guess.team.opponent
            self.winner = Winner(team_color=winner_color, reason=WinningReason.OPPONENT_HIT_BLACK)
            return
        score_team_color = given_guess.team if given_guess.correct else given_guess.team.opponent
        game_ended = self.score.add_point(score_team_color)
        if game_ended:
            self.winner = Winner(team_color=score_team_color, reason=WinningReason.TARGET_SCORE_REACHED)


class HinterGameState(BaseGameState):
    """
    HinterGameState represents all the information that is available to the Hinter.
    """


class GuesserGameState(BaseGameState):
    """
    GuesserGameState represents all the information that is available to the Guesser.
    """

    left_guesses: int

    @cached_property
    def current_hint(self) -> GivenHint:
        return self.given_hints[-1]


def new_game_state(board: Optional[Board] = None, language: Optional[str] = None) -> GameState:
    if board is None and language is None:
        raise ValueError("Either board or language must be provided.")
    if board is None:
        from codenames.boards.builder import (  # pylint: disable=import-outside-toplevel
            generate_board,
        )

        board = generate_board(language=language)  # type: ignore
    if not board.is_clean:
        raise ValueError("Board must be clean.")
    first_team_color = _determine_first_team(board)
    score = build_score(board)
    return GameState(
        board=board,
        score=score,
        current_team_color=first_team_color,
        current_player_role=PlayerRole.HINTER,
    )


def build_score(board: Board) -> Score:
    blue_score = TeamScore(total=len(board.blue_cards), revealed=len(board.revealed_cards_for_color(CardColor.BLUE)))
    red_score = TeamScore(total=len(board.red_cards), revealed=len(board.revealed_cards_for_color(CardColor.RED)))
    score = Score(blue=blue_score, red=red_score)
    return score


def _determine_first_team(board: Board) -> TeamColor:
    if len(board.blue_cards) >= len(board.red_cards):
        return TeamColor.BLUE
    return TeamColor.RED


def get_moves(given_hints: List[GivenHint], given_guesses: List[GivenGuess], current_turn: PlayerRole) -> List[Move]:
    guesses_by_hints = get_guesses_by_hints(given_hints=given_hints, given_guesses=given_guesses)
    moves: List[Move] = []
    for hint, guesses in guesses_by_hints.items():
        hint_move = HintMove(given_hint=hint)
        moves.append(hint_move)
        for guess in guesses:
            guess_move = GuessMove(given_guess=guess)
            moves.append(guess_move)
        if len(guesses) == 0:
            moves.append(PassMove(team=hint.team_color))
            continue
        if len(guesses) < hint.card_amount + 1:
            last_guess = guesses[-1]
            if last_guess.correct:
                moves.append(PassMove(team=hint.team_color))
    if not moves:
        return moves
    last_move = moves[-1]
    if not isinstance(last_move, PassMove):
        return moves
    if current_turn == PlayerRole.GUESSER:
        moves = moves[:-1]
    return moves


def get_guesses_by_hints(
    given_hints: List[GivenHint], given_guesses: List[GivenGuess]
) -> Dict[GivenHint, List[GivenGuess]]:
    guesses_by_hints: Dict[GivenHint, List[GivenGuess]] = {}
    for hint in given_hints:
        guesses_by_hints[hint] = []
    for guess in given_guesses:
        guesses_by_hints[guess.given_hint].append(guess)
    return guesses_by_hints


build_game_state = new_game_state  # Support legacy name
