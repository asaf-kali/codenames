import pytest

from codenames.classic.color import ClassicColor
from codenames.classic.team import ClassicTeam


def test_classic_team_values():
    """Test that all expected teams are defined."""
    assert ClassicTeam.BLUE.value == "BLUE"
    assert ClassicTeam.RED.value == "RED"


def test_classic_team_as_card_color_blue():
    """Test as_card_color for blue team."""
    assert ClassicTeam.BLUE.as_card_color == ClassicColor.BLUE


def test_classic_team_as_card_color_red():
    """Test as_card_color for red team."""
    assert ClassicTeam.RED.as_card_color == ClassicColor.RED


def test_classic_team_opponent_blue():
    """Test opponent property for blue team."""
    assert ClassicTeam.BLUE.opponent == ClassicTeam.RED


def test_classic_team_opponent_red():
    """Test opponent property for red team."""
    assert ClassicTeam.RED.opponent == ClassicTeam.BLUE


def test_classic_team_double_opponent():
    """Test that opponent of opponent returns original team."""
    assert ClassicTeam.BLUE.opponent.opponent == ClassicTeam.BLUE
    assert ClassicTeam.RED.opponent.opponent == ClassicTeam.RED


def test_classic_team_string_representation():
    """Test string representation of teams."""
    assert str(ClassicTeam.BLUE) == "ClassicTeam.BLUE"
    assert str(ClassicTeam.RED) == "ClassicTeam.RED"


def test_classic_team_equality():
    """Test that team instances are equal to themselves."""
    assert ClassicTeam.BLUE == ClassicTeam.BLUE
    assert ClassicTeam.RED == ClassicTeam.RED
    assert ClassicTeam.BLUE != ClassicTeam.RED


def test_classic_team_iteration():
    """Test that we can iterate over all teams."""
    teams = list(ClassicTeam)
    assert len(teams) == 2
    assert ClassicTeam.BLUE in teams
    assert ClassicTeam.RED in teams


def test_classic_team_membership():
    """Test membership checks for team enum."""
    assert "BLUE" in ClassicTeam.__members__
    assert "RED" in ClassicTeam.__members__
    assert "GREEN" not in ClassicTeam.__members__


def test_classic_team_card_color_types():
    """Test that as_card_color returns ClassicColor instances."""
    assert isinstance(ClassicTeam.BLUE.as_card_color, ClassicColor)
    assert isinstance(ClassicTeam.RED.as_card_color, ClassicColor)


def test_classic_team_opponent_types():
    """Test that opponent returns ClassicTeam instances."""
    assert isinstance(ClassicTeam.BLUE.opponent, ClassicTeam)
    assert isinstance(ClassicTeam.RED.opponent, ClassicTeam)


def test_classic_team_all_teams_have_card_color():
    """Test that all teams have a corresponding card color."""
    for team in ClassicTeam:
        card_color = team.as_card_color
        assert card_color is not None
        assert isinstance(card_color, ClassicColor)


def test_classic_team_all_teams_have_opponent():
    """Test that all teams have an opponent."""
    for team in ClassicTeam:
        opponent = team.opponent
        assert opponent is not None
        assert isinstance(opponent, ClassicTeam)
        assert opponent != team


def test_classic_team_card_color_matches_team_name():
    """Test that card color matches team name."""
    assert ClassicTeam.BLUE.as_card_color == ClassicColor.BLUE
    assert ClassicTeam.RED.as_card_color == ClassicColor.RED


def test_classic_team_opponents_are_symmetric():
    """Test that if A's opponent is B, then B's opponent is A."""
    blue_opponent = ClassicTeam.BLUE.opponent
    red_opponent = ClassicTeam.RED.opponent

    assert blue_opponent == ClassicTeam.RED
    assert red_opponent == ClassicTeam.BLUE


def test_classic_team_can_be_used_in_set():
    """Test that teams can be used in sets."""
    team_set = {ClassicTeam.BLUE, ClassicTeam.RED, ClassicTeam.BLUE}
    assert len(team_set) == 2


def test_classic_team_can_be_used_as_dict_key():
    """Test that teams can be used as dictionary keys."""
    team_dict = {
        ClassicTeam.BLUE: "Blue Team",
        ClassicTeam.RED: "Red Team",
    }
    assert team_dict[ClassicTeam.BLUE] == "Blue Team"
    assert team_dict[ClassicTeam.RED] == "Red Team"


def test_classic_team_hashable():
    """Test that teams are hashable."""
    blue_hash = hash(ClassicTeam.BLUE)
    red_hash = hash(ClassicTeam.RED)

    assert isinstance(blue_hash, int)
    assert isinstance(red_hash, int)
    assert blue_hash != red_hash


def test_classic_team_comparison():
    """Test team comparison operations."""
    assert ClassicTeam.BLUE == ClassicTeam.BLUE
    assert not (ClassicTeam.BLUE != ClassicTeam.BLUE)
    assert ClassicTeam.BLUE != ClassicTeam.RED
    assert not (ClassicTeam.BLUE == ClassicTeam.RED)