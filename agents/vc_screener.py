"""
Agent: VC Screener
Layer: A (Agent) — AI reasoning, returns structured JSON

Takes formatted team data + market research text and produces a VC score.
Output: {"decision": 1|2|3, "comment": "..."}
"""

from tools.claude_client import load_prompt, run_agent_json


def score_deal(team_data: str, market_data: str) -> dict:
    """
    Score a startup deal based on team and market data.

    Returns:
        {"decision": int (1, 2, or 3), "comment": str}
        - 1 = High Priority
        - 2 = Medium Priority
        - 3 = Low Priority / Pass
    """
    print("[vc_screener] Scoring deal...")
    system = load_prompt("screener_system.md")
    user = f"TEAM DATA:\n{team_data}\n\nMarket and company info:\n{market_data}"

    result = run_agent_json(system=system, user=user)

    decision = result.get("decision")
    comment = result.get("comment", "")
    conviction = result.get("conviction", "")

    if decision not in (1, 2, 3):
        raise ValueError(
            f"[vc_screener] Invalid decision value: {decision!r}. Expected 1, 2, or 3."
        )

    print(f"[vc_screener] Decision: {decision} | Conviction: {conviction}")
    return {"decision": decision, "comment": comment, "conviction": conviction}
