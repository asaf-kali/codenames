from __future__ import annotations

from abc import ABC

from codenames.duet.card import DuetColor
from codenames.generic.player import Operative, Spymaster, Team


class DuetTeam(Team):
    MAIN = "MAIN"

    @property
    def as_card_color(self) -> DuetColor:
        return DuetColor.GREEN  # Naive implementation


class DuetPlayer(Spymaster[DuetTeam], Operative[DuetTeam], ABC):
    pass
