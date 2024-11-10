from typing import Iterable, NamedTuple

from codenames.classic.color import ClassicTeam
from codenames.classic.runner.models import GamePlayers, TeamPlayers
from codenames.generic.exceptions import QuitGame
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Player, Spymaster
from codenames.generic.state import OperativeState, SpymasterState


class UnexpectedEndOfInput(Exception):
    def __init__(self, player: Player):
        self.player = player


class DictatedSpymaster(Spymaster):
    def __init__(
        self,
        clues: Iterable[Clue],
        team: ClassicTeam,
        name: str = "Test Spymaster",
        auto_quit: bool = False,
    ):
        super().__init__(name=name, team=team)
        self.clues = list(clues)
        self.current_index = 0
        self.auto_quit = auto_quit

    def give_clue(self, game_state: SpymasterState) -> Clue:
        if self.current_index >= len(self.clues):
            if self.auto_quit:
                raise QuitGame(self)
            raise UnexpectedEndOfInput(self)
        clue = self.clues[self.current_index]
        self.current_index += 1
        return clue


class DictatedOperative(Operative):
    def __init__(
        self,
        guesses: Iterable[Guess],
        team: ClassicTeam,
        name: str = "Test Operative",
        auto_quit: bool = False,
    ):
        super().__init__(name=name, team=team)
        self.guesses = list(guesses)
        self.current_index = 0
        self.auto_quit = auto_quit

    def guess(self, game_state: OperativeState) -> Guess:
        if self.current_index >= len(self.guesses):
            if self.auto_quit:
                raise QuitGame(self)
            raise UnexpectedEndOfInput(self)
        guess = self.guesses[self.current_index]
        self.current_index += 1
        return guess


class DictatedTurn(NamedTuple):
    clue: Clue
    guesses: list[int]


def build_players(all_turns: Iterable[DictatedTurn], first_team: ClassicTeam = ClassicTeam.BLUE) -> GamePlayers:
    team_to_turns: dict[ClassicTeam, list[DictatedTurn]] = {ClassicTeam.BLUE: [], ClassicTeam.RED: []}
    current_team = first_team
    for turn in all_turns:
        team_to_turns[current_team].append(turn)
        current_team = current_team.opponent
    blue_team = build_team(ClassicTeam.BLUE, turns=team_to_turns[ClassicTeam.BLUE])
    red_team = build_team(ClassicTeam.RED, turns=team_to_turns[ClassicTeam.RED])
    return GamePlayers(blue_team=blue_team, red_team=red_team)


def build_team(team: ClassicTeam, turns: Iterable[DictatedTurn]) -> TeamPlayers:
    clues = [turn.clue for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    spymaster = DictatedSpymaster(clues=clues, team=team)
    operative = DictatedOperative(guesses=guesses, team=team)
    return TeamPlayers(spymaster=spymaster, operative=operative)
