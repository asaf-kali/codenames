import pytest

from codenames.classic.board import ClassicBoard
from codenames.classic.player import ClassicTeam
from codenames.generic.board import two_integer_factors
from codenames.generic.exceptions import CardNotFoundError
from codenames.utils.vocabulary.languages import SupportedLanguage, get_vocabulary
from tests.classic.utils import constants


def test_get_board_at_integer_index_returns_card(board_10: ClassicBoard):
    card = board_10[0]
    assert card.word == "Card 0"


def test_get_board_at_negative_index_raises_error(board_10: ClassicBoard):
    with pytest.raises(IndexError):
        _ = board_10[-1]


def test_get_board_at_upper_bound_index_raises_error(board_10: ClassicBoard):
    with pytest.raises(IndexError):
        _ = board_10[10]


def test_get_board_at_existing_word_index_returns_card(board_10: ClassicBoard):
    card = board_10["Card 0"]
    assert card.word == "Card 0"


def test_get_board_at_non_existing_word_raises_error(board_10: ClassicBoard):
    with pytest.raises(CardNotFoundError):
        _ = board_10["foo"]


def test_get_board_at_float_index_raises_error(board_10: ClassicBoard):
    with pytest.raises(IndexError):
        _ = board_10[1.1]  # type: ignore


def test_two_integer_factors():
    x, y = two_integer_factors(25)
    assert x == 5 and y == 5

    x, y = two_integer_factors(30)
    assert x == 6 and y == 5

    x, y = two_integer_factors(17)
    assert x == 17 and y == 1


def test_str_is_printable_string(board_10: ClassicBoard, board_25: ClassicBoard):
    assert str(board_10) == board_10.printable_string
    print()
    print(board_10)

    assert str(board_25) == board_25.printable_string
    print()
    print(board_25)

    print()
    print(constants.hebrew_board().printable_string)


@pytest.mark.parametrize(
    "language",
    [
        "english",
        SupportedLanguage.HEBREW,
    ],
)
def test_basic_board_build(language: str):
    vocabulary = get_vocabulary(language=language)
    board = ClassicBoard.from_vocabulary(vocabulary=vocabulary)
    _validate_standard_board(board)


def test_build_board_with_params():
    vocabulary = get_vocabulary(language=SupportedLanguage.ENGLISH)
    board = ClassicBoard.from_vocabulary(
        vocabulary=vocabulary, board_size=17, assassin_amount=2, first_team=ClassicTeam.RED, seed=42
    )
    assert len(board.cards) == 17
    assert len(board.revealed_cards) == 0
    assert len(board.red_cards) == 6
    assert len(board.blue_cards) == 5
    assert len(board.neutral_cards) == 4
    assert len(board.assassin_cards) == 2


def _validate_standard_board(board: ClassicBoard):
    assert len(board.cards) == 25
    assert len(board.revealed_cards) == 0
    assert len(board.red_cards) >= 8
    assert len(board.blue_cards) >= 8
    assert len(board.neutral_cards) == 7
    assert len(board.assassin_cards) == 1
