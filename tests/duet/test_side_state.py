import json

import pytest

from codenames.duet.board import DuetBoard
from codenames.duet.score import GameResult
from codenames.duet.state import DuetSideState
from codenames.generic.exceptions import GameIsOver, InvalidGuess, InvalidTurn
from codenames.generic.move import PASS_GUESS, QUIT_GAME, Clue, Guess
from codenames.generic.player import PlayerRole
from tests.duet.utils.moves import get_side_moves


def test_side_state_json_serialization_and_load(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    side_state.process_clue(clue=Clue(word="A", card_amount=3))
    side_state.process_guess(guess=Guess(card_index=0))
    side_state.process_guess(guess=Guess(card_index=1))

    side_state_json = side_state.model_dump_json()
    side_state_dict = json.loads(side_state_json)
    side_state_from_json = DuetSideState.model_validate(side_state_dict)
    assert side_state_from_json == side_state
    assert side_state_dict == side_state.model_dump(mode="json")

    side_state.process_guess(guess=Guess(card_index=QUIT_GAME))
    side_state_json = side_state.model_dump_json()
    side_state_dict = json.loads(side_state_json)
    side_state_from_json = DuetSideState.model_validate(side_state_dict)
    assert side_state_from_json == side_state
    assert side_state_dict == side_state.model_dump(mode="json")


def test_side_state_win_flow(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    assert side_state.current_player_role == PlayerRole.SPYMASTER
    assert get_side_moves(side_state) == []

    # Round 1
    side_state.process_clue(clue=Clue(word="Clue 1", card_amount=2))
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 0
    assert len(get_side_moves(side_state)) == 1

    side_state.process_guess(guess=Guess(card_index=0))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 1
    assert len(get_side_moves(side_state)) == 2

    side_state.process_guess(guess=Guess(card_index=1))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 2
    assert len(get_side_moves(side_state)) == 3

    with pytest.raises(InvalidGuess):  # Card already revealed
        side_state.process_guess(guess=Guess(card_index=1))

    side_state.process_guess(guess=Guess(card_index=PASS_GUESS))  # Pass
    assert side_state.current_player_role == PlayerRole.SPYMASTER
    assert side_state.score.main.revealed == 2
    assert len(get_side_moves(side_state)) == 4

    # Round 2
    side_state.process_clue(clue=Clue(word="Clue 2", card_amount=1))
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert len(get_side_moves(side_state)) == 5

    side_state.process_guess(guess=Guess(card_index=5))  # Neutral - Incorrect
    assert side_state.current_player_role == PlayerRole.SPYMASTER
    assert side_state.score.main.revealed == 2
    assert len(get_side_moves(side_state)) == 6

    with pytest.raises(InvalidTurn):  # Not operative turn
        side_state.process_guess(guess=Guess(card_index=9))

    # Round 3
    side_state.process_clue(clue=Clue(word="Clue 3", card_amount=1))
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert len(get_side_moves(side_state)) == 7

    side_state.process_guess(guess=Guess(card_index=2))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 3
    assert len(get_side_moves(side_state)) == 8

    side_state.process_guess(guess=Guess(card_index=3))  # Green - Correct, win
    assert side_state.score.main.revealed == 4
    assert len(get_side_moves(side_state)) == 9
    assert side_state.game_result == GameResult.TARGET_REACHED


def test_side_state_assassin_flow(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    assert side_state.current_player_role == PlayerRole.SPYMASTER

    # Round 1
    side_state.process_clue(clue=Clue(word="Clue 1", card_amount=3))
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 0
    assert len(get_side_moves(side_state)) == 1

    side_state.process_guess(guess=Guess(card_index=0))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 1
    assert len(get_side_moves(side_state)) == 2

    side_state.process_guess(guess=Guess(card_index=5))  # Neutral - Incorrect
    assert side_state.current_player_role == PlayerRole.SPYMASTER
    assert side_state.score.main.revealed == 1
    assert len(get_side_moves(side_state)) == 3

    # Round 2
    side_state.process_clue(clue=Clue(word="Clue 2", card_amount=1))
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert len(get_side_moves(side_state)) == 4

    side_state.process_guess(guess=Guess(card_index=1))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 2
    assert len(get_side_moves(side_state)) == 5

    side_state.process_guess(guess=Guess(card_index=2))  # Green - Correct
    assert side_state.current_player_role == PlayerRole.OPERATIVE
    assert side_state.score.main.revealed == 3
    assert len(get_side_moves(side_state)) == 6
    assert not side_state.is_game_over

    side_state.process_guess(guess=Guess(card_index=9))  # Assassin - Incorrect, lose
    assert side_state.score.main.revealed == 3
    assert len(get_side_moves(side_state)) == 7
    assert side_state.is_game_over
    assert side_state.game_result == GameResult.ASSASSIN_HIT

    with pytest.raises(GameIsOver):
        side_state.process_clue(clue=Clue(word="Clue 3", card_amount=1))

    with pytest.raises(GameIsOver):
        side_state.process_guess(guess=Guess(card_index=3))


def test_side_state_spymaster_quit(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    assert side_state.current_player_role == PlayerRole.SPYMASTER

    # Round 1
    side_state.process_clue(clue=Clue(word="Clue 1", card_amount=3))
    side_state.process_guess(guess=Guess(card_index=0))
    side_state.process_guess(guess=Guess(card_index=5))
    assert not side_state.is_game_over

    # Round 2
    side_state.process_clue(clue=Clue(word="Clue 2", card_amount=QUIT_GAME))
    assert side_state.is_game_over
    assert side_state.game_result == GameResult.GAME_QUIT


def test_side_state_operator_quit(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    assert side_state.current_player_role == PlayerRole.SPYMASTER

    # Round 1
    side_state.process_clue(clue=Clue(word="Clue 1", card_amount=3))
    side_state.process_guess(guess=Guess(card_index=0))
    assert not side_state.is_game_over
    side_state.process_guess(guess=Guess(card_index=QUIT_GAME))
    assert side_state.is_game_over
    assert side_state.game_result == GameResult.GAME_QUIT
