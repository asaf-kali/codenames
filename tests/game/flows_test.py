from unittest.mock import MagicMock

import pytest

from codenames.game.board import Board
from codenames.game.color import TeamColor
from codenames.game.move import (
    PASS_GUESS,
    QUIT_GAME,
    GivenGuess,
    GivenHint,
    Guess,
    Hint,
)
from codenames.game.winner import Winner, WinningReason
from tests.utils import constants
from tests.utils.common import run_game
from tests.utils.players.dictated import DictatedTurn


@pytest.fixture()
def board_10() -> Board:
    return constants.board_10()


def test_blue_reveals_all_and_wins(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="C", card_amount=2), guesses=[2, 3]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.TARGET_SCORE_REACHED)


def test_red_reveals_all_and_wins(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        DictatedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.TARGET_SCORE_REACHED)


def test_blue_picks_black_and_red_wins(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 9]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.OPPONENT_HIT_BLACK)


def test_blue_picks_red_and_red_wins(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 7]),  # Hits gray
        DictatedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, 1]),  # Hits blue
        DictatedTurn(hint=Hint(word="C", card_amount=1), guesses=[2, 6]),  # Hits last red
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    expected_given_hints = [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
        GivenHint(word="b", card_amount=2, team_color=TeamColor.RED),
        GivenHint(word="c", card_amount=1, team_color=TeamColor.BLUE),
    ]
    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.TARGET_SCORE_REACHED)
    assert runner.state.given_hints == expected_given_hints
    assert runner.state.given_guesses == [
        GivenGuess(given_hint=expected_given_hints[0], guessed_card=board_10[0]),
        GivenGuess(given_hint=expected_given_hints[0], guessed_card=board_10[7]),
        GivenGuess(given_hint=expected_given_hints[1], guessed_card=board_10[4]),
        GivenGuess(given_hint=expected_given_hints[1], guessed_card=board_10[5]),
        GivenGuess(given_hint=expected_given_hints[1], guessed_card=board_10[1]),
        GivenGuess(given_hint=expected_given_hints[2], guessed_card=board_10[2]),
        GivenGuess(given_hint=expected_given_hints[2], guessed_card=board_10[6]),
    ]


def test_hint_subscribers_are_notified(board_10: Board):
    hint_given_subscriber = MagicMock()
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        DictatedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns, hint_given_sub=hint_given_subscriber)

    sent_args = [call[0] for call in hint_given_subscriber.call_args_list]
    assert sent_args == [
        (
            runner.players.blue_team.hinter,
            Hint(word="A", card_amount=2),
        ),
        (
            runner.players.red_team.hinter,
            Hint(word="B", card_amount=2),
        ),
        (
            runner.players.blue_team.hinter,
            Hint(word="C", card_amount=2),
        ),
        (
            runner.players.red_team.hinter,
            Hint(word="D", card_amount=1),
        ),
    ]


def test_guess_subscribers_are_notified(board_10: Board):
    guess_given_subscriber = MagicMock()
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        DictatedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns, guess_given_sub=guess_given_subscriber)

    sent_args = [call[0] for call in guess_given_subscriber.call_args_list]
    assert sent_args == [
        (
            runner.players.blue_team.guesser,
            Guess(card_index=0),
        ),
        (
            runner.players.blue_team.guesser,
            Guess(card_index=1),
        ),
        (
            runner.players.blue_team.guesser,
            Guess(card_index=PASS_GUESS),
        ),
        (
            runner.players.red_team.guesser,
            Guess(card_index=4),
        ),
        (
            runner.players.red_team.guesser,
            Guess(card_index=5),
        ),
        (
            runner.players.red_team.guesser,
            Guess(card_index=PASS_GUESS),
        ),
        (
            runner.players.blue_team.guesser,
            Guess(card_index=7),
        ),
        (
            runner.players.red_team.guesser,
            Guess(card_index=6),
        ),
    ]


def test_turns_switch_when_guessers_use_extra_guess(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 5]),
        DictatedTurn(hint=Hint(word="C", card_amount=1), guesses=[3]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    expected_given_hints = [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
        GivenHint(word="b", card_amount=1, team_color=TeamColor.RED),
        GivenHint(word="c", card_amount=1, team_color=TeamColor.BLUE),
    ]
    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.TARGET_SCORE_REACHED)
    assert runner.state.given_hints == expected_given_hints
    assert runner.state.given_guesses == [
        GivenGuess(given_hint=expected_given_hints[0], guessed_card=board_10[0]),
        GivenGuess(given_hint=expected_given_hints[0], guessed_card=board_10[1]),
        GivenGuess(given_hint=expected_given_hints[0], guessed_card=board_10[2]),
        GivenGuess(given_hint=expected_given_hints[1], guessed_card=board_10[4]),
        GivenGuess(given_hint=expected_given_hints[1], guessed_card=board_10[5]),
        GivenGuess(given_hint=expected_given_hints[2], guessed_card=board_10[3]),
    ]


def test_hinter_quit_ends_game(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(hint=Hint(word="B", card_amount=QUIT_GAME), guesses=[]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.OPPONENT_QUIT)
    assert runner.state.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
    ]
    assert runner.state.given_guesses == [
        GivenGuess(given_hint=runner.state.given_hints[0], guessed_card=board_10[0]),
        GivenGuess(given_hint=runner.state.given_hints[0], guessed_card=board_10[1]),
    ]


def test_guesser_quit_ends_game(board_10: Board):
    all_turns = [
        DictatedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, QUIT_GAME]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.OPPONENT_QUIT)
    assert runner.state.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
    ]
    assert runner.state.given_guesses == [
        GivenGuess(given_hint=runner.state.given_hints[0], guessed_card=board_10[0]),
        GivenGuess(given_hint=runner.state.given_hints[0], guessed_card=board_10[1]),
    ]
