from typing import Dict, Iterable, List, NamedTuple

from codenames.game.color import TeamColor
from codenames.game.exceptions import QuitGame
from codenames.game.move import Guess, Hint
from codenames.game.player import GamePlayers, Guesser, Hinter, Player, Team
from codenames.game.state import GuesserGameState, HinterGameState


class UnexpectedEndOfInput(Exception):
    def __init__(self, player: Player):
        self.player = player


class DictatedHinter(Hinter):
    def __init__(
        self,
        hints: Iterable[Hint],
        team_color: TeamColor,
        name: str = "Test Hinter",
        auto_quit: bool = False,
    ):
        super().__init__(name=name, team_color=team_color)
        self.hints = list(hints)
        self.current_index = 0
        self.auto_quit = auto_quit

    def pick_hint(self, game_state: HinterGameState) -> Hint:
        if self.current_index >= len(self.hints):
            if self.auto_quit:
                raise QuitGame(self)
            raise UnexpectedEndOfInput(self)
        hint = self.hints[self.current_index]
        self.current_index += 1
        return hint


class DictatedGuesser(Guesser):
    def __init__(
        self,
        guesses: Iterable[Guess],
        team_color: TeamColor,
        name: str = "Test Guesser",
        auto_quit: bool = False,
    ):
        super().__init__(name=name, team_color=team_color)
        self.guesses = list(guesses)
        self.current_index = 0
        self.auto_quit = auto_quit

    def guess(self, game_state: GuesserGameState) -> Guess:
        if self.current_index >= len(self.guesses):
            if self.auto_quit:
                raise QuitGame(self)
            raise UnexpectedEndOfInput(self)
        guess = self.guesses[self.current_index]
        self.current_index += 1
        return guess


class DictatedTurn(NamedTuple):
    hint: Hint
    guesses: List[int]


def build_players(all_turns: Iterable[DictatedTurn], first_team: TeamColor = TeamColor.BLUE) -> GamePlayers:
    team_to_turns: Dict[TeamColor, List[DictatedTurn]] = {TeamColor.BLUE: [], TeamColor.RED: []}
    current_team_color = first_team
    for turn in all_turns:
        team_to_turns[current_team_color].append(turn)
        current_team_color = current_team_color.opponent
    blue_team = build_team(TeamColor.BLUE, turns=team_to_turns[TeamColor.BLUE])
    red_team = build_team(TeamColor.RED, turns=team_to_turns[TeamColor.RED])
    return GamePlayers(blue_team=blue_team, red_team=red_team)


def build_team(team_color: TeamColor, turns: Iterable[DictatedTurn]) -> Team:
    hints = [turn.hint for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    hinter = DictatedHinter(hints=hints, team_color=team_color)
    guesser = DictatedGuesser(guesses=guesses, team_color=team_color)
    return Team(hinter=hinter, guesser=guesser)
