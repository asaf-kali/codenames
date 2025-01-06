from codenames.classic.color import ClassicColor
from codenames.classic.state import ClassicOperativeState, ClassicSpymasterState
from codenames.classic.team import ClassicTeam
from tests.utils.players.dictated import DictatedOperative, DictatedSpymaster


class ClassicDictatedSpymaster(DictatedSpymaster[ClassicColor, ClassicTeam, ClassicSpymasterState]):
    pass


class ClassicDictatedOperative(DictatedOperative[ClassicColor, ClassicTeam, ClassicOperativeState]):
    pass
