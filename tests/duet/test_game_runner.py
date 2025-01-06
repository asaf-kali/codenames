from typing import Generator
from unittest import mock

import pytest

from codenames.duet.board import DuetBoard
from codenames.duet.runner import DuetGameRunner
from codenames.duet.score import (
    MISTAKE_LIMIT_REACHED,
    TARGET_REACHED,
    TIMER_TOKENS_DEPLETED,
)
from codenames.duet.state import (
    DuetGameState,
    DuetOperativeState,
    DuetSide,
    DuetSpymasterState,
)
from codenames.duet.team import DuetTeam
from codenames.duet.types import DuetGivenClue, DuetGivenGuess
from codenames.generic.move import PASS_GUESS, Clue
from tests.duet.utils.runner import build_players, run_duet_game
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
        run_duet_game(state=board_10_state, all_turns=all_turns)

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
    # dual_state_2 - Censored state A, where player B is an operative
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


def test_tokens_run_out_game(board_10_state: DuetGameState):
    board_10_state.timer_tokens = 3
    turns_by_side = {
        DuetSide.SIDE_A: [
            # Timer = 3
            DictatedTurn(clue=Clue(word="A", card_amount=4), guesses=[0, 1, 2, 3]),  # All green
        ],
        DuetSide.SIDE_B: [
            # Timer = 2
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, PASS_GUESS]),  # Green, pass
            # Timer = 1
            DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[5, PASS_GUESS]),  # Green, pass
            # Timer = 0, last chance
            DictatedTurn(clue=Clue(word="D", card_amount=2), guesses=[6]),  # Neutral
        ],
    }
    players = build_players(turns_by_side=turns_by_side)
    runner = DuetGameRunner(players=players, state=board_10_state)
    runner.run_game()

    assert runner.state.game_result == TIMER_TOKENS_DEPLETED


def test_mistakes_run_out_game(board_10_state: DuetGameState):
    board_10_state.allowed_mistakes = 4
    turns_by_side = {
        DuetSide.SIDE_A: [
            DictatedTurn(clue=Clue(word="A", card_amount=3), guesses=[0, 1, 7]),  # Green, Green, Neutral
            DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[6]),  # Neutral
        ],
        DuetSide.SIDE_B: [
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[0, 2, 6]),  # Invalid, Green, Neutral
            DictatedTurn(clue=Clue(word="D", card_amount=2), guesses=[1, 7]),  # Invalid, Neutral
        ],
    }
    players = build_players(turns_by_side=turns_by_side)
    runner = DuetGameRunner(players=players, state=board_10_state)
    runner.run_game()

    assert runner.state.game_result == MISTAKE_LIMIT_REACHED


def test_sudden_death(board_10_state: DuetGameState):
    board_10_state.timer_tokens = 3
    turns_by_side = {
        DuetSide.SIDE_A: [
            DictatedTurn(clue=Clue(word="A", card_amount=3), guesses=[0, 1, 4]),  # Green, Green, Neutral
            DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[2, PASS_GUESS]),  # Green, pass
            # Sudden death
            DictatedTurn(clue=Clue(word="NONE", card_amount=0), guesses=[3]),  # Green
        ],
        DuetSide.SIDE_B: [
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 6]),  # Green, Neutral
            # Sudden death
            DictatedTurn(clue=Clue(word="NONE", card_amount=0), guesses=[5]),  # Green
            DictatedTurn(clue=Clue(word="NONE", card_amount=0), guesses=[9]),  # Green
        ],
    }
    players = build_players(turns_by_side=turns_by_side)
    runner = DuetGameRunner(players=players, state=board_10_state)
    runner.run_game()

    assert runner.state.game_result == TARGET_REACHED
    assert runner.state.timer_tokens == 0
    assert runner.state.is_sudden_death
