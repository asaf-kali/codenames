from enum import StrEnum

from pydantic import BaseModel

from codenames.classic.color import ClassicTeam


class WinningReason(StrEnum):
    TARGET_SCORE_REACHED = "Target score reached"
    OPPONENT_HIT_ASSASSIN = "Opponent hit assassin card"
    OPPONENT_QUIT = "Opponent quit"


class Winner(BaseModel):
    team: ClassicTeam
    reason: WinningReason

    def __str__(self) -> str:
        return f"{self.team} team ({self.reason.value})"
