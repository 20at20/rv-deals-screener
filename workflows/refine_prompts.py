"""
Workflow: Refine Prompts
Layer: W (Workflow) — deterministic pipeline, no AI branching logic

Collects analyst feedback from Google Sheet, passes it to the prompt refiner
agent, pushes updated prompts to GitHub, and marks feedback rows as implemented.

Git history on GitHub serves as the full change log — every refinement is a
commit, so any version can be restored via `git checkout <sha>`.
"""

import os
from datetime import datetime, timezone

import tools.github_client as github_client
import tools.sheets as sheets
from agents.prompt_refiner import refine_prompts
from tools.claude_client import load_prompt

SHEET_NAME = "Sheet1"
MIN_FEEDBACK_ROWS = 1

PROMPT_FILES = {
    "screener_system": "agent_docs/prompts/screener_system.md",
    "market_research_system": "agent_docs/prompts/market_research_system.md",
    "team_research_system": "agent_docs/prompts/team_research_system.md",
}


def run_refinement(sheet_id: str) -> None:
    print(f"[refine_prompts] Starting refinement run for sheet: {sheet_id}")

    # ── 1. Collect unprocessed feedback ──────────────────────────────────────
    feedback_rows = sheets.get_feedback_rows(sheet_id, sheet_name=SHEET_NAME)

    if len(feedback_rows) < MIN_FEEDBACK_ROWS:
        print(f"[refine_prompts] Not enough feedback yet ({len(feedback_rows)}/{MIN_FEEDBACK_ROWS} required). Stopping.")
        return

    # ── 2. Load current prompts ───────────────────────────────────────────────
    screener_prompt = load_prompt("screener_system.md")
    market_prompt = load_prompt("market_research_system.md")
    team_prompt = load_prompt("team_research_system.md")

    # ── 3. Build feedback cases ───────────────────────────────────────────────
    feedback_cases = [
        {
            "company": row.get("Company website") or row.get("Founder Linkedins") or "unknown",
            "ai_decision": row.get("Priority", ""),
            "analyst_decision": row.get("Analyst Decision", ""),
            "analyst_note": row.get("Analyst Note", ""),
        }
        for row in feedback_rows
    ]

    # ── 4. Refine prompts ─────────────────────────────────────────────────────
    revised = refine_prompts(
        feedback_cases=feedback_cases,
        screener_prompt=screener_prompt,
        market_prompt=market_prompt,
        team_prompt=team_prompt,
    )

    # ── 5. Push changed prompts to GitHub ─────────────────────────────────────
    prompt_map = {
        "screener_system": (screener_prompt, "screener_system.md"),
        "market_research_system": (market_prompt, "market_research_system.md"),
        "team_research_system": (team_prompt, "team_research_system.md"),
    }

    changed = []
    for key, (original, filename) in prompt_map.items():
        revised_text = revised[key]
        if revised_text.strip() != original.strip():
            github_client.update_file(
                path=PROMPT_FILES[key],
                content=revised_text,
                commit_message=f"Refine {filename} based on analyst feedback ({len(feedback_cases)} cases)",
            )
            changed.append(filename)
        else:
            print(f"[refine_prompts] No changes to {filename}")

    if not changed:
        print("[refine_prompts] No prompts were changed.")
    else:
        print(f"[refine_prompts] Updated: {', '.join(changed)}")

    # ── 6. Append to CHANGELOG.md ─────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    changed_str = ", ".join(changed) if changed else "no prompts changed"
    entry = f"{timestamp} | {len(feedback_cases)} cases | {changed_str}\n"
    current_log = github_client.read_file("CHANGELOG.md")
    github_client.update_file(
        path="CHANGELOG.md",
        content=current_log + entry,
        commit_message=f"Changelog: refinement run ({len(feedback_cases)} cases)",
    )

    # ── 7. Mark feedback rows as implemented ──────────────────────────────────
    for row in feedback_rows:
        match_col = "Company website" if row.get("Company website") else "Founder Linkedins"
        match_val = (row.get("Company website") or row.get("Founder Linkedins") or "").strip()
        if not match_val:
            continue
        sheets.update_row(
            sheet_id=sheet_id,
            sheet_name=SHEET_NAME,
            match_col=match_col,
            match_val=match_val,
            updates={"Analyst Implemented": "Yes"},
        )

    print(f"[refine_prompts] Done. {len(feedback_rows)} rows marked as implemented.")
