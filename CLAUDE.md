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
- Run pipeline directly: `python main.py`
- Run webhook server locally: `python server.py`
- Credentials: copy `.env.template` → `.env` and fill in all values

## Webhook server (server.py)
Flask server that exposes `POST /run` — used by the Google Sheets button to trigger the pipeline remotely.
- Deployed on Railway at `web-production-5dcdc.up.railway.app`
- GitHub repo: `github.com/20at20/rv-deals-screener` — Railway auto-deploys on push to main
- Auth: `X-Webhook-Secret` header must match `WEBHOOK_SECRET` env var
- Pipeline runs in a background thread; server responds 202 immediately
- Google Sheets button → Apps Script (`runScreener`) → calls `/run` → results appear in sheet

## Deployment env vars (Railway)
Same as `.env` plus:
- `WEBHOOK_SECRET` — shared with Apps Script Script Properties
- `GOOGLE_CREDENTIALS_JSON` — full contents of the service account JSON file (NOT `GOOGLE_CREDENTIALS_PATH`)

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
