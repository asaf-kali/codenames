from __future__ import annotations

from codenames.generic.card import CardColor


class DuetColor(CardColor):
    GREEN = "GREEN"
    NEUTRAL = "NEUTRAL"
    ASSASSIN = "ASSASSIN"
    IRRELEVANT = "IRRELEVANT"

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]


CARD_COLOR_TO_EMOJI = {
    DuetColor.GREEN: "🟩",
    DuetColor.NEUTRAL: "⬜",
    DuetColor.ASSASSIN: "💀",
    DuetColor.IRRELEVANT: "✔️",
}
