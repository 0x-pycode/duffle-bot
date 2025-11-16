# main.py

import random

from core.settings import EMAIL_FILE, REF_CODES, ACCOUNTS
from core.utils import load_json
from core.proxies import load_proxies
from core.tasks import process_account
from core.logger import get_logger

logger = get_logger("main")


def main() -> None:
    logger.info("🚀 Starting Duffle Bot")

    proxies = load_proxies()
    emails_map = load_json(EMAIL_FILE)

    if ACCOUNTS:
        accounts = ACCOUNTS
        logger.info(f"Using accounts from .env: {accounts}")
    else:
        accounts = sorted(set(emails_map.values()))
        logger.info(f"Using all accounts from emails.json: {accounts}")

    random.shuffle(accounts)
    total_accounts = len(accounts)
    logger.info(f"Total accounts to process: {total_accounts}")

    for index, acc_name in enumerate(accounts, start=1):
        try:
            process_account(
                index=index,
                total_accounts=total_accounts,
                acc_name=acc_name,
                emails_map=emails_map,
                proxies=proxies,
                ref_codes=REF_CODES,
            )
        except Exception as e:
            logger.error(f"Account execution error for {acc_name}: {e}", exc_info=True)

    logger.info("✅ Duffle Bot finished")


if __name__ == "__main__":
    main()
