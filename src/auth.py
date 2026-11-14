"""
auth.py

Opens the secure portal in a visible browser so the user can log in
manually (username, password and OTP), then saves the authenticated
session for reuse by downloader.py.

No credentials are stored in code: the user types them in the browser.
"""

import os
import sys

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables from .env
load_dotenv()

PORTAL_URL = os.getenv("PORTAL_URL")
SESSION_FILE = "session.json"


def authenticate(headless: bool = False):
    """
    Opens the login page, waits for the user to finish logging in,
    and saves the session cookies to SESSION_FILE.

    Args:
        headless (bool): Run the browser without a window. Must be False
            for manual login, because the user needs to see the page.
    """
    if not PORTAL_URL:
        print("❌ PORTAL_URL is not set. Add it to your .env file.", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=100)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        print("Opening login page...")
        page.goto(PORTAL_URL, wait_until="domcontentloaded")

        print("\n🔐 Please log in manually in the opened browser.")
        print("✅ Complete username, password, and OTP.")
        print("✅ Once you reach the dashboard, return here.\n")

        input("👉 Press ENTER after login is fully completed...")

        print("Saving authenticated session...")
        context.storage_state(path=SESSION_FILE)

        print(f"✅ Session saved successfully to {SESSION_FILE}")
        browser.close()


if __name__ == "__main__":
    authenticate(headless=False)
