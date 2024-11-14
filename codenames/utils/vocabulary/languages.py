from __future__ import annotations

from enum import StrEnum

from codenames.generic.board import Vocabulary
from codenames.utils.vocabulary.english import ENGLISH_WORDS
from codenames.utils.vocabulary.hebrew import HEBREW_WORDS


class SupportedLanguage(StrEnum):
    ENGLISH = "english"
    HEBREW = "hebrew"


def get_vocabulary(language: str) -> Vocabulary:
    language = language.lower()
    if language == SupportedLanguage.ENGLISH:
        return Vocabulary(language=language, words=ENGLISH_WORDS)
    if language == SupportedLanguage.HEBREW:
        return Vocabulary(language=language, words=HEBREW_WORDS)
    raise NotImplementedError(f"Unknown language: {language}")
