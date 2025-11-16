# core/utils.py

import json
import random
import time
from pathlib import Path
from typing import Any

from .settings import PAUSE_FROM, PAUSE_TO
from .logger import get_logger

logger = get_logger(__name__)


def load_json(path: Path) -> Any:
    logger.debug(f"Loading JSON file: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pause():
    delay = random.randint(PAUSE_FROM, PAUSE_TO)
    logger.info(f"⏸ Pausing for {delay} seconds")
    time.sleep(delay)
