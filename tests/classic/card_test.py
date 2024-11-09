from codenames.classic.color import ClassicColor
from codenames.classic.types import ClassicCard


def test_censored_when_revealed_is_same_as_card():
    card = ClassicCard(word="Card 3", color=ClassicColor.BLUE, revealed=True)
    assert card.censored == card


def test_censored_when_not_revealed_does_not_have_color():
    card = ClassicCard(word="Card 3", color=ClassicColor.BLUE, revealed=False)
    assert card.censored == ClassicCard(word="Card 3", color=None, revealed=False)


def test_cards_can_be_members_of_a_set():
    card1 = ClassicCard(word="Card 1", color=None, revealed=False)
    card2 = ClassicCard(word="Card 1", color=ClassicColor.BLUE, revealed=False)
    card3 = ClassicCard(word="Card 1", color=ClassicColor.BLUE, revealed=True)
    card_set = {card1, card2, card3}
    assert len(card_set) == 3
