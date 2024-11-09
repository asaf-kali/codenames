from typing import Optional
from uuid import uuid4

from codenames.game.card import Card
from codenames.game.color import ClassicTeam
from codenames.game.move import Clue, Guess
from codenames.game.player import Operative, Spymaster
from codenames.game.state import OperativeGameState, SpymasterGameState


class CheaterSpymaster(Spymaster):
    def __init__(self, name: str, team: ClassicTeam, card_amount: int = 4):
        super().__init__(name, team)
        self.game_state: Optional[SpymasterGameState] = None
        self.card_amount = card_amount

    def give_clue(self, game_state: SpymasterGameState) -> Clue:
        self.game_state = game_state
        random_word = uuid4().hex[:4]
        return Clue(word=random_word, card_amount=self.card_amount)


class CheaterOperative(Operative):
    def __init__(self, name: str, team: ClassicTeam, spymaster: CheaterSpymaster):
        super().__init__(name, team)
        self.spymaster = spymaster
        self.team_cards: list[Card] = []

    def guess(self, game_state: OperativeGameState) -> Guess:
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
