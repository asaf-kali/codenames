import pytest

from codenames.game import CardColor, Player, TeamColor
from tests.utils.testing_players import TestGuesser, TestHinter


def test_player_team_card_color():
    p1 = Player("Player 1")
    p1.team_color = TeamColor.RED
    p2 = Player("Player 2")
    p2.team_color = TeamColor.BLUE
    p3 = Player("Player 3")
    p3.team_color = None

    assert p1.team_card_color == CardColor.RED
    assert p2.team_card_color == CardColor.BLUE

    with pytest.raises(ValueError):
        _ = p3.team_card_color


def test_play_to_string():
    p1 = TestGuesser(guesses=[], name="Player 1", team_color=TeamColor.RED)
    p2 = TestHinter(hints=[], name="Player 2")

    assert str(p1) == "Player 1 - Red Guesser (TestGuesser)"
    assert str(p2) == "Player 2 - Hinter (TestHinter)"
