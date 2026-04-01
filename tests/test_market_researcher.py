"""
Test: Market Researcher agent
Usage: python tests/test_market_researcher.py

Calls research_market() with a sample company URL and prints the raw output.
Edit COMPANY_URL below to test different companies.
"""

from dotenv import load_dotenv
load_dotenv()

from agents.market_researcher import research_market

COMPANY_URL = "https://tower.dev"

# ── Run ────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"MARKET RESEARCH: {COMPANY_URL}")
print(f"{'='*60}\n")

result = research_market(COMPANY_URL)

print(result)
print(f"\n[{len(result)} chars]")
