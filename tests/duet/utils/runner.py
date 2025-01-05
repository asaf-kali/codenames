from typing import Iterable, Optional
from unittest.mock import Mock

from codenames.duet.board import DuetBoard
from codenames.duet.player import DuetTeam
from codenames.duet.runner import DuetGamePlayers, DuetGameRunner
from codenames.duet.state import DuetGameState, DuetSide
from codenames.generic.move import Guess
from codenames.generic.runner import (
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from tests.duet.utils.dictated import (
    DictatedDuetOperative,
    DictatedDuetPlayer,
    DictatedDuetSpymaster,
)
from tests.utils.players.dictated import DictatedTurn

Turns = list[DictatedTurn]
TurnsBySide = dict[DuetSide, Turns]


def run_duet_game(
    all_turns: list[DictatedTurn],
    state: DuetGameState | None = None,
    board: DuetBoard | None = None,
    clue_given_sub: Optional[ClueGivenSubscriber] = None,
    guess_given_sub: Optional[GuessGivenSubscriber] = None,
    on_clue_given_mock: Optional[Mock] = None,
    on_guess_given_mock: Optional[Mock] = None,
) -> DuetGameRunner:
    players = build_players_from_turns(all_turns=all_turns)
    runner = DuetGameRunner(players=players, state=state, board=board)
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


def build_players_from_turns(all_turns: Iterable[DictatedTurn]) -> DuetGamePlayers:
    turns_by_side: TurnsBySide = {DuetSide.SIDE_A: [], DuetSide.SIDE_B: []}
    current_side = DuetSide.SIDE_A
    for turn in all_turns:
        turns_by_side[current_side].append(turn)
        current_side = current_side.opposite
    return build_players(turns_by_side=turns_by_side)


def build_players(turns_by_side: TurnsBySide) -> DuetGamePlayers:
    clues = {DuetSide.SIDE_A: [], DuetSide.SIDE_B: []}  # type: ignore[var-annotated]
    guesses = {DuetSide.SIDE_A: [], DuetSide.SIDE_B: []}  # type: ignore[var-annotated]
    for side, turns in turns_by_side.items():
        for turn in turns:
            clues[side].append(turn.clue)
            turn_guesses = [Guess(card_index=index) for index in turn.guesses]
            guesses[side.opposite].extend(turn_guesses)
    player_a = DictatedDuetPlayer(side=DuetSide.SIDE_A, clues=clues[DuetSide.SIDE_A], guesses=guesses[DuetSide.SIDE_A])
    player_b = DictatedDuetPlayer(side=DuetSide.SIDE_B, clues=clues[DuetSide.SIDE_B], guesses=guesses[DuetSide.SIDE_B])
    return DuetGamePlayers(player_a=player_a, player_b=player_b)


def build_side(team: DuetTeam, turns: Iterable[DictatedTurn]) -> TeamPlayers:
    clues = [turn.clue for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    spymaster = DictatedDuetSpymaster(clues=clues, team=team)
    operative = DictatedDuetOperative(guesses=guesses, team=team)
    return TeamPlayers(spymaster=spymaster, operative=operative)
