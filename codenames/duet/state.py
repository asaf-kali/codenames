from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any, Self

from pydantic import BaseModel, field_validator, model_validator

from codenames.duet.board import DuetBoard
from codenames.duet.card import DuetColor
from codenames.duet.player import DuetTeam
from codenames.duet.score import (
    ASSASSIN_HIT,
    GAME_QUIT,
    MISTAKE_LIMIT_REACHED,
    TARGET_REACHED,
    TIMER_TOKENS_DEPLETED,
    GameResult,
    Score,
)
from codenames.duet.types import DuetCard, DuetGivenClue, DuetGivenGuess
from codenames.generic.board import WordGroup
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


class DuetPlayerState(PlayerState[DuetColor, DuetTeam]):
    board: DuetBoard
    score: Score
    current_player_role: PlayerRole = PlayerRole.SPYMASTER
    current_team: DuetTeam = DuetTeam.MAIN
    dual_given_words: list[str] = []

    @property
    def illegal_clue_words(self) -> WordGroup:
        base = super().illegal_clue_words
        return *base, *self.dual_given_words

    @field_validator("board", mode="before")
    @classmethod
    def parse_board(cls, v: Any) -> DuetBoard:
        return DuetBoard.model_validate(v)

    @field_validator("current_team", mode="before")
    @classmethod
    def parse_current_team(cls, v: Any) -> DuetTeam:
        return DuetTeam(v)

    @field_validator("given_clues", mode="before")
    @classmethod
    def parse_given_clues(cls, v: Any) -> list[DuetGivenClue]:
        clues = [DuetGivenClue.model_validate(value) for value in v]
        return clues

    @field_validator("given_guesses", mode="before")
    @classmethod
    def parse_given_guesses(cls, v: Any) -> list[DuetGivenGuess]:
        guesses = [DuetGivenGuess.model_validate(value) for value in v]
        return guesses


class DuetSpymasterState(DuetPlayerState, SpymasterState):
    dual_state: DuetOperativeState | None = None


class DuetOperativeState(DuetPlayerState, OperativeState):
    dual_state: DuetSpymasterState | None = None


class DuetSideState(DuetSpymasterState):
    game_result: GameResult | None = None

    @classmethod
    def from_board(cls, board: DuetBoard) -> Self:
        score = Score.new(green=len(board.green_cards))
        return cls(board=board, score=score)

    @property
    def last_given_clue(self) -> GivenClue:
        return self.given_clues[-1]

    @property
    def is_game_over(self) -> bool:
        return self.game_result is not None

    def process_clue(self, clue: Clue) -> DuetGivenClue | None:
        if self.is_game_over:
            raise GameIsOver()
        if self.current_player_role != PlayerRole.SPYMASTER:
            raise InvalidTurn("It's not the Spymaster's turn now!")
        self.clues.append(clue)
        if clue.card_amount == QUIT_GAME:
            log.info("Spymaster quit the game")
            self._quit()
            return None
        formatted_clue_word = canonical_format(clue.word)
        if formatted_clue_word in self.illegal_clue_words:
            raise InvalidClue("Clue word is on board or was already used!")
        given_clue = DuetGivenClue(word=formatted_clue_word, card_amount=clue.card_amount, team=self.current_team)
        log.info(f"Spymaster: {wrap(clue.word)} {wrap(clue.card_amount)} card(s)")
        self.given_clues.append(given_clue)
        self.current_player_role = PlayerRole.OPERATIVE
        return given_clue

    def process_guess(self, guess: Guess) -> DuetGivenGuess | None:
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
            self._quit()
            return None
        guessed_card = self._reveal_guessed_card(guess)
        given_guess = DuetGivenGuess(guessed_card=guessed_card, for_clue=self.last_given_clue)
        log.info(f"Operative: {given_guess}")
        self.given_guesses.append(given_guess)
        self._update_score(card_color=given_guess.guessed_card.color)  # type: ignore[arg-type]
        if given_guess.correct:
            return given_guess
        log.info("Operative wrong, turn is over")
        self._end_turn()
        return given_guess

    def dual_card_revealed(self, guess: Guess):
        card = self.board[guess.card_index]
        if card.revealed:
            assert not card.color == DuetColor.GREEN  # This should not happen
            return
        if card.color == DuetColor.GREEN:
            self._update_score(card_color=DuetColor.GREEN)
        card.color = DuetColor.IRRELEVANT  # This is a hack, but effectively what happens
        card.revealed = True

    def get_spymaster_state(self, dual_state: DuetSideState | None) -> DuetSpymasterState:
        dual_player_state = dual_state.get_operative_state(None) if dual_state else None
        return DuetSpymasterState(
            board=self.board,
            given_clues=self.given_clues,
            given_guesses=self.given_guesses,
            score=self.score,
            current_team=self.current_team,
            current_player_role=self.current_player_role,
            clues=self.clues,
            dual_given_words=self.dual_given_words,
            dual_state=dual_player_state,
        )

    def get_operative_state(self, dual_state: DuetSideState | None) -> DuetOperativeState:
        dual_player_state = dual_state.get_spymaster_state(None) if dual_state else None
        return DuetOperativeState(
            board=DuetBoard.from_board(self.board.censored),
            given_clues=self.given_clues,
            given_guesses=self.given_guesses,
            score=self.score,
            current_team=self.current_team,
            current_player_role=self.current_player_role,
            dual_given_words=self.dual_given_words,
            dual_state=dual_player_state,
        )

    def _reveal_guessed_card(self, guess: Guess) -> DuetCard:
        try:
            guessed_card = self.board[guess.card_index]
        except (IndexError, CardNotFoundError) as e:
            raise InvalidGuess("Given card index is out of range!") from e
        if guessed_card.revealed:
            raise InvalidGuess("Given card is already revealed!")
        guessed_card.revealed = True
        return guessed_card

    def _end_turn(self):
        self.current_player_role = self.current_player_role.other

    def _quit(self):
        self.game_result = GAME_QUIT
        self._end_turn()

    def _update_score(self, card_color: DuetColor):
        if card_color == DuetColor.NEUTRAL:
            return
        if card_color == DuetColor.ASSASSIN:
            self.game_result = ASSASSIN_HIT
            return
        game_ended = self.score.add_point()
        if game_ended:
            self.game_result = TARGET_REACHED


class DuetSide(StrEnum):
    SIDE_A = "SIDE_A"
    SIDE_B = "SIDE_B"

    @property
    def opposite(self) -> DuetSide:
        return DuetSide.SIDE_B if self == DuetSide.SIDE_A else DuetSide.SIDE_A


class DuetGameState(BaseModel):
    side_a: DuetSideState
    side_b: DuetSideState
    current_playing_side: DuetSide = DuetSide.SIDE_A
    timer_tokens: int = 9
    allowed_mistakes: int = 9

    @classmethod
    def from_board(cls, board: DuetBoard) -> DuetGameState:
        dual_board = DuetBoard.dual_board(board=board)
        return cls.from_boards(board_a=board, board_b=dual_board)

    @classmethod
    def from_boards(cls, board_a: DuetBoard, board_b: DuetBoard) -> DuetGameState:
        if not board_a.is_clean or not board_b.is_clean:
            raise ValueError("Boards must be clean.")
        side_a = DuetSideState.from_board(board_a)
        side_b = DuetSideState.from_board(board_b)
        return cls(side_a=side_a, side_b=side_b)

    @property
    def game_result(self) -> GameResult | None:
        # If the timer runs out, the game is lost
        if self.timer_tokens < 0:
            return TIMER_TOKENS_DEPLETED
        if self.allowed_mistakes == 0:
            return MISTAKE_LIMIT_REACHED
        result_a, result_b = self.side_a.game_result, self.side_b.game_result
        # If no side has a result, the game is still ongoing
        if not result_a and not result_b:
            return None
        # If any side has lost, the game is lost
        if result_a and not result_a.win:
            return result_a
        if result_b and not result_b.win:
            return result_b
        # Otherwise, if only one side one, the game is still ongoing
        if not result_a or not result_b:
            return None
        # Otherwise, both sides, finished, no one lost, means the game is won
        assert result_a.win and result_b.win
        return TARGET_REACHED

    @property
    def is_sudden_death(self) -> bool:
        return self.timer_tokens == 0

    @property
    def is_game_over(self) -> bool:
        return self.game_result is not None

    @property
    def current_side_state(self) -> DuetSideState:
        return self.side_a if self.current_playing_side == DuetSide.SIDE_A else self.side_b

    @property
    def current_dual_state(self) -> DuetSideState:
        return self.side_b if self.current_playing_side == DuetSide.SIDE_A else self.side_a

    @model_validator(mode="after")
    def validate_allowed_mistakes(self) -> Self:
        if self.allowed_mistakes > self.timer_tokens:
            raise ValueError("Allowed mistakes cannot be greater than timer tokens.")
        return self

    def process_clue(self, clue: Clue) -> DuetGivenClue | None:
        side_state = self.current_side_state
        given_clue = side_state.process_clue(clue)
        if given_clue:
            self.current_dual_state.dual_given_words.append(given_clue.formatted_word)
        return given_clue

    def process_guess(self, guess: Guess) -> DuetGivenGuess | None:
        given_guess = self.current_side_state.process_guess(guess)
        # If the guess is wrong or passed the turn, the timer is updated
        if not given_guess or not given_guess.correct:
            self._update_tokens(mistake=given_guess is not None)
            # If the other side did not win yet, it is their turn now
            if not self.current_dual_state.is_game_over:
                self.current_playing_side = self.current_playing_side.opposite
            return given_guess
        # If the guess is correct, the dual card is now irrelevant
        self.current_dual_state.dual_card_revealed(guess=guess)
        # If we reached our target score, and we are not in "sudden death", we consume a timer token
        if self.current_side_state.is_game_over and not self.is_sudden_death:
            self._update_tokens(mistake=False)
        # If we reached our target score, or we are in "sudden death", it is now the other side's turn
        if self.current_side_state.is_game_over or self.is_sudden_death:
            self.current_playing_side = self.current_playing_side.opposite
        return given_guess

    def _update_tokens(self, mistake: bool) -> None:
        if self.timer_tokens >= 0:
            self.timer_tokens -= 1
        if self.timer_tokens == 0:
            log.info("Timer tokens depleted! Entering sudden death")
            self.side_a.current_player_role = PlayerRole.OPERATIVE
            self.side_b.current_player_role = PlayerRole.OPERATIVE
        if not mistake:
            return
        self.allowed_mistakes -= 1
        if self.allowed_mistakes == 0:
            log.info("Mistake limit reached!")
