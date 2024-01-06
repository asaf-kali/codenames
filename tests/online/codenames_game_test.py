import pytest

from codenames.game.color import TeamColor
from codenames.game.player import GamePlayers
from codenames.game.winner import WinningReason
from codenames.online.codenames_game.runner import CodenamesGameRunner
from tests.utils.players.cheaters import CheaterGuesser, CheaterHinter


def get_cheaters() -> GamePlayers:
    blue_hinter = CheaterHinter(name="Yoda", team_color=TeamColor.BLUE, card_amount=5)
    red_hinter = CheaterHinter(name="Einstein", team_color=TeamColor.RED, card_amount=1)
    blue_guesser = CheaterGuesser(name="Anakin", team_color=TeamColor.BLUE, hinter=blue_hinter)
    red_guesser = CheaterGuesser(name="Newton", team_color=TeamColor.RED, hinter=red_hinter)
    return GamePlayers.from_collection([blue_hinter, blue_guesser, red_hinter, red_guesser])


@pytest.mark.web
@pytest.mark.flaky(retries=3)
def test_full_codenames_game_flow():
    players = get_cheaters()
    with CodenamesGameRunner(*players.hinters, *players.guessers, show_host=False) as manager:
        runner = manager.auto_start()
        assert runner.winner is not None
        assert runner.winner.reason == WinningReason.TARGET_SCORE_REACHED
