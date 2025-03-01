import logging

from codenames.duet.score import MISTAKE_LIMIT_REACHED, TIMER_TOKENS_DEPLETED
from codenames.duet.state import DuetSideState
from codenames.duet.types import DuetGivenGuess
from codenames.generic.move import Guess
from codenames.generic.player import PlayerRole

log = logging.getLogger(__name__)


class MiniGameState(DuetSideState):
    timer_tokens: int = 5
    allowed_mistakes: int = 4

    @property
    def is_sudden_death(self) -> bool:
        return self.timer_tokens == 0

    def process_guess(self, guess: Guess) -> DuetGivenGuess | None:
        given_guess = super().process_guess(guess)
        # If the guess is correct, there is nothing to do
        if given_guess and given_guess.correct:
            return given_guess
        # Otherwise, the guess was incorrect or the operator passed the turn
        self._update_tokens(is_mistake=given_guess is not None)
        return given_guess

    def _update_tokens(self, is_mistake: bool) -> None:
        if self.timer_tokens >= 0:
            self.timer_tokens -= 1
        if self.timer_tokens == 0:
            log.info("Timer tokens depleted! Entering sudden death")
            self.current_player_role = PlayerRole.OPERATIVE
        elif self.timer_tokens < 0:
            self.game_result = TIMER_TOKENS_DEPLETED
            log.info("Timer tokens depleted (after sudden death)!")
        if not is_mistake:
            return
        self.allowed_mistakes -= 1
        if self.allowed_mistakes == 0:
            log.info("Mistake limit reached!")
            self.game_result = MISTAKE_LIMIT_REACHED
            return
