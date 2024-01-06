from typing import List, Optional
from uuid import uuid4

from codenames.game.card import Card
from codenames.game.color import TeamColor
from codenames.game.move import Guess, Hint
from codenames.game.player import Guesser, Hinter
from codenames.game.state import GuesserGameState, HinterGameState


class CheaterHinter(Hinter):
    def __init__(self, name: str, team_color: TeamColor, card_amount: int = 4):
        super().__init__(name, team_color)
        self.game_state: Optional[HinterGameState] = None
        self.card_amount = card_amount

    def pick_hint(self, game_state: HinterGameState) -> Hint:
        self.game_state = game_state
        random_word = uuid4().hex[:4]
        return Hint(word=random_word, card_amount=self.card_amount)


class CheaterGuesser(Guesser):
    def __init__(self, name: str, team_color: TeamColor, hinter: CheaterHinter):
        super().__init__(name, team_color)
        self.hinter = hinter
        self.team_cards: List[Card] = []

    def guess(self, game_state: GuesserGameState) -> Guess:
        if not self.team_cards:
            self._init_cheating()
        next_card = self.team_cards.pop()
        card_index = game_state.board.find_card_index(next_card.word)
        return Guess(card_index=card_index)

    def _init_cheating(self):
        hinter_state = self.hinter.game_state
        if hinter_state is None:
            raise ValueError("Hinter has not yet picked a hint")
        self.team_cards = list(hinter_state.board.cards_for_color(card_color=self.team_color.as_card_color))
