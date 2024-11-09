import logging
import time
from time import sleep
from typing import Callable, TypeVar

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


def multi_click(element: WebElement, times: int = 3, warn: bool = False):
    for _ in range(times):
        try:
            element.click()
            log.debug("Element clicked")
            sleep(0.1)
        except Exception:  # pylint: disable=broad-except
            if warn:
                log.debug("Failed to click, trying again...")


def poll_elements(
    element_getters: list[Callable[[], T]],
    timeout_sec: float = 15,
    poll_interval_sec: float = 0.5,
) -> T:
    def safe_getter() -> T | None:
        for element_getter in element_getters:
            try:
                return element_getter()
            except Exception as e:  # pylint: disable=broad-except
                error_line = str(e).replace("\n", " ")
                log.debug(f"Element getter raised an error: {error_line}")
        return None

    start = time.time()
    while not (element := safe_getter()):
        log.debug("No element found, sleeping...")
        now = time.time()
        passed = now - start
        if passed >= timeout_sec:
            raise PollingTimeout(timeout_sec=timeout_sec, started=start, passed=passed)
        sleep(poll_interval_sec)
    log.debug("Element found")
    return element


def poll_condition(test: Callable[[], bool], timeout_sec: float = 5, poll_interval_sec: float = 0.2):
    poll_elements(element_getters=[test], timeout_sec=timeout_sec, poll_interval_sec=poll_interval_sec)
