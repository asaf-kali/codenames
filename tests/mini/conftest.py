import pytest

from codenames.duet.board import DuetBoard
from tests.duet.utils import constants


@pytest.fixture
def board_10() -> DuetBoard:
    return constants.board_10()
