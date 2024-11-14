import json

from codenames.duet.board import DuetBoard
from codenames.duet.state import DuetSideState
from codenames.generic.move import Clue, Guess


def test_side_state_json_serialization_and_load(board_10: DuetBoard):
    side_state = DuetSideState.from_board(board=board_10)
    side_state.process_clue(clue=Clue(word="A", card_amount=2))
    side_state.process_guess(guess=Guess(card_index=0))
    side_state.process_guess(guess=Guess(card_index=1))

    side_state_json = side_state.model_dump_json()
    side_state_dict = json.loads(side_state_json)
    side_state_from_json = DuetSideState.model_validate(side_state_dict)
    assert side_state_from_json == side_state
    assert side_state_dict == side_state.model_dump()
