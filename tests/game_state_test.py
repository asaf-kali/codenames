import json

import pytest

from codenames.game import (
    Board,
    GameState,
    Guess,
    Hint,
    InvalidGuess,
    InvalidTurn,
    PlayerRole,
    TeamColor,
    TeamScore,
    Winner,
    WinningReason,
    build_game_state,
)
from tests.utils import constants


@pytest.fixture()
def board_10() -> Board:
    return constants.board_10()


def test_game_state_flow(board_10: Board):
    game_state = build_game_state(language="en", board=board_10)
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.HINTER

    # Round 1 - blue team
    game_state.process_hint(Hint(word="A", card_amount=2))
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 2

    game_state.process_guess(Guess(card_index=0))  # Blue - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1
    assert game_state.bonus_given is False

    game_state.process_guess(Guess(card_index=1))  # Blue - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1
    assert game_state.bonus_given is True

    with pytest.raises(InvalidGuess):  # Card already guessed
        game_state.process_guess(Guess(card_index=1))

    game_state.process_guess(Guess(card_index=7))  # Gray - Wrong
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.HINTER
    assert game_state.left_guesses == 0

    # Round 2 - red team
    game_state.process_hint(Hint(word="B", card_amount=1))
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1

    game_state.process_guess(Guess(card_index=4))  # Red - Correct
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1
    assert game_state.bonus_given is True

    game_state.process_guess(Guess(card_index=5))  # Red - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.HINTER

    with pytest.raises(InvalidTurn):  # It's not the guesser's turn
        game_state.process_guess(Guess(card_index=8))

    # Round 3 - blue team
    game_state.process_hint(Hint(word="C", card_amount=2))
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 2

    game_state.process_guess(Guess(card_index=9))  # Black - Game over
    assert game_state.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.OPPONENT_HIT_BLACK)

    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_hint(Hint(word="D", card_amount=2))
    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_guess(Guess(card_index=8))


def test_game_state_json_serialization_and_load(board_10: Board):
    game_state = build_game_state(language="english", board=board_10)
    game_state.process_hint(Hint(word="A", card_amount=2))
    game_state.process_guess(Guess(card_index=0))
    game_state.process_guess(Guess(card_index=1))

    game_state_json = game_state.json()
    game_state_data = json.loads(game_state_json)
    game_state_from_json = GameState(**game_state_data)
    assert game_state_from_json.dict() == game_state.dict()
    assert game_state_from_json == game_state


def test_score_is_correct_when_board_is_partially_revealed(board_10: Board):
    board_10.cards[0].revealed = True
    game_state = build_game_state(language="english", board=board_10)
    assert game_state.score.blue == TeamScore(total=4, revealed=1)
    assert game_state.score.red == TeamScore(total=3, revealed=0)
    assert game_state.score.blue.unrevealed == 3
    assert game_state.score.red.unrevealed == 3

    game_state.process_hint(Hint(word="A", card_amount=2))
    game_state.process_guess(Guess(card_index=1))
    assert game_state.score.blue == TeamScore(total=4, revealed=2)
    assert game_state.score.red == TeamScore(total=3, revealed=0)

    game_state.process_guess(Guess(card_index=4))
    assert game_state.score.blue == TeamScore(total=4, revealed=2)
    assert game_state.score.red == TeamScore(total=3, revealed=1)

    assert game_state.score.blue.unrevealed == 2
    assert game_state.score.red.unrevealed == 2
