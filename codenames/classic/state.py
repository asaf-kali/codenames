import logging
from typing import Any

from pydantic import field_validator

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicColor, ClassicTeam
from codenames.classic.score import Score
from codenames.classic.types import ClassicCard, ClassicGivenClue, ClassicGivenGuess
from codenames.classic.winner import Winner, WinningReason
from codenames.generic.card import canonical_format
from codenames.generic.exceptions import (
    CardNotFoundError,
    GameIsOver,
    InvalidClue,
    InvalidGuess,
    InvalidTurn,
)
from codenames.generic.move import PASS_GUESS, QUIT_GAME, Clue, GivenClue, Guess
from codenames.generic.player import PlayerRole
from codenames.generic.state import OperativeState, PlayerState, SpymasterState
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)


class ClassicPlayerState(PlayerState[ClassicColor, ClassicTeam]):
    score: Score
    current_player_role: PlayerRole = PlayerRole.SPYMASTER

    @field_validator("board", mode="before")
    @classmethod
    def parse_board(cls, v: Any) -> ClassicBoard:
        return ClassicBoard.model_validate(v)

    @field_validator("current_team", mode="before")
    @classmethod
    def parse_current_team(cls, v: Any) -> ClassicTeam:
        return ClassicTeam(v)

    @field_validator("given_clues", mode="before")
    @classmethod
    def parse_given_clues(cls, v: Any) -> list[ClassicGivenClue]:
        clues = [ClassicGivenClue.model_validate(value) for value in v]
        return clues

    @field_validator("given_guesses", mode="before")
    @classmethod
    def parse_given_guesses(cls, v: Any) -> list[ClassicGivenGuess]:
        guesses = [ClassicGivenGuess.model_validate(value) for value in v]
        return guesses


class ClassicSpymasterState(SpymasterState, ClassicPlayerState):
    pass


class ClassicOperativeState(OperativeState, ClassicPlayerState):
    left_guesses: int


class ClassicGameState(ClassicSpymasterState):
    left_guesses: int = 0
    winner: Winner | None = None

    @property
    def spymaster_state(self) -> ClassicSpymasterState:
        return ClassicSpymasterState(
            board=self.board,
            given_clues=self.given_clues,
            given_guesses=self.given_guesses,
            score=self.score,
            current_team=self.current_team,
            current_player_role=self.current_player_role,
            clues=self.clues,
        )

    @property
    def operative_state(self) -> ClassicOperativeState:
        return ClassicOperativeState(
            board=self.board.censored,
            given_clues=self.given_clues,
            given_guesses=self.given_guesses,
            score=self.score,
            current_team=self.current_team,
            current_player_role=self.current_player_role,
            left_guesses=self.left_guesses,
        )

    @property
    def last_given_clue(self) -> GivenClue:
        return self.given_clues[-1]

    @property
    def is_game_over(self) -> bool:
        return self.winner is not None

    def process_clue(self, clue: Clue) -> ClassicGivenClue | None:
        if self.is_game_over:
            raise GameIsOver()
        if self.current_player_role != PlayerRole.SPYMASTER:
            raise InvalidTurn("It's not the Spymaster's turn now!")
        self.clues.append(clue)
        if clue.card_amount == QUIT_GAME:
            log.info("Spymaster quit the game")
            self._team_quit()
            return None
        formatted_clue_word = canonical_format(clue.word)
        if formatted_clue_word in self.illegal_clue_words:
            raise InvalidClue("Clue word is on board or was already used!")
        given_clue = ClassicGivenClue(word=formatted_clue_word, card_amount=clue.card_amount, team=self.current_team)
        log.info(f"Spymaster: {wrap(clue.word)} {clue.card_amount} card(s)")
        self.given_clues.append(given_clue)
        self.left_guesses = given_clue.card_amount + 1
        self.current_player_role = PlayerRole.OPERATIVE
        return given_clue

    def process_guess(self, guess: Guess) -> ClassicGivenGuess | None:
        if self.is_game_over:
            raise GameIsOver()
        if self.current_player_role != PlayerRole.OPERATIVE:
            raise InvalidTurn("It's not the Operative's turn now!")
        if guess.card_index == PASS_GUESS:
            log.info("Operative passed the turn")
            self._end_turn()
            return None
        if guess.card_index == QUIT_GAME:
            log.info("Operative quit the game")
            self._team_quit()
            return None
        guessed_card = self._reveal_guessed_card(guess)
        given_guess = ClassicGivenGuess(guessed_card=guessed_card, for_clue=self.last_given_clue)
        log.info(f"Operative: {given_guess}")
        self.given_guesses.append(given_guess)
        self._update_score(given_guess)
        if self.is_game_over:
            log.info("Winner found, turn is over")
            self._end_turn()
            return given_guess
        if not given_guess.correct:
            log.info("Operative wrong, turn is over")
            self._end_turn()
            return given_guess
        self.left_guesses -= 1
        if self.left_guesses > 0:
            return given_guess
        log.info("Turn is over")
        self._end_turn()
        return given_guess

    def _reveal_guessed_card(self, guess: Guess) -> ClassicCard:
        try:
            guessed_card = self.board[guess.card_index]
        except (IndexError, CardNotFoundError) as e:
            raise InvalidGuess("Given card index is out of range!") from e
        if guessed_card.revealed:
            raise InvalidGuess("Given card is already revealed!")
        guessed_card.revealed = True
        return guessed_card

    def _end_turn(self, switch_role: bool = True):
        self.left_guesses = 0
        self.current_team = self.current_team.opponent
        if switch_role:
            self.current_player_role = self.current_player_role.other

    def _team_quit(self):
        winner_color = self.current_team.opponent
        self.winner = Winner(team=winner_color, reason=WinningReason.OPPONENT_QUIT)
        self._end_turn()

    def _update_score(self, given_guess: ClassicGivenGuess):
        card_color = given_guess.guessed_card.color
        if card_color == ClassicColor.NEUTRAL:
            return
        if card_color == ClassicColor.ASSASSIN:
            winner_color = given_guess.team.opponent
            self.winner = Winner(team=winner_color, reason=WinningReason.OPPONENT_HIT_ASSASSIN)
            return
        score_team = given_guess.team if given_guess.correct else given_guess.team.opponent
        game_ended = self.score.add_point(score_team)
        if game_ended:
            self.winner = Winner(team=score_team, reason=WinningReason.TARGET_SCORE_REACHED)
