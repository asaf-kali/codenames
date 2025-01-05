from __future__ import annotations

import abc

from codenames.duet.card import DuetColor
from codenames.generic.player import Operative, Spymaster, Team


class DuetTeam(Team):
    MAIN = "MAIN"

    @property
    def as_card_color(self) -> DuetColor:
        return DuetColor.GREEN  # Naive implementation


class DuetPlayer(Spymaster[DuetColor, DuetTeam], Operative[DuetColor, DuetTeam], abc.ABC):
    pass


class DuetSpymaster(Spymaster[DuetColor, DuetTeam], abc.ABC):
    pass


class DuetOperative(Operative[DuetColor, DuetTeam], abc.ABC):
    pass
