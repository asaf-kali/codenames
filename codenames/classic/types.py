from codenames.classic.color import ClassicColor
from codenames.classic.team import ClassicTeam
from codenames.generic.card import Card
from codenames.generic.move import GivenClue, GivenGuess

ClassicCard = Card[ClassicColor]
ClassicCards = tuple[ClassicCard, ...]
ClassicGivenClue = GivenClue[ClassicTeam]
ClassicGivenGuess = GivenGuess[ClassicColor, ClassicTeam]
