import logging
from functools import cached_property
from typing import Dict, List, Optional

from pydantic import root_validator

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
    language: str
    board: Board
    score: Score
    current_team_color: TeamColor = TeamColor.BLUE
    given_hints: List[GivenHint] = []
    given_guesses: List[GivenGuess] = []

    class Config:
        abstract = True

    @cached_property
    def moves(self) -> List[Move]:
        return get_moves(given_hints=self.given_hints, given_guesses=self.given_guesses)


class GameState(BaseGameState):
    current_player_role: PlayerRole = PlayerRole.HINTER
    left_guesses: int = 0
    bonus_given: bool = False
    winner: Optional[Winner] = None
    raw_hints: List[Hint] = []

    @root_validator(pre=True)
    def init_score(cls, values: dict) -> dict:  # pylint: disable=no-self-argument
        score = values.get("score")
        if score:
            return values
        board = values["board"]
        if isinstance(board, dict):
            board = Board.parse_obj(board)
        score = build_score(board)
        values["score"] = score
        return values

    @property
    def hinter_state(self) -> "HinterGameState":
        return HinterGameState(
            language=self.language,
            board=self.board,
            score=self.score,
            current_team_color=self.current_team_color,
            given_hints=self.given_hints,
            given_guesses=self.given_guesses,
        )

    @property
    def guesser_state(self) -> "GuesserGameState":
        return GuesserGameState(
            language=self.language,
            board=self.board.censured,
            score=self.score,
            current_team_color=self.current_team_color,
            given_hints=self.given_hints,
            given_guesses=self.given_guesses,
            left_guesses=self.left_guesses,
            bonus_given=self.bonus_given,
        )

    @property
    def last_given_hint(self) -> GivenHint:
        return self.given_hints[-1]

    @property
    def is_game_over(self) -> bool:
        return self.winner is not None

    @property
    def given_hint_words(self) -> WordGroup:
        return tuple(hint.word for hint in self.given_hints)

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
        if formatted_hint_word in self.hinter_state.illegal_words:
            raise InvalidHint("Hint word is on board or was already used!")
        given_hint = GivenHint(
            word=formatted_hint_word, card_amount=hint.card_amount, team_color=self.current_team_color
        )
        log.info(f"Hinter: {wrap(hint.word)} {hint.card_amount} card(s)")
        self.given_hints.append(given_hint)
        self.left_guesses = given_hint.card_amount
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
        if self.bonus_given:
            log.info("Bonus already given, turn is over")
            self._end_turn()
            return given_guess
        log.info("Giving bonus guess!")
        self.bonus_given = True
        self.left_guesses += 1
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
        self.bonus_given = False
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
    @cached_property
    def given_hint_words(self) -> WordGroup:
        return tuple(hint.formatted_word for hint in self.given_hints)

    @cached_property
    def illegal_words(self) -> WordGroup:
        return *self.board.all_words, *self.given_hint_words


class GuesserGameState(BaseGameState):
    left_guesses: int
    bonus_given: bool

    @cached_property
    def current_hint(self) -> GivenHint:
        return self.given_hints[-1]


def build_game_state(language: str, board: Optional[Board] = None) -> GameState:
    if board is None:
        from codenames.boards.builder import (  # pylint: disable=import-outside-toplevel
            generate_standard_board,
        )

        board = generate_standard_board(language=language)
    first_team_color = _determine_first_team(board)
    score = build_score(board)
    return GameState(
        language=language,
        board=board,
        score=score,
        current_team_color=first_team_color,
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


def get_moves(given_hints: List[GivenHint], given_guesses: List[GivenGuess]) -> List[Move]:
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
    # TODO: Determine if last pass move should be removed.
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
