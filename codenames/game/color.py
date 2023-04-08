from __future__ import annotations

from enum import Enum


class TeamColor(str, Enum):
    BLUE = "BLUE"
    RED = "RED"

    def __str__(self) -> str:
        return self.value.title()

    @property
    def opponent(self) -> TeamColor:
        return TeamColor.BLUE if self == TeamColor.RED else TeamColor.RED

    @property
    def as_card_color(self) -> CardColor:
        return CardColor.BLUE if self == TeamColor.BLUE else CardColor.RED


class CardColor(str, Enum):
    BLUE = "BLUE"
    RED = "RED"
    GRAY = "GRAY"
    BLACK = "BLACK"

    def __str__(self) -> str:
        return self.value.title()

    @property
    def as_team_color(self) -> TeamColor:
        if self == CardColor.RED:
            return TeamColor.RED
        if self == CardColor.BLUE:
            return TeamColor.BLUE
        raise ValueError(f"No such team color: {self.value}.")

    @property
    def opponent(self) -> CardColor:
        return self.as_team_color.opponent.as_card_color

    @property
    def emoji(self) -> str:
        return CARD_COLOR_TO_EMOJI[self]


CARD_COLOR_TO_EMOJI = {
    CardColor.RED: "🟥",
    CardColor.BLUE: "🟦",
    CardColor.GRAY: "⬜",
    CardColor.BLACK: "💀",
}
