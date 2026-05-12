"""
Konfigurasi untuk Push FYP Threads Tool
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_accounts():
    """Parse akun dari environment variable"""
    accounts_str = os.getenv("ACCOUNTS", "")
    accounts = []
    for acc in accounts_str.split(","):
        acc = acc.strip()
        if ":" in acc:
            username, password = acc.split(":", 1)
            accounts.append({"username": username.strip(), "password": password.strip()})
    return accounts


def get_comments():
    """Parse komentar random dari environment variable"""
    comments_str = os.getenv("COMMENTS", "keren!|mantap|bagus sekali|nice!")
    return [c.strip() for c in comments_str.split("|") if c.strip()]


# Settings
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
DELAY_MIN = int(os.getenv("DELAY_MIN", "5"))
DELAY_MAX = int(os.getenv("DELAY_MAX", "15"))
ENABLE_LIKE = os.getenv("LIKE", "true").lower() == "true"
ENABLE_REPOST = os.getenv("REPOST", "true").lower() == "true"
ENABLE_COMMENT = os.getenv("COMMENT", "true").lower() == "true"

# Threads URLs
THREADS_BASE_URL = "https://www.threads.net"
THREADS_LOGIN_URL = "https://www.threads.net/login"
