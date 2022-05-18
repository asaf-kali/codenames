from codenames.game.base import Card, CardColor


def test_censored_when_revealed_is_same_as_card():
    card = Card(word="Card 3", color=CardColor.BLUE, revealed=True)
    assert card.censored == card


def test_censored_when_not_revealed_does_not_have_color():
    card = Card(word="Card 3", color=CardColor.BLUE, revealed=False)
    assert card.censored == Card(word="Card 3", color=None, revealed=False)


def test_cards_can_be_members_of_a_set():
    card1 = Card(word="Card 1", color=None, revealed=False)
    card2 = Card(word="Card 1", color=CardColor.BLUE, revealed=False)
    card3 = Card(word="Card 1", color=CardColor.BLUE, revealed=True)
    card_set = {card1, card2, card3}
    assert len(card_set) == 3
