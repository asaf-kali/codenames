import json

import pytest

from codenames.game.board import Board, Card
from codenames.game.color import CardColor, TeamColor
from codenames.game.exceptions import InvalidGuess, InvalidTurn
from codenames.game.move import (
    PASS_GUESS,
    GivenGuess,
    GivenHint,
    Guess,
    GuessMove,
    Hint,
    HintMove,
    PassMove,
)
from codenames.game.player import PlayerRole
from codenames.game.score import TeamScore
from codenames.game.state import GameState, build_game_state
from codenames.game.winner import Winner, WinningReason
from tests.utils import constants


@pytest.fixture()
def board_10() -> Board:
    return constants.board_10()


def test_game_state_flow(board_10: Board):
    game_state = build_game_state(board=board_10)
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.HINTER
    assert game_state.moves == []

    # Round 1 - blue team
    game_state.process_hint(Hint(word="Hint 1", card_amount=2))
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 3
    assert len(game_state.moves) == 1

    game_state.process_guess(Guess(card_index=0))  # Blue - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 2
    assert len(game_state.moves) == 2

    game_state.process_guess(Guess(card_index=1))  # Blue - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1
    assert len(game_state.moves) == 3

    with pytest.raises(InvalidGuess):  # Card already guessed
        game_state.process_guess(Guess(card_index=1))

    game_state.process_guess(Guess(card_index=PASS_GUESS))  # Pass
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.HINTER
    assert game_state.left_guesses == 0
    assert len(game_state.moves) == 4

    # Round 2 - red team
    game_state.process_hint(Hint(word="Hint 2", card_amount=1))
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 2
    assert len(game_state.moves) == 5

    game_state.process_guess(Guess(card_index=4))  # Red - Correct
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 1
    assert len(game_state.moves) == 6

    game_state.process_guess(Guess(card_index=5))  # Red - Correct
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.HINTER
    assert game_state.left_guesses == 0
    assert len(game_state.moves) == 7

    with pytest.raises(InvalidTurn):  # It's not the guesser's turn
        game_state.process_guess(Guess(card_index=8))

    # Round 3 - blue team
    game_state.process_hint(Hint(word="Hint 3", card_amount=2))
    assert game_state.current_team_color == TeamColor.BLUE
    assert game_state.current_player_role == PlayerRole.GUESSER
    assert game_state.left_guesses == 3
    assert len(game_state.moves) == 8

    game_state.process_guess(Guess(card_index=PASS_GUESS))
    assert game_state.current_team_color == TeamColor.RED
    assert game_state.current_player_role == PlayerRole.HINTER
    assert game_state.left_guesses == 0
    assert len(game_state.moves) == 9

    # Round 4 - red team
    game_state.process_hint(Hint(word="Hint 4", card_amount=2))
    assert len(game_state.moves) == 10
    game_state.process_guess(Guess(card_index=9))  # Black - Game over
    assert len(game_state.moves) == 11
    assert game_state.winner == Winner(team_color=TeamColor.BLUE, reason=WinningReason.OPPONENT_HIT_BLACK)

    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_hint(Hint(word="E", card_amount=1))
    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_guess(Guess(card_index=8))

    expected_moves = [
        HintMove(given_hint=GivenHint(word="hint 1", card_amount=2, team_color=TeamColor.BLUE)),
        GuessMove(
            given_guess=GivenGuess(
                given_hint=GivenHint(word="hint 1", card_amount=2, team_color=TeamColor.BLUE),
                guessed_card=Card(word="Card 0", color=CardColor.BLUE, revealed=True),
            )
        ),
        GuessMove(
            given_guess=GivenGuess(
                given_hint=GivenHint(word="hint 1", card_amount=2, team_color=TeamColor.BLUE),
                guessed_card=Card(word="Card 1", color=CardColor.BLUE, revealed=True),
            )
        ),
        PassMove(team=TeamColor.BLUE),
        HintMove(given_hint=GivenHint(word="hint 2", card_amount=1, team_color=TeamColor.RED)),
        GuessMove(
            given_guess=GivenGuess(
                given_hint=GivenHint(word="hint 2", card_amount=1, team_color=TeamColor.RED),
                guessed_card=Card(word="Card 4", color=CardColor.RED, revealed=True),
            )
        ),
        GuessMove(
            given_guess=GivenGuess(
                given_hint=GivenHint(word="hint 2", card_amount=1, team_color=TeamColor.RED),
                guessed_card=Card(word="Card 5", color=CardColor.RED, revealed=True),
            )
        ),
        HintMove(given_hint=GivenHint(word="hint 3", card_amount=2, team_color=TeamColor.BLUE)),
        PassMove(team=TeamColor.BLUE),
        HintMove(given_hint=GivenHint(word="hint 4", card_amount=2, team_color=TeamColor.RED)),
        GuessMove(
            given_guess=GivenGuess(
                given_hint=GivenHint(word="hint 4", card_amount=2, team_color=TeamColor.RED),
                guessed_card=Card(word="Card 9", color=CardColor.BLACK, revealed=True),
            )
        ),
    ]
    assert game_state.hinter_state.moves == expected_moves
    assert game_state.guesser_state.moves == expected_moves


def test_game_state_json_serialization_and_load(board_10: Board):
    game_state = build_game_state(board=board_10)
    game_state.process_hint(Hint(word="A", card_amount=2))
    game_state.process_guess(Guess(card_index=0))
    game_state.process_guess(Guess(card_index=1))

    game_state_json = game_state.json()
    game_state_data = json.loads(game_state_json)
    game_state_from_json = GameState(**game_state_data)
    assert game_state_from_json.dict() == game_state.dict()
    assert game_state_from_json == game_state


def test_score_is_correct_when_board_is_partially_revealed(board_10: Board):
    board_10.cards[0].revealed = True
    game_state = build_game_state(board=board_10)
    assert game_state.score.blue == TeamScore(total=4, revealed=1)
    assert game_state.score.red == TeamScore(total=3, revealed=0)
    assert game_state.score.blue.unrevealed == 3
    assert game_state.score.red.unrevealed == 3

    game_state.process_hint(Hint(word="A", card_amount=2))
    game_state.process_guess(Guess(card_index=1))
    assert game_state.score.blue == TeamScore(total=4, revealed=2)
    assert game_state.score.red == TeamScore(total=3, revealed=0)

    game_state.process_guess(Guess(card_index=4))
    assert game_state.score.blue == TeamScore(total=4, revealed=2)
    assert game_state.score.red == TeamScore(total=3, revealed=1)

    assert game_state.score.blue.unrevealed == 2
    assert game_state.score.red.unrevealed == 2
