# Prompt Refinement Changelog

Each entry is a YAML block: date, case count, and per-file description of what changed and why.

---

- date: 2026-04-07 14:34 UTC
  cases: 7
  changes:
    screener_system.md:
      - "Added tone rule: do not speculate on market data for stealth companies"
      - "Tightened conviction definitions: High now requires 'all founders' LinkedIn data; Medium explicitly allows stealth/limited-market cases"
      - "Updated comment format: must explain conviction level with specific reasons, not just state it"
      - "Added end-of-prompt clarification: for stealth companies, note market opportunity cannot be assessed"
    market_research_system.md:
      - "Added stealth-mode guard at top: if company is in stealth, skip research and return standard fallback message"
    team_research_system.md:
      - "Added requirement to include company name, title, duration, and outcome/product shipped for each role"
      - "Tightened 'be concise' instruction to explicitly require per-role descriptions"

---

- date: 2026-04-11 15:08 UTC
  cases: 6
  changes:
    screener_system.md:
      - "Added rule: always provide conviction + multi-sentence comment even when data is limited"
    market_research_system.md:
      - "Extended stealth guard: also skip research if founder is transitioning between companies or startup details are ambiguous"
      - "Added final rule: only conduct market research when company status and market focus are clear and not in stealth mode"
    team_research_system.md:
      - "Added dedicated 'Founding/Early-Stage Experience' section requirement — critical for doer-status assessment"
      - "Added clarification: if founder transitioned to a new company, research only the prior company as execution evidence"

---

- date: 2026-04-11 16:02 UTC
  cases: 6
  changes:
    market_research_system.md:
      - "Consolidated stealth conditions into one unified check: stealth, unclear current startup, or ambiguous profile all trigger the same fallback"
    team_research_system.md:
      - "Added CRITICAL opening note: if founder recently transitioned, research only the previous company — do not treat current role as prior achievement"

---

- date: 2026-04-11 16:23 UTC
  cases: 7
  changes:
    screener_system.md:
      - "Revised comment format: removed 'key risk' from structure; conviction explanation is now always required with specific reasons"
      - "Tightened conviction definitions: High now requires 'clear execution history'; Medium requires strong team signal even without market data"
      - "MID tier expanded: added high-growth scaleups with demonstrated execution impact"
      - "WEAK tier expanded: added marketing-focused roles without product shipping or revenue generation"
      - "Disqualifier #1 clarified: US = USA only — HQ must be in the United States"
      - "IMPORTANT note expanded: stealth comment required; generic early-stage risks banned; blank fields banned; prior company exit uncertainty should reduce conviction, not count as a negative signal"
    market_research_system.md:
      - "Unified fallback message: merged two separate stealth/ambiguity messages into one standard response"
      - "Changed final rule to: when in doubt about stealth status, err on the side of caution and skip research"
    team_research_system.md:
      - "Added CRITICAL block at top about transitioning founders — mirrors screener rule"
      - "Added 'high-growth scaleups' to the C-level/VP experience focus list"
      - "Added requirement for specific descriptions of what was built, shipped, or accomplished in each role"
      - "Tightened 'be concise' instruction: marketing roles without product shipping must be explicitly marked as such"
      - "Added explicit STRUCTURE section with four ordered sections: Founding/Early-Stage, C-Level and VP, Product/Engineering Leadership, Domain Expertise"
2026-04-29 17:17 UTC | 13 cases | screener_system.md, market_research_system.md, team_research_system.md
