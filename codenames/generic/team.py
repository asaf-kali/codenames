from __future__ import annotations

from enum import StrEnum


class Team(StrEnum):
    @property
    def as_card_color(self) -> str:
        raise NotImplementedError
