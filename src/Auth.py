"""
auth.py

Handles authentication to a secure web portal using username/password
and manual OTP input. Saves authenticated session cookies for reuse
in downstream pipeline steps.
"""

import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PORTAL_URL = os.getenv("PORTAL_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

SESSION_FILE = "session.json"


def authenticate(headless: bool = False):
    """
    Authenticates the user and saves session cookies.

    Args:
        headless (bool): Run browser in headless mode or not.
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=100)
        context = browser.new_context( user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )   )
        page = context.new_page()

        print("Opening login page...")
        page.goto(PORTAL_URL,wait_until='domcontentloaded')

        print("\n🔐 Please log in manually in the opened browser.")
        print("✅ Complete username, password, and OTP.")
        print("✅ Once you reach the dashboard, return here.\n")

        input("👉 Press ENTER after login is fully completed...")

        # Optional verification
        print("Saving authenticated session...")
        context.storage_state(path=SESSION_FILE)

        print(f"✅ Session saved successfully to {SESSION_FILE}")
        browser.close()


if __name__ == "__main__":
    authenticate(headless=False)
