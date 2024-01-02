from enum import Enum
from typing import Optional, Union

from codenames.boards.english import ENGLISH_WORDS
from codenames.boards.hebrew import HEBREW_WORDS
from codenames.game.board import Board
from codenames.game.color import TeamColor


class SupportedLanguage(str, Enum):
    ENGLISH = "english"
    HEBREW = "hebrew"


def generate_board(
    language: Union[str, SupportedLanguage],
    board_size: int = 25,
    black_amount: int = 1,
    seed: Optional[int] = None,
    first_team: Optional[TeamColor] = None,
) -> Board:
    if language == SupportedLanguage.ENGLISH:
        words = ENGLISH_WORDS
    elif language == SupportedLanguage.HEBREW:
        words = HEBREW_WORDS
    else:
        raise NotImplementedError(f"Unknown language: {language}")
    return Board.from_vocabulary(
        language=language,
        vocabulary=words,
        board_size=board_size,
        black_amount=black_amount,
        seed=seed,
        first_team=first_team,
    )
