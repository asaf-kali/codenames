from typing import Optional
from uuid import uuid4

from codenames.generic.card import Card, CardColor
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster, Team
from codenames.generic.state import OperativeState, SpymasterState


class CheaterSpymaster[C: CardColor, T: Team, S: SpymasterState](Spymaster[C, T, S]):
    def __init__(self, name: str, team: T, card_amount: int = 4):
        super().__init__(name, team)
        self.game_state: Optional[S] = None
        self.card_amount = card_amount

    def give_clue(self, game_state: S) -> Clue:
        self.game_state = game_state
        random_word = uuid4().hex[:4]
        return Clue(word=random_word, card_amount=self.card_amount)


class CheaterOperative[C: CardColor, T: Team, S: OperativeState](Operative[C, T, S]):
    def __init__(self, name: str, team: T, spymaster: CheaterSpymaster):
        super().__init__(name, team)
        self.spymaster = spymaster
        self.team_cards: list[Card[C]] = []

    def guess(self, game_state: S) -> Guess:
        if not self.team_cards:
            self._init_cheating()
        next_card = self.team_cards.pop()
        card_index = game_state.board.find_card_index(next_card.word)
        return Guess(card_index=card_index)

    def _init_cheating(self):
        spymaster_state = self.spymaster.game_state
        if spymaster_state is None:
            raise ValueError("Spymaster has not yet picked a clue")
        card_color = self.team.as_card_color
        cards_for_color = spymaster_state.board.cards_for_color(card_color=card_color)
        self.team_cards = list(cards_for_color)
