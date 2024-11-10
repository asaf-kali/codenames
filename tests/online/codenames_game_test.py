import pytest

from codenames.classic.color import ClassicTeam
from codenames.classic.runner.models import GamePlayers
from codenames.classic.winner import WinningReason
from codenames.online.codenames_game.runner import CodenamesGameRunner
from codenames.online.codenames_game.screenshot import reset_screenshot_run
from tests.utils.players.cheaters import CheaterOperative, CheaterSpymaster


def get_cheaters() -> GamePlayers:
    blue_spymaster = CheaterSpymaster(name="Yoda", team=ClassicTeam.BLUE, card_amount=5)
    red_spymaster = CheaterSpymaster(name="Einstein", team=ClassicTeam.RED, card_amount=1)
    blue_operative = CheaterOperative(name="Anakin", team=ClassicTeam.BLUE, spymaster=blue_spymaster)
    red_operative = CheaterOperative(name="Newton", team=ClassicTeam.RED, spymaster=red_spymaster)
    return GamePlayers.from_collection([blue_spymaster, blue_operative, red_spymaster, red_operative])


@pytest.mark.web
@pytest.mark.flaky(retries=3)
def test_full_codenames_game_flow():
    reset_screenshot_run()
    players = get_cheaters()
    with CodenamesGameRunner(*players.spymasters, *players.operatives, show_host=False) as manager:
        runner = manager.auto_start()
        assert runner.winner is not None
        assert runner.winner.reason == WinningReason.TARGET_SCORE_REACHED
