"""
Workflow: HTTP webhook server
Layer: W — triggers screen_all_deals in a background thread

Usage:
  python server.py

Set WEBHOOK_SECRET, GOOGLE_SHEET_ID, and all other credentials in .env.
"""

import os
import threading
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

from workflows.screen_deals import screen_all_deals

app = Flask(__name__)

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")


@app.route("/run", methods=["POST"])
def run():
    if WEBHOOK_SECRET and request.headers.get("X-Webhook-Secret") != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    if not GOOGLE_SHEET_ID:
        return jsonify({"error": "GOOGLE_SHEET_ID not configured"}), 500

    thread = threading.Thread(target=screen_all_deals, args=(GOOGLE_SHEET_ID,), daemon=True)
    thread.start()

    return jsonify({"status": "Run started"}), 202


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
