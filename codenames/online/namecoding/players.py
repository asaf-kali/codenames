import logging
from abc import ABC

from codenames.game.move import Clue, Guess
from codenames.game.player import Operative, Player, Spymaster
from codenames.game.state import OperativeGameState, SpymasterGameState
from codenames.online.namecoding.adapter import NamecodingPlayerAdapter

log = logging.getLogger(__name__)


class Agent(Player, ABC):
    def __init__(self, name: str):
        super().__init__(name)
        self.adapter: NamecodingPlayerAdapter | None = None

    def set_host_adapter(self, adapter: NamecodingPlayerAdapter):
        self.adapter = adapter


class SpymasterAgent(Agent, Spymaster):
    def give_clue(self, game_state: SpymasterGameState) -> Clue:
        if not self.adapter:
            raise RuntimeError("SpymasterAgent.adapter is not set")
        return self.adapter.poll_clue_given()


class OperativeAgent(Agent, Operative):
    def guess(self, game_state: OperativeGameState) -> Guess:
        if not self.adapter:
            raise RuntimeError("OperativeAgent.adapter is not set")
        return self.adapter.poll_guess_given(game_state=game_state)
