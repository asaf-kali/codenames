from codenames.duet.board import DuetBoard
from codenames.duet.card import DuetColor
from codenames.duet.types import DuetCard
from codenames.utils.vocabulary.languages import get_vocabulary


def board_10() -> DuetBoard:
    return DuetBoard(
        language="english",
        cards=[
            DuetCard(word="Card 0", color=DuetColor.GREEN),
            DuetCard(word="Card 1", color=DuetColor.GREEN),
            DuetCard(word="Card 2", color=DuetColor.GREEN),
            DuetCard(word="Card 3", color=DuetColor.GREEN),
            DuetCard(word="Card 4", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 5", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 6", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 7", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 8", color=DuetColor.ASSASSIN),
            DuetCard(word="Card 9", color=DuetColor.ASSASSIN),
        ],
    )


def board_10_dual() -> DuetBoard:
    return DuetBoard(
        language="english",
        cards=[
            DuetCard(word="Card 0", color=DuetColor.NEUTRAL, revealed=False),
            DuetCard(word="Card 1", color=DuetColor.GREEN, revealed=False),
            DuetCard(word="Card 2", color=DuetColor.NEUTRAL, revealed=False),
            DuetCard(word="Card 3", color=DuetColor.ASSASSIN, revealed=False),
            DuetCard(word="Card 4", color=DuetColor.GREEN, revealed=False),
            DuetCard(word="Card 5", color=DuetColor.GREEN, revealed=False),
            DuetCard(word="Card 6", color=DuetColor.NEUTRAL, revealed=False),
            DuetCard(word="Card 7", color=DuetColor.NEUTRAL, revealed=False),
            DuetCard(word="Card 8", color=DuetColor.ASSASSIN, revealed=False),
            DuetCard(word="Card 9", color=DuetColor.GREEN, revealed=False),
        ],
    )


def board_25() -> DuetBoard:
    return DuetBoard(
        language="english",
        cards=[
            DuetCard(word="Card 0", color=DuetColor.GREEN),
            DuetCard(word="Card 1", color=DuetColor.GREEN),
            DuetCard(word="Card 2", color=DuetColor.GREEN),
            DuetCard(word="Card 3", color=DuetColor.GREEN),
            DuetCard(word="Card 4", color=DuetColor.GREEN),
            DuetCard(word="Card 5", color=DuetColor.GREEN),
            DuetCard(word="Card 6", color=DuetColor.GREEN),
            DuetCard(word="Card 7", color=DuetColor.GREEN),
            DuetCard(word="Card 8", color=DuetColor.GREEN),
            DuetCard(word="Card 9", color=DuetColor.GREEN),
            DuetCard(word="Card 10", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 11", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 12", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 13", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 14", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 15", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 16", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 17", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 18", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 19", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 20", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 21", color=DuetColor.NEUTRAL),
            DuetCard(word="Card 22", color=DuetColor.ASSASSIN),
            DuetCard(word="Card 23", color=DuetColor.ASSASSIN),
            DuetCard(word="Card 24", color=DuetColor.ASSASSIN),
        ],
    )


def english_board() -> DuetBoard:
    vocabulary = get_vocabulary("english")
    return DuetBoard.from_vocabulary(vocabulary, seed=0)
