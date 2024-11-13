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

**Game rules**:
* [Classic](https://czechgames.com/files/rules/codenames-rules-en.pdf)
* [Duet](https://czechgames.com/files/rules/codenames-duet-rules-en.pdf)

### Installation

Install from PyPI using pip: `pip install codenames`

### Usage
Here is a simple example of command-line based players, and a `GameRunner` that runs a game between them:

```python
import logging
import sys

from codenames.classic.board import ClassicBoard
from codenames.classic.color import ClassicTeam
from codenames.classic.runner import ClassicGamePlayers, ClassicGameRunner
from codenames.generic.move import Clue, Guess
from codenames.generic.player import Operative, Spymaster
from codenames.generic.state import OperativeState, SpymasterState
from codenames.utils.vocabulary.languages import get_vocabulary

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


####################################
# Naive CLI players implementation #
####################################


class CLISpymaster(Spymaster):
    def give_clue(self, game_state: SpymasterState) -> Clue:
        print("\nGive a hint. Board: \n" + game_state.board.printable_string)
        print(f"Revealed cards: {list(game_state.board.revealed_card_indexes)}")
        hint_word = input("Enter hint word: ")
        card_amount = int(input("Enter card amount: "))
        return Clue(word=hint_word, card_amount=card_amount)


class CLIOperative(Operative):
    def guess(self, game_state: OperativeState) -> Guess:
        print(f"\nGuess a card. Given clue: {game_state.current_clue}. Current board state: ")
        print(game_state.board.printable_string)
        card_word = input("Enter card word: ")
        card_index = game_state.board.find_card_index(word=card_word)
        return Guess(card_index=card_index)

############
# Run Game #
############

def run_classic_cli_game():
    # Init players
    blue_spymaster = CLISpymaster(name="Yoda",team= ClassicTeam.BLUE)
    blue_operative = CLIOperative(name="Luke", team=ClassicTeam.BLUE)
    red_spymaster = CLISpymaster(name="Einstein", team=ClassicTeam.RED)
    red_operative = CLIOperative(name="Newton", team=ClassicTeam.RED)
    players = ClassicGamePlayers.from_collection(blue_spymaster, blue_operative, red_spymaster, red_operative)
    # Init board
    vocabulary = get_vocabulary(language="english")
    board = ClassicBoard.from_vocabulary(vocabulary=vocabulary)
    # Run game
    runner = ClassicGameRunner(players=players, board=board)
    winner = runner.run_game()
    print(f"Winner: {winner}")


if __name__ == "__main__":
    run_classic_cli_game()
```

Example output:
```
-----
[RED] turn.

Give a hint. Board:
+-----------+-------------+------------+-----------------+------------+
| ‎🟦 pretty |  ‎⬜ young   |  ‎⬜ essay  |    ‎🟥 apple     |  ‎⬜ kiss   |
+-----------+-------------+------------+-----------------+------------+
|  ‎⬜ poem  |  ‎🟦 solve   |   ‎🟥 pan   | ‎🟦 organization |  ‎🟦 union  |
+-----------+-------------+------------+-----------------+------------+
|  ‎🟥 myth  |   ‎🟥 neck   | ‎🟥 shelter |    ‎🟦 locate    |   ‎🟥 pet   |
+-----------+-------------+------------+-----------------+------------+
| ‎🟥 react  |  ‎⬜ person  |  ‎⬜ mood   |    ‎🟥 heart     | ‎⬜ breath  |
+-----------+-------------+------------+-----------------+------------+
|  ‎🟥 rich  | ‎🟦 standard |  ‎🟦 crop   |   ‎💀 chicken    | ‎🟦 wedding |
+-----------+-------------+------------+-----------------+------------+
Revealed cards: []
Enter hint word: example
Enter card amount: 2
Spymaster: [example] 2 card(s)

Guess a card. Given clue: [example] [2]. Current board state:
+--------+----------+---------+--------------+---------+
| ‎pretty |  ‎young   |  ‎essay  |    ‎apple     |  ‎kiss   |
+--------+----------+---------+--------------+---------+
|  ‎poem  |  ‎solve   |   ‎pan   | ‎organization |  ‎union  |
+--------+----------+---------+--------------+---------+
|  ‎myth  |   ‎neck   | ‎shelter |    ‎locate    |   ‎pet   |
+--------+----------+---------+--------------+---------+
| ‎react  |  ‎person  |  ‎mood   |    ‎heart     | ‎breath  |
+--------+----------+---------+--------------+---------+
|  ‎rich  | ‎standard |  ‎crop   |   ‎chicken    | ‎wedding |
+--------+----------+---------+--------------+---------+
Enter card word: heart
Operative: '🟥 heart', correct!

Guess a card. Given clue: [example] [2]. Current board state:
+--------+----------+---------+--------------+---------+
| ‎pretty |  ‎young   |  ‎essay  |    ‎apple     |  ‎kiss   |
+--------+----------+---------+--------------+---------+
|  ‎poem  |  ‎solve   |   ‎pan   | ‎organization |  ‎union  |
+--------+----------+---------+--------------+---------+
|  ‎myth  |   ‎neck   | ‎shelter |    ‎locate    |   ‎pet   |
+--------+----------+---------+--------------+---------+
| ‎react  |  ‎person  |  ‎mood   |   ‎🟥 heart   | ‎breath  |
+--------+----------+---------+--------------+---------+
|  ‎rich  | ‎standard |  ‎crop   |   ‎chicken    | ‎wedding |
+--------+----------+---------+--------------+---------+
Enter card word: pet
Operative: '🟥 pet', correct!

Guess a card. Given clue: [example] [2]. Current board state:
+--------+----------+---------+--------------+---------+
| ‎pretty |  ‎young   |  ‎essay  |    ‎apple     |  ‎kiss   |
+--------+----------+---------+--------------+---------+
|  ‎poem  |  ‎solve   |   ‎pan   | ‎organization |  ‎union  |
+--------+----------+---------+--------------+---------+
|  ‎myth  |   ‎neck   | ‎shelter |    ‎locate    | ‎🟥 pet  |
+--------+----------+---------+--------------+---------+
| ‎react  |  ‎person  |  ‎mood   |   ‎🟥 heart   | ‎breath  |
+--------+----------+---------+--------------+---------+
|  ‎rich  | ‎standard |  ‎crop   |   ‎chicken    | ‎wedding |
+--------+----------+---------+--------------+---------+
Enter card word: mood
Operative: '⬜ mood', wrong!
Operative wrong, turn is over

-----
[BLUE] turn.

Give a hint. Board:
+-----------+-------------+------------+-----------------+------------+
| ‎🟦 pretty |  ‎⬜ young   |  ‎⬜ essay  |    ‎🟥 apple     |  ‎⬜ kiss   |
+-----------+-------------+------------+-----------------+------------+
|  ‎⬜ poem  |  ‎🟦 solve   |   ‎🟥 pan   | ‎🟦 organization |  ‎🟦 union  |
+-----------+-------------+------------+-----------------+------------+
|  ‎🟥 myth  |   ‎🟥 neck   | ‎🟥 shelter |    ‎🟦 locate    |   ‎🟥 pet   |
+-----------+-------------+------------+-----------------+------------+
| ‎🟥 react  |  ‎⬜ person  |  ‎⬜ mood   |    ‎🟥 heart     | ‎⬜ breath  |
+-----------+-------------+------------+-----------------+------------+
|  ‎🟥 rich  | ‎🟦 standard |  ‎🟦 crop   |   ‎💀 chicken    | ‎🟦 wedding |
+-----------+-------------+------------+-----------------+------------+
Revealed cards: [14, 17, 18]
Enter hint word:
......
```
