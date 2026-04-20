import pytest

from codenames.classic.color import CARD_COLOR_TO_EMOJI, ClassicColor


def test_classic_color_values():
    """Test that all expected colors are defined."""
    assert ClassicColor.BLUE.value == "BLUE"
    assert ClassicColor.RED.value == "RED"
    assert ClassicColor.NEUTRAL.value == "NEUTRAL"
    assert ClassicColor.ASSASSIN.value == "ASSASSIN"


def test_classic_color_emoji_blue():
    """Test emoji property for blue color."""
    assert ClassicColor.BLUE.emoji == "🟦"


def test_classic_color_emoji_red():
    """Test emoji property for red color."""
    assert ClassicColor.RED.emoji == "🟥"


def test_classic_color_emoji_neutral():
    """Test emoji property for neutral color."""
    assert ClassicColor.NEUTRAL.emoji == "⬜"


def test_classic_color_emoji_assassin():
    """Test emoji property for assassin color."""
    assert ClassicColor.ASSASSIN.emoji == "💀"


def test_all_colors_have_emoji_mapping():
    """Test that all colors have corresponding emoji in the mapping."""
    for color in ClassicColor:
        assert color in CARD_COLOR_TO_EMOJI
        assert isinstance(CARD_COLOR_TO_EMOJI[color], str)
        assert len(CARD_COLOR_TO_EMOJI[color]) > 0


def test_emoji_mapping_contains_only_valid_colors():
    """Test that emoji mapping doesn't contain extra keys."""
    assert len(CARD_COLOR_TO_EMOJI) == 4
    assert set(CARD_COLOR_TO_EMOJI.keys()) == {
        ClassicColor.RED,
        ClassicColor.BLUE,
        ClassicColor.NEUTRAL,
        ClassicColor.ASSASSIN,
    }


def test_color_string_representation():
    """Test string representation of colors."""
    assert str(ClassicColor.BLUE) == "ClassicColor.BLUE"
    assert str(ClassicColor.RED) == "ClassicColor.RED"


def test_color_equality():
    """Test that color instances are equal to themselves."""
    assert ClassicColor.BLUE == ClassicColor.BLUE
    assert ClassicColor.RED != ClassicColor.BLUE


def test_color_iteration():
    """Test that we can iterate over all colors."""
    colors = list(ClassicColor)
    assert len(colors) == 4
    assert ClassicColor.BLUE in colors
    assert ClassicColor.RED in colors
    assert ClassicColor.NEUTRAL in colors
    assert ClassicColor.ASSASSIN in colors


def test_color_membership():
    """Test membership checks for color enum."""
    assert "BLUE" in ClassicColor.__members__
    assert "RED" in ClassicColor.__members__
    assert "NEUTRAL" in ClassicColor.__members__
    assert "ASSASSIN" in ClassicColor.__members__
    assert "INVALID" not in ClassicColor.__members__