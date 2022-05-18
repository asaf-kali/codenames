from codenames.game import Card, CardColor


def test_card_to_dict_returns_without_cached_properties():
    card = Card(word="Dog", color=CardColor.BLUE, revealed=True)
    assert card.formatted_word == "dog"
    card_dict = card.dict()
    assert card_dict == {
        "word": "Dog",
        "color": CardColor.BLUE,
        "revealed": True,
    }


def test_card_to_dict_returns_with_cached_properties_if_included():
    card = Card(word="Dog", color=CardColor.BLUE, revealed=True)
    assert card.formatted_word == "dog"
    card_dict = card.dict(include={"formatted_word"})
    assert card_dict == {
        "formatted_word": "dog",
    }
