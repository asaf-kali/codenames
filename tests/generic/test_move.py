import pytest

from codenames.classic.color import ClassicColor
from codenames.classic.team import ClassicTeam
from codenames.classic.types import ClassicCard, ClassicGivenClue, ClassicGivenGuess
from codenames.generic.move import PASS_GUESS, QUIT_GAME, Clue, Guess


def test_clue_creation():
    """Test creating a Clue object."""
    clue = Clue(word="ocean", card_amount=3)
    assert clue.word == "ocean"
    assert clue.card_amount == 3
    assert clue.for_words is None


def test_clue_with_for_words():
    """Test creating a Clue with for_words specified."""
    for_words = ("beach", "wave", "sand")
    clue = Clue(word="ocean", card_amount=3, for_words=for_words)
    assert clue.word == "ocean"
    assert clue.card_amount == 3
    assert clue.for_words == for_words


def test_clue_str_without_for_words():
    """Test string representation of Clue without for_words."""
    clue = Clue(word="ocean", card_amount=3)
    clue_str = str(clue)
    assert "ocean" in clue_str
    assert "3" in clue_str


def test_clue_str_with_for_words():
    """Test string representation of Clue with for_words."""
    for_words = ("beach", "wave")
    clue = Clue(word="ocean", card_amount=2, for_words=for_words)
    clue_str = str(clue)
    assert "ocean" in clue_str
    assert "2" in clue_str
    assert "for:" in clue_str


def test_clue_with_zero_card_amount():
    """Test creating a Clue with zero card amount."""
    clue = Clue(word="zero", card_amount=0)
    assert clue.card_amount == 0


def test_clue_with_unlimited_card_amount():
    """Test creating a Clue with unlimited (9) card amount."""
    clue = Clue(word="all", card_amount=9)
    assert clue.card_amount == 9


def test_given_clue_creation():
    """Test creating a GivenClue object."""
    given_clue = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.BLUE)
    assert given_clue.word == "ocean"
    assert given_clue.card_amount == 3
    assert given_clue.team == ClassicTeam.BLUE


def test_given_clue_str():
    """Test string representation of GivenClue."""
    given_clue = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.RED)
    clue_str = str(given_clue)
    assert "ocean" in clue_str
    assert "3" in clue_str


def test_given_clue_formatted_word():
    """Test formatted_word property of GivenClue."""
    given_clue = ClassicGivenClue(word="Ocean Wave", card_amount=2, team=ClassicTeam.BLUE)
    # formatted_word should use canonical_format which lowercases and removes spaces
    assert given_clue.formatted_word == "ocean wave"


def test_given_clue_hash_same_word_and_amount():
    """Test that GivenClues with same word and amount have same hash."""
    clue1 = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.BLUE)
    clue2 = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.RED)
    # Hash should be based on word and card_amount, not team
    assert clue1.hash == clue2.hash
    assert hash(clue1) == hash(clue2)


def test_given_clue_hash_different_word():
    """Test that GivenClues with different words have different hash."""
    clue1 = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.BLUE)
    clue2 = ClassicGivenClue(word="beach", card_amount=3, team=ClassicTeam.BLUE)
    assert clue1.hash != clue2.hash


def test_given_clue_hash_different_amount():
    """Test that GivenClues with different amounts have different hash."""
    clue1 = ClassicGivenClue(word="ocean", card_amount=3, team=ClassicTeam.BLUE)
    clue2 = ClassicGivenClue(word="ocean", card_amount=2, team=ClassicTeam.BLUE)
    assert clue1.hash != clue2.hash


def test_guess_creation():
    """Test creating a Guess object."""
    guess = Guess(card_index=5)
    assert guess.card_index == 5


def test_guess_with_zero_index():
    """Test creating a Guess with zero index."""
    guess = Guess(card_index=0)
    assert guess.card_index == 0


def test_guess_pass_constant():
    """Test PASS_GUESS constant value."""
    assert PASS_GUESS == -1


def test_guess_quit_constant():
    """Test QUIT_GAME constant value."""
    assert QUIT_GAME == -2


def test_guess_with_pass_value():
    """Test creating a Guess with pass value."""
    guess = Guess(card_index=PASS_GUESS)
    assert guess.card_index == -1


def test_guess_with_quit_value():
    """Test creating a Guess with quit value."""
    guess = Guess(card_index=QUIT_GAME)
    assert guess.card_index == -2


def test_given_guess_correct_when_matching_team():
    """Test GivenGuess.correct returns True when card color matches team."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    assert given_guess.correct is True


def test_given_guess_incorrect_when_different_team():
    """Test GivenGuess.correct returns False when card color doesn't match team."""
    card = ClassicCard(word="ocean", color=ClassicColor.RED, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    assert given_guess.correct is False


def test_given_guess_neutral_is_incorrect():
    """Test GivenGuess.correct returns False for neutral cards."""
    card = ClassicCard(word="ocean", color=ClassicColor.NEUTRAL, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    assert given_guess.correct is False


def test_given_guess_assassin_is_incorrect():
    """Test GivenGuess.correct returns False for assassin cards."""
    card = ClassicCard(word="killer", color=ClassicColor.ASSASSIN, revealed=True)
    clue = ClassicGivenClue(word="danger", card_amount=1, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    assert given_guess.correct is False


def test_given_guess_raises_error_when_card_has_no_color():
    """Test GivenGuess.correct raises ValueError when card has no color."""
    card = ClassicCard(word="unknown", color=None, revealed=False)
    clue = ClassicGivenClue(word="test", card_amount=1, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    with pytest.raises(ValueError, match="has no color set"):
        _ = given_guess.correct


def test_given_guess_str_correct():
    """Test string representation of correct GivenGuess."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    guess_str = str(given_guess)
    assert "correct!" in guess_str
    assert "ocean" in guess_str


def test_given_guess_str_incorrect():
    """Test string representation of incorrect GivenGuess."""
    card = ClassicCard(word="ocean", color=ClassicColor.RED, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.BLUE)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    guess_str = str(given_guess)
    assert "wrong!" in guess_str
    assert "ocean" in guess_str


def test_given_guess_team_property():
    """Test GivenGuess.team property returns the clue's team."""
    card = ClassicCard(word="ocean", color=ClassicColor.BLUE, revealed=True)
    clue = ClassicGivenClue(word="water", card_amount=2, team=ClassicTeam.RED)
    given_guess = ClassicGivenGuess(guessed_card=card, for_clue=clue)

    assert given_guess.team == ClassicTeam.RED


def test_clue_with_negative_card_amount():
    """Test edge case of Clue with negative card amount."""
    clue = Clue(word="test", card_amount=-1)
    assert clue.card_amount == -1


def test_clue_with_large_card_amount():
    """Test edge case of Clue with very large card amount."""
    clue = Clue(word="test", card_amount=100)
    assert clue.card_amount == 100


def test_given_clue_case_insensitive_hash():
    """Test that GivenClue hash is case-insensitive."""
    clue1 = ClassicGivenClue(word="Ocean", card_amount=2, team=ClassicTeam.BLUE)
    clue2 = ClassicGivenClue(word="ocean", card_amount=2, team=ClassicTeam.BLUE)
    # Both should produce same formatted_word and thus same hash
    assert clue1.formatted_word == clue2.formatted_word
    assert clue1.hash == clue2.hash