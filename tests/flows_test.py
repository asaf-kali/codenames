from unittest.mock import MagicMock

import pytest

from codenames.game import (
    PASS_GUESS,
    Board,
    GameRunner,
    GivenGuess,
    GivenHint,
    Guess,
    Hint,
    TeamColor,
    Winner,
    WinningReason,
)
from tests.utils import constants
from tests.utils.testing_players import PredictedTurn, build_teams


@pytest.fixture()
def board_10() -> Board:
    return constants.board_10()


def test_blue_reveals_all_and_wins(board_10: Board):
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="C", card_amount=2), guesses=[2, 3]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.run_game(language="english", board=board_10)
    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.TARGET_SCORE_REACHED)


def test_red_reveals_all_and_wins(board_10: Board):
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        PredictedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.run_game(language="english", board=board_10)
    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.TARGET_SCORE_REACHED)


def test_blue_picks_black_and_red_wins(board_10: Board):
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 9]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.run_game(language="english", board=board_10)
    assert runner.winner == Winner(team_color=TeamColor.RED, reason=WinningReason.OPPONENT_HIT_BLACK)


def test_blue_picks_red_and_red_wins(board_10: Board):
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 7]),  # Hits gray
        PredictedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, 1]),  # Hits blue
        PredictedTurn(hint=Hint(word="C", card_amount=1), guesses=[2, 6]),  # Hits last red
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.run_game(language="english", board=board_10)

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
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        PredictedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.hint_given_subscribers.append(hint_given_subscriber)
    runner.run_game(language="english", board=board_10)

    sent_args = [call[0] for call in hint_given_subscriber.call_args_list]
    assert sent_args == [
        (
            blue_team.hinter,
            Hint(word="A", card_amount=2),
        ),
        (
            red_team.hinter,
            Hint(word="B", card_amount=2),
        ),
        (
            blue_team.hinter,
            Hint(word="C", card_amount=2),
        ),
        (
            red_team.hinter,
            Hint(word="D", card_amount=1),
        ),
    ]


def test_turns_switch_when_guessers_use_extra_guess(board_10: Board):
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        PredictedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 5]),
        PredictedTurn(hint=Hint(word="C", card_amount=1), guesses=[3]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.run_game(language="english", board=board_10)

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


def test_guess_subscribers_are_notified(board_10: Board):
    guess_given_subscriber = MagicMock()
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        PredictedTurn(hint=Hint(word="C", card_amount=2), guesses=[7]),  # Hits gray
        PredictedTurn(hint=Hint(word="D", card_amount=1), guesses=[6]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    runner.guess_given_subscribers.append(guess_given_subscriber)
    runner.run_game(language="english", board=board_10)

    sent_args = [call[0] for call in guess_given_subscriber.call_args_list]
    assert sent_args == [
        (
            blue_team.guesser,
            Guess(card_index=0),
        ),
        (
            blue_team.guesser,
            Guess(card_index=1),
        ),
        (
            blue_team.guesser,
            Guess(card_index=PASS_GUESS),
        ),
        (
            red_team.guesser,
            Guess(card_index=4),
        ),
        (
            red_team.guesser,
            Guess(card_index=5),
        ),
        (
            red_team.guesser,
            Guess(card_index=PASS_GUESS),
        ),
        (
            blue_team.guesser,
            Guess(card_index=7),
        ),
        (
            red_team.guesser,
            Guess(card_index=6),
        ),
    ]
