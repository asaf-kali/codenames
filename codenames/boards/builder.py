import random
from typing import List, Sequence, Tuple

from codenames.boards.english import ENGLISH_WORDS
from codenames.boards.hebrew import HEBREW_WORDS
from codenames.game import Board, Card, CardColor


def generate_standard_board(language: str, board_size: int = 25, black_amount: int = 1, seed: int = None) -> Board:
    if language == "english":
        words = ENGLISH_WORDS
    elif language == "hebrew":
        words = HEBREW_WORDS
    else:
        raise NotImplementedError(f"Unknown language: {language}")
    return build_board(vocabulary=words, board_size=board_size, black_amount=black_amount, seed=seed)


def build_board(vocabulary: List[str], board_size: int = 25, black_amount: int = 1, seed: int = None) -> Board:
    random.seed(seed)

    red_amount = board_size // 3
    blue_amount = red_amount + 1
    gray_amount = board_size - red_amount - blue_amount - black_amount

    words_list, red_words = _extract_random_subset(vocabulary, red_amount)
    words_list, blue_words = _extract_random_subset(words_list, blue_amount)
    words_list, gray_words = _extract_random_subset(words_list, gray_amount)
    words_list, black_words = _extract_random_subset(words_list, black_amount)

    red_cards = [Card(word=word, color=CardColor.RED) for word in red_words]
    blue_cards = [Card(word=word, color=CardColor.BLUE) for word in blue_words]
    gray_cards = [Card(word=word, color=CardColor.GRAY) for word in gray_words]
    black_cards = [Card(word=word, color=CardColor.BLACK) for word in black_words]

    all_cards = red_cards + blue_cards + gray_cards + black_cards
    random.shuffle(all_cards)
    return Board(cards=all_cards)


def _extract_random_subset(elements: Sequence, subset_size: int) -> Tuple[tuple, tuple]:
    sample = tuple(random.sample(elements, k=subset_size))
    remaining = tuple(e for e in elements if e not in sample)
    return remaining, sample
