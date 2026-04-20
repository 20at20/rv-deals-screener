"""
Tool: Apify API client
Layer: T (Tool) — stateless, input in / output out

Actors used:
  - code_crafter~leads-finder                                          : find founders by company domain (contact DB)
  - s-r~free-linkedin-company-finder---linkedin-address-from-any-site : find company LinkedIn URL from website domain
  - harvestapi~linkedin-company-employees                              : scrape company LinkedIn page, filter by founder titles, return full profiles
  - anchor~linkedin-profile-enrichment                                 : enrich LinkedIn profiles (used when URLs come from contact DB)
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


def get_company_linkedin_url(company_website: str) -> str:
    """
    Find a company's LinkedIn page URL from their website domain.

    Uses s-r/free-linkedin-company-finder (pay-per-use, no subscription).
    Returns the LinkedIn company URL string, or empty string if not found.
    """
    domain = company_website.replace("https://", "").replace("http://", "").rstrip("/")
    print(f"[apify] Finding company LinkedIn URL for: {domain}")
    results = _post(
        "s-r~free-linkedin-company-finder---linkedin-address-from-any-site",
        {"domains": [domain]},
    )
    linkedin_url = (results[0].get("linkedin_url") or "") if results else ""
    print(f"[apify] Company LinkedIn URL: {linkedin_url or '(not found)'}")
    return linkedin_url


_FOUNDER_TITLES = ["Founder", "Co-Founder", "Co-founder", "CEO", "CTO", "COO", "CPO"]


def get_company_founders(company_linkedin_url: str, max_items: int = 10) -> list[dict]:
    """
    Scrape a LinkedIn company page for founders and return full normalized profile dicts.

    Uses harvestapi/linkedin-company-employees (pay-per-use, no subscription).
    Filters by current job title at the company — not by headline — so it catches
    founders whose LinkedIn headline doesn't mention "founder".
    Returns profiles normalized to the same format as enrich_linkedin() so that
    _format_team_profiles() in screen_deals.py works without changes.
    """
    print(f"[apify] Fetching founders from LinkedIn company page: {company_linkedin_url}")
    results = _post(
        "harvestapi~linkedin-company-employees",
        {
            "companies": [company_linkedin_url],
            "currentJobTitles": _FOUNDER_TITLES,
            "maxItems": max_items,
        },
    )

    company_id = company_linkedin_url.rstrip("/").rsplit("/", 1)[-1].lower()

    profiles = []
    for item in results:
        location = item.get("location") or {}
        parsed = location.get("parsed") or {}

        experiences = []
        for e in (item.get("experience") or []):
            end_text = (e.get("endDate") or {}).get("text", "")
            experiences.append({
                "title": e.get("position"),
                "company": e.get("companyName"),
                "starts_at": (e.get("startDate") or {}).get("text", ""),
                "ends_at": "" if end_text == "Present" else end_text,
                "description": e.get("description") or "",
            })

        # Keep only people who have a "founder" role specifically at the target company
        has_founder_role = any(
            company_id in (e["company"] or "").lower()
            and "founder" in (e["title"] or "").lower()
            for e in experiences
        )
        if not has_founder_role:
            continue

        education = [
            {"degree_name": e.get("degree"), "school": e.get("schoolName")}
            for e in (item.get("education") or [])
        ]

        profiles.append({
            "full_name": f"{item.get('firstName', '')} {item.get('lastName', '')}".strip(),
            "country": parsed.get("country") or location.get("linkedinText", ""),
            "follower_count": item.get("followerCount"),
            "summary": item.get("about") or "",
            "experiences": experiences,
            "education": education,
        })

    print(f"[apify] Found {len(profiles)} founder profile(s)")
    return profiles


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
