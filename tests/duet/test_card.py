import json

from codenames.duet.card import DuetColor
from codenames.duet.types import DuetCard


def test_card_serialization():
    card = DuetCard(word="Card 1", color=DuetColor.GREEN, revealed=True)
    as_json = card.model_dump_json()
    as_dict = json.loads(as_json)
    expected_dict = {"word": "Card 1", "color": "GREEN", "revealed": True, "formatted_word": "card 1"}
    assert as_dict == expected_dict
    assert card.model_dump() == expected_dict
    card_loaded = DuetCard.model_validate_json(as_json)
    assert hash(card_loaded) == hash(card)
