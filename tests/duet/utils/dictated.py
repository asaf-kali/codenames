from typing import Iterable

from codenames.duet.player import DuetPlayer, DuetTeam
from codenames.duet.state import DuetSide
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster
from codenames.generic.state import OperativeState, SpymasterState
from tests.utils.players.dictated import DictatedOperative, DictatedSpymaster


class DictatedDuetPlayer(DuetPlayer, Spymaster[DuetTeam], Operative[DuetTeam]):
    def __init__(
        self,
        clues: Iterable[Clue],
        guesses: Iterable[Guess],
        side: DuetSide,
        auto_quit: bool = False,
    ):
        super().__init__(name=f"Duet player {side}", team=DuetTeam.MAIN)
        self._spymaster = DictatedSpymaster(clues=clues, team=DuetTeam.MAIN, auto_quit=auto_quit)
        self._operative = DictatedOperative(guesses=guesses, team=DuetTeam.MAIN, auto_quit=auto_quit)

    def give_clue(self, game_state: SpymasterState) -> Clue:
        return self._spymaster.give_clue(game_state=game_state)

    def guess(self, game_state: OperativeState) -> Guess:
        return self._operative.guess(game_state=game_state)
