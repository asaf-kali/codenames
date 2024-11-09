from typing import Optional
from unittest.mock import Mock

from codenames.classic.classic_board import ClassicBoard
from codenames.classic.runner.runner import (
    ClassicGameRunner,
    ClueGivenSubscriber,
    GuessGivenSubscriber,
)
from tests.utils.players.dictated import DictatedTurn, build_players


def run_game(
    board: ClassicBoard,
    all_turns: list[DictatedTurn],
    clue_given_sub: Optional[ClueGivenSubscriber] = None,
    guess_given_sub: Optional[GuessGivenSubscriber] = None,
    on_clue_given_mock: Optional[Mock] = None,
    on_guess_given_mock: Optional[Mock] = None,
) -> ClassicGameRunner:
    players = build_players(all_turns=all_turns)
    runner = ClassicGameRunner(players=players, board=board)
    if clue_given_sub:
        runner.clue_given_subscribers.append(clue_given_sub)
    if guess_given_sub:
        runner.guess_given_subscribers.append(guess_given_sub)
    for player in players:
        if on_clue_given_mock:
            player.on_clue_given = on_clue_given_mock  # type: ignore
        if on_guess_given_mock:
            player.on_guess_given = on_guess_given_mock  # type: ignore
    runner.run_game()
    return runner
