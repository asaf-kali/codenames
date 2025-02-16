from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

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


class GameResult(Enum):
    def __init__(self, win: bool, reason: str):
        self.win = win
        self.reason = reason

    TARGET_REACHED = (True, "Target score reached")
    ASSASSIN_HIT = (False, "Assassin card was hit")
    GAME_QUIT = (False, "The game was quit")
    TIMER_TOKENS_DEPLETED = (False, "Timer tokens depleted")
    MISTAKE_LIMIT_REACHED = (False, "Mistake limit reached")
