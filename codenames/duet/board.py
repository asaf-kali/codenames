from __future__ import annotations

import logging
import random

from codenames.duet.card import DuetColor
from codenames.duet.types import DuetCard, DuetCards
from codenames.generic.board import Board, Vocabulary
from codenames.utils.builder import extract_random_subset

log = logging.getLogger(__name__)


class DuetBoard(Board[DuetColor]):

    @property
    def is_clean(self) -> bool:
        base = super().is_clean
        return base and not self.irrelevant_cards

    @property
    def green_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.GREEN)

    @property
    def neutral_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.NEUTRAL)

    @property
    def assassin_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.ASSASSIN)

    @property
    def irrelevant_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.IRRELEVANT)

    @classmethod
    def from_vocabulary(
        cls,
        vocabulary: Vocabulary,
        board_size: int = 25,
        green_amount: int = 9,
        assassin_amount: int = 3,
        seed: int | None = None,
    ) -> DuetBoard:
        if seed:
            random.seed(seed)

        neutral_amount = board_size - green_amount - assassin_amount
        extract_green = extract_random_subset(vocabulary.words, green_amount)
        extract_neutral = extract_random_subset(extract_green.remaining, neutral_amount)
        extract_assassin = extract_random_subset(extract_neutral.remaining, assassin_amount)

        green_cards = [DuetCard(word=word, color=DuetColor.GREEN) for word in extract_green.sample]
        neutral_cards = [DuetCard(word=word, color=DuetColor.NEUTRAL) for word in extract_neutral.sample]
        assassin_cards = [DuetCard(word=word, color=DuetColor.ASSASSIN) for word in extract_assassin.sample]

        all_cards = green_cards + neutral_cards + assassin_cards
        random.shuffle(all_cards)
        return cls(language=vocabulary.language, cards=all_cards)

    @classmethod
    def from_board(cls, board: Board[DuetColor]) -> DuetBoard:
        return cls(language=board.language, cards=board.cards)

    @classmethod
    def dual_board(cls, board: DuetBoard, overlap_ratio: float = 3, seed: int | None = None) -> DuetBoard:
        if seed:
            random.seed(seed)
        # Given board analysis
        cards_range = range(len(board.cards))
        card_colors = [card.color for card in board.cards]
        green_indices = [i for i, color in enumerate(card_colors) if color == DuetColor.GREEN]
        non_green_colors = [color for color in card_colors if color != DuetColor.GREEN]
        non_green_indices = list(set(cards_range) - set(green_indices))

        # Dual board construction. We start with all green cards.
        dual_colors = [DuetColor.GREEN] * len(board.cards)
        # Now we need to:
        #  1. Pick *overlapping* green card indices
        overlap = round(len(green_indices) / overlap_ratio)
        common_green_indices = set(random.sample(green_indices, overlap))
        #  2. Pick the remaining green card indices from the *non-green* indices
        remaining_green_count = len(green_indices) - overlap
        unique_green_indices = set(random.sample(non_green_indices, remaining_green_count))
        dst_non_green_indices = set(cards_range) - set(unique_green_indices) - set(common_green_indices)
        #  3. Fill up the rest of the places with the non-green colors.
        assert len(dst_non_green_indices) == len(non_green_colors)
        random.shuffle(non_green_colors)
        for i, color in zip(dst_non_green_indices, non_green_colors):
            dual_colors[i] = color  # type: ignore
        dual_cards = [DuetCard(word=card.word, color=color) for card, color in zip(board.cards, dual_colors)]
        return cls(language=board.language, cards=dual_cards)
