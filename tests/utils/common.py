from typing import List, Optional
from unittest.mock import Mock

from codenames.game.board import Board
from codenames.game.runner import GameRunner, GuessGivenSubscriber, HintGivenSubscriber
from tests.utils.players import PredictedTurn, build_players


def run_game(
    board: Board,
    all_turns: List[PredictedTurn],
    hint_given_sub: Optional[HintGivenSubscriber] = None,
    guess_given_sub: Optional[GuessGivenSubscriber] = None,
    on_hint_given_mock: Optional[Mock] = None,
    on_guess_given_mock: Optional[Mock] = None,
) -> GameRunner:
    players = build_players(all_turns=all_turns)
    runner = GameRunner(players=players, board=board)
    if hint_given_sub:
        runner.hint_given_subscribers.append(hint_given_sub)
    if guess_given_sub:
        runner.guess_given_subscribers.append(guess_given_sub)
    for player in players:
        if on_hint_given_mock:
            player.on_hint_given = on_hint_given_mock  # type: ignore
        if on_guess_given_mock:
            player.on_guess_given = on_guess_given_mock  # type: ignore
    runner.run_game()
    return runner
