from __future__ import annotations

from codenames.generic.card import CardColor
from codenames.generic.player import Team


class ClassicColor(CardColor):
    BLUE = "BLUE"
    RED = "RED"
    NEUTRAL = "NEUTRAL"
    ASSASSIN = "ASSASSIN"

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]


class ClassicTeam(Team):
    BLUE = "BLUE"
    RED = "RED"

    @property
    def as_card_color(self) -> ClassicColor:
        return ClassicColor.BLUE if self == ClassicTeam.BLUE else ClassicColor.RED

    @property
    def opponent(self) -> ClassicTeam:
        return ClassicTeam.BLUE if self == ClassicTeam.RED else ClassicTeam.RED


CARD_COLOR_TO_EMOJI = {
    ClassicColor.RED: "🟥",
    ClassicColor.BLUE: "🟦",
    ClassicColor.NEUTRAL: "⬜",
    ClassicColor.ASSASSIN: "💀",
}
