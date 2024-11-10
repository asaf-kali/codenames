import logging
import os
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codenames.online.codenames_game.adapter import CodenamesGamePlayerAdapter

log = logging.getLogger(__name__)


BAD_PATH_CHARS = {"\\", "/", ":", "*", "?", '"', "<", ">", "|", "\r", "\n"}
RUN_ID = 0
SCREENSHOT_COUNT = 0


def save_screenshot(adapter: "CodenamesGamePlayerAdapter", tag: str, raise_on_error: bool = False) -> str | None:
    try:
        global SCREENSHOT_COUNT  # pylint: disable=global-statement
        SCREENSHOT_COUNT += 1
        run_dir = _run_dir()
        file_name = sanitize_for_path(f"{SCREENSHOT_COUNT:03d} {adapter.player} - {tag}.png")
        path = os.path.join(run_dir, file_name)
        path_abs = os.path.abspath(path)
        adapter.driver.save_screenshot(path_abs)
    except Exception as e:  # pylint: disable=broad-except
        if raise_on_error:
            raise e
        log.warning(f"Failed to save screenshot: {e}")
        return None
    log.info(f"{adapter.log_prefix} Screenshot saved to {path_abs}")
    return path_abs


def sanitize_for_path(string: str) -> str:
    string = string.lower()
    for char in BAD_PATH_CHARS:
        string = string.replace(char, "")
    return string


def _run_dir():
    run_directory = os.path.join(".", "debug", str(RUN_ID))
    os.makedirs(run_directory, exist_ok=True)
    return run_directory


def reset_screenshot_run():
    global RUN_ID  # pylint: disable=global-statement
    RUN_ID = 10**10 - int(time.time())
    log.info(f"Run reset, new ID: {RUN_ID}")
    return RUN_ID


reset_screenshot_run()
