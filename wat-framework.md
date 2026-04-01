# WAT Framework — Full Reference

Loaded on demand. Not read every session.

---

## When to use each layer

| Task | Layer |
|---|---|
| Fetch data on a schedule | W |
| Process a form submission | W |
| Send notifications or emails | W |
| Sync data between systems | W |
| Analyze or score with AI | A |
| Answer a natural language question | A |
| Summarize or classify content | A |
| Enrich or research a data record | A |
| Query a database | T |
| Call an external API | T |
| Handle file upload/download | T |
| Format or transform data | T |

---

## Workflows (W)

- Write as plain scripts — no AI branching logic
- Must fail loudly — no silent errors, always log run status
- Validate all inputs before processing
- One workflow = one clearly named job
- If it can be deterministic, it must be deterministic

## Agents (A)

- One agent = one clearly defined job. Never combine unrelated responsibilities.
- Pass structured, clean context — never raw unstructured blobs
- Return structured output (JSON preferred) so Workflows can consume it
- Prompts are versioned markdown files, not inline strings
- Never call an agent in a tight loop — batch inputs
- Cache outputs where TTL makes sense
- Include in every prompt: role, task, input format, output format, constraints

## Tools (T)

- Stateless: input in, output out, no side effects
- Typed inputs, typed outputs, explicit error handling
- Shared across the codebase — never duplicate, always reuse
- First thing to build when starting any new feature

---

## Multi-agent patterns

**Writer/Reviewer**: one agent writes, a fresh agent reviews.
Fresh context improves review quality — the reviewer won't be biased toward code it wrote.

**Parallel workers**: for large tasks, spawn multiple agents on subsets of the work,
then aggregate results. Use `claude -p` in a loop with `--allowedTools` scoped appropriately.

**Subagents**: keep the main context window clean by delegating focused subtasks.
One task per subagent. Pass only what it needs.

---

## Planning protocol

Before any non-trivial task:
1. Identify the WAT layer(s) involved
2. State the build order (Tools → Workflow/Agent → UI)
3. Flag risks and dependencies
4. Get confirmation before making large changes

---

## What goes in hooks vs CLAUDE.md

| Concern | Where |
|---|---|
| Must happen 100% of the time (formatting, linting) | Hook (PostToolUse) |
| Must never happen (push to main, destructive deletes) | Hook (PreToolUse, exit 2) |
| Guidance Claude should follow | CLAUDE.md |
| Detailed patterns for specific tasks | agent_docs/ skills |

CLAUDE.md is advisory (~80% followed). Hooks are deterministic (100%).
