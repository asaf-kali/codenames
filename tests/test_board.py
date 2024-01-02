from codenames.boards.builder import SupportedLanguage, generate_board
from codenames.game.board import Board
from codenames.game.color import TeamColor


def test_basic_english_board_build():
    board = generate_board(language="english")
    _validate_standard_board(board)


def test_basic_hebrew_board_build():
    board = generate_board(language=SupportedLanguage.HEBREW)
    _validate_standard_board(board)


def test_build_board_with_params():
    board = generate_board(
        language=SupportedLanguage.ENGLISH,
        board_size=17,
        black_amount=2,
        seed=42,
        first_team=TeamColor.RED,
    )
    assert len(board.cards) == 17
    assert len(board.revealed_cards) == 0
    assert len(board.red_cards) == 6
    assert len(board.blue_cards) == 5
    assert len(board.gray_cards) == 4
    assert len(board.black_cards) == 2


def _validate_standard_board(board: Board):
    assert len(board.cards) == 25
    assert len(board.revealed_cards) == 0
    assert len(board.red_cards) >= 8
    assert len(board.blue_cards) >= 8
    assert len(board.gray_cards) == 7
    assert len(board.black_cards) == 1
