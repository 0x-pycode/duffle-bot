# core/tasks.py

import random
import time
import uuid
from typing import Dict

from .account import Account
from .duffle import authorize_account, complete_task
from .proxies import get_proxy_for_account
from .utils import pause
from .logger import get_logger

logger = get_logger(__name__)


def process_account(
    index: int,
    total_accounts: int,
    acc_name: str,
    emails_map: Dict[str, str],
    proxies: Dict[str, dict],
    ref_codes: list[str],
) -> None:
    """
    Main logic for single account:
    - resolve email
    - build Account model
    - authorize via Twitter / Privy / Duffle
    - output stats
    - complete tasks
    """
    # find email by account name
    email = next((email for email, name in emails_map.items() if name == acc_name), None)
    if not email:
        logger.warning(f"No email found for account: {acc_name}")
        return

    proxy_cfg = get_proxy_for_account(acc_name, proxies) or {}

    account = Account(
        acc_name=acc_name,
        email=email,
        privi_ca=str(uuid.uuid4()),
        twitter_username="",
        ref_code=random.choice(ref_codes),
        proxy=proxy_cfg,
    )

    logger.info(f"[{index}/{total_accounts}] Processing account: {account.acc_name}")

    session, user_info = authorize_account(account)
    if not session or not user_info:
        logger.error(f"Skipping account {acc_name} due to authorization error")
        return

    account.twitter_username = user_info["twitter_username"]

    pause()

    logger.info(f"ACCOUNT STATS for {account.acc_name}")
    logger.info(f"  Total points: {user_info['total_points']}")
    logger.info(f"  Amount referred: {user_info['amount_referred']}")
    logger.info(f"  Tasks: {user_info['task_statuses']}")

    task_names = ["follow-x", "join-discord", "follow-instagram", "join-telegram"]
    random.shuffle(task_names)

    for task in task_names:
        status = user_info["task_statuses"].get(task)
        if status is False:
            logger.info(f"Task '{task}' is not completed yet — claiming")
            complete_task(session, account, task)
            pause()

    delay = random.randint(30, 60)
    logger.info(f"Finished account {account.acc_name}, sleeping {delay} seconds")
    time.sleep(delay)
