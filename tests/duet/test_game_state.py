import json

import pytest

from codenames.duet.board import DuetBoard
from codenames.duet.score import TARGET_REACHED
from codenames.duet.state import DuetGameState, DuetSide
from codenames.generic.exceptions import InvalidGuess
from codenames.generic.move import PASS_GUESS, Clue, Guess
from codenames.generic.player import PlayerRole
from tests.duet.utils.moves import get_duet_moves, get_side_moves


def test_game_state_json_serialization_and_load(board_10: DuetBoard):
    game_state = DuetGameState.from_board(board=board_10)
    game_state.process_clue(clue=Clue(word="A", card_amount=2))
    game_state.process_guess(guess=Guess(card_index=0))
    game_state.process_guess(guess=Guess(card_index=1))

    game_state_json = game_state.model_dump_json()
    game_state_dict = json.loads(game_state_json)
    game_state_from_json = DuetGameState.model_validate(game_state_dict)
    assert game_state_from_json == game_state
    assert game_state_dict == game_state.model_dump()


def test_game_state_flow(board_10: DuetBoard, board_10_dual: DuetBoard):
    game_state = DuetGameState.from_boards(board_a=board_10, board_b=board_10_dual)
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.timer_tokens == 9
    assert get_duet_moves(game_state) == []
    assert not game_state.is_game_over

    # Round 1 - Side A
    game_state.process_clue(clue=Clue(word="Clue 1", card_amount=2))
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.current_dual_state.dual_given_words == ["clue 1"]
    assert game_state.timer_tokens == 9
    assert len(get_duet_moves(game_state)) == 1

    game_state.process_guess(guess=Guess(card_index=0))  # Green - Correct
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.current_side_state.score.main.revealed == 1
    assert game_state.current_dual_state.score.main.revealed == 0
    assert game_state.timer_tokens == 9
    assert len(get_duet_moves(game_state)) == 2

    game_state.process_guess(guess=Guess(card_index=1))  # Green - Correct
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.current_side_state.score.main.revealed == 2
    assert game_state.current_dual_state.score.main.revealed == 1  # Card is green in dual state as well
    assert game_state.timer_tokens == 9
    assert len(get_duet_moves(game_state)) == 3
    assert len(get_side_moves(game_state.side_a)) == 3
    assert len(get_side_moves(game_state.side_b)) == 0

    with pytest.raises(InvalidGuess):  # Card already revealed
        game_state.process_guess(guess=Guess(card_index=1))

    game_state.process_guess(guess=Guess(card_index=PASS_GUESS))  # Pass
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_side_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.timer_tokens == 8
    assert len(get_duet_moves(game_state)) == 4
    assert not game_state.is_game_over

    # Round 2 - Side B
    game_state.process_clue(clue=Clue(word="Clue 2", card_amount=1))
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.timer_tokens == 8
    assert len(get_duet_moves(game_state)) == 5

    with pytest.raises(InvalidGuess):  # Card already revealed by the other side
        game_state.process_guess(guess=Guess(card_index=1))

    game_state.process_guess(guess=Guess(card_index=4))  # Green - Correct
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.current_side_state.score.main.revealed == 2
    assert game_state.current_dual_state.score.main.revealed == 2
    assert game_state.timer_tokens == 8
    assert len(get_duet_moves(game_state)) == 6
    assert len(get_side_moves(game_state.side_a)) == 4
    assert len(get_side_moves(game_state.side_b)) == 2

    game_state.process_guess(guess=Guess(card_index=2))  # Neutral - Incorrect
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.current_side_state.score.main.revealed == 2
    assert game_state.current_dual_state.score.main.revealed == 2
    assert game_state.timer_tokens == 7

    # Round 3 - Side A
    game_state.process_clue(clue=Clue(word="Clue 3", card_amount=2))
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE

    game_state.process_guess(guess=Guess(card_index=2))  # Green - Correct
    assert game_state.current_playing_side == DuetSide.SIDE_A
    assert game_state.current_side_state.score.main.revealed == 3
    assert not game_state.side_a.is_game_over

    game_state.process_guess(guess=Guess(card_index=3))  # Green - Correct, last for board A
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_dual_state.score.main.revealed == 4
    assert game_state.current_side_state.score.main.revealed == 2
    assert game_state.side_a.is_game_over
    assert game_state.side_a.game_result == TARGET_REACHED
    assert not game_state.side_b.is_game_over
    assert game_state.side_b.game_result is None
    assert not game_state.is_game_over
    assert game_state.game_result is None

    # Round 4 - Side B
    game_state.process_clue(clue=Clue(word="Clue 4", card_amount=2))
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE

    game_state.process_guess(guess=Guess(card_index=6))  # Neutral - Incorrect
    assert game_state.current_playing_side == DuetSide.SIDE_B  # Still Side B, as A already won
    assert game_state.timer_tokens == 6

    # Round 5 - Side B
    game_state.process_clue(clue=Clue(word="Clue 5", card_amount=2))
    assert game_state.current_playing_side == DuetSide.SIDE_B
    assert game_state.current_side_state.current_player_role == PlayerRole.OPERATIVE

    game_state.process_guess(guess=Guess(card_index=5))  # Green - Correct
    game_state.process_guess(guess=Guess(card_index=9))  # Green - Correct

    assert game_state.timer_tokens == 6
    assert game_state.is_game_over
    assert game_state.game_result == TARGET_REACHED
