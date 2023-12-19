import logging

from selenium.webdriver.remote.webelement import WebElement

from codenames.game.card import Card
from codenames.game.color import CardColor

log = logging.getLogger(__name__)


def _parse_card(card_element: WebElement) -> Card:
    word = _parse_card_word(card_element=card_element)
    card_color = _parse_card_color(card_element=card_element)
    revealed = _is_card_revealed(card_element=card_element)
    card = Card(word=word, color=card_color, revealed=revealed)
    log.debug(f"Parsed card: {card}")
    return card


def _parse_card_word(card_element: WebElement) -> str:
    card_word = card_element.text.strip().lower()
    return card_word


def _parse_card_color(card_element: WebElement) -> CardColor:
    element_classes = card_element.get_attribute("class").split(" ")
    for card_color in CardColor:
        if card_color.lower() in element_classes:
            return card_color  # type: ignore
    raise ValueError(f"Could not parse card color from element classes: {element_classes}")


def _is_card_revealed(card_element: WebElement) -> bool:
    # TODO: Implement this
    return False
