import pytest

from codenames.game.base import CardColor, TeamColor
from codenames.game.player import Player


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
