import pytest

from codenames.classic.board import ClassicBoard
from tests.utils import constants


@pytest.fixture()
def board_10() -> ClassicBoard:
    return constants.board_10()


@pytest.fixture()
def board_25() -> ClassicBoard:
    return constants.board_25()
