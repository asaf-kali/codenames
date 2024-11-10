import logging
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from codenames.classic.color import ClassicColor
from codenames.classic.types import ClassicCard

log = logging.getLogger(__name__)


CSS_CLASS_TO_CLASSIC_COLOR = {
    "red": ClassicColor.RED,
    "blue": ClassicColor.BLUE,
    "gray": ClassicColor.NEUTRAL,
    "black": ClassicColor.ASSASSIN,
}


@dataclass
class ParseResult:
    card: ClassicCard
    index: int


def _parse_card(card_container: WebElement) -> ParseResult:
    card_element = card_container.find_element(By.TAG_NAME, value="div")
    word = _parse_card_word(card_element=card_element)
    card_color = _parse_card_color(card_element=card_element)
    revealed = _is_card_revealed(card_container=card_container)
    index = _parse_card_index(card_container=card_container)
    card = ClassicCard(word=word, color=card_color, revealed=revealed)
    log.debug(f"Parsed card {index}: {card}")
    return ParseResult(card=card, index=index)


def _parse_card_index(card_container: WebElement) -> int:
    return int(card_container.get_attribute("tabindex"))  # type: ignore


def _parse_card_word(card_element: WebElement) -> str:
    card_word = card_element.text.strip().lower()
    return card_word


def _parse_card_color(card_element: WebElement) -> ClassicColor:
    element_classes = card_element.get_attribute("class").split(" ")  # type: ignore
    for css_class, classic_color in CSS_CLASS_TO_CLASSIC_COLOR.items():
        if css_class.lower() in element_classes:
            return classic_color
    raise ValueError(f"Could not parse card color from element classes: {element_classes}")


def _is_card_revealed(card_container: WebElement) -> bool:  # pylint: disable=unused-argument
    if "revealed" in card_container.accessible_name:
        return True
    return False
