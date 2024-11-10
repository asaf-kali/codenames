from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicColor
from codenames.classic.types import ClassicCard


def board_10() -> ClassicBoard:
    return ClassicBoard(
        language="english",
        cards=[
            ClassicCard(word="Card 0", color=ClassicColor.BLUE),
            ClassicCard(word="Card 1", color=ClassicColor.BLUE),
            ClassicCard(word="Card 2", color=ClassicColor.BLUE),
            ClassicCard(word="Card 3", color=ClassicColor.BLUE),
            ClassicCard(word="Card 4", color=ClassicColor.RED),
            ClassicCard(word="Card 5", color=ClassicColor.RED),
            ClassicCard(word="Card 6", color=ClassicColor.RED),
            ClassicCard(word="Card 7", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 8", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 9", color=ClassicColor.ASSASSIN),
        ],
    )


def board_25() -> ClassicBoard:
    return ClassicBoard(
        language="english",
        cards=[
            ClassicCard(word="Card 0", color=ClassicColor.BLUE),
            ClassicCard(word="Card 1", color=ClassicColor.BLUE),
            ClassicCard(word="Card 2", color=ClassicColor.BLUE),
            ClassicCard(word="Card 3", color=ClassicColor.BLUE),
            ClassicCard(word="Card 4", color=ClassicColor.BLUE),
            ClassicCard(word="Card 5", color=ClassicColor.BLUE),
            ClassicCard(word="Card 6", color=ClassicColor.BLUE),
            ClassicCard(word="Card 7", color=ClassicColor.BLUE),
            ClassicCard(word="Card 8", color=ClassicColor.BLUE),
            ClassicCard(word="Card 9", color=ClassicColor.RED),
            ClassicCard(word="Card 10", color=ClassicColor.RED),
            ClassicCard(word="Card 11", color=ClassicColor.RED),
            ClassicCard(word="Card 12", color=ClassicColor.RED),
            ClassicCard(word="Card 13", color=ClassicColor.RED),
            ClassicCard(word="Card 14", color=ClassicColor.RED),
            ClassicCard(word="Card 15", color=ClassicColor.RED),
            ClassicCard(word="Card 16", color=ClassicColor.RED),
            ClassicCard(word="Card 17", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 18", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 19", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 20", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 21", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 22", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 23", color=ClassicColor.NEUTRAL),
            ClassicCard(word="Card 24", color=ClassicColor.ASSASSIN),
        ],
    )


def hebrew_board() -> ClassicBoard:
    return ClassicBoard(
        language="hebrew",
        cards=[
            ClassicCard(word="חיים", color=ClassicColor.NEUTRAL),
            ClassicCard(word="ערך", color=ClassicColor.ASSASSIN),
            ClassicCard(word="מסוק", color=ClassicColor.BLUE),
            ClassicCard(word="שבוע", color=ClassicColor.NEUTRAL),
            ClassicCard(word="רובוט", color=ClassicColor.RED),
            ClassicCard(word="פוטר", color=ClassicColor.NEUTRAL),
            ClassicCard(word="אסור", color=ClassicColor.BLUE),
            ClassicCard(word="דינוזאור", color=ClassicColor.BLUE),
            ClassicCard(word="מחשב", color=ClassicColor.RED),
            ClassicCard(word="מעמד", color=ClassicColor.NEUTRAL),
            ClassicCard(word="בעל", color=ClassicColor.RED),
            ClassicCard(word="פנים", color=ClassicColor.RED),
            ClassicCard(word="פרק", color=ClassicColor.RED),
            ClassicCard(word="גפילטע", color=ClassicColor.BLUE),
            ClassicCard(word="שונה", color=ClassicColor.RED),
            ClassicCard(word="שכר", color=ClassicColor.RED),
            ClassicCard(word="קפיץ", color=ClassicColor.BLUE),
            ClassicCard(word="תרסיס", color=ClassicColor.NEUTRAL),
            ClassicCard(word="דגל", color=ClassicColor.NEUTRAL),
            ClassicCard(word="חופשה", color=ClassicColor.BLUE),
            ClassicCard(word="מועדון", color=ClassicColor.RED),
            ClassicCard(word="ציון", color=ClassicColor.BLUE),
            ClassicCard(word="שק", color=ClassicColor.NEUTRAL),
            ClassicCard(word="אקורדיון", color=ClassicColor.RED),
            ClassicCard(word="ילד", color=ClassicColor.BLUE),
        ],
    )
