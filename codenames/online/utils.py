import logging
import time
from time import sleep
from typing import Callable, List, Optional, Tuple, TypeVar

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement

log = logging.getLogger(__name__)
T = TypeVar("T")
CLEAR = "\b\b\b\b\b"


class PollingTimeout(Exception):
    def __init__(self, timeout_sec: float, started: float, passed: float):
        self.timeout_sec = timeout_sec
        self.started = started
        self.passed = passed
        super().__init__(f"Polling timeout after {passed:.2f} seconds (timeout was {timeout_sec})")


def fill_input(element: WebElement, value: str):
    element.send_keys(CLEAR)
    element.send_keys(CLEAR)
    sleep(0.1)
    element.send_keys(value)
    sleep(0.1)


def multi_click(element: WebElement, times: int = 3):
    for _ in range(times):
        try:
            element.click()
            sleep(0.1)
        except Exception:  # pylint: disable=broad-except
            log.debug("Failed to click, trying again...")


def poll_element(element_getter: Callable[[], T], timeout_sec: float = 15, poll_interval_sec: float = 0.5) -> T:
    def safe_getter() -> Optional[T]:
        try:
            return element_getter()
        except Exception as e:  # pylint: disable=broad-except
            error_line = str(e).replace("\n", " ")
            log.debug(f"Element getter raised an error: {error_line}")
            return None

    start = time.time()
    while not (element := safe_getter()):
        log.debug("Element not found, sleeping...")
        now = time.time()
        passed = now - start
        if passed >= timeout_sec:
            raise PollingTimeout(timeout_sec=timeout_sec, started=start, passed=passed)
        sleep(poll_interval_sec)
    log.debug("Element found")
    return element


def poll_condition(test: Callable[[], bool], timeout_sec: float = 5, poll_interval_sec: float = 0.2):
    poll_element(test, timeout_sec=timeout_sec, poll_interval_sec=poll_interval_sec)


def _by_to_using(by: str, value: str) -> Tuple[str, str]:
    if by == By.ID:
        by = By.CSS_SELECTOR
        value = f'[id="{value}"]'
    elif by == By.TAG_NAME:
        by = By.CSS_SELECTOR
    elif by == By.CLASS_NAME:
        by = By.CSS_SELECTOR
        value = f".{value}"
    elif by == By.NAME:
        by = By.CSS_SELECTOR
        value = f'[name="{value}"]'
    return by, value


class ShadowRootElement:
    def __init__(self, shadow_root: ShadowRoot):
        self.shadow_root = shadow_root

    def find_element(self, by: str, value: str) -> WebElement:
        using, value = _by_to_using(by, value)
        return self.shadow_root.find_element(using=using, value=value)  # type: ignore

    def find_elements(self, by: str, value: str) -> List[WebElement]:
        using, value = _by_to_using(by, value)
        return self.shadow_root.find_elements(using=using, value=value)  # type: ignore
