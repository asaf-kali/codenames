from __future__ import annotations

from pydantic import BaseModel

from codenames.classic.color import ClassicTeam


class TeamScore(BaseModel):
    total: int
    revealed: int

    @staticmethod
    def new(total: int) -> TeamScore:
        return TeamScore(total=total, revealed=0)

    @property
    def unrevealed(self) -> int:
        return self.total - self.revealed


class Score(BaseModel):
    blue: TeamScore
    red: TeamScore

    @staticmethod
    def new(blue: int, red: int) -> Score:
        return Score(blue=TeamScore.new(blue), red=TeamScore.new(red))

    def add_point(self, team: ClassicTeam) -> bool:
        team_score = self.blue if team == ClassicTeam.BLUE else self.red
        team_score.revealed += 1
        if team_score.unrevealed == 0:
            return True
        return False
