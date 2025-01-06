from __future__ import annotations

from codenames.duet.card import DuetColor
from codenames.generic.team import Team


class DuetTeam(Team):
    MAIN = "MAIN"

    @property
    def as_card_color(self) -> DuetColor:
        return DuetColor.GREEN  # Naive implementation
