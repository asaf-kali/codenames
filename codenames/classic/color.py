from __future__ import annotations

from codenames.generic.card import CardColor
from codenames.generic.player import Team


class ClassicColor(CardColor):
    BLUE = "BLUE"
    RED = "RED"
    NEUTRAL = "NEUTRAL"
    ASSASSIN = "ASSASSIN"

    @property
    def as_team(self) -> ClassicTeam:
        if self == ClassicColor.RED:
            return ClassicTeam.RED
        if self == ClassicColor.BLUE:
            return ClassicTeam.BLUE
        raise ValueError(f"No such team color: {self.value}.")

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]

    @property
    def opponent(self) -> ClassicColor:
        if self == ClassicColor.RED:
            return ClassicColor.BLUE
        if self == ClassicColor.BLUE:
            return ClassicColor.RED
        raise ValueError(f"No such team color: {self.value}.")


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
