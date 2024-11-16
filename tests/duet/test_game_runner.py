from typing import Generator
from unittest import mock

import pytest

from codenames.duet.board import DuetBoard
from codenames.duet.player import DuetTeam
from codenames.duet.state import DuetGameState, DuetOperativeState, DuetSpymasterState
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from codenames.generic.move import PASS_GUESS, Clue
from tests.duet.utils.runner import run_duet_game
from tests.utils.hooks import hook_method
from tests.utils.players.dictated import DictatedSpymaster, DictatedTurn


@pytest.fixture(autouse=True)
def board_10_state(board_10: DuetBoard, board_10_dual: DuetBoard) -> Generator[DuetGameState, None, None]:
    with mock.patch.object(target=DuetGameState, attribute="from_board") as from_board_mock:
        game_state = DuetGameState.from_boards(board_a=board_10, board_b=board_10_dual)
        from_board_mock.return_value = game_state
        yield game_state


def test_game_runner_spymaster_state(board_10_state: DuetGameState):
    board_a, board_b = board_10_state.side_a.board, board_10_state.side_b.board  # noqa: F841
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 3]),
    ]

    with hook_method(DictatedSpymaster, "give_clue") as give_clue_mock:
        run_duet_game(board=board_a, all_turns=all_turns)

    calls = give_clue_mock.hook.calls
    assert len(calls) == 2
    game_state_1: DuetSpymasterState = calls[0].kwargs["game_state"]
    game_state_2: DuetSpymasterState = calls[1].kwargs["game_state"]

    # game_state_1 - First turn - Player A spymaster, Player B operative
    assert isinstance(game_state_1, DuetSpymasterState)
    for card in game_state_1.board:
        assert card.color is not None
    assert game_state_1.given_clues == []
    assert game_state_1.given_guesses == []
    assert game_state_1.given_clue_words == ()
    dual_state_1 = game_state_1.dual_state
    assert isinstance(dual_state_1, DuetOperativeState)
    for card in dual_state_1.board:
        assert card.color is None

    # game_state_2 - Second turn - Player B spymaster, Player A operative
    assert isinstance(game_state_2, DuetSpymasterState)
    for card in game_state_2.board:
        assert card.color is not None
    assert game_state_2.given_clues == []
    assert game_state_2.given_guesses == []
    assert game_state_2.given_clue_words == ()
    assert "a" in game_state_2.illegal_clue_words
    # dual_state_2 is the state of the game where B is an operative
    dual_state_2 = game_state_2.dual_state
    assert isinstance(dual_state_2, DuetOperativeState)
    assert dual_state_2.board.cards[0].revealed
    assert dual_state_2.board.cards[1].revealed
    for i in range(2, 10):
        assert not dual_state_2.board.cards[i].revealed
    assert dual_state_2.given_clues == [DuetGivenClue(word="a", card_amount=2, team=DuetTeam.MAIN)]
    assert dual_state_2.given_guesses == [
        DuetGivenGuess(for_clue=dual_state_2.given_clues[0], guessed_card=board_a[0]),
        DuetGivenGuess(for_clue=dual_state_2.given_clues[0], guessed_card=board_a[1]),
    ]
    assert dual_state_2.given_clue_words == ("a",)
