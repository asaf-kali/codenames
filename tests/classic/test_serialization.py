from codenames.classic.color import ClassicColor
from codenames.classic.types import ClassicCard


def test_card_to_dict_returns_without_cached_properties():
    card = ClassicCard(word="Dog", color=ClassicColor.BLUE, revealed=True)
    assert card.formatted_word == "dog"
    card_dict = card.model_dump()
    assert card_dict == {
        "word": "Dog",
        "formatted_word": "dog",
        "color": ClassicColor.BLUE,
        "revealed": True,
    }


def test_card_to_dict_returns_with_cached_properties_if_included():
    card = ClassicCard(word="Dog", color=ClassicColor.BLUE, revealed=True)
    assert card.formatted_word == "dog"
    card_dict = card.model_dump(include={"formatted_word"})
    assert card_dict == {
        "formatted_word": "dog",
    }
