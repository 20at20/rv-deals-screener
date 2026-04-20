"""
Agent: Market Researcher
Layer: A (Agent) — AI reasoning, returns structured text

Uses Claude with web search to research market opportunity for a company.
Called once per deal, result passed to vc_screener as context.
"""

from tools.claude_client import load_prompt, run_agent, run_agent_with_web_search


def research_market(company_website: str) -> str:
    """
    Research market opportunity for a company.
    Returns a text summary (passed as context to the VC screener).
    """
    print(f"[market_researcher] Researching market for: {company_website}")
    system = load_prompt("market_research_system.md")
    user = f"Research market opportunity for this company: {company_website}"
    result = run_agent_with_web_search(system=system, user=user, max_tokens=1500)

    # Strip narration preamble — slicing is more reliable than prompt instructions.
    # Try the normal section header first; fall back to the skip message.
    for marker in ("## MARKET SIZE", "Market data cannot be reliably determined"):
        idx = result.find(marker)
        if idx > 0:
            result = result[idx:]
            break

    print(f"[market_researcher] Done ({len(result)} chars)")
    return result


def summarize_market(market_data: str) -> str:
    """
    Condense full market research into a 2–3 sentence summary for the screener.
    Returns empty string if market_data is empty.
    """
    if not market_data.strip():
        return ""
    print("[market_researcher] Summarizing market data for screener...")
    system = load_prompt("market_summary_system.md")
    summary = run_agent(system=system, user=market_data)
    print(f"[market_researcher] Summary: {summary[:100]}...")
    return summary
