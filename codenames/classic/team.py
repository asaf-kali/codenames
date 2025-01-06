from __future__ import annotations

from codenames.classic.color import ClassicColor
from codenames.generic.team import Team


class ClassicTeam(Team):
    BLUE = "BLUE"
    RED = "RED"

    @property
    def as_card_color(self) -> ClassicColor:
        return ClassicColor.BLUE if self == ClassicTeam.BLUE else ClassicColor.RED

    @property
    def opponent(self) -> ClassicTeam:
        return ClassicTeam.BLUE if self == ClassicTeam.RED else ClassicTeam.RED
