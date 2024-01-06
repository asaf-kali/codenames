# Codenames

[![Pipeline](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml/badge.svg)](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/github/asaf-kali/codenames/graph/badge.svg?token=HET5E8P1UK)](https://codecov.io/github/asaf-kali/codenames)
[![PyPI version](https://badge.fury.io/py/codenames.svg)](https://badge.fury.io/py/codenames)

Code infrastructure for the Codenames board game. \
Designed to serve as a base for implementing different Codenames players (solvers).


### Installation

Install from PyPI using pip: `pip install codenames`

### Usage
Here is a simple example of command-line based players, and a `GameRunner` that runs a game between them:

```python
import logging

import sys

from codenames.boards.builder import generate_board
from codenames.game.color import TeamColor
from codenames.game.move import Guess, Hint
from codenames.game.player import Guesser, Hinter, GamePlayers
from codenames.game.runner import GameRunner
from codenames.game.state import GuesserGameState, HinterGameState

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


# Implement basic players

class CLIHinter(Hinter):
    def pick_hint(self, game_state: HinterGameState) -> Hint:
        print("Board state: \n" + game_state.board.printable_string)
        hint_word = input("Enter hint word: ")
        card_amount = int(input("Enter card amount: "))
        return Hint(word=hint_word, card_amount=card_amount)


class CLIGuesser(Guesser):
    def guess(self, game_state: GuesserGameState) -> Guess:
        print(game_state.board.printable_string)
        card_word = input("Enter card word: ")
        card_index = game_state.board.find_card_index(word=card_word)
        return Guess(card_index=card_index)


# Run game

def run_cli_game():
    language = "english"
    board = generate_board(language=language)
    blue_hinter, blue_guesser = CLIHinter("Yoda", TeamColor.BLUE), CLIGuesser("Luke", TeamColor.BLUE)
    red_hinter, red_guesser = CLIHinter("Einstein", TeamColor.RED), CLIGuesser("Newton", TeamColor.RED)
    players = GamePlayers.from_collection([blue_hinter, blue_guesser, red_hinter, red_guesser])
    runner = GameRunner(players=players, board=board)
    winner = runner.run_game()
    print(f"Winner: {winner}")


if __name__ == "__main__":
    run_cli_game()
```
Example output:
```
[Blue] turn.
Board state:
+------------+------------+--------------+-------------+-------------------+
|   ‎🟦 tax   |  ‎⬜ drama  |   ‎⬜ thick   |  ‎🟥 africa  | ‎💀 transformation |
+------------+------------+--------------+-------------+-------------------+
| ‎⬜ project | ‎🟦 athlete | ‎🟥 vegetable | ‎⬜ engineer |     ‎🟥 human      |
+------------+------------+--------------+-------------+-------------------+
|  ‎⬜ chain  |  ‎🟦 cake   |   ‎🟦 shift   |  ‎🟦 study   |      ‎🟥 will      |
+------------+------------+--------------+-------------+-------------------+
| ‎🟥 outcome |  ‎🟥 desk   |  ‎🟥 soviet   |   ‎⬜ rare   |     ‎🟥 youth      |
+------------+------------+--------------+-------------+-------------------+
| ‎🟦 account | ‎🟦 couple  |   ‎⬜ solve   | ‎🟦 academic |     ‎🟦 stable     |
+------------+------------+--------------+-------------+-------------------+
Enter hint word: example
Enter card amount: 2
Hinter: [example] 2 card(s)
+---------+---------+-----------+----------+----------------+
|   ‎tax   |  ‎drama  |   ‎thick   |  ‎africa  | ‎transformation |
+---------+---------+-----------+----------+----------------+
| ‎project | ‎athlete | ‎vegetable | ‎engineer |     ‎human      |
+---------+---------+-----------+----------+----------------+
|  ‎chain  |  ‎cake   |   ‎shift   |  ‎study   |      ‎will      |
+---------+---------+-----------+----------+----------------+
| ‎outcome |  ‎desk   |  ‎soviet   |   ‎rare   |     ‎youth      |
+---------+---------+-----------+----------+----------------+
| ‎account | ‎couple  |   ‎solve   | ‎academic |     ‎stable     |
+---------+---------+-----------+----------+----------------+
Enter card word: account
Guesser: '🟦 account', correct!
+------------+---------+-----------+----------+----------------+
|    ‎tax     |  ‎drama  |   ‎thick   |  ‎africa  | ‎transformation |
+------------+---------+-----------+----------+----------------+
|  ‎project   | ‎athlete | ‎vegetable | ‎engineer |     ‎human      |
+------------+---------+-----------+----------+----------------+
|   ‎chain    |  ‎cake   |   ‎shift   |  ‎study   |      ‎will      |
+------------+---------+-----------+----------+----------------+
|  ‎outcome   |  ‎desk   |  ‎soviet   |   ‎rare   |     ‎youth      |
+------------+---------+-----------+----------+----------------+
| ‎🟦 account | ‎couple  |   ‎solve   | ‎academic |     ‎stable     |
+------------+---------+-----------+----------+----------------+
Enter card word: rare
Guesser: '⬜ rare', wrong!
Guesser wrong, turn is over
...
```
