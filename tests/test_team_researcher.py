"""
Test: Team Researcher agent
Usage: python tests/test_team_researcher.py

Calls research_team() with a sample company URL or LinkedIn URL and prints the raw output.
Edit TARGET below to test different companies or founders.
"""

from dotenv import load_dotenv
load_dotenv()

from agents.team_researcher import research_team

# Can be a company URL or a LinkedIn profile URL
TARGET = "https://tower.dev"

# ── Run ────────────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"TEAM RESEARCH: {TARGET}")
print(f"{'='*60}\n")

result = research_team(TARGET)

print(result)
print(f"\n[{len(result)} chars]")
