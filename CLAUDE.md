# CLAUDE.md

## Project
This project is created to make a screening of the projects for early-stage VC firm. It will be used by analytical team. 

## Structure
- `tools/` — stateless API wrappers: Google Sheets, Apify, Claude client
- `agents/` — AI agents: market_researcher, team_researcher, vc_screener
- `workflows/` — main pipeline: screen_deals.py
- `agent_docs/prompts/` — versioned system prompt files (never inline prompts)

## How to run & verify
- Install: `pip install -r requirements.txt`
- Run: `python main.py`
- Credentials: copy `.env.template` → `.env` and fill in all values

## WAT Framework
All work follows three layers. Identify the layer before writing any code.

**W — Workflows**: deterministic pipelines, scheduled jobs, data sync, form handling.
No AI calls inside. Fail loudly. Log all runs.

**A — Agents**: AI reasoning, analysis, summarization, Q&A. One job per agent.
Always receive structured input. Always return structured output (JSON).
Prompts live in versioned files, never inline.

**T — Tools**: stateless reusable functions — DB helpers, API clients, formatters.
Build Tools first. If logic is written twice, make it a Tool.

**Build order: Tools → Workflows/Agents → UI. Never build UI before the data layer.**

## Working style
- Plan before coding on any non-trivial task. State the WAT layer and approach first.
- Ask if the requirement is ambiguous — do not assume.
- Never delete existing functionality to make something new work.
- Use env variables for secrets, never hardcode.
- When you make a mistake and get corrected, add a rule to `lessons.md`.

## Key docs
Read these when relevant — do not load all of them every session:
- `lessons.md` — read at the start of every session, rules learned from past mistakes
- `agent_docs/wat-framework.md` — full WAT rules and patterns
- `agent_docs/[other project-specific docs]`
