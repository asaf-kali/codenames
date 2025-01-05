from __future__ import annotations

from codenames.generic.card import CardColor


class ClassicColor(CardColor):
    BLUE = "BLUE"
    RED = "RED"
    NEUTRAL = "NEUTRAL"
    ASSASSIN = "ASSASSIN"

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]


CARD_COLOR_TO_EMOJI = {
    ClassicColor.RED: "🟥",
    ClassicColor.BLUE: "🟦",
    ClassicColor.NEUTRAL: "⬜",
    ClassicColor.ASSASSIN: "💀",
}
