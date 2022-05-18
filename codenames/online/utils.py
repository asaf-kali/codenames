import logging
import time
from time import sleep
from typing import Callable, List, Tuple, TypeVar

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement

log = logging.getLogger(__name__)
T = TypeVar("T")


class PollingTimeout(Exception):
    pass


# def poll_not_none(fn: Callable[[], T], timeout_seconds: float = 5, interval_sleep_seconds: float = 0.2) -> T:
#     start = time.time()
#     while True:
#         result = fn()
#         if result is not None:
#             return result
#         log.debug("Result was none, sleeping...")
#         now = time.time()
#         passed = now - start
#         if passed >= timeout_seconds:
#             raise PollingTimeout()
#         sleep(interval_sleep_seconds)


def poll_condition(test: Callable[[], bool], timeout_sec: float = 5, poll_interval_sec: float = 0.2):
    start = time.time()
    while not test():
        log.debug("Test not passed, sleeping...")
        now = time.time()
        passed = now - start
        if passed >= timeout_sec:
            raise PollingTimeout()
        sleep(poll_interval_sec)


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
