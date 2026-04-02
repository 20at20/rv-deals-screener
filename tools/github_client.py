"""
Tool: GitHub API client
Layer: T (Tool) — stateless, input in / output out

Updates files in the GitHub repo via REST API.
Used by the prompt refiner workflow to persist prompt changes with full git history.

Required env vars:
  GITHUB_TOKEN — personal access token with repo write scope
  GITHUB_REPO  — e.g. "20at20/rv-deals-screener"
"""

import base64
import os

import httpx

GITHUB_API = "https://api.github.com"
TIMEOUT = 30


def _headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise EnvironmentError("GITHUB_TOKEN is not set in .env")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _repo() -> str:
    repo = os.environ.get("GITHUB_REPO", "")
    if not repo:
        raise EnvironmentError("GITHUB_REPO is not set in .env")
    return repo


def update_file(path: str, content: str, commit_message: str) -> None:
    """
    Create or update a file in the GitHub repo.

    Args:
        path: File path relative to repo root (e.g. "agent_docs/prompts/screener_system.md")
        content: New file content (plain text)
        commit_message: Git commit message
    """
    repo = _repo()
    headers = _headers()
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"

    # GET current file sha (required for updates)
    get_resp = httpx.get(url, headers=headers, timeout=TIMEOUT)
    if get_resp.status_code == 200:
        sha = get_resp.json()["sha"]
    elif get_resp.status_code == 404:
        sha = None  # new file
    else:
        get_resp.raise_for_status()

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if sha:
        payload["sha"] = sha

    put_resp = httpx.put(url, json=payload, headers=headers, timeout=TIMEOUT)
    put_resp.raise_for_status()
    print(f"[github_client] Updated '{path}' — commit: {put_resp.json()['commit']['sha'][:7]}")
