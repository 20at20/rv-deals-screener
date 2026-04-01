"""
Tool: Apify API client
Layer: T (Tool) — stateless, input in / output out

Two actors used:
  - code_crafter~leads-finder       : find founders by company domain
  - anchor~linkedin-profile-enrichment : enrich LinkedIn profiles
"""

import os
import httpx

APIFY_BASE = "https://api.apify.com/v2/acts"
TIMEOUT = 300  # Apify run-sync can take a while


def _api_key() -> str:
    key = os.environ.get("APIFY_API_KEY", "")
    if not key:
        raise EnvironmentError("APIFY_API_KEY is not set in .env")
    return key


def _post(actor: str, payload: dict) -> list[dict]:
    url = f"{APIFY_BASE}/{actor}/run-sync-get-dataset-items"
    headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Accept": "application/json",
    }
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except httpx.HTTPStatusError as e:
        print(f"[apify] HTTP error from {actor}: {e.response.status_code} — {e.response.text[:200]}")
        return []
    except Exception as e:
        print(f"[apify] Error calling {actor}: {e}")
        return []


def find_founders(company_domain: str) -> list[dict]:
    """
    Call leads-finder actor to find founders for a given company domain.
    Returns list of {name, linkedin, company_name}.
    """
    print(f"[apify] Finding founders for: {company_domain}")
    results = _post(
        "code_crafter~leads-finder",
        {
            "company_domain": [company_domain],
            "contact_job_title": ["founder"],
        },
    )

    founders = []
    for item in results:
        name = f"{item.get('first_name', '')} {item.get('last_name', '')}".strip()
        linkedin = item.get("linkedin", "")
        if linkedin:
            founders.append({
                "name": name,
                "linkedin": linkedin,
                "company_name": item.get("company_name", ""),
            })

    print(f"[apify] Found {len(founders)} founders with LinkedIn URLs")
    return founders


def enrich_linkedin(linkedin_urls: list[str]) -> list[dict]:
    """
    Enrich a list of LinkedIn profile URLs using the anchor enrichment actor.
    Returns list of enriched profile dicts.
    """
    if not linkedin_urls:
        return []

    print(f"[apify] Enriching {len(linkedin_urls)} LinkedIn profile(s)")
    start_urls = [{"url": u, "id": str(i + 1)} for i, u in enumerate(linkedin_urls)]

    results = _post("anchor~linkedin-profile-enrichment", {"startUrls": start_urls})
    print(f"[apify] Enriched {len(results)} profile(s)")
    return results
