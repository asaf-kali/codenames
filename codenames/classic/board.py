from __future__ import annotations

import logging
import random

from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.types import ClassicCard, ClassicCards
from codenames.generic.board import Board, Vocabulary
from codenames.utils.builder import extract_random_subset

log = logging.getLogger(__name__)


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

    @classmethod
    def from_vocabulary(
        cls,
        vocabulary: Vocabulary,
        board_size: int = 25,
        assassin_amount: int = 1,
        first_team: ClassicTeam | None = None,
        seed: int | None = None,
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

        extract_red = extract_random_subset(vocabulary.words, red_amount)
        extract_blue = extract_random_subset(extract_red.remaining, blue_amount)
        extract_neutral = extract_random_subset(extract_blue.remaining, neutral_amount)
        extract_assassin = extract_random_subset(extract_neutral.remaining, assassin_amount)

        red_cards = [ClassicCard(word=word, color=ClassicColor.RED) for word in extract_red.sample]
        blue_cards = [ClassicCard(word=word, color=ClassicColor.BLUE) for word in extract_blue.sample]
        neutral_cards = [ClassicCard(word=word, color=ClassicColor.NEUTRAL) for word in extract_neutral.sample]
        assassin_cards = [ClassicCard(word=word, color=ClassicColor.ASSASSIN) for word in extract_assassin.sample]

        all_cards = red_cards + blue_cards + neutral_cards + assassin_cards
        random.shuffle(all_cards)
        return cls(language=vocabulary.language, cards=all_cards)
