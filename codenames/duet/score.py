from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from codenames.generic.state import TeamScore


class Score(BaseModel):
    main: TeamScore

    @staticmethod
    def new(green: int) -> Score:
        return Score(main=TeamScore.new(green))

    def add_point(self) -> bool:
        self.main.revealed += 1
        return self.target_reached

    @property
    def target_reached(self) -> bool:
        return self.main.revealed == self.main.total


class GameResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    win: bool
    reason: str


TARGET_REACHED = GameResult(win=True, reason="Target score reached")
ASSASSIN_HIT = GameResult(win=False, reason="Assassin card was hit")
GAME_QUIT = GameResult(win=False, reason="Team quit the game")
TIMER_TOKENS_DEPLETED = GameResult(win=False, reason="Timer tokens depleted")
MISTAKE_LIMIT_REACHED = GameResult(win=False, reason="Mistake limit reached")
