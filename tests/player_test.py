import pytest

from codenames.game.color import CardColor, TeamColor
from codenames.game.player import GamePlayers, Player, PlayerRole, Team
from tests.utils.players import DictatedGuesser, DictatedHinter


def test_player_team_card_color():
    p1 = Player("Player 1", team_color=TeamColor.RED)
    p2 = Player("Player 2", team_color=TeamColor.BLUE)
    assert p1.team_card_color == CardColor.RED
    assert p2.team_card_color == CardColor.BLUE


def test_play_to_string():
    p1 = DictatedGuesser(guesses=[], name="Player 1", team_color=TeamColor.RED)
    p2 = DictatedHinter(hints=[], name="Player 2", team_color=TeamColor.BLUE)

    assert str(p1) == "Player 1 | Red Dictated Guesser"
    assert str(p2) == "Player 2 | Blue Dictated Hinter"


def test_game_players_builder():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    blue_guesser = DictatedGuesser(guesses=[], name="Blue Guesser", team_color=TeamColor.BLUE)
    red_hinter = DictatedHinter(hints=[], name="Red Hinter", team_color=TeamColor.RED)
    red_guesser = DictatedGuesser(guesses=[], name="Red Guesser", team_color=TeamColor.RED)

    all_players = [blue_hinter, blue_guesser, red_hinter, red_guesser]
    players = GamePlayers.from_collection(all_players)

    assert players.blue_team == Team(blue_hinter, blue_guesser)
    assert players.red_team == Team(red_hinter, red_guesser)


def test_game_players_builder_raises_if_not_enough_players():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    blue_guesser = DictatedGuesser(guesses=[], name="Blue Guesser", team_color=TeamColor.BLUE)
    red_hinter = DictatedHinter(hints=[], name="Red Hinter", team_color=TeamColor.RED)

    all_players = [blue_hinter, blue_guesser, red_hinter]
    with pytest.raises(ValueError):
        GamePlayers.from_collection(all_players)


def test_game_players_builder_raises_if_guesser_missing_from_team():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    blue_guesser = DictatedGuesser(guesses=[], name="Blue Guesser", team_color=TeamColor.BLUE)
    red_hinter = DictatedHinter(hints=[], name="Red Hinter", team_color=TeamColor.RED)
    blue_guesser_2 = DictatedGuesser(guesses=[], name="Blue Guesser 2", team_color=TeamColor.BLUE)

    all_players = [blue_hinter, blue_guesser, red_hinter, blue_guesser_2]
    with pytest.raises(ValueError):
        GamePlayers.from_collection(all_players)


def test_get_player():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    blue_guesser = DictatedGuesser(guesses=[], name="Blue Guesser", team_color=TeamColor.BLUE)
    red_hinter = DictatedHinter(hints=[], name="Red Hinter", team_color=TeamColor.RED)
    red_guesser = DictatedGuesser(guesses=[], name="Red Guesser", team_color=TeamColor.RED)

    players = GamePlayers.from_collection([blue_hinter, blue_guesser, red_hinter, red_guesser])
    blue_hinter_2 = players.get_player(team_color=TeamColor.BLUE, role=PlayerRole.HINTER)
    red_guesser_2 = players.get_player(team_color=TeamColor.RED, role=PlayerRole.GUESSER)

    assert blue_hinter_2 == blue_hinter
    assert red_guesser_2 == red_guesser


def test_game_players_properties():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    blue_guesser = DictatedGuesser(guesses=[], name="Blue Guesser", team_color=TeamColor.BLUE)
    red_hinter = DictatedHinter(hints=[], name="Red Hinter", team_color=TeamColor.RED)
    red_guesser = DictatedGuesser(guesses=[], name="Red Guesser", team_color=TeamColor.RED)

    players = GamePlayers.from_collection([blue_hinter, blue_guesser, red_hinter, red_guesser])
    assert players.hinters == (blue_hinter, red_hinter)
    assert players.guessers == (blue_guesser, red_guesser)


def test_team_raises_if_hinter_and_guesser_have_different_team_colors():
    blue_hinter = DictatedHinter(hints=[], name="Blue Hinter", team_color=TeamColor.BLUE)
    red_guesser = DictatedGuesser(guesses=[], name="Red Guesser", team_color=TeamColor.RED)

    with pytest.raises(ValueError):
        Team(hinter=blue_hinter, guesser=red_guesser)
