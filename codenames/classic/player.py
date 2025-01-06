from __future__ import annotations

import abc

from codenames.classic.color import ClassicColor
from codenames.classic.state import ClassicOperativeState, ClassicSpymasterState
from codenames.classic.team import ClassicTeam
from codenames.generic.player import Operative, Player, Spymaster


class ClassicPlayer(Player[ClassicColor, ClassicTeam]):
    pass


class ClassicSpymaster(Spymaster[ClassicColor, ClassicTeam, ClassicSpymasterState], abc.ABC):
    pass


class ClassicOperative(Operative[ClassicColor, ClassicTeam, ClassicOperativeState], abc.ABC):
    pass
