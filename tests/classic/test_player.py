import pytest

from codenames.classic.color import ClassicColor
from codenames.classic.player import ClassicPlayer
from codenames.classic.runner import ClassicGamePlayers
from codenames.classic.team import ClassicTeam
from codenames.generic.player import PlayerRole
from codenames.generic.runner import TeamPlayers
from tests.classic.utils.dictated import (
    ClassicDictatedOperative,
    ClassicDictatedSpymaster,
)


def test_player_team_card_color():
    p1 = ClassicPlayer("Player 1", team=ClassicTeam.RED)
    p2 = ClassicPlayer("Player 2", team=ClassicTeam.BLUE)
    assert p1.team.as_card_color == ClassicColor.RED
    assert p2.team.as_card_color == ClassicColor.BLUE


def test_play_to_string():
    p1 = ClassicDictatedOperative(guesses=[], name="Player 1", team=ClassicTeam.RED)
    p2 = ClassicDictatedSpymaster(clues=[], name="Player 2", team=ClassicTeam.BLUE)

    assert str(p1) == "Player 1 | Red Classic Dictated Operative"
    assert str(p2) == "Player 2 | Blue Classic Dictated Spymaster"


def test_game_players_builder():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = ClassicDictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = ClassicDictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = ClassicDictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    players = ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster, red_operative)

    assert players.blue_team == TeamPlayers(blue_spymaster, blue_operative)
    assert players.red_team == TeamPlayers(red_spymaster, red_operative)


def test_game_players_builder_raises_if_not_enough_players():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = ClassicDictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = ClassicDictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)

    with pytest.raises(ValueError):
        ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster)


def test_game_players_builder_raises_if_operative_missing_from_team():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = ClassicDictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = ClassicDictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    blue_operative_2 = ClassicDictatedOperative(guesses=[], name="Blue Operative 2", team=ClassicTeam.BLUE)

    with pytest.raises(ValueError):
        ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster, blue_operative_2)


def test_get_player():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = ClassicDictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = ClassicDictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = ClassicDictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    players = ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster, red_operative)
    blue_spymaster_2 = players.get_player(team=ClassicTeam.BLUE, role=PlayerRole.SPYMASTER)
    red_operative_2 = players.get_player(team=ClassicTeam.RED, role=PlayerRole.OPERATIVE)

    assert blue_spymaster_2 == blue_spymaster
    assert red_operative_2 == red_operative


def test_game_players_properties():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    blue_operative = ClassicDictatedOperative(guesses=[], name="Blue Operative", team=ClassicTeam.BLUE)
    red_spymaster = ClassicDictatedSpymaster(clues=[], name="Red Spymaster", team=ClassicTeam.RED)
    red_operative = ClassicDictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    players = ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster, red_operative)
    assert players.spymasters == (blue_spymaster, red_spymaster)
    assert players.operatives == (blue_operative, red_operative)


def test_team_raises_if_spymaster_and_operative_have_different_teams():
    blue_spymaster = ClassicDictatedSpymaster(clues=[], name="Blue Spymaster", team=ClassicTeam.BLUE)
    red_operative = ClassicDictatedOperative(guesses=[], name="Red Operative", team=ClassicTeam.RED)

    with pytest.raises(ValueError):
        TeamPlayers(spymaster=blue_spymaster, operative=red_operative)
