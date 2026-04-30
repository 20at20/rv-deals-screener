"""
Agent: VC Screener
Layer: A (Agent) — AI reasoning, returns structured JSON

Takes formatted team data + market research text and produces a VC score.
Output: {"decision": 0|1|2|3, "comment": "..."}
"""

from datetime import date

from tools.claude_client import load_prompt, run_agent_json


def score_deal(team_data: str, market_data: str, additional_context: str = "") -> dict:
    """
    Score a startup deal based on team and market data.

    Returns:
        {"decision": int (0, 1, 2, or 3), "comment": str, "conviction": str, "short_description": str}
        - 0 = Disqualified (hard red flag confirmed with 100% certainty)
        - 1 = High Priority
        - 2 = Medium Priority
        - 3 = Low Priority / Pass
    """
    print("[vc_screener] Scoring deal...")
    system = load_prompt("screener_system.md")
    today = date.today().strftime("%Y-%m-%d")
    user = f"Today's date: {today}\n\nTEAM DATA:\n{team_data}\n\nMarket and company info:\n{market_data}"
    if additional_context:
        user += f"\n\nAdditional context from analyst:\n{additional_context}"

    result = run_agent_json(system=system, user=user)

    decision = result.get("decision")
    comment = result.get("comment", "")
    conviction = result.get("conviction", "")

    if decision not in (0, 1, 2, 3):
        raise ValueError(
            f"[vc_screener] Invalid decision value: {decision!r}. Expected 0, 1, 2, or 3."
        )

    print(f"[vc_screener] Decision: {decision} | Conviction: {conviction}")
    return {"decision": decision, "comment": comment, "conviction": conviction}
