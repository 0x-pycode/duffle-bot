# core/proxies.py

from pathlib import Path
from typing import Dict, Any

from .settings import PROXIES_FILE
from .utils import load_json
from .logger import get_logger

logger = get_logger(__name__)


def load_proxies(path: Path | None = None) -> Dict[str, Any]:
    path = path or PROXIES_FILE
    logger.debug(f"Loading proxies from {path}")
    return load_json(path)


def get_proxy_for_account(account_name: str, proxies: Dict[str, Any]):
    proxy = proxies.get(account_name)
    if proxy:
        logger.debug(f"Proxy found for {account_name}")
    else:
        logger.debug(f"No proxy for {account_name}")
    return proxy
