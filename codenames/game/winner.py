from enum import Enum

from codenames.game.base import BaseModel
from codenames.game.color import TeamColor


class WinningReason(str, Enum):
    TARGET_SCORE_REACHED = "Target score reached"
    OPPONENT_HIT_BLACK = "Opponent hit black card"
    OPPONENT_QUIT = "Opponent quit"


class Winner(BaseModel):
    team_color: TeamColor
    reason: WinningReason

    def __str__(self) -> str:
        return f"{self.team_color} team ({self.reason.value})"
