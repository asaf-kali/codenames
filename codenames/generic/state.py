from __future__ import annotations

import logging
from typing import Generic

from pydantic import BaseModel

from codenames.generic.board import Board, WordGroup
from codenames.generic.card import C
from codenames.generic.move import Clue, GivenClue, GivenGuess

log = logging.getLogger(__name__)


class PlayerState(BaseModel, Generic[C]):
    """
    Represents all the information that is available to any player
    """

    board: Board[C]
    given_clues: list[GivenClue] = []
    given_guesses: list[GivenGuess] = []

    @property
    def given_clue_words(self) -> WordGroup:
        return tuple(clue.formatted_word for clue in self.given_clues)

    @property
    def illegal_clue_words(self) -> WordGroup:
        return *self.board.all_words, *self.given_clue_words


class SpymasterState(PlayerState):
    """
    Represents all the information that is available to a Spymaster.
    """

    clues: list[Clue] = []


class OperativeState(PlayerState):
    """
    Represents all the information that is available to an Operative.
    """

    @property
    def current_clue(self) -> GivenClue:
        return self.given_clues[-1]
