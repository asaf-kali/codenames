from typing import Iterable, NamedTuple

from codenames.generic.card import CardColor
from codenames.generic.exceptions import QuitGame
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Player, Spymaster
from codenames.generic.state import OperativeState, SpymasterState
from codenames.generic.team import Team


class UnexpectedEndOfInput(Exception):
    def __init__(self, player: Player):
        self.player = player


class DictatedSpymaster[C: CardColor, T: Team, S: SpymasterState](Spymaster[C, T, S]):
    def __init__(
        self,
        clues: Iterable[Clue],
        team: T,
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


class DictatedOperative[C: CardColor, T: Team, S: OperativeState](Operative[C, T, S]):
    def __init__(
        self,
        guesses: Iterable[Guess],
        team: T,
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
