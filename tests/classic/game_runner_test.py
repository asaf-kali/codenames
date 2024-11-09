from unittest.mock import MagicMock

import pytest

from codenames.classic.classic_board import ClassicBoard
from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.runner.runner import ClassicGameRunner
from codenames.classic.state import ClassicOperativeState
from codenames.classic.winner import Winner, WinningReason
from codenames.generic.move import Clue, GivenClue, GivenGuess
from tests.utils import constants
from tests.utils.common import run_game
from tests.utils.hooks import hook_method
from tests.utils.players.dictated import (
    DictatedOperative,
    DictatedSpymaster,
    DictatedTurn,
    build_players,
)


@pytest.fixture()
def board() -> ClassicBoard:
    return constants.board_10()


def test_game_runner_notifies_all_players_on_clue_given(board: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(clue=Clue(word="B", card_amount=1), guesses=[4, 9]),
    ]
    on_clue_given_mock = MagicMock()
    on_guess_given_mock = MagicMock()
    run_game(
        board=board,
        all_turns=all_turns,
        on_clue_given_mock=on_clue_given_mock,
        on_guess_given_mock=on_guess_given_mock,
    )

    expected_given_clue_1 = GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE)
    expected_given_clue_2 = GivenClue(word="b", card_amount=1, team=ClassicTeam.RED)
    assert on_clue_given_mock.call_count == 2 * 4
    assert on_clue_given_mock.call_args_list[0][1] == {"given_clue": expected_given_clue_1}
    assert on_clue_given_mock.call_args_list[4][1] == {"given_clue": expected_given_clue_2}

    assert on_guess_given_mock.call_count == 5 * 4
    assert on_guess_given_mock.call_args_list[0][1] == {
        "given_guess": GivenGuess(for_clue=expected_given_clue_1, guessed_card=board[0])
    }
    assert on_guess_given_mock.call_args_list[4][1] == {
        "given_guess": GivenGuess(for_clue=expected_given_clue_1, guessed_card=board[1])
    }
    assert on_guess_given_mock.call_args_list[8][1] == {
        "given_guess": GivenGuess(for_clue=expected_given_clue_1, guessed_card=board[2])
    }
    assert on_guess_given_mock.call_args_list[12][1] == {
        "given_guess": GivenGuess(for_clue=expected_given_clue_2, guessed_card=board[4])
    }
    assert on_guess_given_mock.call_args_list[16][1] == {
        "given_guess": GivenGuess(for_clue=expected_given_clue_2, guessed_card=board[9])
    }


def test_game_starts_with_team_with_most_cards(board: ClassicBoard):
    players = build_players(
        all_turns=[
            DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[9]),
        ],
        first_team=ClassicTeam.RED,
    )
    board.cards[3].color = ClassicColor.RED
    assert len(board.red_cards) > len(board.blue_cards)
    runner = ClassicGameRunner(players=players, board=board)
    runner.run_game()

    assert runner.winner == Winner(team=ClassicTeam.BLUE, reason=WinningReason.OPPONENT_HIT_ASSASSIN)


def test_game_runner_spymaster_state(board: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(clue=Clue(word="B", card_amount=1), guesses=[4, 9]),
    ]

    with hook_method(DictatedSpymaster, "give_clue") as give_clue_mock:
        run_game(board=board, all_turns=all_turns)

    calls = give_clue_mock.hook.calls
    assert len(calls) == 2
    game_state_1: ClassicOperativeState = calls[0].kwargs["game_state"]
    game_state_2: ClassicOperativeState = calls[1].kwargs["game_state"]

    for card in game_state_1.board:
        assert card.color is not None
    assert game_state_1.current_team == ClassicTeam.BLUE
    assert game_state_1.given_clues == []
    assert game_state_1.given_guesses == []
    assert game_state_1.given_clue_words == ()

    for card in game_state_2.board:
        assert card.color is not None
    assert game_state_2.current_team == ClassicTeam.RED
    assert game_state_2.given_clues == [GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE)]
    assert game_state_2.given_guesses == [
        GivenGuess(for_clue=game_state_2.given_clues[0], guessed_card=board[0]),
        GivenGuess(for_clue=game_state_2.given_clues[0], guessed_card=board[1]),
        GivenGuess(for_clue=game_state_2.given_clues[0], guessed_card=board[2]),
    ]
    assert game_state_2.given_clue_words == ("a",)


def test_game_runner_operative_state(board: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(clue=Clue(word="B", card_amount=1), guesses=[4, 9]),
    ]
    with hook_method(DictatedOperative, "guess") as pick_guess_mock:
        run_game(board=board, all_turns=all_turns)

    calls = pick_guess_mock.hook.calls
    assert len(calls) == 5  # This game has 5 operative turns
    game_states: tuple[ClassicOperativeState, ...] = tuple(call.kwargs["game_state"] for call in calls)
    game_state_1, game_state_2, game_state_3, game_state_4, game_state_5 = game_states

    # game_state_1
    assert sum(1 for card in game_state_1.board if card.color is not None) == 0
    assert game_state_1.current_team == ClassicTeam.BLUE
    assert game_state_1.left_guesses == 3
    assert game_state_1.given_clues == [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
    ]
    assert game_state_1.given_guesses == []
    assert game_state_1.current_clue == game_state_1.given_clues[0]

    # game_state_3
    assert sum(1 for card in game_state_3.board if card.color is not None) == 2
    assert game_state_3.current_team == ClassicTeam.BLUE
    assert game_state_3.left_guesses == 1
    assert game_state_3.given_clues == [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
    ]
    assert game_state_3.given_guesses == [
        GivenGuess(for_clue=game_state_3.given_clues[0], guessed_card=board[0]),
        GivenGuess(for_clue=game_state_3.given_clues[0], guessed_card=board[1]),
    ]
    assert game_state_3.current_clue == game_state_3.given_clues[0]

    # game_state_5
    assert sum(1 for card in game_state_5.board if card.color is not None) == 4
    assert game_state_5.current_team == ClassicTeam.RED
    assert game_state_5.left_guesses == 1
    assert game_state_5.given_clues == [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
        GivenClue(word="b", card_amount=1, team=ClassicTeam.RED),
    ]
    assert game_state_5.given_guesses == [
        GivenGuess(for_clue=game_state_5.given_clues[0], guessed_card=board[0]),
        GivenGuess(for_clue=game_state_5.given_clues[0], guessed_card=board[1]),
        GivenGuess(for_clue=game_state_5.given_clues[0], guessed_card=board[2]),
        GivenGuess(for_clue=game_state_5.given_clues[1], guessed_card=board[4]),
    ]
    assert game_state_5.current_clue == game_state_5.given_clues[1]
