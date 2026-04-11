"""
Tool: Anthropic Claude API wrapper
Layer: T (Tool) — stateless, input in / output out

Provides two functions used by agents:
  - run_agent()      : returns text response
  - run_agent_json() : returns parsed JSON dict
"""

import json
import os
import re
import time
from pathlib import Path

import anthropic

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
PROMPTS_DIR = Path(__file__).parent.parent / "agent_docs" / "prompts"

_client: anthropic.Anthropic | None = None


def _call_with_retry(client: "anthropic.Anthropic", **kwargs) -> "anthropic.types.Message":
    """Call client.messages.create with up to 3 retries on rate limit errors (60s wait)."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait = 60
            print(f"[claude_client] Rate limit hit, waiting {wait}s before retry {attempt + 2}/{max_retries}...")
            time.sleep(wait)


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY is not set in .env")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def load_prompt(filename: str) -> str:
    """Load a system prompt from agent_docs/prompts/<filename>."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def run_agent(
    system: str,
    user: str,
    tools: list | None = None,
    model: str | None = None,
    max_tokens: int = 2048,
) -> str:
    """
    Call Claude and return the text response.
    If tools are provided (e.g. web_search), Claude may call them automatically.
    """
    resolved_model = model or os.environ.get("SCREENER_MODEL", DEFAULT_MODEL)
    client = _get_client()

    kwargs: dict = {
        "model": resolved_model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }

    if tools:
        kwargs["tools"] = tools

    response = _call_with_retry(client, **kwargs)

    # Collect all text blocks from the response
    text_parts = []
    for block in response.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)

    return "\n".join(text_parts).strip()


def run_agent_with_web_search(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 2048,
) -> str:
    """
    Call Claude with the web_search tool enabled.
    Handles the agentic loop: continues until Claude stops calling tools or max_iterations is reached.
    """
    resolved_model = model or os.environ.get("SCREENER_MODEL", DEFAULT_MODEL)
    client = _get_client()

    web_search_tool = {"type": "web_search_20250305", "name": "web_search"}

    messages = [{"role": "user", "content": user}]
    final_text = ""
    max_iterations = 2

    for _ in range(max_iterations):
        response = _call_with_retry(
            client,
            model=resolved_model,
            max_tokens=max_tokens,
            system=system,
            tools=[web_search_tool],
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            break


        # Build tool results and continue the loop
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                # Web search results come back automatically in the next turn;
                # we just need to pass the assistant message back.
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "",  # server fills this in for web_search
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    return final_text.strip()


def run_agent_json(
    system: str,
    user: str,
    model: str | None = None,
    max_tokens: int = 2048,
) -> dict:
    """
    Call Claude and parse the response as JSON.
    Claude is instructed to respond with a JSON object only.
    """
    json_instruction = "\n\nIMPORTANT: Respond with a valid JSON object only. No markdown, no explanation outside the JSON."
    text = run_agent(system + json_instruction, user, model=model, max_tokens=max_tokens)

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"[claude_client] Failed to parse JSON response: {e}\nRaw: {text[:500]}")
