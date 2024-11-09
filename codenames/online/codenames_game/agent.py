from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

from codenames.game.color import TeamColor
from codenames.game.move import Clue, Guess
from codenames.game.player import Operative, Player, Spymaster
from codenames.game.state import OperativeGameState, SpymasterGameState

if TYPE_CHECKING:
    from codenames.online.codenames_game.adapter import CodenamesGamePlayerAdapter

log = logging.getLogger(__name__)


class Agent(Player, ABC):
    def __init__(self, name: str, team: TeamColor):
        super().__init__(name, team)
        self.adapter: CodenamesGamePlayerAdapter | None = None

    def set_host_adapter(self, adapter: CodenamesGamePlayerAdapter):
        self.adapter = adapter


class SpymasterAgent(Agent, Spymaster):
    def give_clue(self, game_state: SpymasterGameState) -> Clue:
        if not self.adapter:
            raise RuntimeError("SpymasterAgent.adapter is not set")
        return self.adapter.poll_clue_given()  # type: ignore


class OperativeAgent(Agent, Operative):
    def guess(self, game_state: OperativeGameState) -> Guess:
        if not self.adapter:
            raise RuntimeError("OperativeAgent.adapter is not set")
        return self.adapter.poll_guess_given(game_state=game_state)  # type: ignore
