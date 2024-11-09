class CardNotFoundError(ValueError):
    def __init__(self, word: str):
        self.word = word
        super().__init__(f"Card not found: {self.word}")


class QuitGame(Exception):
    pass


class GameRuleError(Exception):
    pass


class InvalidTurn(GameRuleError):
    pass


class GameIsOver(InvalidTurn):
    def __init__(self):
        super().__init__("Game is over!")


class InvalidClue(GameRuleError):
    pass


class InvalidGuess(GameRuleError):
    pass
