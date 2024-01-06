from typing import Tuple
from unittest.mock import MagicMock

import pytest

from codenames.game.board import Board
from codenames.game.color import CardColor, TeamColor
from codenames.game.move import GivenGuess, GivenHint, Hint
from codenames.game.runner import GameRunner
from codenames.game.state import GameState, GuesserGameState
from codenames.game.winner import Winner, WinningReason
from tests.utils import constants
from tests.utils.common import run_game
from tests.utils.hooks import hook_method
from tests.utils.players.dictated import (
    DictatedGuesser,
    DictatedHinter,
    DictatedTurn,
    build_players,
)


@pytest.fixture()
def board() -> Board:
    return constants.board_10()


def test_game_runner_notifies_all_players_on_hint_given(board: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]
    on_hint_given_mock = MagicMock()
    on_guess_given_mock = MagicMock()
    run_game(
        board=board,
        all_turns=all_turns,
        on_hint_given_mock=on_hint_given_mock,
        on_guess_given_mock=on_guess_given_mock,
    )

    expected_given_hint_1 = GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE)
    expected_given_hint_2 = GivenHint(word="b", card_amount=1, team_color=TeamColor.RED)
    assert on_hint_given_mock.call_count == 2 * 4
    assert on_hint_given_mock.call_args_list[0][1] == {"given_hint": expected_given_hint_1}
    assert on_hint_given_mock.call_args_list[4][1] == {"given_hint": expected_given_hint_2}

    assert on_guess_given_mock.call_count == 5 * 4
    assert on_guess_given_mock.call_args_list[0][1] == {
        "given_guess": GivenGuess(given_hint=expected_given_hint_1, guessed_card=board[0])
    }
    assert on_guess_given_mock.call_args_list[4][1] == {
        "given_guess": GivenGuess(given_hint=expected_given_hint_1, guessed_card=board[1])
    }
    assert on_guess_given_mock.call_args_list[8][1] == {
        "given_guess": GivenGuess(given_hint=expected_given_hint_1, guessed_card=board[2])
    }
    assert on_guess_given_mock.call_args_list[12][1] == {
        "given_guess": GivenGuess(given_hint=expected_given_hint_2, guessed_card=board[4])
    }
    assert on_guess_given_mock.call_args_list[16][1] == {
        "given_guess": GivenGuess(given_hint=expected_given_hint_2, guessed_card=board[9])
    }


def test_game_starts_with_team_with_most_cards(board: Board):
    players = build_players(
        all_turns=[
            DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[9]),
        ],
        first_team=TeamColor.RED,
    )
    board.cards[3].color = CardColor.RED
    assert len(board.red_cards) > len(board.blue_cards)
    runner = GameRunner(players=players, board=board)
    runner.run_game()

    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.OPPONENT_HIT_BLACK)


def test_game_runner_hinter_state(board: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]

    with hook_method(DictatedHinter, "pick_hint") as pick_hint_mock:
        run_game(board=board, all_turns=all_turns)

    calls = pick_hint_mock.hook.calls
    assert len(calls) == 2
    game_state_1: GameState = calls[0].kwargs["game_state"]
    game_state_2: GameState = calls[1].kwargs["game_state"]

    for card in game_state_1.board:
        assert card.color is not None
    assert game_state_1.current_team_color == TeamColor.BLUE
    assert game_state_1.given_hints == []
    assert game_state_1.given_guesses == []
    assert game_state_1.given_hint_words == ()

    for card in game_state_2.board:
        assert card.color is not None
    assert game_state_2.current_team_color == TeamColor.RED
    assert game_state_2.given_hints == [GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE)]
    assert game_state_2.given_guesses == [
        GivenGuess(given_hint=game_state_2.given_hints[0], guessed_card=board[0]),
        GivenGuess(given_hint=game_state_2.given_hints[0], guessed_card=board[1]),
        GivenGuess(given_hint=game_state_2.given_hints[0], guessed_card=board[2]),
    ]
    assert game_state_2.given_hint_words == ("a",)


def test_game_runner_guesser_state(board: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]
    with hook_method(DictatedGuesser, "guess") as pick_guess_mock:
        run_game(board=board, all_turns=all_turns)

    calls = pick_guess_mock.hook.calls
    assert len(calls) == 5  # This game has 5 guesser turns
    game_states: Tuple[GuesserGameState, ...] = tuple(call.kwargs["game_state"] for call in calls)
    game_state_1, game_state_2, game_state_3, game_state_4, game_state_5 = game_states

    # game_state_1
    assert sum(1 for card in game_state_1.board if card.color is not None) == 0
    assert game_state_1.current_team_color == TeamColor.BLUE
    assert game_state_1.left_guesses == 3
    assert game_state_1.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
    ]
    assert game_state_1.given_guesses == []
    assert game_state_1.current_hint == game_state_1.given_hints[0]

    # game_state_3
    assert sum(1 for card in game_state_3.board if card.color is not None) == 2
    assert game_state_3.current_team_color == TeamColor.BLUE
    assert game_state_3.left_guesses == 1
    assert game_state_3.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
    ]
    assert game_state_3.given_guesses == [
        GivenGuess(given_hint=game_state_3.given_hints[0], guessed_card=board[0]),
        GivenGuess(given_hint=game_state_3.given_hints[0], guessed_card=board[1]),
    ]
    assert game_state_3.current_hint == game_state_3.given_hints[0]

    # game_state_5
    assert sum(1 for card in game_state_5.board if card.color is not None) == 4
    assert game_state_5.current_team_color == TeamColor.RED
    assert game_state_5.left_guesses == 1
    assert game_state_5.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
        GivenHint(word="b", card_amount=1, team_color=TeamColor.RED),
    ]
    assert game_state_5.given_guesses == [
        GivenGuess(given_hint=game_state_5.given_hints[0], guessed_card=board[0]),
        GivenGuess(given_hint=game_state_5.given_hints[0], guessed_card=board[1]),
        GivenGuess(given_hint=game_state_5.given_hints[0], guessed_card=board[2]),
        GivenGuess(given_hint=game_state_5.given_hints[1], guessed_card=board[4]),
    ]
    assert game_state_5.current_hint == game_state_5.given_hints[1]
