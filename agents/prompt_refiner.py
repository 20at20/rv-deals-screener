"""
Agent: Prompt Refiner
Layer: A (Agent) — AI reasoning, returns structured JSON

Receives analyst feedback cases + current prompts.
Returns revised versions of all 3 prompts (unchanged if no relevant feedback).
"""

import json

from tools.claude_client import load_prompt, run_agent_json


def refine_prompts(
    feedback_cases: list[dict],
    screener_prompt: str,
    market_prompt: str,
    team_prompt: str,
) -> dict:
    """
    Revise the 3 system prompts based on analyst feedback, processing one case at a time.

    Args:
        feedback_cases: list of {company, ai_decision, analyst_decision, analyst_note}
        screener_prompt: current text of screener_system.md
        market_prompt: current text of market_research_system.md
        team_prompt: current text of team_research_system.md

    Returns:
        {"screener_system": str, "market_research_system": str, "team_research_system": str}
    """
    print(f"[prompt_refiner] Refining prompts based on {len(feedback_cases)} feedback cases...")
    system = load_prompt("prompt_refiner_system.md")

    current = {
        "screener_system": screener_prompt,
        "market_research_system": market_prompt,
        "team_research_system": team_prompt,
    }

    for i, case in enumerate(feedback_cases):
        company = case.get("company", "unknown")
        print(f"[prompt_refiner] Case {i + 1}/{len(feedback_cases)}: {company}")

        user = f"""CURRENT PROMPTS:

--- screener_system.md ---
{current["screener_system"]}

--- market_research_system.md ---
{current["market_research_system"]}

--- team_research_system.md ---
{current["team_research_system"]}

---

FEEDBACK CASE:
{json.dumps(case, indent=2, ensure_ascii=False)}
"""

        result = run_agent_json(system=system, user=user, max_tokens=8192)

        for key in ("screener_system", "market_research_system", "team_research_system"):
            if key not in result:
                raise ValueError(f"[prompt_refiner] Missing key '{key}' in response for case {i + 1}")

        current = result

    print("[prompt_refiner] Done.")
    return current
