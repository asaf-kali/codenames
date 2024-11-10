import pytest

from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.runner.models import GamePlayers, TeamPlayers
from codenames.generic.player import Player, PlayerRole
from tests.utils.players.dictated import DictatedOperative, DictatedSpymaster


def test_player_team_card_color():
    p1 = Player("Player 1", team=ClassicTeam.RED)
    p2 = Player("Player 2", team=ClassicTeam.BLUE)
    assert p1.team.as_card_color == ClassicColor.RED
    assert p2.team.as_card_color == ClassicColor.BLUE


def test_play_to_string():
    p1 = DictatedOperative(guesses=[], name="Player 1", team=ClassicTeam.RED)
    p2 = DictatedSpymaster(clues=[], name="Player 2", team=ClassicTeam.BLUE)

    assert str(p1) == "Player 1 | Red Dictated Operative"
    assert str(p2) == "Player 2 | Blue Dictated Spymaster"


def test_game_players_builder():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = DictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = DictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = DictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    all_players = [blue_spymaster, blue_operative, red_spymaster, red_operative]
    players = GamePlayers.from_collection(all_players)

    assert players.blue_team == TeamPlayers(blue_spymaster, blue_operative)
    assert players.red_team == TeamPlayers(red_spymaster, red_operative)


def test_game_players_builder_raises_if_not_enough_players():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = DictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = DictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)

    all_players = [blue_spymaster, blue_operative, red_spymaster]
    with pytest.raises(ValueError):
        GamePlayers.from_collection(all_players)


def test_game_players_builder_raises_if_operative_missing_from_team():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = DictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = DictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    blue_operative_2 = DictatedOperative(guesses=[], name="Blue Operative 2", team=ClassicTeam.BLUE)

    all_players = [blue_spymaster, blue_operative, red_spymaster, blue_operative_2]
    with pytest.raises(ValueError):
        GamePlayers.from_collection(all_players)


def test_get_player():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = DictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = DictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = DictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    players = GamePlayers.from_collection([blue_spymaster, blue_operative, red_spymaster, red_operative])
    blue_spymaster_2 = players.get_player(team=ClassicTeam.BLUE, role=PlayerRole.SPYMASTER)
    red_operative_2 = players.get_player(team=ClassicTeam.RED, role=PlayerRole.OPERATIVE)

    assert blue_spymaster_2 == blue_spymaster
    assert red_operative_2 == red_operative


def test_game_players_properties():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = DictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = DictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = DictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    players = GamePlayers.from_collection([blue_spymaster, blue_operative, red_spymaster, red_operative])
    assert players.spymasters == (blue_spymaster, red_spymaster)
    assert players.operatives == (blue_operative, red_operative)


def test_team_raises_if_spymaster_and_operative_have_different_teams():
    blue_spymaster = DictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    red_operative = DictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    with pytest.raises(ValueError):
        TeamPlayers(spymaster=blue_spymaster, operative=red_operative)
