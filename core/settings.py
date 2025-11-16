# core/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

load_dotenv(BASE_DIR / ".env")

PAUSE_FROM = int(os.getenv("PAUSE_FROM", 10))
PAUSE_TO = int(os.getenv("PAUSE_TO", 15))

BASE_URL = os.getenv("BASE_URL", "https://duffle.money")

TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "duffleinc")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

EMAIL_FILE = DATA_DIR / "emails.json"
PROXIES_FILE = DATA_DIR / "proxies.json"
TWITTER_COOKIES_DIR = DATA_DIR / "twitter_cookies"
REF_FILE = DATA_DIR / "referral_codes.txt"

ACCOUNTS = [
    acc.strip()
    for acc in os.getenv("ACCOUNTS", "").split(",")
    if acc.strip()
]

REF_CODES = [
    code.strip()
    for code in os.getenv("REF_CODES", "default_code").split(",")
    if code.strip()
]
