from typing import List, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement


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
