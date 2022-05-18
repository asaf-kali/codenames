import logging
from enum import Enum
from functools import cached_property
from typing import Dict, List, Optional

from pydantic import validator

from codenames.game import (
    BaseModel,
    Board,
    Card,
    CardColor,
    GivenGuess,
    GivenHint,
    Guess,
    Hint,
    PlayerRole,
    TeamColor,
    WordGroup,
    canonical_format,
)
from codenames.game.exceptions import (
    CardNotFoundError,
    GameIsOver,
    InvalidGuess,
    InvalidHint,
    InvalidTurn,
)
from codenames.utils import wrap

log = logging.getLogger(__name__)

PASS_GUESS = -1
QUIT_GAME = -2


class WinningReason(str, Enum):
    TARGET_SCORE_REACHED = "Target score reached"
    OPPONENT_HIT_BLACK = "Opponent hit black card"
    OPPONENT_QUIT = "Opponent quit"


class Winner(BaseModel):
    team_color: TeamColor
    reason: WinningReason

    def __str__(self) -> str:
        return f"{self.team_color.value} team ({self.reason.value})"


class GameState(BaseModel):
    language: str
    board: Board
    current_team_color: TeamColor = TeamColor.BLUE
    current_player_role: PlayerRole = PlayerRole.HINTER
    left_guesses: int = 0
    bonus_given: bool = False
    winner: Optional[Winner] = None
    remaining_score: Dict[TeamColor, int] = {}
    raw_hints: List[Hint] = []
    given_hints: List[GivenHint] = []
    given_guesses: List[GivenGuess] = []

    @validator("remaining_score", always=True)
    def init_scores(cls, value: Dict[TeamColor, int], values) -> Dict[TeamColor, int]:
        if value:
            return value
        board = values["board"]
        return {TeamColor.BLUE: len(board.blue_cards), TeamColor.RED: len(board.red_cards)}

    @property
    def hinter_state(self) -> "HinterGameState":
        return HinterGameState(
            board=self.board,
            current_team_color=self.current_team_color,
            given_hints=self.given_hints,
            given_guesses=self.given_guesses,
        )

    @property
    def guesser_state(self) -> "GuesserGameState":
        board = self.board.censured
        return GuesserGameState(
            board=board,
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
        self.remaining_score[score_team_color] -= 1
        if self.remaining_score[score_team_color] == 0:
            self.winner = Winner(team_color=score_team_color, reason=WinningReason.TARGET_SCORE_REACHED)


class HinterGameState(BaseModel):
    board: Board
    current_team_color: TeamColor
    given_hints: List[GivenHint]
    given_guesses: List[GivenGuess]

    @cached_property
    def given_hint_words(self) -> WordGroup:
        return tuple(hint.formatted_word for hint in self.given_hints)

    @cached_property
    def illegal_words(self) -> WordGroup:
        return *self.board.all_words, *self.given_hint_words


class GuesserGameState(BaseModel):
    board: Board
    current_team_color: TeamColor
    given_hints: List[GivenHint]
    given_guesses: List[GivenGuess]
    left_guesses: int
    bonus_given: bool

    @cached_property
    def current_hint(self) -> GivenHint:
        return self.given_hints[-1]


def build_game_state(language: str, board: Board = None) -> GameState:
    if board is None:
        from codenames.boards import generate_standard_board

        board = generate_standard_board(language=language)
    first_team_color = _determine_first_team(board)
    return GameState(
        language=language,
        board=board,
        current_team_color=first_team_color,
    )


def _determine_first_team(board: Board) -> TeamColor:
    if len(board.blue_cards) >= len(board.red_cards):
        return TeamColor.BLUE
    return TeamColor.RED
