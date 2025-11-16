# core/duffle.py

import random
import time
from typing import Any, Dict, Optional

import requests

from .account import Account
from .settings import BASE_URL, REF_FILE
from .twitter import connect_to_site
from .utils import pause
from .logger import get_logger

logger = get_logger(__name__)


def save_referral_code(code: str) -> None:
    REF_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REF_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{code}\n")
    logger.info(f"Saved referral code: {code}")


def build_headers(ref_code: str) -> Dict[str, str]:
    return {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": BASE_URL,
        "priority": "u=1, i",
        "referer": f"{BASE_URL}/?ref_id={ref_code}",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
    }


def member(session: requests.Session, account: Account) -> Optional[Dict[str, Any]]:
    headers = build_headers(account.ref_code)
    json_data = {"email": account.email}

    try:
        logger.debug(f"Sending member request for {account.email}")
        r = session.post(f"{BASE_URL}/api/waitlist/member", headers=headers, json=json_data)
        if r.status_code == 200:
            logger.info("Member request successful")
            return r.json()
        logger.warning(f"Member request failed: {r.status_code} - {r.text}")
        return None
    except Exception as e:
        logger.error(f"Member request error: {e}")
        return None


def authenticate_privy(
    session: requests.Session,
    account: Account,
    code_verifier: str,
    state_code: str,
    auth_code: str,
) -> Optional[Dict[str, Any]]:
    headers = {
        "accept": "application/json",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": BASE_URL,
        "priority": "u=1, i",
        "privy-app-id": "cma8nnukg004bkw0m9xw5m4h8",
        "privy-ca-id": account.privi_ca,
        "privy-client": "react-auth:3.0.1",
        "referer": f"{BASE_URL}/",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-storage-access": "active",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
    }

    json_data = {
        "authorization_code": auth_code,
        "state_code": state_code,
        "code_verifier": code_verifier,
        "mode": "login-or-sign-up",
    }

    try:
        logger.debug("Authenticating via Privy")
        r = session.post("https://auth.privy.io/api/v1/oauth/authenticate", headers=headers, json=json_data)
        r.raise_for_status()
        logger.info("Privy authentication successful")
        return r.json()
    except Exception as e:
        logger.error(f"Authenticate error: {e}")
        return None


def sign_up(session: requests.Session, account: Account, auth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    headers = build_headers(account.ref_code)

    twitter_username = auth_data["user"]["linked_accounts"][0]["username"]
    json_data = {
        "email": account.email,
        "metadata": {
            "twitter_handle": twitter_username,
            "privy_user_id": auth_data["user"]["id"],
            "avatar_url": auth_data["user"]["linked_accounts"][0]["profile_picture_url"],
        },
        "referralLink": f"{BASE_URL}/?ref_id={account.ref_code}",
    }

    try:
        logger.debug(f"Signing up {account.email} to Duffle")
        r = session.post(f"{BASE_URL}/api/waitlist/signup", headers=headers, json=json_data)
        if r.status_code == 200:
            data = r.json()
            user_info = {
                "amount_referred": data["amount_referred"],
                "ref_code": data["referral_token"],
                "total_points": data["total_points"],
                "task_statuses": data["task_statuses"],
                "twitter_username": twitter_username,
            }
            logger.info(
                f"Sign up successful: points={user_info['total_points']}, "
                f"referred={user_info['amount_referred']}"
            )
            save_referral_code(data["referral_token"])
            return user_info

        logger.error(f"SignUp error: {r.status_code} - {r.text}")
        return None
    except Exception as e:
        logger.error(f"SignUp exception: {e}")
        return None


def twitter_follow_check(session: requests.Session, account: Account) -> None:
    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": BASE_URL,
        "priority": "u=1, i",
        "referer": f"{BASE_URL}/",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
    }

    json_data = {"twitterHandle": account.twitter_username}

    try:
        logger.debug(f"Checking follow status for @{account.twitter_username}")
        r = session.post(f"{BASE_URL}/api/social/check-follow", headers=headers, json=json_data)
        if r.status_code == 200:
            follow_status = r.json().get("following")
            if follow_status:
                logger.info(f"Follow task confirmed for @{account.twitter_username}")
            else:
                logger.warning(f"Follow task not confirmed: {r.text}")
        else:
            logger.error(f"Follow check failed: {r.status_code} - {r.text}")
    except Exception as e:
        logger.error(f"Follow check error: {e}")


def complete_task(session: requests.Session, account: Account, task_name: str):
    """
    Complete a Duffle social task.
    If task_name == "follow-x" — follow on Twitter + verify.
    """
    from .twitter import authorize  # local import to avoid circular

    logger.info(f"Completing task '{task_name}' for {account.email}")

    if task_name == "follow-x":
        import asyncio

        logger.debug("Executing Twitter follow flow before claiming task")
        asyncio.run(authorize(account, twitter_follow=True))
        time.sleep(random.randint(5, 10))
        twitter_follow_check(session, account)
        time.sleep(random.randint(5, 10))

    headers = {
        "accept": "*/*",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/json",
        "origin": BASE_URL,
        "priority": "u=1, i",
        "referer": f"{BASE_URL}/",
        "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/141.0.0.0 Safari/537.36"
        ),
    }

    json_data = {
        "email": account.email,
        "taskId": task_name,
    }

    try:
        r = session.post(f"{BASE_URL}/api/waitlist/tasks/complete", headers=headers, json=json_data)
        if r.status_code == 200:
            data = r.json()
            logger.info(
                f"Task '{task_name}' completed. Total points: {data['total_points']}"
            )
            return data["task_statuses"]
        else:
            logger.warning(
                f"Task '{task_name}' not completed: {r.status_code} - {r.text}"
            )
            return None
    except Exception as e:
        logger.error(f"Claim task '{task_name}' failed: {e}")
        return None


def authorize_account(account: Account) -> tuple[Optional[requests.Session], Optional[Dict[str, Any]]]:
    """
    High-level authorization:
    - Twitter login
    - Privy OAuth
    - Duffle signup
    Returns (session, user_info) or (None, None).
    """
    logger.info(f"Starting full authorization flow for {account.acc_name}")
    try:
        session = requests.Session()

        proxy_cfg = account.get_proxy_dict()
        if proxy_cfg:
            logger.debug(f"Using proxy for HTTP session: {proxy_cfg}")
            session.proxies.update(proxy_cfg)

        connect_result = connect_to_site(session, account)
        if not connect_result:
            logger.error("Authorization failed: unable to connect to site")
            return None, None

        code_verifier, state_code, auth_code = connect_result
        time.sleep(random.randint(3, 7))
        auth_data = authenticate_privy(session, account, code_verifier, state_code, auth_code)
        if not auth_data:
            logger.error("Authorization failed: Privy auth_data is None")
            return None, None

        time.sleep(random.randint(3, 7))
        _ = member(session, account)
        time.sleep(random.randint(3, 7))
        user_info = sign_up(session, account, auth_data)

        if user_info:
            logger.info(
                f"Authorization completed for {account.acc_name}, "
                f"points={user_info['total_points']}, "
                f"referred={user_info['amount_referred']}"
            )
            return session, user_info

        logger.error("Authorization failed: user_info is None after sign_up")
        return None, None
    except Exception as e:
        logger.error(f"Authorization failed with exception: {e}")
        return None, None
