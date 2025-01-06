from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from codenames.classic.player import ClassicOperative, ClassicPlayer, ClassicSpymaster
from codenames.classic.team import ClassicTeam
from codenames.generic.move import Clue, Guess
from codenames.generic.state import OperativeState, SpymasterState

if TYPE_CHECKING:
    from codenames.online.codenames_game.adapter import CodenamesGamePlayerAdapter

log = logging.getLogger(__name__)


class Agent(ClassicPlayer):
    def __init__(self, name: str, team: ClassicTeam):
        super().__init__(name, team)
        self.adapter: CodenamesGamePlayerAdapter | None = None

    def set_host_adapter(self, adapter: CodenamesGamePlayerAdapter):
        self.adapter = adapter


class SpymasterAgent(Agent, ClassicSpymaster):
    def give_clue(self, game_state: SpymasterState) -> Clue:
        if not self.adapter:
            raise RuntimeError("SpymasterAgent.adapter is not set")
        return self.adapter.poll_clue_given()


class OperativeAgent(Agent, ClassicOperative):
    def guess(self, game_state: OperativeState) -> Guess:
        if not self.adapter:
            raise RuntimeError("OperativeAgent.adapter is not set")
        return self.adapter.poll_guess_given(game_state=game_state)
