# Codenames

[![PyPI version](https://badge.fury.io/py/codenames.svg)](https://badge.fury.io/py/codenames)
[![Pipeline](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml/badge.svg)](https://github.com/asaf-kali/codenames/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/github/asaf-kali/codenames/graph/badge.svg?token=HET5E8P1UK)](https://codecov.io/github/asaf-kali/codenames)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-111111.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/imports-isort-%231674b1)](https://pycqa.github.io/isort/)
[![Type checked: mypy](https://img.shields.io/badge/type%20check-mypy-22aa11)](http://mypy-lang.org/)
[![Linting: pylint](https://img.shields.io/badge/linting-pylint-22aa11)](https://github.com/pylint-dev/pylint)

Code infrastructure for the Codenames board game. \
Designed to serve as a base for implementing players (agents) with different strategies and algorithms. \
See the [codenames-solvers](https://github.com/asaf-kali/codenames-solvers) repository for such examples.


### Installation

Install from PyPI using pip: `pip install codenames`

### Usage
Here is a simple example of command-line based players, and a `GameRunner` that runs a game between them:

```python
import logging
import sys

from codenames.classic.builder import generate_board
from codenames.classic.color import ClassicTeam
from codenames.classic.runner.models import GamePlayers
from codenames.classic.runner.runner import ClassicGameRunner
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster
from codenames.generic.state import OperativeState, SpymasterState

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


# Implement basic players

class CLIHinter(Spymaster):
    def give_clue(self, game_state: SpymasterState) -> Clue:
        print("Board state: \n" + game_state.board.printable_string)
        hint_word = input("Enter hint word: ")
        card_amount = int(input("Enter card amount: "))
        return Clue(word=hint_word, card_amount=card_amount)


class CLIGuesser(Operative):
    def guess(self, game_state: OperativeState) -> Guess:
        print(game_state.board.printable_string)
        card_word = input("Enter card word: ")
        card_index = game_state.board.find_card_index(word=card_word)
        return Guess(card_index=card_index)


# Run game

def run_cli_game():
    language = "english"
    board = generate_board(language=language)
    blue_hinter, blue_guesser = CLIHinter("Yoda", ClassicTeam.BLUE), CLIGuesser("Luke", ClassicTeam.BLUE)
    red_hinter, red_guesser = CLIHinter("Einstein", ClassicTeam.RED), CLIGuesser("Newton", ClassicTeam.RED)
    players = GamePlayers.from_collection([blue_hinter, blue_guesser, red_hinter, red_guesser])
    runner = ClassicGameRunner(players=players, board=board)
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
