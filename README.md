# Codenames

[![Pipeline](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml/badge.svg)](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml)
[![PyPI version](https://badge.fury.io/py/codenames.svg)](https://badge.fury.io/py/codenames)

Code infrastructure for the Codenames board game.


## Installation

```bash
pip install codenames
```

## Usage

Here is a simple example of players implementation for CLI:
```python
import logging
import sys

from codenames.boards.builder import generate_board
from codenames.game.move import Guess, Hint
from codenames.game.player import Guesser, Hinter
from codenames.game.runner import GameRunner
from codenames.game.state import GuesserGameState, HinterGameState

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


# Implement basic players

class CLIHinter(Hinter):
    def pick_hint(self, game_state: HinterGameState) -> Hint:
        print(game_state.board.printable_string)
        hint_word = input("Enter hint word: ")
        card_amount = int(input("Enter card amount: "))
        return Hint(word=hint_word, card_amount=card_amount)


class CLIGuesser(Guesser):
    def guess(self, game_state: "GuesserGameState") -> Guess:
        print(game_state.board.printable_string)
        card_word = input("Enter card word: ")
        card_index = game_state.board.find_card_index(word=card_word)
        return Guess(card_index=card_index)

# Run game

def run_cli_game():
    language = "english"
    board = generate_board(language=language)
    red_hinter, red_guesser = CLIHinter(name="Einstein"), CLIGuesser(name="Newton")
    blue_hinter, blue_guesser = CLIHinter(name="Yoda"), CLIGuesser(name="Luke")
    runner = GameRunner(
        blue_hinter=blue_hinter,
        blue_guesser=blue_guesser,
        red_hinter=red_hinter,
        red_guesser=red_guesser,
    )
    runner.run_game(language=language, board=board)


if __name__ == "__main__":
    run_cli_game()
