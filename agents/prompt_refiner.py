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
    Revise the 3 system prompts based on analyst feedback.

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

    user = f"""CURRENT PROMPTS:

--- screener_system.md ---
{screener_prompt}

--- market_research_system.md ---
{market_prompt}

--- team_research_system.md ---
{team_prompt}

---

FEEDBACK CASES:
{json.dumps(feedback_cases, indent=2, ensure_ascii=False)}
"""

    result = run_agent_json(system=system, user=user)

    for key in ("screener_system", "market_research_system", "team_research_system"):
        if key not in result:
            raise ValueError(f"[prompt_refiner] Missing key in response: '{key}'")

    print("[prompt_refiner] Done.")
    return result
