import pytest

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicColor
from codenames.classic.team import ClassicTeam
from codenames.classic.types import ClassicCard
from codenames.generic.board import two_integer_factors
from codenames.generic.exceptions import CardNotFoundError


def test_board_size_property():
    """Test that board size property returns correct length."""
    cards = [
        ClassicCard(word=f"Card {i}", color=ClassicColor.BLUE, revealed=False)
        for i in range(10)
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.size == 10


def test_board_len():
    """Test that len() works on board."""
    cards = [
        ClassicCard(word=f"Card {i}", color=ClassicColor.BLUE, revealed=False)
        for i in range(5)
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert len(board) == 5


def test_board_is_clean_when_no_reveals():
    """Test is_clean returns True when no cards are revealed."""
    cards = [
        ClassicCard(word=f"Card {i}", color=ClassicColor.BLUE, revealed=False)
        for i in range(5)
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.is_clean is True


def test_board_is_not_clean_when_card_revealed():
    """Test is_clean returns False when a card is revealed."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.is_clean is False


def test_board_all_words():
    """Test all_words property returns formatted words."""
    cards = [
        ClassicCard(word="Ocean", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Beach_Sand", color=ClassicColor.RED, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.all_words == ("ocean", "beach sand")


def test_board_all_reveals():
    """Test all_reveals property returns reveal states."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=False),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.all_reveals == (True, False, True)


def test_board_revealed_card_indexes():
    """Test revealed_card_indexes returns correct indexes."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 3", color=ClassicColor.NEUTRAL, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.revealed_card_indexes == (1, 3)


def test_board_unrevealed_cards():
    """Test unrevealed_cards property returns only unrevealed cards."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    unrevealed = board.unrevealed_cards
    assert len(unrevealed) == 2
    assert unrevealed[0].word == "Card 0"
    assert unrevealed[1].word == "Card 2"


def test_board_revealed_cards():
    """Test revealed_cards property returns only revealed cards."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    revealed = board.revealed_cards
    assert len(revealed) == 2
    assert revealed[0].word == "Card 1"
    assert revealed[1].word == "Card 2"


def test_board_censored():
    """Test censored property hides colors of unrevealed cards."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    censored = board.censored

    assert censored.cards[0].color is None  # Unrevealed, color hidden
    assert censored.cards[1].color == ClassicColor.RED  # Revealed, color shown


def test_board_cards_for_color():
    """Test cards_for_color returns cards of specified color."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=False),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 3", color=ClassicColor.NEUTRAL, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    blue_cards = board.cards_for_color(ClassicColor.BLUE)
    assert len(blue_cards) == 2
    assert all(card.color == ClassicColor.BLUE for card in blue_cards)


def test_board_revealed_cards_for_color():
    """Test revealed_cards_for_color returns revealed cards of specified color."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 2", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 3", color=ClassicColor.RED, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    revealed_blue = board.revealed_cards_for_color(ClassicColor.BLUE)
    assert len(revealed_blue) == 2
    assert all(card.color == ClassicColor.BLUE and card.revealed for card in revealed_blue)


def test_board_unrevealed_cards_for_color():
    """Test unrevealed_cards_for_color returns unrevealed cards of specified color."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.RED, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=False),
        ClassicCard(word="Card 2", color=ClassicColor.RED, revealed=False),
        ClassicCard(word="Card 3", color=ClassicColor.BLUE, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    unrevealed_red = board.unrevealed_cards_for_color(ClassicColor.RED)
    assert len(unrevealed_red) == 2
    assert all(card.color == ClassicColor.RED and not card.revealed for card in unrevealed_red)


def test_board_find_card_index():
    """Test find_card_index returns correct index."""
    cards = [
        ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="beach", color=ClassicColor.RED, revealed=False),
        ClassicCard(word="sand", color=ClassicColor.NEUTRAL, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.find_card_index("beach") == 1


def test_board_find_card_index_case_insensitive():
    """Test find_card_index is case insensitive."""
    cards = [
        ClassicCard(word="Ocean", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Beach", color=ClassicColor.RED, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.find_card_index("OCEAN") == 0
    assert board.find_card_index("beach") == 1


def test_board_find_card_index_raises_error_for_missing_word():
    """Test find_card_index raises CardNotFoundError for missing word."""
    cards = [
        ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    with pytest.raises(CardNotFoundError):
        board.find_card_index("missing")


def test_board_reset_state():
    """Test reset_state sets all cards to unrevealed."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
        ClassicCard(word="Card 2", color=ClassicColor.NEUTRAL, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)
    board.reset_state()

    assert all(not card.revealed for card in board.cards)


def test_board_iteration():
    """Test that board can be iterated over."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=False),
    ]
    board = ClassicBoard(language="english", cards=cards)

    words = [card.word for card in board]
    assert words == ["Card 0", "Card 1"]


def test_two_integer_factors_perfect_square():
    """Test two_integer_factors with perfect square."""
    x, y = two_integer_factors(16)
    assert x * y == 16
    assert x == 4
    assert y == 4


def test_two_integer_factors_prime():
    """Test two_integer_factors with prime number."""
    x, y = two_integer_factors(7)
    assert x * y == 7
    assert x == 7
    assert y == 1


def test_two_integer_factors_rectangle():
    """Test two_integer_factors with non-square number."""
    x, y = two_integer_factors(12)
    assert x * y == 12
    # Should return factors close to square root
    assert (x, y) in [(4, 3), (3, 4), (6, 2), (2, 6)]


def test_two_integer_factors_zero():
    """Test two_integer_factors with zero."""
    x, y = two_integer_factors(0)
    assert x == 0
    assert y == 0


def test_two_integer_factors_one():
    """Test two_integer_factors with one."""
    x, y = two_integer_factors(1)
    assert x * y == 1


def test_board_from_vocabulary_creates_correct_size():
    """Test that from_vocabulary creates board of correct size."""
    board = ClassicBoard.from_vocabulary(
        vocabulary=type("Vocabulary", (), {"language": "english", "words": [f"word{i}" for i in range(100)]})(),
        board_size=20,
        seed=42,
    )
    assert len(board.cards) == 20


def test_board_from_vocabulary_respects_assassin_amount():
    """Test that from_vocabulary respects assassin_amount parameter."""
    board = ClassicBoard.from_vocabulary(
        vocabulary=type("Vocabulary", (), {"language": "english", "words": [f"word{i}" for i in range(100)]})(),
        board_size=20,
        assassin_amount=3,
        seed=42,
    )
    assert len(board.assassin_cards) == 3


def test_board_from_vocabulary_respects_first_team():
    """Test that from_vocabulary respects first_team parameter."""
    board = ClassicBoard.from_vocabulary(
        vocabulary=type("Vocabulary", (), {"language": "english", "words": [f"word{i}" for i in range(100)]})(),
        board_size=15,
        first_team=ClassicTeam.BLUE,
        seed=42,
    )
    # Blue team should have one more card (15 // 3 = 5, blue gets 6)
    assert len(board.blue_cards) == len(board.red_cards) + 1


def test_board_from_vocabulary_with_seed_is_reproducible():
    """Test that same seed produces same board."""
    vocab = type("Vocabulary", (), {"language": "english", "words": [f"word{i}" for i in range(100)]})()

    board1 = ClassicBoard.from_vocabulary(vocabulary=vocab, board_size=10, seed=42)
    board2 = ClassicBoard.from_vocabulary(vocabulary=vocab, board_size=10, seed=42)

    assert board1.all_words == board2.all_words
    assert [card.color for card in board1.cards] == [card.color for card in board2.cards]


def test_board_getitem_with_negative_index_raises():
    """Test that accessing board with negative index raises IndexError."""
    cards = [ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=False)]
    board = ClassicBoard(language="english", cards=cards)
    with pytest.raises(IndexError):
        _ = board[-1]


def test_board_empty_board():
    """Test board with no cards."""
    board = ClassicBoard(language="english", cards=[])
    assert board.size == 0
    assert len(board.cards) == 0
    assert board.is_clean is True
    assert board.revealed_cards == ()
    assert board.unrevealed_cards == ()


def test_board_all_cards_revealed():
    """Test board where all cards are revealed."""
    cards = [
        ClassicCard(word="Card 0", color=ClassicColor.BLUE, revealed=True),
        ClassicCard(word="Card 1", color=ClassicColor.RED, revealed=True),
    ]
    board = ClassicBoard(language="english", cards=cards)
    assert board.is_clean is False
    assert len(board.revealed_cards) == 2
    assert len(board.unrevealed_cards) == 0