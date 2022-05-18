from typing import Dict, Iterable, List, NamedTuple, Tuple

from codenames.game import GuesserGameState, HinterGameState
from codenames.game.base import Guess, Hint, TeamColor
from codenames.game.exceptions import QuitGame
from codenames.game.player import Guesser, Hinter, Player
from codenames.game.runner import Team


class UnexpectedEndOfInput(Exception):
    def __init__(self, player: Player):
        self.player = player


class TestHinter(Hinter):
    def __init__(
        self,
        hints: Iterable[Hint],
        name: str = "Test Hinter",
        auto_quit: bool = False,
    ):
        super().__init__(name=name)
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


class TestGuesser(Guesser):
    def __init__(
        self,
        guesses: Iterable[Guess],
        name: str = "Test Guesser",
        auto_quit: bool = False,
    ):
        super().__init__(name=name)
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


class PredictedTurn(NamedTuple):
    hint: Hint
    guesses: List[int]


def build_team(team_color: TeamColor, turns: Iterable[PredictedTurn]) -> Team:
    hints = [turn.hint for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    hinter = TestHinter(hints=hints)
    guesser = TestGuesser(guesses=guesses)
    return Team(hinter=hinter, guesser=guesser, team_color=team_color)


def build_teams(all_turns: Iterable[PredictedTurn]) -> Tuple[Team, Team]:
    team_to_turns: Dict[TeamColor, List[PredictedTurn]] = {TeamColor.BLUE: [], TeamColor.RED: []}
    current_team_color = TeamColor.BLUE
    for turn in all_turns:
        team_to_turns[current_team_color].append(turn)
        current_team_color = current_team_color.opponent
    blue_team = build_team(TeamColor.BLUE, turns=team_to_turns[TeamColor.BLUE])
    red_team = build_team(TeamColor.RED, turns=team_to_turns[TeamColor.RED])
    return blue_team, red_team
