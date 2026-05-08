# RV Deals Screener

An AI-powered pipeline for pre-screening early-stage startup deals. Reads companies from a Google Sheet, runs multi-agent research, and writes a structured investment memo back to the sheet — ready for analyst review.

## What it does

For each company row in Google Sheets the pipeline:

1. **Researches the market** — pulls web data via Apify, then uses Claude to size the TAM and assess competitive dynamics
2. **Researches the team** — looks up founders on LinkedIn and scores their background and execution signals
3. **Screens with a VC lens** — a final Claude agent synthesises all signals and writes a short investment memo with a pass/flag recommendation

Results are written back to the same row so analysts see everything in one place.

## Architecture

```
main.py / server.py
       │
       └── workflows/screen_deals.py      ← orchestration (W layer)
                   │
                   ├── agents/market_researcher.py   ← Claude agent
                   ├── agents/team_researcher.py     ← Claude agent
                   └── agents/vc_screener.py         ← Claude agent
                               │
                               └── tools/            ← stateless API wrappers
                                   ├── sheets.py         (Google Sheets read/write)
                                   ├── apify.py          (web scraping)
                                   ├── claude_client.py  (Anthropic API)
                                   └── github_client.py  (prompt version sync)
```

The project follows the **WAT framework**: Tools → Agents → Workflows. Prompts live in versioned files under `agent_docs/prompts/`, never inline.

## Setup

### Prerequisites

- Python 3.10+
- A Google Cloud service account with Sheets API enabled
- An Apify account
- An Anthropic API key

### Installation

```bash
git clone <this-repo>
cd rv-deals-screener
pip install -r requirements.txt
```

### Credentials

```bash
cp .env.template .env
```

Fill in `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
APIFY_API_KEY=apify_api_...
GOOGLE_SHEET_ID=<your sheet id>
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json
WEBHOOK_SECRET=<random string, used by server.py>
GITHUB_TOKEN=ghp_...      # optional, needed for prompt refinement
GITHUB_REPO=owner/repo    # optional
```

Download your service account JSON from Google Cloud Console and point `GOOGLE_CREDENTIALS_PATH` at it. The service account needs **Editor** access to your Google Sheet.

### Google Sheet format

The sheet must have a header row. Required columns:

| Column | Description |
|--------|-------------|
| `Company` | Startup name |
| `Website` | Company URL |
| `Additional Context` | Optional analyst notes passed to agents |

The pipeline writes results into: `Short Description`, `Market Research`, `Team Research`, `VC Screen`, `Status`.

## Running

### Local — one-shot

```bash
python main.py
```

Processes all rows where `Status` is empty.

### Local — webhook server

```bash
python server.py
```

Starts a Flask server on port 8080 (configurable via `PORT`). Two endpoints:

- `POST /run` — triggers `screen_deals` in a background thread
- `POST /refine` — triggers the prompt refinement workflow

Both require the `X-Webhook-Secret` header to match `WEBHOOK_SECRET`.

## Deployment (Railway)

The repo includes a `Procfile` for Railway:

```
web: python server.py
```

Set all env vars from `.env` in Railway's dashboard, plus:

- `GOOGLE_CREDENTIALS_JSON` — paste the full contents of your service account JSON (Railway doesn't support file paths)

Railway auto-deploys on push to `main`.

### Triggering from Google Sheets

An Apps Script button in the sheet calls `POST /run` with the `X-Webhook-Secret` header. Set `WEBHOOK_SECRET` in both Railway env vars and the Apps Script Script Properties.

## Project structure

```
agents/          AI agents (one job each, structured I/O)
agent_docs/      WAT framework docs + versioned prompt files
tools/           Stateless API wrappers
workflows/       Orchestration pipelines
tests/           Test suite
main.py          CLI entry point
server.py        Webhook server
```

## Development

```bash
# Run tests
python -m pytest tests/

# Lint
ruff check .
```

Prompts live in `agent_docs/prompts/`. Edit them there; the agents load them at runtime.
