from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from enum import Enum
from time import sleep, time
from typing import Callable, List, Optional, Set, TypeVar

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from codenames.game.board import Board
from codenames.game.move import PASS_GUESS, Guess, Hint
from codenames.game.player import Player, PlayerRole
from codenames.game.state import GuesserGameState
from codenames.online.codenames_game.agent import Agent
from codenames.online.codenames_game.card_parser import _parse_card
from codenames.online.utils import PollingTimeout, fill_input, multi_click, poll_element
from codenames.utils.formatting import wrap

log = logging.getLogger(__name__)

T = TypeVar("T")
WEBAPP_URL = "https://codenames.game/"


class CodenamesGameLanguage(str, Enum):
    ENGLISH = "english"
    HEBREW = "hebrew"


class IllegalOperation(Exception):
    pass


@dataclass
class GameConfigs:
    language: CodenamesGameLanguage = CodenamesGameLanguage.ENGLISH


class CodenamesGamePlayerAdapter:
    def __init__(
        self,
        player: Player,
        implicitly_wait: int = 1,
        headless: bool = True,
        chromedriver_path: Optional[str] = None,
        game_url: Optional[str] = None,
    ):
        options = webdriver.ChromeOptions()
        if player.is_human or isinstance(player, Agent):
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

    def open(self) -> CodenamesGamePlayerAdapter:
        game_url = self.game_url or WEBAPP_URL
        log.info(f"{self.log_prefix} opening {game_url}")
        self.driver.get(game_url)
        return self

    def host_game(self, game_configs: Optional[GameConfigs] = None) -> CodenamesGamePlayerAdapter:
        log.info(f"{self.log_prefix} creating a room...")
        if game_configs is None:
            game_configs = GameConfigs()
        create_room_button = self.poll_element(self.get_create_room_button)
        multi_click(create_room_button)
        sleep(2)
        self.configure_language(language=game_configs.language)
        self.login()
        log.info("New game created")
        return self

    def configure_language(self, language: CodenamesGameLanguage):
        # TODO: Implement
        pass

    def login(self):
        log.info(f"{self.log_prefix} logging in...")
        # Enter nickname
        nickname_input = self.poll_element(self.get_nickname_input)
        fill_input(nickname_input, value=self.player.name)
        # Submit
        submit_button = self.get_login_submit_button()
        multi_click(submit_button)
        return self

    def choose_role(self) -> CodenamesGamePlayerAdapter:
        log.info(f"{self.log_prefix} picking role...")
        join_button = self.get_join_button()
        # suffix = f"{self.player.name.lower()}-{time()}"
        # self.screenshot(f"before-join-{suffix}")
        sleep(0.3)
        multi_click(join_button)
        sleep(0.2)
        # self.screenshot(f"after-join-{suffix}")
        return self

    def get_game_url(self) -> str:
        if self.game_url:
            return self.game_url
        players_button = self.poll_element(self.get_players_button)
        players_button.click()
        clip_input = self.poll_element(self.get_clip_input)
        self.game_url = clip_input.get_attribute("value")
        players_button.click()
        return self.game_url  # type: ignore

    def start_game(self):
        start_game_button = self.poll_element(self.get_start_game_button)
        multi_click(start_game_button)
        return self

    def parse_board(self, language: str) -> Board:
        log.debug("Parsing board...")
        card_containers = self.poll_element(self.get_card_containers)
        parse_results = [_parse_card(card) for card in card_containers]
        parse_results.sort(key=lambda result: result.index)
        cards = [result.card for result in parse_results]
        log.debug("Board parsed.")
        return Board(language=language, cards=cards)

    def transmit_hint(self, hint: Hint) -> CodenamesGamePlayerAdapter:
        log.debug(f"Sending hint: {hint}")
        # Clue value
        clue_input = self.poll_element(self.get_clue_input)
        fill_input(clue_input, hint.word)
        sleep(0.5)
        # Number
        number_selector = self.poll_element(self.get_number_wrapper)
        number_selector.click()
        sleep(1)
        number_to_select = self.poll_element(lambda: self.get_number_option(number_selector, hint.card_amount))
        number_to_select.click()
        sleep(0.5)
        # Submit
        submit_button = self.poll_element(self.get_give_clue_button)
        submit_button.click()
        sleep(3)
        return self

    def transmit_guess(self, guess: Guess) -> CodenamesGamePlayerAdapter:
        log.debug(f"Sending guess: {guess}")
        if guess.card_index == PASS_GUESS:
            end_guessing_button = self.poll_element(self.get_end_guessing_button)
            multi_click(end_guessing_button, times=10)
        else:
            picker = self.poll_element(lambda: self.get_card_picker(guess.card_index))
            multi_click(picker, times=10)
        sleep(2)
        return self

    def close(self):
        try:
            self.driver.close()
        except:  # noqa  # pylint: disable=bare-except
            pass

    # Elements #

    def get_create_room_button(self) -> WebElement:
        return self.driver.find_element(by=By.CLASS_NAME, value="create-button")

    def get_start_game_button(self) -> WebElement:
        return self.driver.find_element(By.XPATH, value="//button[contains(text(),'Play with')]")

    def get_login_submit_button(self) -> WebElement:
        return self.driver.find_element(by=By.CSS_SELECTOR, value="button[type='submit']")

    def get_nickname_input(self) -> WebElement:
        return self.driver.find_element(by=By.ID, value="nickname-input")

    def get_team_window(self) -> WebElement:
        team_window_id = f"teamBoard-{self.player.team_color.value.lower()}"  # type: ignore
        return self.driver.find_element(by=By.ID, value=team_window_id)

    def get_join_button(self) -> WebElement:
        team_window = self.poll_element(self.get_team_window)
        role_name = "Spymaster" if self.player.role == PlayerRole.HINTER else "Operative"
        join_button_text = f"Join as {role_name}"
        return team_window.find_element(by=By.XPATH, value=f".//*[contains(text(),'{join_button_text}')]")

    def get_players_button(self) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value="//*[contains(text(),'Players')]")

    def get_clip_input(self) -> WebElement:
        return self.driver.find_element(by=By.ID, value="clip-input")

    def get_card_containers(self) -> List[WebElement]:
        card_elements = self.driver.find_elements(by=By.CLASS_NAME, value="card")
        card_elements = [element for element in card_elements if element.text != ""]
        if len(card_elements) < 25:
            raise ValueError(f"Expected 25 cards, loaded {len(card_elements)}")
        return self.driver.find_elements(By.XPATH, value="//div[@role='img']")

    def get_clue_input(self) -> WebElement:
        return self.driver.find_element(By.CSS_SELECTOR, value="input[name='clue']")

    def get_number_wrapper(self) -> WebElement:
        return self.driver.find_element(By.CLASS_NAME, value="numSelect-wrapper")

    def get_number_option(self, container: WebElement, number: int) -> WebElement:
        number_css_selector = f".//div[contains(text(),'{number}')]"
        return container.find_element(By.XPATH, value=number_css_selector)

    def get_give_clue_button(self) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value="//button[contains(text(),'Give Clue')]")

    def get_card_picker(self, card_index: int) -> WebElement:
        picker_xpath = f"//button[@tabindex='{card_index}']"
        return self.driver.find_element(By.XPATH, value=picker_xpath)

    def get_end_guessing_button(self) -> WebElement:
        end_guessing_xpath = "//button[contains(text(),'End Guessing')]"
        return self.driver.find_element(by=By.XPATH, value=end_guessing_xpath)

    def get_clue_text(self) -> WebElement:
        xpath = "/html/body/div/div/div/div/div[3]/div/main/div[2]/main/div/article/p[1]"
        return self.driver.find_element(by=By.XPATH, value=xpath)

    def get_cards_text(self) -> WebElement:
        xpath = "/html/body/div/div/div/div/div[3]/div/main/div[2]/main/div/article/p[2]"
        return self.driver.find_element(by=By.XPATH, value=xpath)

    # Other #

    def poll_element(
        self,
        element_getter: Callable[[], T],
        timeout_sec: float = 15,
        poll_interval_sec: float = 0.5,
        screenshot: bool = True,
    ) -> T:
        log.debug(f"Polling [{element_getter.__name__}]...")
        try:
            return poll_element(element_getter, timeout_sec=timeout_sec, poll_interval_sec=poll_interval_sec)
        except Exception as e:
            if screenshot:
                file_name = self.screenshot(f"failed-polling-{time()}")
                log.info(f"Failed polling, screenshot saved to {file_name}")
            raise e

    def screenshot(self, file_name: str):
        os.makedirs("./debug", exist_ok=True)
        path = os.path.abspath(f"./debug/{file_name}.png")
        self.driver.save_screenshot(path)
        return path

    def poll_hint_given(self) -> Hint:
        log.debug("Polling for hint given...")
        clue_text = self.poll_element(self.get_clue_text, timeout_sec=180, poll_interval_sec=2)
        cards_text = self.poll_element(self.get_cards_text)
        return Hint(word=clue_text.text.strip(), card_amount=int(cards_text.text[0]))

    def detect_visibility_change(self, revealed_card_indexes: Set[int]) -> Optional[int]:
        log.debug("Looking for visibility change...")
        board = self.parse_board(language="")
        for i, card in enumerate(board.cards):
            if card.revealed and i not in revealed_card_indexes:
                log.debug(f"Found a visibility change at index {wrap(i)}")
                return i
        log.debug("No visibility change found")
        return None

    def has_clue_text(self) -> bool:
        try:
            self.poll_element(self.get_clue_text, screenshot=False, timeout_sec=2)
            return True
        except PollingTimeout:
            return False

    def poll_guess_given(self, game_state: GuesserGameState) -> Guess:
        log.debug("Polling for guess given...")
        revealed_card_indexes = set(game_state.board.revealed_card_indexes)
        should_return = False
        while not should_return:
            if not self.has_clue_text():
                log.debug("No clue text found, detecting changes last time...")
                should_return = True
            card_index = self.detect_visibility_change(revealed_card_indexes)
            if card_index is not None:
                return Guess(card_index=card_index)
            sleep(1)
        log.debug("Returning pass guess.")
        return Guess(card_index=PASS_GUESS)
