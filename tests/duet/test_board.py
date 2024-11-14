from codenames.duet.board import DuetBoard
from codenames.duet.card import DuetColor


def test_dual_board_construction(board_10: DuetBoard):
    dual_board = DuetBoard.dual_board(board_10, seed=0)
    assert dual_board.size == board_10.size
    assert dual_board.all_words == board_10.all_words
    assert _color_count(dual_board) == _color_count(board_10)
    assert _color_order(dual_board) != _color_order(board_10)


def _color_order(board: DuetBoard) -> list[DuetColor]:
    return [card.color for card in board]  # type: ignore


def _color_count(board: DuetBoard) -> dict[str, int]:
    return {color: sum(card.color == color for card in board) for color in DuetColor}
