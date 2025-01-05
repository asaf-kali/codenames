from __future__ import annotations

import abc

from codenames.classic.color import ClassicColor
from codenames.generic.player import Operative, Player, Spymaster, Team


class ClassicTeam(Team):
    BLUE = "BLUE"
    RED = "RED"

    @property
    def as_card_color(self) -> ClassicColor:
        return ClassicColor.BLUE if self == ClassicTeam.BLUE else ClassicColor.RED

    @property
    def opponent(self) -> ClassicTeam:
        return ClassicTeam.BLUE if self == ClassicTeam.RED else ClassicTeam.RED


class ClassicPlayer(Player[ClassicColor, ClassicTeam]):
    pass


class ClassicSpymaster(Spymaster[ClassicColor, ClassicTeam], abc.ABC):
    pass


class ClassicOperative(Operative[ClassicColor, ClassicTeam], abc.ABC):
    pass
