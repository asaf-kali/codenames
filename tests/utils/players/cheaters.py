from typing import Generic, Optional
from uuid import uuid4

from codenames.generic.card import C, Card
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster, T
from codenames.generic.state import OperativeState, SpymasterState


class CheaterSpymaster(Spymaster, Generic[C, T]):
    def __init__(self, name: str, team: T, card_amount: int = 4):
        super().__init__(name, team)
        self.game_state: Optional[SpymasterState[C, T]] = None
        self.card_amount = card_amount

    def give_clue(self, game_state: SpymasterState[C, T]) -> Clue:
        self.game_state = game_state
        random_word = uuid4().hex[:4]
        return Clue(word=random_word, card_amount=self.card_amount)


class CheaterOperative(Operative, Generic[C, T]):
    def __init__(self, name: str, team: T, spymaster: CheaterSpymaster):
        super().__init__(name, team)
        self.spymaster = spymaster
        self.team_cards: list[Card[C]] = []

    def guess(self, game_state: OperativeState) -> Guess:
        if not self.team_cards:
            self._init_cheating()
        next_card = self.team_cards.pop()
        card_index = game_state.board.find_card_index(next_card.word)
        return Guess(card_index=card_index)

    def _init_cheating(self):
        spymaster_state = self.spymaster.game_state
        if spymaster_state is None:
            raise ValueError("Spymaster has not yet picked a clue")
        self.team_cards = list(spymaster_state.board.cards_for_color(card_color=self.team.as_card_color))
