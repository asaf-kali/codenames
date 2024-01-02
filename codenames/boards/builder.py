import random
from enum import Enum
from typing import List, Optional, Sequence, Tuple, Union

from codenames.boards.english import ENGLISH_WORDS
from codenames.boards.hebrew import HEBREW_WORDS
from codenames.game.board import Board
from codenames.game.card import Card
from codenames.game.color import CardColor, TeamColor


class SupportedLanguage(str, Enum):
    ENGLISH = "english"
    HEBREW = "hebrew"


def generate_board(
    language: Union[str, SupportedLanguage],
    board_size: int = 25,
    black_amount: int = 1,
    seed: Optional[int] = None,
    first_team: Optional[TeamColor] = None,
) -> Board:
    if language == SupportedLanguage.ENGLISH:
        words = ENGLISH_WORDS
    elif language == SupportedLanguage.HEBREW:
        words = HEBREW_WORDS
    else:
        raise NotImplementedError(f"Unknown language: {language}")
    return generate_board_from_vocabulary(
        vocabulary=words,
        board_size=board_size,
        black_amount=black_amount,
        seed=seed,
        first_team=first_team,
    )


def generate_board_from_vocabulary(
    vocabulary: List[str],
    board_size: int = 25,
    black_amount: int = 1,
    seed: Optional[int] = None,
    first_team: Optional[TeamColor] = None,
) -> Board:
    if seed:
        random.seed(seed)

    first_team = first_team or random.choice(list(TeamColor))
    red_amount = blue_amount = board_size // 3
    if first_team == TeamColor.RED:
        red_amount += 1
    else:
        blue_amount += 1
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
