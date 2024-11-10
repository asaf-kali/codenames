from __future__ import annotations

import logging
import random
from typing import Sequence

from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.types import ClassicCard, ClassicCards
from codenames.generic.board import Board

log = logging.getLogger(__name__)
LTR = "\u200E"


class ClassicBoard(Board[ClassicColor]):

    @property
    def red_cards(self) -> ClassicCards:
        return self.cards_for_color(ClassicColor.RED)

    @property
    def blue_cards(self) -> ClassicCards:
        return self.cards_for_color(ClassicColor.BLUE)

    @property
    def neutral_cards(self) -> ClassicCards:
        return self.cards_for_color(ClassicColor.NEUTRAL)

    @property
    def assassin_cards(self) -> ClassicCards:
        return self.cards_for_color(ClassicColor.ASSASSIN)

    @staticmethod
    def from_vocabulary(
        language: str,
        vocabulary: list[str],
        board_size: int = 25,
        assassin_amount: int = 1,
        seed: int | None = None,
        first_team: ClassicTeam | None = None,
    ) -> ClassicBoard:
        if seed:
            random.seed(seed)

        first_team = first_team or random.choice(list(ClassicTeam))  # type: ignore[assignment]
        red_amount = blue_amount = board_size // 3
        if first_team == ClassicTeam.RED:
            red_amount += 1
        else:
            blue_amount += 1
        neutral_amount = board_size - red_amount - blue_amount - assassin_amount

        words_list, red_words = _extract_random_subset(vocabulary, red_amount)
        words_list, blue_words = _extract_random_subset(words_list, blue_amount)
        words_list, neutral_words = _extract_random_subset(words_list, neutral_amount)
        words_list, assassin_words = _extract_random_subset(words_list, assassin_amount)

        red_cards = [ClassicCard(word=word, color=ClassicColor.RED) for word in red_words]
        blue_cards = [ClassicCard(word=word, color=ClassicColor.BLUE) for word in blue_words]
        neutral_cards = [ClassicCard(word=word, color=ClassicColor.NEUTRAL) for word in neutral_words]
        assassin_cards = [ClassicCard(word=word, color=ClassicColor.ASSASSIN) for word in assassin_words]

        all_cards = red_cards + blue_cards + neutral_cards + assassin_cards
        random.shuffle(all_cards)
        return ClassicBoard(language=language, cards=all_cards)


def _extract_random_subset(elements: Sequence, subset_size: int) -> tuple[tuple, tuple]:
    sample = tuple(random.sample(elements, k=subset_size))
    remaining = tuple(e for e in elements if e not in sample)
    return remaining, sample
