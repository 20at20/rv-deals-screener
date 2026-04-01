"""
Agent: Market Researcher
Layer: A (Agent) — AI reasoning, returns structured text

Uses Claude with web search to research market opportunity for a company.
Called once per deal, result passed to vc_screener as context.
"""

from tools.claude_client import load_prompt, run_agent_with_web_search


def research_market(company_website: str) -> str:
    """
    Research market opportunity for a company.
    Returns a text summary (passed as context to the VC screener).
    """
    print(f"[market_researcher] Researching market for: {company_website}")
    system = load_prompt("market_research_system.md")
    user = f"Research market opportunity for this company: {company_website}"
    result = run_agent_with_web_search(system=system, user=user, max_tokens=500)
    print(f"[market_researcher] Done ({len(result)} chars)")
    return result
