from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster

SEPARATOR = "\n-----\n"
ClueGivenSubscriber = Callable[[Spymaster, Clue], None]
GuessGivenSubscriber = Callable[[Operative, Guess], None]


@dataclass(frozen=True)
class TeamPlayers:
    spymaster: Spymaster
    operative: Operative

    def __iter__(self):
        return iter([self.spymaster, self.operative])

    def __post_init__(self):
        if self.spymaster.team != self.operative.team:
            raise ValueError("Spymaster and Operative must be on the same team")
