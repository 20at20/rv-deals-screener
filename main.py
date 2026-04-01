"""
Entry point for the RV Deals Screener.

Usage:
  python main.py

Set credentials in .env before running (copy from .env.template).
"""

import os
from dotenv import load_dotenv

load_dotenv()

from workflows.screen_deals import screen_all_deals


def main():
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sheet_id:
        raise EnvironmentError(
            "GOOGLE_SHEET_ID is not set. Copy .env.template to .env and fill in values."
        )

    screen_all_deals(sheet_id)


if __name__ == "__main__":
    main()
