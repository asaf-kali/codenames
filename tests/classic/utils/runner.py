from typing import Iterable, Optional
from unittest.mock import Mock

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicTeam
from codenames.classic.runner import ClassicGamePlayers, ClassicGameRunner
from codenames.generic.move import Guess
from codenames.generic.runner import (
    ClueGivenSubscriber,
    GuessGivenSubscriber,
    TeamPlayers,
)
from tests.utils.players.dictated import (
    DictatedOperative,
    DictatedSpymaster,
    DictatedTurn,
)


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


def build_players(all_turns: Iterable[DictatedTurn], first_team: ClassicTeam = ClassicTeam.BLUE) -> ClassicGamePlayers:
    team_to_turns: dict[ClassicTeam, list[DictatedTurn]] = {ClassicTeam.BLUE: [], ClassicTeam.RED: []}
    current_team = first_team
    for turn in all_turns:
        team_to_turns[current_team].append(turn)
        current_team = current_team.opponent
    blue_team = build_team(ClassicTeam.BLUE, turns=team_to_turns[ClassicTeam.BLUE])
    red_team = build_team(ClassicTeam.RED, turns=team_to_turns[ClassicTeam.RED])
    return ClassicGamePlayers(blue_team=blue_team, red_team=red_team)


def build_team(team: ClassicTeam, turns: Iterable[DictatedTurn]) -> TeamPlayers:
    clues = [turn.clue for turn in turns]
    guesses = [Guess(card_index=index) for turn in turns for index in turn.guesses]
    spymaster = DictatedSpymaster(clues=clues, team=team)
    operative = DictatedOperative(guesses=guesses, team=team)
    return TeamPlayers(spymaster=spymaster, operative=operative)
