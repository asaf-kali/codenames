import pytest

from codenames.boards.builder import SupportedLanguage, generate_board
from codenames.game.board import Board, two_integer_factors
from codenames.game.color import TeamColor
from codenames.game.exceptions import CardNotFoundError
from tests.utils import constants


@pytest.fixture()
def board_10() -> Board:
    return constants.board_10()


@pytest.fixture()
def board_25() -> Board:
    return constants.board_25()


def test_get_board_at_integer_index_returns_card(board_10: Board):
    card = board_10[0]
    assert card.word == "Card 0"


def test_get_board_at_negative_index_raises_error(board_10: Board):
    with pytest.raises(IndexError):
        _ = board_10[-1]


def test_get_board_at_upper_bound_index_raises_error(board_10: Board):
    with pytest.raises(IndexError):
        _ = board_10[10]


def test_get_board_at_existing_word_index_returns_card(board_10: Board):
    card = board_10["Card 0"]
    assert card.word == "Card 0"


def test_get_board_at_non_existing_word_raises_error(board_10: Board):
    with pytest.raises(CardNotFoundError):
        _ = board_10["foo"]


def test_get_board_at_float_index_raises_error(board_10: Board):
    with pytest.raises(IndexError):
        _ = board_10[1.1]  # type: ignore


def test_two_integer_factors():
    x, y = two_integer_factors(25)
    assert x == 5 and y == 5

    x, y = two_integer_factors(30)
    assert x == 6 and y == 5

    x, y = two_integer_factors(17)
    assert x == 17 and y == 1


def test_str_is_printable_string(board_10: Board, board_25: Board):
    assert str(board_10) == board_10.printable_string
    print()
    print(board_10)

    assert str(board_25) == board_25.printable_string
    print()
    print(board_25)

    print()
    print(constants.hebrew_board().printable_string)


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
