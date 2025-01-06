from codenames.classic.color import ClassicColor
from codenames.classic.team import ClassicTeam
from codenames.classic.types import ClassicCard, ClassicGivenClue


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


def test_given_clue_parsing():
    data = {"word": "dog", "card_amount": 4, "team": "BLUE"}
    given_clue = ClassicGivenClue.model_validate(data)
    assert given_clue.word == "dog"
    assert given_clue.card_amount == 4
    assert given_clue.team == ClassicTeam.BLUE
