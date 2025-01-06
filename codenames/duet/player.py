from __future__ import annotations

import abc

from codenames.duet.card import DuetColor
from codenames.duet.state import DuetOperativeState, DuetSpymasterState
from codenames.duet.team import DuetTeam
from codenames.generic.player import Operative, Spymaster


class DuetSpymaster(Spymaster[DuetColor, DuetTeam, DuetSpymasterState], abc.ABC):
    pass


class DuetOperative(Operative[DuetColor, DuetTeam, DuetOperativeState], abc.ABC):
    pass


class DuetPlayer(DuetSpymaster, DuetOperative, abc.ABC):
    pass
