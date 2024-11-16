from typing import Iterable, Optional
from unittest.mock import Mock

from codenames.duet.board import DuetBoard
from codenames.duet.player import DuetTeam
from codenames.duet.runner import DuetGamePlayers, DuetGameRunner
from codenames.duet.state import DuetSide
from codenames.generic.move import Clue, Guess
from codenames.generic.runner import (
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from tests.duet.utils.dictated import DictatedDuetPlayer
from tests.utils.players.dictated import (
    DictatedOperative,
    DictatedSpymaster,
    DictatedTurn,
)


def run_duet_game(
    board: DuetBoard,
    all_turns: list[DictatedTurn],
    clue_given_sub: Optional[ClueGivenSubscriber] = None,
    guess_given_sub: Optional[GuessGivenSubscriber] = None,
    on_clue_given_mock: Optional[Mock] = None,
    on_guess_given_mock: Optional[Mock] = None,
) -> DuetGameRunner:
    players = build_players(all_turns=all_turns)
    runner = DuetGameRunner(players=players, board=board)
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


def build_players(all_turns: Iterable[DictatedTurn]) -> DuetGamePlayers:
    current_side = DuetSide.SIDE_A
    clues_a: list[Clue] = []
    clues_b: list[Clue] = []
    guesses_a: list[Guess] = []
    guesses_b: list[Guess] = []
    for turn in all_turns:
        if current_side == DuetSide.SIDE_A:
            clues, guesses = clues_a, guesses_b
        else:
            clues, guesses = clues_b, guesses_a
        clues.append(turn.clue)
        guesses.extend([Guess(card_index=index) for index in turn.guesses])
        current_side = current_side.opposite
    player_a = DictatedDuetPlayer(side=DuetSide.SIDE_A, clues=clues_a, guesses=guesses_a)
    player_b = DictatedDuetPlayer(side=DuetSide.SIDE_B, clues=clues_b, guesses=guesses_b)
    return DuetGamePlayers(player_a=player_a, player_b=player_b)


def build_side(team: DuetTeam, turns: Iterable[DictatedTurn]) -> TeamPlayers:
    clues = [turn.clue for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    spymaster = DictatedSpymaster(clues=clues, team=team)
    operative = DictatedOperative(guesses=guesses, team=team)
    return TeamPlayers(spymaster=spymaster, operative=operative)
