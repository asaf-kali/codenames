from codenames.duet.card import DuetColor
from codenames.duet.player import DuetTeam
from codenames.generic.card import Card
from codenames.generic.move import GivenClue, GivenGuess

DuetCard = Card[DuetColor]
DuetCards = tuple[DuetCard, ...]
DuetGivenClue = GivenClue[DuetTeam]
DuetGivenGuess = GivenGuess[DuetColor, DuetTeam]
