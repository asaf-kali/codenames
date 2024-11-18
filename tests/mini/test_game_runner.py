from codenames.duet.board import DuetBoard
from codenames.duet.score import (
    MISTAKE_LIMIT_REACHED,
    TARGET_REACHED,
    TIMER_TOKENS_DEPLETED,
)
from codenames.duet.state import DuetSide
from codenames.generic.move import PASS_GUESS, Clue
from codenames.mini.runner import MiniGameRunner
from codenames.mini.state import MiniGameState
from tests.duet.utils.runner import build_players
from tests.utils.players.dictated import DictatedTurn


def test_happy_flow(board_10: DuetBoard):
    turns_by_side = {
        DuetSide.SIDE_A: [
            DictatedTurn(clue=Clue(word="A", card_amount=3), guesses=[0, 1, 4]),  # Green, Green, Neutral
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[2, PASS_GUESS]),  # Green, pass
            DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[3]),  # Green
        ]
    }
    players = build_players(turns_by_side=turns_by_side)
    state = MiniGameState.from_board(board=board_10)
    runner = MiniGameRunner(players=players.team_a, state=state)
    runner.run_game()

    assert runner.state.game_result == TARGET_REACHED
    assert runner.state.timer_tokens == 2
    assert runner.state.allowed_mistakes == 3
    assert len(runner.state.given_clues) == 3
    assert len(runner.state.given_guesses) == 5


def test_timer_token_depleted(board_10: DuetBoard):
    turns_by_side = {
        DuetSide.SIDE_A: [
            DictatedTurn(clue=Clue(word="A", card_amount=3), guesses=[4]),  # Neutral
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[PASS_GUESS]),  # pass
            DictatedTurn(clue=Clue(word="NONE", card_amount=2), guesses=[4, 1, 5]),  # Green, Neutral
        ]
    }
    players = build_players(turns_by_side=turns_by_side)
    state = MiniGameState.from_board(board=board_10)
    state.timer_tokens = 2
    runner = MiniGameRunner(players=players.team_a, state=state)
    runner.run_game()

    assert runner.state.game_result == TIMER_TOKENS_DEPLETED
    assert runner.state.timer_tokens == -1
    assert runner.state.allowed_mistakes == 2
    assert len(runner.state.given_clues) == 2
    assert len(runner.state.given_guesses) == 3


def test_mistake_limit_reached(board_10: DuetBoard):
    turns_by_side = {
        DuetSide.SIDE_A: [
            DictatedTurn(clue=Clue(word="A", card_amount=3), guesses=[4]),  # Neutral
            DictatedTurn(clue=Clue(word="B", card_amount=2), guesses=[PASS_GUESS]),  # pass
            DictatedTurn(clue=Clue(word="C", card_amount=2), guesses=[0, 1, 5]),  # Green, Green, Neutral
        ]
    }
    players = build_players(turns_by_side=turns_by_side)
    state = MiniGameState.from_board(board=board_10)
    state.allowed_mistakes = 2
    runner = MiniGameRunner(players=players.team_a, state=state)
    runner.run_game()

    assert runner.state.game_result == MISTAKE_LIMIT_REACHED
    assert runner.state.timer_tokens == 2
    assert runner.state.allowed_mistakes == 0
    assert len(runner.state.given_clues) == 3
    assert len(runner.state.given_guesses) == 4
