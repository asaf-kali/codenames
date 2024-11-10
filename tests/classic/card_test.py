import json

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


def test_card_serialization():
    card = ClassicCard(word="Card 1", color=ClassicColor.BLUE, revealed=True)
    as_json = card.model_dump_json()
    as_dict = json.loads(as_json)
    expected_dict = {"word": "Card 1", "color": "BLUE", "revealed": True, "formatted_word": "card 1"}
    assert as_dict == expected_dict
    assert card.model_dump() == expected_dict
    card_loaded = ClassicCard.model_validate_json(as_json)
    assert hash(card_loaded) == hash(card)
