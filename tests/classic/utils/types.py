from codenames.classic.color import ClassicColor
from codenames.classic.state import ClassicOperativeState, ClassicSpymasterState
from codenames.classic.team import ClassicTeam
from tests.utils.players.cheaters import CheaterOperative, CheaterSpymaster

ClassicCheaterSpymaster = CheaterSpymaster[ClassicColor, ClassicTeam, ClassicSpymasterState]
ClassicCheaterOperator = CheaterOperative[ClassicColor, ClassicTeam, ClassicOperativeState]
