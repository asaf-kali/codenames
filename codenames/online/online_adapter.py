import logging
from enum import Enum
from time import sleep
from typing import Iterable, Optional

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from codenames.game import (
    PASS_GUESS,
    Board,
    Card,
    CardColor,
    Guess,
    GuesserGameState,
    Hint,
    Player,
    PlayerRole,
)
from codenames.online.utils import ShadowRootElement, poll_condition
from codenames.utils import wrap

log = logging.getLogger(__name__)

WEBAPP_URL = "https://namecoding.herokuapp.com/"
CLEAR = "\b\b\b\b\b"


class NamecodingLanguage(str, Enum):
    ENGLISH = "english"
    HEBREW = "hebrew"


class IllegalOperation(Exception):
    pass


def fill_input(element: WebElement, value: str):
    element.send_keys(CLEAR)
    element.send_keys(CLEAR)
    sleep(0.1)
    element.send_keys(value)
    sleep(0.1)


def _is_card_revealed(card_element: ShadowRootElement) -> bool:
    image_overlay = card_element.find_element(by=By.ID, value="image-overlay")
    revealed = image_overlay.get_attribute("revealed") is not None
    return revealed


def _parse_card(card_element: ShadowRootElement) -> Card:
    word = card_element.find_element(by=By.ID, value="bottom").text.strip().lower()
    namecoding_color = card_element.find_element(by=By.ID, value="right").get_attribute("team")
    card_color = parse_card_color(namecoding_color=namecoding_color)
    revealed = _is_card_revealed(card_element=card_element)
    card = Card(word=word, color=card_color, revealed=revealed)
    log.debug(f"Parsed card: {card}")
    return card


def get_shadow_root(parent, tag_name: str) -> ShadowRootElement:
    element = parent.find_element(by=By.TAG_NAME, value=tag_name)
    shadow_root = ShadowRootElement(element.shadow_root)
    return shadow_root


class NamecodingPlayerAdapter:
    def __init__(self, player: Player, implicitly_wait: int = 1, headless: bool = True, chromedriver_path: str = None):
        options = webdriver.ChromeOptions()
        if player.is_human:
            headless = False
        if headless:
            options.add_argument("headless")
        if not chromedriver_path:
            log.warning("Chromedriver path not given, searching in root directory...")
            chromedriver_path = "./chromedriver"  # TODO: Make default path a config
        self.driver = webdriver.Chrome(chromedriver_path, options=options)
        self.driver.implicitly_wait(implicitly_wait)
        self.player = player

    # Utils #

    @property
    def log_prefix(self) -> str:
        return wrap(self.player.name)

    def __str__(self) -> str:
        return f"{self.player} adapter"

    # Pages #

    @property
    def codenames_app(self) -> ShadowRootElement:
        return get_shadow_root(self.driver, tag_name="codenames-app")

    def get_page(self, page_name: str) -> ShadowRootElement:
        return get_shadow_root(self.codenames_app, tag_name=page_name)

    def get_login_page(self) -> ShadowRootElement:
        return self.get_page("login-page")

    def get_menu_page(self) -> ShadowRootElement:
        return self.get_page("menu-page")

    def get_lobby_page(self) -> ShadowRootElement:
        return self.get_page("lobby-page")

    def get_game_page(self) -> ShadowRootElement:
        return self.get_page("codenames-game")

    def get_clue_area(self) -> ShadowRootElement:
        return get_shadow_root(self.get_game_page(), tag_name="clue-area")

    # Methods #

    def open(self) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is logging in...")
        self.driver.get(WEBAPP_URL)
        login_page = self.get_login_page()
        username_textbox = login_page.find_element(by=By.ID, value="username-input")
        login_button = login_page.find_element(by=By.ID, value="login-button")
        fill_input(username_textbox, self.player.name)
        login_button.click()
        return self

    def host_game(self) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is hosting...")
        menu_page = self.get_menu_page()
        host_button = menu_page.find_element(by=By.ID, value="host-button")
        host_button.click()
        return self

    def join_game(self, game_id: str) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is joining game {wrap(game_id)}...")
        menu_page = self.get_menu_page()
        game_id_input = menu_page.find_element(by=By.ID, value="game-id-input")
        join_game_button = menu_page.find_element(by=By.ID, value="join-game-button")
        fill_input(game_id_input, game_id)
        join_game_button.click()
        return self

    def get_game_id(self) -> str:
        lobby_page = self.get_lobby_page()
        game_id_container = lobby_page.find_element(by=By.ID, value="game-code")
        game_id = game_id_container.text.strip()
        return game_id

    def choose_role(self) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is picking role...")
        lobby_page = self.get_lobby_page()
        team_element_id = f"{self.player.team_color.value.lower()}-team"  # type: ignore
        role_button_class_name = "guessers" if self.player.role == PlayerRole.GUESSER else "hinters"
        team_element = lobby_page.find_element(by=By.ID, value=team_element_id)
        role_button = team_element.find_element(by=By.CLASS_NAME, value=role_button_class_name)
        role_button.click()
        return self

    def set_language(self, language: NamecodingLanguage) -> "NamecodingPlayerAdapter":
        lobby_page = self.get_lobby_page()
        options_section = lobby_page.find_element(by=By.ID, value="options-section")
        language_options = get_shadow_root(options_section, tag_name="x-options")
        button_index = 0 if language == NamecodingLanguage.HEBREW else 1
        buttons = language_options.find_elements(by=By.TAG_NAME, value="x-button")
        buttons[button_index].click()
        sleep(0.1)
        return self

    def set_clock(self, clock: bool) -> "NamecodingPlayerAdapter":
        lobby_page = self.get_lobby_page()
        options_section = lobby_page.find_element(by=By.ID, value="options-section")
        checkbox = options_section.find_element(by=By.TAG_NAME, value="x-checkbox")
        is_checked_now = checkbox.get_attribute("value") is not None
        if is_checked_now != clock:
            checkbox.click()
            sleep(0.1)
        return self

    def ready(self, ready: bool = True) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is ready!")
        lobby_page = self.get_lobby_page()
        switch = lobby_page.find_element(by=By.ID, value="ready-switch")
        is_checked_now = switch.get_attribute("value") is not None
        if is_checked_now != ready:
            switch.click()
            sleep(0.1)
        return self

    def click_start_game(self) -> "NamecodingPlayerAdapter":
        log.info(f"{self.log_prefix} is starting the game!")
        try:
            lobby_page = self.get_lobby_page()
        except NoSuchElementException:
            log.warning("Lobby page is not found, assuming start was already clicked.")
            return self
        start_game_button = lobby_page.find_element(by=By.ID, value="start-game-button")
        poll_condition(
            lambda: start_game_button.get_attribute("disabled") is None, timeout_sec=300, poll_interval_sec=0.5
        )
        start_game_button.click()
        return self

    # def is_my_turn(self) -> bool:
    #     clue_area = self.get_clue_area()
    #     if (
    #         self.player.role == PlayerRole.HINTER
    #         and clue_area.find_elements(by=By.ID, value="submit-clue-button") != []
    #     ):
    #         return True
    #     if (
    #         self.player.role == PlayerRole.GUESSER
    #         and clue_area.find_elements(by=By.ID, value="finish-turn-button") != []
    #     ):
    #         return True
    #     return False

    def parse_board(self) -> Board:
        log.debug("Parsing board...")
        game_page = self.get_game_page()
        card_containers = game_page.find_elements(by=By.ID, value="card-padding-container")
        card_elements = [get_shadow_root(card_container, "card-element") for card_container in card_containers]
        cards = [_parse_card(card_element) for card_element in card_elements]
        log.debug("Parse board done")
        return Board(cards=cards)

    def detect_visibility_change(self, revealed_card_indexes: Iterable[int]) -> Optional[int]:
        log.debug("Looking for visibility change...")
        game_page = self.get_game_page()
        card_containers = game_page.find_elements(by=By.ID, value="card-padding-container")
        for i, card_container in enumerate(card_containers):
            card_root = get_shadow_root(card_container, "card-element")
            is_revealed = _is_card_revealed(card_root)
            if is_revealed and i not in revealed_card_indexes:
                log.debug(f"Found a visibility change at index {wrap(i)}")
                return i
        log.debug("No visibility change found")
        return None

    def transmit_hint(self, hint: Hint) -> "NamecodingPlayerAdapter":
        log.debug(f"Sending hint: {hint}")
        clue_area = self.get_clue_area()
        sleep(0.1)
        clue_input = clue_area.find_element(by=By.ID, value="clue-input")
        cards_input = clue_area.find_element(by=By.ID, value="cards-input")
        submit_clue_button = clue_area.find_element(by=By.ID, value="submit-clue-button")
        fill_input(clue_input, hint.word.title())
        fill_input(cards_input, str(hint.card_amount))
        submit_clue_button.click()
        sleep(0.2)
        self.approve_alert()
        sleep(0.5)
        return self

    def approve_alert(self, max_tries: int = 20, interval_seconds: float = 0.5):
        log.debug("Approve alert called.")
        tries = 0
        while True:
            tries += 1
            try:
                self.driver.switch_to.alert.accept()
                log.debug("Alert found.")
                return
            except NoAlertPresentException as e:
                if tries >= max_tries:
                    log.warning(f"Alert not found after {max_tries} tries, quitting.")
                    raise e
                log.debug(f"Alert not found, sleeping {interval_seconds} seconds.")
                sleep(interval_seconds)

    def transmit_guess(self, guess: Guess) -> "NamecodingPlayerAdapter":
        log.debug(f"Sending guess: {guess}")
        game_page = self.get_game_page()
        if guess.card_index == PASS_GUESS:
            clue_area = self.get_clue_area()
            finish_turn_button = clue_area.find_element(by=By.ID, value="finish-turn-button")
            finish_turn_button.click()
            sleep(0.2)
            self.approve_alert()
        else:
            card_containers = game_page.find_elements(by=By.ID, value="card-padding-container")
            selected_card = card_containers[guess.card_index]
            selected_card.click()
        sleep(0.5)
        return self

    def poll_hint_given(self) -> Hint:
        log.debug("Polling for hint given...")
        clue_area = self.get_clue_area()
        sleep(0.1)

        poll_condition(lambda: self.has_clue_text(clue_area), timeout_sec=600)
        clue_input = clue_area.find_element(by=By.ID, value="clue-text")
        cards_input = clue_area.find_element(by=By.ID, value="cards-num-container")
        return Hint(word=clue_input.text.strip(), card_amount=int(cards_input.text[0]))

    def poll_guess_given(self, game_state: GuesserGameState) -> Guess:
        log.debug("Polling for guess given...")
        revealed_card_indexes = game_state.board.revealed_card_indexes
        clue_area = self.get_clue_area()
        should_return = False
        while not should_return:
            if not self.has_clue_text(clue_area):
                log.debug("No clue text found, detecting changes last time...")
                should_return = True
            card_index = self.detect_visibility_change(revealed_card_indexes)
            if card_index is not None:
                return Guess(card_index=card_index)
        log.debug("Returning pass guess.")
        return Guess(card_index=PASS_GUESS)

    def has_clue_text(self, clue_area: ShadowRootElement = None) -> bool:
        if not clue_area:
            clue_area = self.get_clue_area()
        return clue_area.find_elements(by=By.ID, value="clue-text") != []

    def close(self):
        try:
            self.driver.close()
        except:  # noqa
            pass


def parse_card_color(namecoding_color: str) -> CardColor:
    namecoding_color = namecoding_color.strip().upper()
    if namecoding_color == "GREEN":
        namecoding_color = "GRAY"
    return CardColor[namecoding_color]
