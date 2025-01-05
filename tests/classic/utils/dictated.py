from codenames.classic.color import ClassicColor
from codenames.classic.player import ClassicTeam
from tests.utils.players.dictated import DictatedOperative, DictatedSpymaster


class DictatedClassicSpymaster(DictatedSpymaster[ClassicColor, ClassicTeam]):
    pass


class DictatedClassicOperative(DictatedOperative[ClassicColor, ClassicTeam]):
    pass
