import pytest

from codenames.game import Board, CardNotFoundError, two_integer_factors
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
