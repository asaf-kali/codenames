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
    def green_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.GREEN)

    @property
    def neutral_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.NEUTRAL)

    @property
    def assassin_cards(self) -> DuetCards:
        return self.cards_for_color(DuetColor.ASSASSIN)

    @staticmethod
    def from_vocabulary(
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
        return DuetBoard(language=vocabulary.language, cards=all_cards)

    @staticmethod
    def dual_board(board: DuetBoard, seed: int | None = None) -> DuetBoard:
        if seed:
            random.seed(seed)
        card_colors = [card.color for card in board.cards]
        random.shuffle(card_colors)
        dual_cards = [DuetCard(word=card.word, color=color) for card, color in zip(board.cards, card_colors)]
        return DuetBoard(language=board.language, cards=dual_cards)
