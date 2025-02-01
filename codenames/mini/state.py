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
        # If the guess is wrong or passed the turn, the timer is updated
        if not given_guess or not given_guess.correct:
            self._update_tokens(mistake=given_guess is not None)
            return given_guess
        # If we reached our target score, and we are not in "sudden death", we consume a timer token
        if self.is_game_over and not self.is_sudden_death:
            self._update_tokens(mistake=False)
        return given_guess

    def _update_tokens(self, mistake: bool) -> None:
        if self.timer_tokens >= 0:
            self.timer_tokens -= 1
        if self.timer_tokens == 0:
            log.info("Timer tokens depleted! Entering sudden death")
            self.current_player_role = PlayerRole.OPERATIVE
        elif self.timer_tokens < 0:
            self.game_result = TIMER_TOKENS_DEPLETED
            log.info("Timer tokens depleted (after sudden death)!")
        if not mistake:
            return
        self.allowed_mistakes -= 1
        if self.allowed_mistakes == 0:
            log.info("Mistake limit reached!")
            self.game_result = MISTAKE_LIMIT_REACHED
            return
