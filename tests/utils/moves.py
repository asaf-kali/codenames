from dataclasses import dataclass

from codenames.classic.state import ClassicState
from codenames.generic.move import GivenClue, GivenGuess
from codenames.generic.player import PlayerRole, Team


@dataclass
class Move:
    @property
    def team_color(self) -> Team:
        raise NotImplementedError()


@dataclass
class ClueMove(Move):
    given_clue: GivenClue

    @property
    def team_color(self) -> Team:
        return self.given_clue.team


@dataclass
class GuessMove(Move):
    given_guess: GivenGuess

    @property
    def team_color(self) -> Team:
        return self.given_guess.team


@dataclass
class PassMove(Move):
    team: Team

    @property
    def team_color(self) -> Team:
        return self.team


def get_moves(state: ClassicState) -> list[Move]:
    return _get_moves(
        given_clues=state.given_clues,
        given_guesses=state.given_guesses,
        current_turn=state.current_player_role,
    )


def _get_moves(given_clues: list[GivenClue], given_guesses: list[GivenGuess], current_turn: PlayerRole) -> list[Move]:
    guesses_by_clues = get_guesses_by_clues(given_clues=given_clues, given_guesses=given_guesses)
    moves: list[Move] = []
    for clue, guesses in guesses_by_clues.items():
        clue_move = ClueMove(given_clue=clue)
        moves.append(clue_move)
        for guess in guesses:
            guess_move = GuessMove(given_guess=guess)
            moves.append(guess_move)
        if len(guesses) == 0:
            moves.append(PassMove(team=clue.team))
            continue
        if len(guesses) < clue.card_amount + 1:
            last_guess = guesses[-1]
            if last_guess.correct:
                moves.append(PassMove(team=clue.team))
    if not moves:
        return moves
    last_move = moves[-1]
    if not isinstance(last_move, PassMove):
        return moves
    if current_turn == PlayerRole.OPERATIVE:
        moves = moves[:-1]
    return moves


def get_guesses_by_clues(
    given_clues: list[GivenClue], given_guesses: list[GivenGuess]
) -> dict[GivenClue, list[GivenGuess]]:
    guesses_by_clues: dict[GivenClue, list[GivenGuess]] = {}
    for clue in given_clues:
        guesses_by_clues[clue] = []
    for guess in given_guesses:
        guesses_by_clues[guess.for_clue].append(guess)
    return guesses_by_clues
