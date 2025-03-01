import pytest

from codenames.duet.board import DuetBoard
from tests.duet.utils import constants


@pytest.fixture
def board_10() -> DuetBoard:
    return constants.board_10()


@pytest.fixture
def board_10_dual() -> DuetBoard:
    return constants.board_10_dual()


@pytest.fixture
def board_25() -> DuetBoard:
    return constants.board_25()
