from codenames.classic.color import ClassicColor
from codenames.classic.player import ClassicTeam
from tests.utils.players.cheaters import CheaterOperative, CheaterSpymaster

ClassicCheaterSpymaster = CheaterSpymaster[ClassicColor, ClassicTeam]
ClassicCheaterOperator = CheaterOperative[ClassicColor, ClassicTeam]
