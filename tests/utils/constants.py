from codenames.game import Board, Card, CardColor


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
            Card(word="????????", color=CardColor.GRAY),
            Card(word="??????", color=CardColor.BLACK),
            Card(word="????????", color=CardColor.BLUE),
            Card(word="????????", color=CardColor.GRAY),
            Card(word="??????????", color=CardColor.RED),
            Card(word="????????", color=CardColor.GRAY),
            Card(word="????????", color=CardColor.BLUE),
            Card(word="????????????????", color=CardColor.BLUE),
            Card(word="????????", color=CardColor.RED),
            Card(word="????????", color=CardColor.GRAY),
            Card(word="??????", color=CardColor.RED),
            Card(word="????????", color=CardColor.RED),
            Card(word="??????", color=CardColor.RED),
            Card(word="????????????", color=CardColor.BLUE),
            Card(word="????????", color=CardColor.RED),
            Card(word="??????", color=CardColor.RED),
            Card(word="????????", color=CardColor.BLUE),
            Card(word="??????????", color=CardColor.GRAY),
            Card(word="??????", color=CardColor.GRAY),
            Card(word="??????????", color=CardColor.BLUE),
            Card(word="????????????", color=CardColor.RED),
            Card(word="????????", color=CardColor.BLUE),
            Card(word="????", color=CardColor.GRAY),
            Card(word="????????????????", color=CardColor.RED),
            Card(word="??????", color=CardColor.BLUE),
        ]
    )
