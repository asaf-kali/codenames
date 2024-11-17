import logging
from typing import Self

from pydantic import BaseModel, model_validator

from codenames.duet.board import DuetBoard
from codenames.duet.score import (
    MISTAKE_LIMIT_REACHED,
    TIMER_TOKENS_DEPLETED,
    GameResult,
)
from codenames.duet.state import DuetSideState
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from codenames.generic.move import Clue, Guess
from codenames.generic.player import PlayerRole

log = logging.getLogger(__name__)


class MiniGameState(BaseModel):
    side_state: DuetSideState
    timer_tokens: int = 5
    allowed_mistakes: int = 4

    @classmethod
    def from_board(cls, board: DuetBoard) -> Self:
        if not board.is_clean:
            raise ValueError("Board must be clean.")
        side_state = DuetSideState.from_board(board)
        return cls(side_state=side_state)

    @property
    def game_result(self) -> GameResult | None:
        # If the timer runs out, the game is lost
        if self.timer_tokens < 0:
            return TIMER_TOKENS_DEPLETED
        if self.allowed_mistakes == 0:
            return MISTAKE_LIMIT_REACHED
        return self.side_state.game_result

    @property
    def is_sudden_death(self) -> bool:
        return self.timer_tokens == 0

    @property
    def is_game_over(self) -> bool:
        return self.game_result is not None

    @model_validator(mode="after")
    def validate_allowed_mistakes(self) -> Self:
        if self.allowed_mistakes > self.timer_tokens:
            raise ValueError("Allowed mistakes cannot be greater than timer tokens.")
        return self

    def process_clue(self, clue: Clue) -> DuetGivenClue | None:
        return self.side_state.process_clue(clue)

    def process_guess(self, guess: Guess) -> DuetGivenGuess | None:
        given_guess = self.side_state.process_guess(guess)
        # If the guess is wrong or passed the turn, the timer is updated
        if not given_guess or not given_guess.correct:
            self._update_tokens(mistake=given_guess is not None)
            return given_guess
        # If we reached our target score, and we are not in "sudden death", we consume a timer token
        if self.side_state.is_game_over and not self.is_sudden_death:
            self._update_tokens(mistake=False)
        return given_guess

    def _update_tokens(self, mistake: bool) -> None:
        if self.timer_tokens >= 0:
            self.timer_tokens -= 1
        if self.timer_tokens == 0:
            log.info("Timer tokens depleted! Entering sudden death")
            self.side_state.current_player_role = PlayerRole.OPERATIVE
        if not mistake:
            return
        self.allowed_mistakes -= 1
        if self.allowed_mistakes == 0:
            log.info("Mistake limit reached!")
