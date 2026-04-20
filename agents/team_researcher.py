"""
Agent: Team Researcher (fallback)
Layer: A (Agent) — AI reasoning, returns structured text

Used ONLY when Apify returns no LinkedIn data.
Uses Claude with web search to find founding team background.
"""

from tools.claude_client import load_prompt, run_agent_with_web_search


def research_team(company_website: str) -> str:
    """
    Research the founding team for a company using web search.
    Returns a text summary (passed as context to the VC screener).
    """
    print(f"[team_researcher] Researching team for: {company_website}")
    system = load_prompt("team_research_system.md")
    user = f"Research founding team for this company: {company_website}"
    result = run_agent_with_web_search(system=system, user=user)

    marker = "## TEAM RESEARCH"
    idx = result.find(marker)
    if idx > 0:
        result = result[idx:]

    print(f"[team_researcher] Done ({len(result)} chars)")
    return result
