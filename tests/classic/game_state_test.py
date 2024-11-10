import json

import pytest

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.runner.runner import new_game_state
from codenames.classic.state import ClassicGameState
from codenames.classic.winner import Winner, WinningReason
from codenames.generic.card import Card
from codenames.generic.exceptions import InvalidGuess, InvalidTurn
from codenames.generic.move import PASS_GUESS, Clue, GivenClue, GivenGuess, Guess
from codenames.generic.player import PlayerRole
from tests.utils.moves import ClueMove, GuessMove, PassMove, get_moves


def test_game_state_flow(board_10: ClassicBoard):
    game_state = new_game_state(board=board_10)
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.SPYMASTER
    assert get_moves(game_state) == []

    # Round 1 - blue team
    game_state.process_clue(Clue(word="Clue 1", card_amount=2))
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 3
    assert len(get_moves(game_state)) == 1

    game_state.process_guess(Guess(card_index=0))  # Blue - Correct
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 2
    assert len(get_moves(game_state)) == 2

    game_state.process_guess(Guess(card_index=1))  # Blue - Correct
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 1
    assert len(get_moves(game_state)) == 3

    with pytest.raises(InvalidGuess):  # Card already guessed
        game_state.process_guess(Guess(card_index=1))

    game_state.process_guess(Guess(card_index=PASS_GUESS))  # Pass
    assert game_state.current_team == ClassicTeam.RED
    assert game_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.left_guesses == 0
    assert len(get_moves(game_state)) == 4

    # Round 2 - red team
    game_state.process_clue(Clue(word="Clue 2", card_amount=1))
    assert game_state.current_team == ClassicTeam.RED
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 2
    assert len(get_moves(game_state)) == 5

    game_state.process_guess(Guess(card_index=4))  # Red - Correct
    assert game_state.current_team == ClassicTeam.RED
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 1
    assert len(get_moves(game_state)) == 6

    game_state.process_guess(Guess(card_index=5))  # Red - Correct
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.left_guesses == 0
    assert len(get_moves(game_state)) == 7

    with pytest.raises(InvalidTurn):  # It's not the operative's turn
        game_state.process_guess(Guess(card_index=8))

    # Round 3 - blue team
    game_state.process_clue(Clue(word="Clue 3", card_amount=2))
    assert game_state.current_team == ClassicTeam.BLUE
    assert game_state.current_player_role == PlayerRole.OPERATIVE
    assert game_state.left_guesses == 3
    assert len(get_moves(game_state)) == 8

    game_state.process_guess(Guess(card_index=PASS_GUESS))
    assert game_state.current_team == ClassicTeam.RED
    assert game_state.current_player_role == PlayerRole.SPYMASTER
    assert game_state.left_guesses == 0
    assert len(get_moves(game_state)) == 9

    # Round 4 - red team
    game_state.process_clue(Clue(word="Clue 4", card_amount=2))
    assert len(get_moves(game_state)) == 10
    game_state.process_guess(Guess(card_index=9))  # Black - Game over
    assert len(get_moves(game_state)) == 11
    assert game_state.winner == Winner(team=ClassicTeam.BLUE, reason=WinningReason.OPPONENT_HIT_ASSASSIN)

    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_clue(Clue(word="E", card_amount=1))
    with pytest.raises(InvalidTurn):  # Game is over
        game_state.process_guess(Guess(card_index=8))

    expected_moves = [
        ClueMove(given_clue=GivenClue(word="clue 1", card_amount=2, team=ClassicTeam.BLUE)),
        GuessMove(
            given_guess=GivenGuess(
                for_clue=GivenClue(word="clue 1", card_amount=2, team=ClassicTeam.BLUE),
                guessed_card=Card(word="Card 0", color=ClassicColor.BLUE, revealed=True),
            )
        ),
        GuessMove(
            given_guess=GivenGuess(
                for_clue=GivenClue(word="clue 1", card_amount=2, team=ClassicTeam.BLUE),
                guessed_card=Card(word="Card 1", color=ClassicColor.BLUE, revealed=True),
            )
        ),
        PassMove(team=ClassicTeam.BLUE),
        ClueMove(given_clue=GivenClue(word="clue 2", card_amount=1, team=ClassicTeam.RED)),
        GuessMove(
            given_guess=GivenGuess(
                for_clue=GivenClue(word="clue 2", card_amount=1, team=ClassicTeam.RED),
                guessed_card=Card(word="Card 4", color=ClassicColor.RED, revealed=True),
            )
        ),
        GuessMove(
            given_guess=GivenGuess(
                for_clue=GivenClue(word="clue 2", card_amount=1, team=ClassicTeam.RED),
                guessed_card=Card(word="Card 5", color=ClassicColor.RED, revealed=True),
            )
        ),
        ClueMove(given_clue=GivenClue(word="clue 3", card_amount=2, team=ClassicTeam.BLUE)),
        PassMove(team=ClassicTeam.BLUE),
        ClueMove(given_clue=GivenClue(word="clue 4", card_amount=2, team=ClassicTeam.RED)),
        GuessMove(
            given_guess=GivenGuess(
                for_clue=GivenClue(word="clue 4", card_amount=2, team=ClassicTeam.RED),
                guessed_card=Card(word="Card 9", color=ClassicColor.ASSASSIN, revealed=True),
            )
        ),
    ]
    assert get_moves(game_state) == expected_moves
    assert get_moves(game_state.operative_state) == expected_moves


def test_game_state_json_serialization_and_load(board_10: ClassicBoard):
    game_state = new_game_state(board=board_10)
    game_state.process_clue(Clue(word="A", card_amount=2))
    game_state.process_guess(Guess(card_index=0))
    game_state.process_guess(Guess(card_index=1))

    game_state_json = game_state.model_dump_json()
    game_state_dict = json.loads(game_state_json)
    game_state_from_json = ClassicGameState.model_validate(game_state_dict)
    assert game_state_from_json == game_state
    assert game_state_dict == game_state.model_dump()
