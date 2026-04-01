# lessons.md

Rules learned from real mistakes. Read this at the start of every session.
Updated by Claude whenever a correction is made during work.

---

## Format
Each entry: what went wrong → rule that prevents it from happening again.

## Rules

### 1. Web search loop must capture text only on the final turn
**What went wrong:** `run_agent_with_web_search` used `final_text = block.text` in every loop iteration. When Claude emits a partial sentence before calling a tool (e.g. "Tower's focus on Python runtimes may allow it to..."), that fragment overwrote `final_text` and ended up in the output.
**Rule:** Only collect text when `stop_reason != "tool_use"` (the final turn). Intermediate turns may contain partial thoughts that are not the result.

### 2. Web search loop needs a hard iteration cap
**What went wrong:** The `while True` loop had no limit. With a detailed prompt, Claude issued 5+ consecutive searches, making the run take many minutes and hit rate limits repeatedly.
**Rule:** Always set `max_iterations` (e.g. 5) on the web search agentic loop. This caps runtime and API usage without meaningfully reducing research quality.

### 3. Prompt instructions alone don't reliably control output length
**What went wrong:** Adding "be concise" and "1-2 bullets per section" to the market research prompt still produced 4,000–6,000 char outputs with full markdown headers and a conclusion essay.
**Rule:** Use `max_tokens` to mechanically enforce output length. For short research summaries, pass `max_tokens=500`. Prompt instructions guide format; token caps enforce length.

### 4. LinkedIn experience descriptions bloat tokens significantly
**What went wrong:** `_format_team_profiles` included full job description text for each experience entry. With 3 founders, this exceeded the free-tier 50K tokens/min rate limit on every call.
**Rule:** Strip experience descriptions from LinkedIn profiles before passing to Claude. Title + company + period is sufficient signal for VC screening. Also cap education to top 2 entries and summary to 150 chars.

### 5. Free-tier Anthropic rate limits (50K tokens/min) are tight for this pipeline
**What went wrong:** Running two deals back-to-back with LinkedIn enrichment + market research exhausted the rate bucket within a minute, causing all calls to fail.
**Rule:** Add retry with 60s backoff on `RateLimitError`. Keep team and market data concise. For production use, add billing to reach Tier 1 (400K tokens/min).

### 6. On Railway, use GOOGLE_CREDENTIALS_JSON not GOOGLE_CREDENTIALS_PATH
**What went wrong:** Railway env var was named `GOOGLE_CREDENTIALS_PATH` but set to the JSON content (not a file path). The code tried to open the JSON string as a filename and crashed with `FileNotFoundError`.
**Rule:** When deploying to Railway (or any cloud), always use `GOOGLE_CREDENTIALS_JSON` (the JSON content as a string). `GOOGLE_CREDENTIALS_PATH` is only for local runs where the file actually exists on disk. `tools/sheets.py` already handles both — just use the right variable name.

---
*Last updated: 2026-04-02*
