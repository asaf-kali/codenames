from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING, Optional

from codenames.game.color import TeamColor
from codenames.game.move import Guess, Hint
from codenames.game.player import Guesser, Hinter, Player
from codenames.game.state import GuesserGameState, HinterGameState

if TYPE_CHECKING:
    from codenames.online.codenames_game.adapter import CodenamesGamePlayerAdapter

log = logging.getLogger(__name__)


class Agent(Player, ABC):
    def __init__(self, name: str, team_color: TeamColor):
        super().__init__(name, team_color)
        self.adapter: Optional[CodenamesGamePlayerAdapter] = None

    def set_host_adapter(self, adapter: CodenamesGamePlayerAdapter):
        self.adapter = adapter


class HinterAgent(Agent, Hinter):
    def pick_hint(self, game_state: HinterGameState) -> Hint:
        if not self.adapter:
            raise RuntimeError("HinterAgent.adapter is not set")
        return self.adapter.poll_hint_given()  # type: ignore


class GuesserAgent(Agent, Guesser):
    def guess(self, game_state: GuesserGameState) -> Guess:
        if not self.adapter:
            raise RuntimeError("GuesserAgent.adapter is not set")
        return self.adapter.poll_guess_given(game_state=game_state)  # type: ignore
