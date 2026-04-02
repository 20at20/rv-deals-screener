"""
Workflow: Screen Deals
Layer: W (Workflow) — deterministic pipeline, no AI branching logic

Input branching (per row):
  - Founder Linkedins present → enrich directly (skip founder-finder)
  - Company website only      → find founders via Apify, then enrich

Steps per company:
  1. Collect LinkedIn URLs (via Apify finder OR directly from sheet)
  2. Enrich LinkedIn profiles via Apify
  3. Run Claude web search for team ONLY if no LinkedIn data was found
  4. Use LinkedIn data as team_data (or web research if LinkedIn unavailable)
  5. Research market via Claude web search
  6. Score deal via VC screener agent
  7. Write results back to Google Sheet
"""

import os
import re
import time

import tools.apify as apify
import tools.sheets as sheets
from agents.market_researcher import research_market
from agents.team_researcher import research_team
from agents.vc_screener import score_deal

SHEET_NAME = "Sheet1"


def _parse_linkedin_urls(raw: str) -> list[str]:
    """Extract valid LinkedIn URLs from a comma-separated string."""
    urls = [
        re.sub(r"[\u200B-\u200D\uFEFF\u2060]", "", u).strip()
        for u in raw.split(",")
    ]
    return [u for u in urls if re.match(r"^https?://.+", u, re.IGNORECASE)]


def _format_team_profiles(profiles: list[dict]) -> str:
    """Format enriched LinkedIn profiles into a readable text block."""
    blocks = []
    for f in profiles:
        summary = (f.get("summary") or "").replace("\n", " ")[:150]

        exp_lines = []
        for e in (f.get("experiences") or [])[:5]:
            starts = e.get("starts_at") or ""
            ends = e.get("ends_at") or ""
            period = f"{starts}–{ends}" if ends else starts
            exp_lines.append(f"- {e.get('title')} at {e.get('company')} ({period})")

        edu_lines = [
            f"- {e.get('degree_name')}, {e.get('school')}"
            for e in (f.get("education") or [])[:2]
        ]

        block = (
            f"FOUNDER: {f.get('full_name')}\n"
            f"Location: {f.get('country')}\n"
            f"Followers: {f.get('follower_count')}\n\n"
            f"Profile Summary:\n{summary}\n\n"
            f"Top Experience:\n" + "\n".join(exp_lines) + "\n\n"
            f"Education:\n" + "\n".join(edu_lines)
        )
        blocks.append(block)

    return "\n\n----------------------\n\n".join(blocks)


def process_one_deal(sheet_id: str, row: dict) -> None:
    company_website = (row.get("Company website") or "").strip()
    founder_linkedin_raw = (row.get("Founder Linkedins") or "").strip()

    print(f"\n[workflow] Processing: {company_website or founder_linkedin_raw or '(empty row)'}")

    # ── 1. Collect LinkedIn URLs ──────────────────────────────────────────
    if founder_linkedin_raw:
        # LinkedIn URLs already provided — skip founder-finder, enrich directly
        linkedin_urls = _parse_linkedin_urls(founder_linkedin_raw)
        match_col, match_val = "Founder Linkedins", founder_linkedin_raw
    elif company_website:
        # Find founders by domain first
        founders_raw = apify.find_founders(company_website)
        linkedin_urls = [f["linkedin"] for f in founders_raw if f.get("linkedin")]
        match_col, match_val = "Company website", company_website
    else:
        raise ValueError("Row has neither Company website nor Founder Linkedins — skipping")

    # ── 2. Enrich LinkedIn profiles ───────────────────────────────────────
    profiles = apify.enrich_linkedin(linkedin_urls) if linkedin_urls else []
    linkedin_team_data = _format_team_profiles(profiles) if profiles else ""

    # If we came from the LinkedIn path, try to extract company_website from profile data
    if not company_website and profiles:
        company_website = (profiles[0].get("company_website") or "").strip()

    # ── 3. Run Claude web search only when no LinkedIn data available ─────
    if linkedin_team_data:
        team_data = linkedin_team_data
    else:
        web_team_data = research_team(company_website or founder_linkedin_raw)
        team_data = web_team_data

    # ── 4. Research market ────────────────────────────────────────────────
    market_data = research_market(company_website) if company_website else ""

    # ── 5. Score ─────────────────────────────────────────────────────────
    result = score_deal(team_data=team_data, market_data=market_data)

    # ── 6. Write back ─────────────────────────────────────────────────────
    conviction = result.get("conviction", "")
    comment = f"Conviction: {conviction}\n\n{result['comment']}" if conviction else result["comment"]

    sheets.update_row(
        sheet_id=sheet_id,
        sheet_name=SHEET_NAME,
        match_col=match_col,
        match_val=match_val,
        updates={
            "Priority": result["decision"],
            "Comments": comment,
            "Team data": team_data,
            "Market data": market_data,
            "Make analysis": "Done",
        },
    )
    print(f"[workflow] ✓ {company_website or founder_linkedin_raw} → Priority {result['decision']}")


def screen_all_deals(sheet_id: str) -> None:
    """
    Poll Google Sheet for pending rows and process each one.
    Each company is processed independently — one failure never stops the loop.
    """
    print(f"[workflow] Starting screen run for sheet: {sheet_id}")
    rows = sheets.get_pending_rows(sheet_id, sheet_name=SHEET_NAME)

    if not rows:
        print("[workflow] Nothing to process.")
        return

    errors = []
    for i, row in enumerate(rows):
        try:
            process_one_deal(sheet_id, row)
        except Exception as e:
            company = row.get("Company website") or row.get("Founder Linkedins") or "unknown"
            print(f"[workflow] ERROR processing '{company}': {e}")
            errors.append((company, str(e)))

        if i < len(rows) - 1:
            # Wait between companies to let Anthropic rate limit bucket refill (50K tokens/min free tier)
            print("[workflow] Waiting 5s before next company...")
            time.sleep(5)

    print(f"\n[workflow] Run complete. {len(rows) - len(errors)}/{len(rows)} succeeded.")
    if errors:
        print("[workflow] Failures:")
        for company, err in errors:
            print(f"  - {company}: {err}")
