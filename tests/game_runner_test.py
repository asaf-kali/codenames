from typing import Tuple
from unittest.mock import MagicMock

from codenames.game import (
    CardColor,
    GameRunner,
    GivenGuess,
    GivenHint,
    Guess,
    GuesserGameState,
    Hint,
    HinterGameState,
    TeamColor,
    Winner,
    WinningReason,
)
from tests.utils.constants import board_10
from tests.utils.hooks import hook_method
from tests.utils.testing_players import (
    PredictedTurn,
    TestGuesser,
    TestHinter,
    build_teams,
)


def test_game_runner_assigns_team_colors_to_players_on_game_runner_construction():
    blue_hinter = TestHinter([])
    blue_guesser = TestGuesser([])
    red_hinter = TestHinter([])
    red_guesser = TestGuesser([])

    assert blue_hinter.team_color is None
    assert red_hinter.team_color is None
    assert blue_guesser.team_color is None
    assert red_guesser.team_color is None

    GameRunner(blue_hinter=blue_hinter, red_hinter=red_hinter, blue_guesser=blue_guesser, red_guesser=red_guesser)

    assert blue_hinter.team_color == TeamColor.BLUE
    assert red_hinter.team_color == TeamColor.RED
    assert blue_guesser.team_color == TeamColor.BLUE
    assert red_guesser.team_color == TeamColor.RED


def test_game_runner_notifies_all_players_on_hint_given():
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        PredictedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    on_hint_given_mock = MagicMock()
    on_guess_given_mock = MagicMock()
    board = board_10()
    for player in runner.players:
        player.on_hint_given = on_hint_given_mock
        player.on_guess_given = on_guess_given_mock
    runner.run_game(language="english", board=board)

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


def test_game_starts_with_team_with_most_cards():
    blue_team, red_team = build_teams(all_turns=[])
    red_team.hinter.hints = [Hint(word="A", card_amount=2)]
    red_team.guesser.guesses = [Guess(card_index=9)]
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    board = board_10()
    board.cards[3].color = CardColor.RED
    assert len(board.red_cards) > len(board.blue_cards)
    runner.run_game(language="english", board=board)

    assert runner.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.OPPONENT_HIT_BLACK)


def test_game_runner_hinter_state():
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        PredictedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    board = board_10()

    with hook_method(TestHinter, "pick_hint") as pick_hint_mock:
        runner.run_game(language="english", board=board)

    calls = pick_hint_mock.hook.calls
    assert len(calls) == 2
    game_state_1: HinterGameState = calls[0].kwargs["game_state"]
    game_state_2: HinterGameState = calls[1].kwargs["game_state"]

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


def test_game_runner_guesser_state():
    all_turns = [
        PredictedTurn(hint=Hint(word="A", card_amount=2), guesses=[0, 1, 2]),
        PredictedTurn(hint=Hint(word="B", card_amount=1), guesses=[4, 9]),
    ]
    blue_team, red_team = build_teams(all_turns=all_turns)
    runner = GameRunner.from_teams(blue_team=blue_team, red_team=red_team)
    board = board_10()

    with hook_method(TestGuesser, "guess") as pick_guess_mock:
        runner.run_game(language="english", board=board)

    calls = pick_guess_mock.hook.calls
    assert len(calls) == 5
    game_states: Tuple[GuesserGameState, ...] = tuple(call.kwargs["game_state"] for call in calls)
    game_state_1, game_state_2, game_state_3, game_state_4, game_state_5 = game_states

    # game_state_1
    assert sum(1 for card in game_state_1.board if card.color is not None) == 0
    assert game_state_1.current_team_color == TeamColor.BLUE
    assert game_state_1.left_guesses == 2
    assert game_state_1.given_hints == [
        GivenHint(word="a", card_amount=2, team_color=TeamColor.BLUE),
    ]
    assert game_state_1.given_guesses == []
    assert game_state_1.current_hint == game_state_1.given_hints[0]
    assert game_state_1.bonus_given is False

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
    assert game_state_3.bonus_given

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
    assert game_state_5.bonus_given
