import json

from codenames.duet.board import DuetBoard
from codenames.duet.state import DuetGameState
from codenames.generic.move import Clue, Guess


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
