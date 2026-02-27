import pytest

from codenames.classic.color import ClassicColor
from codenames.classic.types import ClassicCard
from codenames.generic.card import canonical_format


def test_canonical_format_lowercase():
    """Test that canonical_format converts to lowercase."""
    assert canonical_format("HELLO") == "hello"
    assert canonical_format("Hello") == "hello"
    assert canonical_format("HeLLo WoRLD") == "hello world"


def test_canonical_format_replaces_underscores():
    """Test that canonical_format replaces underscores with spaces."""
    assert canonical_format("hello_world") == "hello world"
    assert canonical_format("one_two_three") == "one two three"


def test_canonical_format_strips_whitespace():
    """Test that canonical_format strips leading/trailing whitespace."""
    assert canonical_format("  hello  ") == "hello"
    assert canonical_format("\thello\n") == "hello"
    assert canonical_format("  hello world  ") == "hello world"


def test_canonical_format_combined_transformations():
    """Test canonical_format with multiple transformations."""
    assert canonical_format("  Hello_World  ") == "hello world"
    assert canonical_format("HELLO_WORLD") == "hello world"
    assert canonical_format("  ONE_TWO_THREE  ") == "one two three"


def test_canonical_format_empty_string():
    """Test canonical_format with empty string."""
    assert canonical_format("") == ""


def test_canonical_format_only_whitespace():
    """Test canonical_format with only whitespace."""
    assert canonical_format("   ") == ""
    assert canonical_format("\t\n") == ""


def test_canonical_format_already_formatted():
    """Test canonical_format with already formatted string."""
    assert canonical_format("hello world") == "hello world"
    assert canonical_format("test") == "test"


def test_canonical_format_multiple_spaces():
    """Test canonical_format preserves internal spaces."""
    assert canonical_format("hello  world") == "hello  world"
    assert canonical_format("one   two") == "one   two"


def test_canonical_format_special_characters():
    """Test canonical_format with special characters."""
    assert canonical_format("Hello-World") == "hello-world"
    assert canonical_format("Test@123") == "test@123"
    assert canonical_format("Word!") == "word!"


def test_canonical_format_numbers():
    """Test canonical_format with numbers."""
    assert canonical_format("Test123") == "test123"
    assert canonical_format("123_456") == "123 456"


def test_card_str_with_color():
    """Test Card string representation with color."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card_str = str(card)
    assert "ocean" in card_str
    assert "🟦" in card_str  # Blue emoji


def test_card_str_without_color():
    """Test Card string representation without color."""
    card = ClassicCard(word="ocean", color=None, revealed=False)
    assert str(card) == "ocean"


def test_card_str_red_color():
    """Test Card string representation with red color."""
    card = ClassicCard(word="fire", color=ClassicColor.RED, revealed=False)
    card_str = str(card)
    assert "fire" in card_str
    assert "🟥" in card_str  # Red emoji


def test_card_str_neutral_color():
    """Test Card string representation with neutral color."""
    card = ClassicCard(word="table", color=ClassicColor.NEUTRAL, revealed=False)
    card_str = str(card)
    assert "table" in card_str
    assert "⬜" in card_str  # Neutral emoji


def test_card_str_assassin_color():
    """Test Card string representation with assassin color."""
    card = ClassicCard(word="death", color=ClassicColor.ASSASSIN, revealed=False)
    card_str = str(card)
    assert "death" in card_str
    assert "💀" in card_str  # Assassin emoji


def test_card_hash_different_for_different_attributes():
    """Test that cards with different attributes have different hashes."""
    card1 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card2 = ClassicCard(word="ocean", color=ClassicColor.RED, revealed=False)
    card3 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    card4 = ClassicCard(word="beach", color=ClassicColor.BLUE, revealed=False)

    # All should have different hashes
    hashes = {hash(card1), hash(card2), hash(card3), hash(card4)}
    assert len(hashes) == 4


def test_card_hash_same_for_identical_cards():
    """Test that identical cards have the same hash."""
    card1 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card2 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)

    assert hash(card1) == hash(card2)


def test_card_hash_allows_set_membership():
    """Test that cards can be used in sets."""
    card1 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card2 = ClassicCard(word="beach", color=ClassicColor.RED, revealed=False)
    card3 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)

    card_set = {card1, card2, card3}
    # card1 and card3 are identical, so set should have 2 elements
    assert len(card_set) == 2


def test_card_censored_revealed_returns_self():
    """Test that censored property returns self when revealed."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    assert card.censored is card


def test_card_censored_not_revealed_hides_color():
    """Test that censored property hides color when not revealed."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    censored = card.censored

    assert censored.word == "ocean"
    assert censored.color is None
    assert censored.revealed is False


def test_card_censored_preserves_word():
    """Test that censored property preserves word."""
    card = ClassicCard(word="test", color=ClassicColor.RED, revealed=False)
    assert card.censored.word == "test"


def test_card_censored_preserves_revealed_false():
    """Test that censored property preserves revealed=False."""
    card = ClassicCard(word="test", color=ClassicColor.BLUE, revealed=False)
    assert card.censored.revealed is False


def test_card_formatted_word_uses_canonical_format():
    """Test that formatted_word uses canonical_format."""
    card = ClassicCard(word="Hello_World", color=ClassicColor.BLUE, revealed=False)
    assert card.formatted_word == "hello world"


def test_card_formatted_word_lowercase():
    """Test formatted_word converts to lowercase."""
    card = ClassicCard(word="OCEAN", color=ClassicColor.BLUE, revealed=False)
    assert card.formatted_word == "ocean"


def test_card_formatted_word_with_underscores():
    """Test formatted_word replaces underscores."""
    card = ClassicCard(word="sea_creature", color=ClassicColor.BLUE, revealed=False)
    assert card.formatted_word == "sea creature"


def test_card_equality():
    """Test card equality comparison."""
    card1 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card2 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)
    card3 = ClassicCard(word="beach", color=ClassicColor.BLUE, revealed=False)

    assert card1 == card2
    assert card1 != card3


def test_card_with_none_color_hash():
    """Test that cards with None color can be hashed."""
    card = ClassicCard(word="ocean", color=None, revealed=False)
    # Should not raise an error
    hash_value = hash(card)
    assert isinstance(hash_value, int)


def test_card_revealed_affects_hash():
    """Test that revealed status affects hash."""
    card1 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    card2 = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=False)

    assert hash(card1) != hash(card2)


def test_canonical_format_unicode():
    """Test canonical_format with unicode characters."""
    assert canonical_format("Café") == "café"
    assert canonical_format("Über_Cool") == "über cool"


def test_canonical_format_mixed_case_underscore():
    """Test canonical_format with mixed transformations."""
    assert canonical_format("  HELLO_World_TEST  ") == "hello world test"