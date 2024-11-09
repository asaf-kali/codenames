from unittest.mock import MagicMock

import pytest

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicTeam
from codenames.classic.winner import Winner, WinningReason
from codenames.generic.move import (
    PASS_GUESS,
    QUIT_GAME,
    Clue,
    GivenClue,
    GivenGuess,
    Guess,
)
from tests.utils import constants
from tests.utils.common import run_game
from tests.utils.players.dictated import DictatedTurn


@pytest.fixture()
def board_10() -> ClassicBoard:
    return constants.board_10()


def test_blue_reveals_all_and_wins(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[2, 3]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team=ClassicTeam.BLUE, reason=WinningReason.TARGET_SCORE_REACHED)


def test_red_reveals_all_and_wins(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[7]),  # Hits neutral
        DictatedTurn(clue=Clue(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team=ClassicTeam.RED, reason=WinningReason.TARGET_SCORE_REACHED)


def test_blue_picks_assassin_and_red_wins(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 9]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)
    assert runner.winner == Winner(team=ClassicTeam.RED, reason=WinningReason.OPPONENT_HIT_ASSASSIN)


def test_blue_picks_red_and_red_wins(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 7]),  # Hits neutral
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 5, 1]),  # Hits blue
        DictatedTurn(clue=Clue(word="C", card_amount=1), guesses=[2, 6]),  # Hits last red
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    expected_given_clues = [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
        GivenClue(word="b", card_amount=2, team=ClassicTeam.RED),
        GivenClue(word="c", card_amount=1, team=ClassicTeam.BLUE),
    ]
    assert runner.winner == Winner(team=ClassicTeam.RED, reason=WinningReason.TARGET_SCORE_REACHED)
    assert runner.state.given_clues == expected_given_clues
    assert runner.state.given_guesses == [
        GivenGuess(for_clue=expected_given_clues[0], guessed_card=board_10[0]),
        GivenGuess(for_clue=expected_given_clues[0], guessed_card=board_10[7]),
        GivenGuess(for_clue=expected_given_clues[1], guessed_card=board_10[4]),
        GivenGuess(for_clue=expected_given_clues[1], guessed_card=board_10[5]),
        GivenGuess(for_clue=expected_given_clues[1], guessed_card=board_10[1]),
        GivenGuess(for_clue=expected_given_clues[2], guessed_card=board_10[2]),
        GivenGuess(for_clue=expected_given_clues[2], guessed_card=board_10[6]),
    ]


def test_clue_subscribers_are_notified(board_10: ClassicBoard):
    clue_given_subscriber = MagicMock()
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[7]),  # Hits neutral
        DictatedTurn(clue=Clue(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns, clue_given_sub=clue_given_subscriber)

    sent_args = [call[0] for call in clue_given_subscriber.call_args_list]
    assert sent_args == [
        (
            runner.players.blue_team.spymaster,
            Clue(word="A", card_amount=2),
        ),
        (
            runner.players.red_team.spymaster,
            Clue(word="B", card_amount=2),
        ),
        (
            runner.players.blue_team.spymaster,
            Clue(word="C", card_amount=2),
        ),
        (
            runner.players.red_team.spymaster,
            Clue(word="D", card_amount=1),
        ),
    ]


def test_guess_subscribers_are_notified(board_10: ClassicBoard):
    guess_given_subscriber = MagicMock()
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[4, 5, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[7]),  # Hits neutral
        DictatedTurn(clue=Clue(word="D", card_amount=1), guesses=[6]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns, guess_given_sub=guess_given_subscriber)

    sent_args = [call[0] for call in guess_given_subscriber.call_args_list]
    assert sent_args == [
        (
            runner.players.blue_team.operative,
            Guess(card_index=0),
        ),
        (
            runner.players.blue_team.operative,
            Guess(card_index=1),
        ),
        (
            runner.players.blue_team.operative,
            Guess(card_index=PASS_GUESS),
        ),
        (
            runner.players.red_team.operative,
            Guess(card_index=4),
        ),
        (
            runner.players.red_team.operative,
            Guess(card_index=5),
        ),
        (
            runner.players.red_team.operative,
            Guess(card_index=PASS_GUESS),
        ),
        (
            runner.players.blue_team.operative,
            Guess(card_index=7),
        ),
        (
            runner.players.red_team.operative,
            Guess(card_index=6),
        ),
    ]


def test_turns_switch_when_operatives_use_extra_guess(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, 2]),
        DictatedTurn(clue=Clue(word="B", card_amount=1), guesses=[4, 5]),
        DictatedTurn(clue=Clue(word="C", card_amount=1), guesses=[3]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    expected_given_clues = [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
        GivenClue(word="b", card_amount=1, team=ClassicTeam.RED),
        GivenClue(word="c", card_amount=1, team=ClassicTeam.BLUE),
    ]
    assert runner.winner == Winner(team=ClassicTeam.BLUE, reason=WinningReason.TARGET_SCORE_REACHED)
    assert runner.state.given_clues == expected_given_clues
    assert runner.state.given_guesses == [
        GivenGuess(for_clue=expected_given_clues[0], guessed_card=board_10[0]),
        GivenGuess(for_clue=expected_given_clues[0], guessed_card=board_10[1]),
        GivenGuess(for_clue=expected_given_clues[0], guessed_card=board_10[2]),
        GivenGuess(for_clue=expected_given_clues[1], guessed_card=board_10[4]),
        GivenGuess(for_clue=expected_given_clues[1], guessed_card=board_10[5]),
        GivenGuess(for_clue=expected_given_clues[2], guessed_card=board_10[3]),
    ]


def test_spymaster_quit_ends_game(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, PASS_GUESS]),
        DictatedTurn(clue=Clue(word="B", card_amount=QUIT_GAME), guesses=[]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    assert runner.winner == Winner(team=ClassicTeam.BLUE, reason=WinningReason.OPPONENT_QUIT)
    assert runner.state.given_clues == [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
    ]
    assert runner.state.given_guesses == [
        GivenGuess(for_clue=runner.state.given_clues[0], guessed_card=board_10[0]),
        GivenGuess(for_clue=runner.state.given_clues[0], guessed_card=board_10[1]),
    ]


def test_operative_quit_ends_game(board_10: ClassicBoard):
    all_turns = [
        DictatedTurn(clue=Clue(word="A", card_amount=2), guesses=[0, 1, QUIT_GAME]),
    ]
    runner = run_game(board=board_10, all_turns=all_turns)

    assert runner.winner == Winner(team=ClassicTeam.RED, reason=WinningReason.OPPONENT_QUIT)
    assert runner.state.given_clues == [
        GivenClue(word="a", card_amount=2, team=ClassicTeam.BLUE),
    ]
    assert runner.state.given_guesses == [
        GivenGuess(for_clue=runner.state.given_clues[0], guessed_card=board_10[0]),
        GivenGuess(for_clue=runner.state.given_clues[0], guessed_card=board_10[1]),
    ]
