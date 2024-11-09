from enum import StrEnum
from typing import Union

from codenames.classic.board import ClassicBoard
from codenames.generic.player import T
from codenames.resources.english import ENGLISH_WORDS
from codenames.resources.hebrew import HEBREW_WORDS


class SupportedLanguage(StrEnum):
    ENGLISH = "english"
    HEBREW = "hebrew"


def generate_board(
    language: Union[str, SupportedLanguage],
    board_size: int = 25,
    assassin_amount: int = 1,
    seed: int | None = None,
    first_team: T | None = None,
) -> ClassicBoard:
    if language == SupportedLanguage.ENGLISH:
        words = ENGLISH_WORDS
    elif language == SupportedLanguage.HEBREW:
        words = HEBREW_WORDS
    else:
        raise NotImplementedError(f"Unknown language: {language}")
    return ClassicBoard.from_vocabulary(
        language=language,
        vocabulary=words,
        board_size=board_size,
        assassin_amount=assassin_amount,
        seed=seed,
        first_team=first_team,
    )
