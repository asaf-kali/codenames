import logging
from enum import Enum
from time import sleep
from typing import Iterable, Optional

from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from codenames.game.board import Board, Card
from codenames.game.color import CardColor
from codenames.game.move import PASS_GUESS, Guess, Hint
from codenames.game.player import Player, PlayerRole
from codenames.game.state import GuesserGameState
from codenames.online.utils import ShadowRootElement, poll_condition, poll_element
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)

WEBAPP_URL = "https://codenames.game/"
CLEAR = "\b\b\b\b\b"


class CodenamesGameLanguage(str, Enum):
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
    codenames_game_color = card_element.find_element(by=By.ID, value="right").get_attribute("team")
    card_color = parse_card_color(codenames_game_color=codenames_game_color)
    revealed = _is_card_revealed(card_element=card_element)
    card = Card(word=word, color=card_color, revealed=revealed)
    log.debug(f"Parsed card: {card}")
    return card


def get_shadow_root(parent, tag_name: str) -> ShadowRootElement:
    element = parent.find_element(by=By.TAG_NAME, value=tag_name)
    shadow_root = ShadowRootElement(element.shadow_root)
    return shadow_root


class CodenamesGamePlayerAdapter:
    def __init__(
        self,
        player: Player,
        implicitly_wait: int = 1,
        headless: bool = False,
        chromedriver_path: Optional[str] = None,
        game_url: Optional[str] = None,
    ):
        options = webdriver.ChromeOptions()
        if player.is_human:
            headless = False
        if headless:
            options.add_argument("headless")
        if not chromedriver_path:
            log.warning("Chromedriver path not given, searching in root directory...")
            chromedriver_path = "./chromedriver"  # TODO: Make default path a config
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(implicitly_wait)
        self.player = player
        self.game_url = game_url

    # Utils #

    @property
    def log_prefix(self) -> str:
        return wrap(self.player.name)

    def __str__(self) -> str:
        return f"{self.player} adapter"

    # Methods #

    def open(self) -> "CodenamesGamePlayerAdapter":
        log.info(f"{self.log_prefix} window open...")
        game_url = self.game_url or WEBAPP_URL
        self.driver.get(game_url)
        return self

    def host_game(
        self,
        language: CodenamesGameLanguage,
    ) -> "CodenamesGamePlayerAdapter":
        log.info(f"{self.log_prefix} is creating a room...")
        create_room_button = poll_element(self.get_create_room_button)
        create_room_button.click()
        self.configure_language()
        self.login()
        log.info("New game created")
        return self

    def configure_language(self):
        # TODO: Implement
        pass

    def login(self):
        # Enter nickname
        nickname_input = poll_element(self.get_nickname_input)
        # nickname_input.click()
        fill_input(nickname_input, value=self.player.name)
        # Submit
        submit_button = self.get_login_submit_button()
        submit_button.click()
        return self

    def choose_role(self) -> "CodenamesGamePlayerAdapter":
        log.info(f"{self.log_prefix} is picking role...")
        join_button = self.get_join_button()
        join_button.click()
        log.info(f"{self.log_prefix} picked role")
        return self

    def get_game_url(self) -> str:
        if self.game_url:
            return self.game_url
        players_button = poll_element(self.get_players_button)
        players_button.click()
        clip_input = poll_element(self.get_clip_input)
        self.game_url = clip_input.get_attribute("value")
        players_button.click()
        return self.game_url

    # Elements #

    def get_create_room_button(self) -> WebElement:
        return self.driver.find_element(by=By.CLASS_NAME, value="create-button")

    def get_start_new_game_button(self) -> WebElement:
        return self.driver.find_element(By.XPATH, value="//*[contains(text(),'Play with')]")

    def get_login_submit_button(self) -> WebElement:
        return self.driver.find_element(by=By.CSS_SELECTOR, value="button[type='submit']")

    def get_nickname_input(self) -> WebElement:
        return self.driver.find_element(by=By.ID, value="nickname-input")

    def get_team_window(self) -> WebElement:
        team_window_id = f"teamBoard-{self.player.team_color.value.lower()}"  # type: ignore
        return self.driver.find_element(by=By.ID, value=team_window_id)

    def get_join_button(self) -> WebElement:
        team_window = poll_element(self.get_team_window)
        role_name = "Spymaster" if self.player.role == PlayerRole.HINTER else "Operative"
        join_button_text = f"Join as {role_name}"
        return team_window.find_element(by=By.XPATH, value=f"//*[contains(text(),'{join_button_text}')]")

    def get_players_button(self) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value="//*[contains(text(),'Players')]")

    def get_clip_input(self) -> WebElement:
        return self.driver.find_element(by=By.ID, value="clip-input")

    # Polling #

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

    def transmit_hint(self, hint: Hint) -> "CodenamesGamePlayerAdapter":
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

    def transmit_guess(self, guess: Guess) -> "CodenamesGamePlayerAdapter":
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

    def has_clue_text(self, clue_area: Optional[ShadowRootElement] = None) -> bool:
        if not clue_area:
            clue_area = self.get_clue_area()
        return clue_area.find_elements(by=By.ID, value="clue-text") != []

    def close(self):
        try:
            self.driver.close()
        except:  # noqa  # pylint: disable=bare-except
            pass


def parse_card_color(codenames_game_color: str) -> CardColor:
    codenames_game_color = codenames_game_color.strip().upper()
    if codenames_game_color == "GREEN":
        codenames_game_color = "GRAY"
    return CardColor[codenames_game_color]
