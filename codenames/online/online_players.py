import logging
from abc import ABC
from typing import Optional

from codenames.game import (
    Guess,
    Guesser,
    GuesserGameState,
    Hint,
    Hinter,
    HinterGameState,
    Player,
)
from codenames.online import NamecodingPlayerAdapter

log = logging.getLogger(__name__)


class Agent(Player, ABC):
    def __init__(self, name: str):
        super().__init__(name)
        self.adapter: Optional[NamecodingPlayerAdapter] = None

    def set_host_adapter(self, adapter: NamecodingPlayerAdapter):
        self.adapter = adapter


class HinterAgent(Agent, Hinter):
    def pick_hint(self, game_state: HinterGameState) -> Hint:
        if not self.adapter:
            raise RuntimeError("HinterAgent.adapter is not set")
        return self.adapter.poll_hint_given()


class GuesserAgent(Agent, Guesser):
    def guess(self, game_state: GuesserGameState) -> Guess:
        if not self.adapter:
            raise RuntimeError("GuesserAgent.adapter is not set")
        return self.adapter.poll_guess_given(game_state=game_state)
