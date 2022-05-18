from codenames.game.base import Board, Card, CardColor


def board_10() -> Board:
    return Board(
        cards=[
            Card(word="Card 0", color=CardColor.BLUE),  # 0
            Card(word="Card 1", color=CardColor.BLUE),  # 1
            Card(word="Card 2", color=CardColor.BLUE),  # 2
            Card(word="Card 3", color=CardColor.BLUE),  # 3
            Card(word="Card 4", color=CardColor.RED),  # 4
            Card(word="Card 5", color=CardColor.RED),  # 5
            Card(word="Card 6", color=CardColor.RED),  # 6
            Card(word="Card 7", color=CardColor.GRAY),  # 7
            Card(word="Card 8", color=CardColor.GRAY),  # 8
            Card(word="Card 9", color=CardColor.BLACK),  # 9
        ]
    )


def board_25() -> Board:
    return Board(
        cards=[
            Card(word="Card 0", color=CardColor.BLUE),
            Card(word="Card 1", color=CardColor.BLUE),
            Card(word="Card 2", color=CardColor.BLUE),
            Card(word="Card 3", color=CardColor.BLUE),
            Card(word="Card 4", color=CardColor.BLUE),
            Card(word="Card 5", color=CardColor.BLUE),
            Card(word="Card 6", color=CardColor.BLUE),
            Card(word="Card 7", color=CardColor.BLUE),
            Card(word="Card 8", color=CardColor.BLUE),
            Card(word="Card 9", color=CardColor.RED),
            Card(word="Card 10", color=CardColor.RED),
            Card(word="Card 11", color=CardColor.RED),
            Card(word="Card 12", color=CardColor.RED),
            Card(word="Card 13", color=CardColor.RED),
            Card(word="Card 14", color=CardColor.RED),
            Card(word="Card 15", color=CardColor.RED),
            Card(word="Card 16", color=CardColor.RED),
            Card(word="Card 17", color=CardColor.GRAY),
            Card(word="Card 18", color=CardColor.GRAY),
            Card(word="Card 19", color=CardColor.GRAY),
            Card(word="Card 20", color=CardColor.GRAY),
            Card(word="Card 21", color=CardColor.GRAY),
            Card(word="Card 22", color=CardColor.GRAY),
            Card(word="Card 23", color=CardColor.GRAY),
            Card(word="Card 24", color=CardColor.BLACK),
        ]
    )


def hebrew_board() -> Board:
    return Board(
        cards=[
            Card(word="חיים", color=CardColor.GRAY),
            Card(word="ערך", color=CardColor.BLACK),
            Card(word="מסוק", color=CardColor.BLUE),
            Card(word="שבוע", color=CardColor.GRAY),
            Card(word="רובוט", color=CardColor.RED),
            Card(word="פוטר", color=CardColor.GRAY),
            Card(word="אסור", color=CardColor.BLUE),
            Card(word="דינוזאור", color=CardColor.BLUE),
            Card(word="מחשב", color=CardColor.RED),
            Card(word="מעמד", color=CardColor.GRAY),
            Card(word="בעל", color=CardColor.RED),
            Card(word="פנים", color=CardColor.RED),
            Card(word="פרק", color=CardColor.RED),
            Card(word="גפילטע", color=CardColor.BLUE),
            Card(word="שונה", color=CardColor.RED),
            Card(word="שכר", color=CardColor.RED),
            Card(word="קפיץ", color=CardColor.BLUE),
            Card(word="תרסיס", color=CardColor.GRAY),
            Card(word="דגל", color=CardColor.GRAY),
            Card(word="חופשה", color=CardColor.BLUE),
            Card(word="מועדון", color=CardColor.RED),
            Card(word="ציון", color=CardColor.BLUE),
            Card(word="שק", color=CardColor.GRAY),
            Card(word="אקורדיון", color=CardColor.RED),
            Card(word="ילד", color=CardColor.BLUE),
        ]
    )
