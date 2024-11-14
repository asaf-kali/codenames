import random

import pytest

from codenames.duet.board import DuetBoard
from codenames.duet.card import DuetColor
from codenames.utils.vocabulary.languages import get_vocabulary


@pytest.mark.parametrize("seed", list(range(10)))
def test_dual_board_construction(seed: int):
    random.seed(seed)
    english_vocabulary = get_vocabulary(language="english")
    board_a = DuetBoard.from_vocabulary(vocabulary=english_vocabulary)
    board_b = DuetBoard.dual_board(board=board_a)

    # Basic properties
    assert board_b.size == board_a.size
    assert board_b.all_words == board_a.all_words
    assert _color_count(board_b) == _color_count(board_a)
    assert _color_order(board_b) != _color_order(board_a)

    # Color intersection - must have exactly 3 common green cards
    green_indices_a = _get_green_indices(board=board_a)
    green_indices_b = _get_green_indices(board=board_b)
    green_common = green_indices_a & green_indices_b
    green_union = green_indices_a | green_indices_b
    assert len(green_common) == 3
    assert len(green_union) == 15


def _get_green_indices(board: DuetBoard) -> set[int]:
    return _get_color_indices(board=board, color=DuetColor.GREEN)


def _get_color_indices(board: DuetBoard, color: str) -> set[int]:
    return {i for i, card in enumerate(board.cards) if card.color == color}


def _color_count(board: DuetBoard) -> dict[str, int]:
    return {color: sum(card.color == color for card in board) for color in DuetColor}


def _color_order(board: DuetBoard) -> list[DuetColor]:
    return [card.color for card in board]  # type: ignore
