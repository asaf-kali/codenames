import pytest

from codenames.generic.exceptions import (
    CardNotFoundError,
    GameIsOver,
    GameRuleError,
    InvalidClue,
    InvalidGuess,
    InvalidTurn,
    QuitGame,
)


def test_card_not_found_error_message():
    """Test CardNotFoundError creates proper error message."""
    error = CardNotFoundError("test_word")
    assert str(error) == "Card not found: test_word"
    assert error.word == "test_word"


def test_card_not_found_error_is_value_error():
    """Test CardNotFoundError inherits from ValueError."""
    error = CardNotFoundError("test")
    assert isinstance(error, ValueError)


def test_card_not_found_error_stores_word():
    """Test CardNotFoundError stores the word that wasn't found."""
    word = "banana"
    error = CardNotFoundError(word)
    assert error.word == word


def test_card_not_found_error_can_be_raised():
    """Test that CardNotFoundError can be raised and caught."""
    with pytest.raises(CardNotFoundError) as exc_info:
        raise CardNotFoundError("missing")
    assert exc_info.value.word == "missing"


def test_quit_game_exception():
    """Test QuitGame exception can be instantiated and raised."""
    error = QuitGame()
    assert isinstance(error, Exception)

    with pytest.raises(QuitGame):
        raise QuitGame()


def test_game_rule_error():
    """Test GameRuleError exception."""
    error = GameRuleError("Invalid move")
    assert isinstance(error, Exception)
    assert str(error) == "Invalid move"


def test_game_rule_error_can_be_raised():
    """Test that GameRuleError can be raised."""
    with pytest.raises(GameRuleError):
        raise GameRuleError("Test error")


def test_invalid_turn_inherits_from_game_rule_error():
    """Test InvalidTurn is a subclass of GameRuleError."""
    error = InvalidTurn("Wrong turn")
    assert isinstance(error, GameRuleError)
    assert isinstance(error, Exception)


def test_invalid_turn_can_be_raised():
    """Test that InvalidTurn can be raised."""
    with pytest.raises(InvalidTurn):
        raise InvalidTurn("Not your turn")


def test_game_is_over_inherits_from_invalid_turn():
    """Test GameIsOver is a subclass of InvalidTurn."""
    error = GameIsOver()
    assert isinstance(error, InvalidTurn)
    assert isinstance(error, GameRuleError)
    assert isinstance(error, Exception)


def test_game_is_over_has_default_message():
    """Test GameIsOver has default error message."""
    error = GameIsOver()
    assert str(error) == "Game is over!"


def test_game_is_over_can_be_raised():
    """Test that GameIsOver can be raised and caught."""
    with pytest.raises(GameIsOver) as exc_info:
        raise GameIsOver()
    assert str(exc_info.value) == "Game is over!"


def test_game_is_over_can_be_caught_as_invalid_turn():
    """Test GameIsOver can be caught as InvalidTurn."""
    with pytest.raises(InvalidTurn):
        raise GameIsOver()


def test_game_is_over_can_be_caught_as_game_rule_error():
    """Test GameIsOver can be caught as GameRuleError."""
    with pytest.raises(GameRuleError):
        raise GameIsOver()


def test_invalid_clue_inherits_from_game_rule_error():
    """Test InvalidClue is a subclass of GameRuleError."""
    error = InvalidClue("Bad clue")
    assert isinstance(error, GameRuleError)


def test_invalid_clue_can_be_raised():
    """Test that InvalidClue can be raised."""
    with pytest.raises(InvalidClue):
        raise InvalidClue("Clue contains card word")


def test_invalid_guess_inherits_from_game_rule_error():
    """Test InvalidGuess is a subclass of GameRuleError."""
    error = InvalidGuess("Invalid card")
    assert isinstance(error, GameRuleError)


def test_invalid_guess_can_be_raised():
    """Test that InvalidGuess can be raised."""
    with pytest.raises(InvalidGuess):
        raise InvalidGuess("Card already revealed")


def test_exception_hierarchy():
    """Test the exception class hierarchy is correct."""
    # GameRuleError is base for game rules
    assert issubclass(InvalidTurn, GameRuleError)
    assert issubclass(InvalidClue, GameRuleError)
    assert issubclass(InvalidGuess, GameRuleError)

    # GameIsOver extends InvalidTurn
    assert issubclass(GameIsOver, InvalidTurn)
    assert issubclass(GameIsOver, GameRuleError)

    # Other exceptions are standalone
    assert issubclass(CardNotFoundError, ValueError)
    assert issubclass(QuitGame, Exception)


def test_card_not_found_error_with_empty_word():
    """Test CardNotFoundError with empty string."""
    error = CardNotFoundError("")
    assert str(error) == "Card not found: "
    assert error.word == ""


def test_card_not_found_error_with_special_characters():
    """Test CardNotFoundError with special characters in word."""
    word = "test-word_123!@#"
    error = CardNotFoundError(word)
    assert error.word == word
    assert word in str(error)