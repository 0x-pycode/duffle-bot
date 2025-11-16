# core/twitter.py

import asyncio
import base64
import hashlib
import json
import os
import secrets
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, unquote

import httpx
from twikit import Client

from .account import Account
from .settings import (
    BASE_URL,
    TWITTER_USERNAME,
    TWITTER_COOKIES_DIR,
    TWITTER_BEARER_TOKEN,
    DATA_DIR,
)
from .logger import get_logger

logger = get_logger(__name__)

INIT_URL = "https://auth.privy.io/api/v1/oauth/init"


def clean(value: str) -> str:
    return value.strip().encode("latin-1", "ignore").decode("latin-1")


def generate_pkce_pair() -> tuple[str, str]:
    logger.debug("Generating PKCE verifier + challenge")
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode("utf-8")
    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        )
        .rstrip(b"=")
        .decode("utf-8")
    )
    return code_verifier, code_challenge


def extract_oauth_params(url: str) -> Dict[str, str]:
    logger.debug(f"Extracting OAuth params from URL: {url}")
    try:
        query = urlparse(url).query
        params = {k: unquote(v[0]) for k, v in parse_qs(query).items()}
        if not params:
            logger.error("No OAuth parameters found in URL")
            return {}
        return params
    except Exception as e:
        logger.error(f"Failed to extract OAuth parameters: {e}")
        return {}


def cookie_header(cookies: Dict[str, str]) -> str:
    return "; ".join(f"{k}={v}" for k, v in cookies.items() if v)


def transform_cookies(account: Account, output_path: Optional[Path] = None) -> Path:
    """
    Reads browser-exported cookies from data/twitter_cookies/<acc_name>.json
    and transforms them to simple {name: value} format for twikit.
    """
    output_path = output_path or (DATA_DIR / "cookies_clean.json")
    source_path = TWITTER_COOKIES_DIR / f"{account.acc_name}.json"

    logger.info(f"Loading raw Twitter cookies from: {source_path}")

    with source_path.open("r", encoding="utf-8") as f:
        raw_cookies = json.load(f)

    cookies = {cookie["name"]: cookie["value"] for cookie in raw_cookies}

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

    logger.debug("Transformed cookies saved to cookies_clean.json")
    return output_path


async def authorize(account: Account, twitter_follow: bool = False) -> Dict[str, str]:
    """
    Login to Twitter using twikit and saved cookies.
    Optionally follow the project Twitter account.
    Returns cookies dict for Twitter API requests.
    """
    logger.info(f"Authorizing Twitter for account: {account.acc_name}")
    try:
        proxy_cfg = account.get_proxy_dict()
        proxy_url = proxy_cfg.get("http") if proxy_cfg else None

        if proxy_url:
            logger.debug(f"Using proxy for Twitter: {proxy_url}")
        else:
            logger.debug("No proxy configured for Twitter")

        transport = httpx.AsyncHTTPTransport(proxy=proxy_url)
        http_client = httpx.AsyncClient(transport=transport)

        client = Client("en-US")
        client.http = http_client

        cookies_path = transform_cookies(account)
        client.load_cookies(str(cookies_path))

        http_client = client.http
        cookies_jar = http_client.cookies
        cookies = {cookie.name: cookie.value for cookie in cookies_jar.jar}

        try:
            twid = client.http.cookies.get("twid")
            if twid:
                twid_decoded = unquote(twid)
                user_id = twid_decoded.split("=")[1]
                user_me = await client.get_user_by_id(user_id)
                logger.info(
                    f"Successful Twitter login as {user_me.name} (@{user_me.screen_name})"
                )
            else:
                logger.info("Successful Twitter login (no twid user info)")
        except Exception as e:
            logger.warning(f"Twitter user info check failed, but login likely OK: {e}")

        if twitter_follow:
            try:
                logger.info(f"Trying to follow @{TWITTER_USERNAME}")
                project_twitter = await client.get_user_by_screen_name(TWITTER_USERNAME)
                await project_twitter.follow()
                logger.info("Follow successful")
            except Exception as e:
                logger.error(f"Follow failed: {e}")

        return cookies

    except Exception as e:
        logger.error(f"Unable to log in to Twitter: {e}")
        return {}


def connect_to_site(session, account: Account) -> Optional[tuple[str, str, str]]:
    """
    Flow:
    - log into Twitter (twikit) and get cookies
    - init OAuth in Privy
    - confirm authorization through Twitter API
    - obtain privy_oauth_code from redirect
    """
    logger.info(f"Connecting to Privy for account: {account.acc_name}")

    if not TWITTER_BEARER_TOKEN:
        logger.error("TWITTER_BEARER_TOKEN is not set in .env")
        return None

    try:
        # 1) Twitter cookies
        twitter_cookies = asyncio.run(authorize(account))
        if not twitter_cookies:
            logger.error("Unable to retrieve Twitter cookies")
            return None

        # Headers for Privy init
        project_headers = {
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

        # 2) PKCE + state
        code_verifier, code_challenge = generate_pkce_pair()
        state_code = secrets.token_urlsafe(32)

        payload = {
            "provider": "twitter",
            "redirect_to": f"{BASE_URL}/?ref_id={account.ref_code}",
            "code_challenge": code_challenge,
            "state_code": state_code,
        }

        # 3) Init OAuth in Privy
        logger.debug("Initializing OAuth in Privy")
        res = session.post(INIT_URL, json=payload, headers=project_headers)
        res.raise_for_status()
        r_url = res.json()["url"]

        params = extract_oauth_params(r_url)
        if not params:
            logger.error("Invalid OAuth redirect URL from Privy")
            return None

        # 4) Get auth_code via Twitter API
        twitter_headers = {
            "Authorization": clean(f"Bearer {TWITTER_BEARER_TOKEN}"),
            "cookie": cookie_header(
                {
                    "guest_id": twitter_cookies.get("guest_id"),
                    "auth_token": twitter_cookies.get("auth_token"),
                    "ct0": twitter_cookies.get("ct0"),
                    "twid": twitter_cookies.get("twid"),
                }
            ),
            "x-csrf-token": clean(twitter_cookies.get("ct0", "")),
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/141.0.0.0 Safari/537.36"
            ),
        }

        authorize_url = (
            "https://x.com/i/api/2/oauth2/authorize?"
            f"client_id={params['client_id']}&code_challenge={params['code_challenge']}"
            f"&code_challenge_method={params['code_challenge_method']}"
            f"&redirect_uri={params['redirect_uri']}"
            f"&response_type=code&scope=tweet.read%20users.read&state={params['state']}"
        )

        logger.debug("Requesting auth_code from Twitter API")
        r = session.get(authorize_url, headers=twitter_headers)
        auth_code = r.json().get("auth_code")
        if not auth_code:
            logger.error("Failed to get auth_code from Twitter")
            return None

        # 5) Confirm authorization and get redirect
        response = session.post(
            "https://x.com/i/api/2/oauth2/authorize",
            headers=twitter_headers,
            data={"approval": "true", "code": auth_code},
        )
        redirect_url = response.json()["redirect_uri"]
        logger.debug(f"Twitter redirect URL: {redirect_url}")

        r = session.get(redirect_url, headers=project_headers, allow_redirects=False)
        qs = parse_qs(urlparse(r.text).query)
        privy_auth_code = unquote(qs.get("privy_oauth_code", [""])[0])

        logger.info("Successfully obtained privy_oauth_code")
        return code_verifier, params["state"], privy_auth_code

    except Exception as e:
        logger.error(f"Error in connect_to_site: {e}")
        return None
