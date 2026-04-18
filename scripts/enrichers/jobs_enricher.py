"""
jobs_enricher.py — Phase 3B
============================
Detects whether a company is actively hiring ML / Platform / Infra engineers
by scraping Google Jobs (via SerpAPI) and a lightweight LinkedIn Jobs search.

Sets:
  is_hiring_ml_eng  →  TRUE / FALSE

Strategy (in order, first hit wins):
  1. SerpAPI Google Jobs  (if SERPAPI_KEY is set)
  2. LinkedIn Jobs URL head-check  (no auth, just HTTP 200/ title check)
  3. Apollo organization jobs field  (if already populated in existing_row)

Returns {} if unable to determine, {"is_hiring_ml_eng": "FALSE"} only if
we have a confident negative signal.
"""

import os
import re
import time
import requests

_USER_AGENT  = "Mozilla/5.0 (compatible; LeadForge-Enricher/1.0)"
_SERPAPI_URL = "https://serpapi.com/search.json"

# Keywords we look for in job titles / descriptions
_ML_KEYWORDS = [
    "ml platform", "mlops", "machine learning platform", "ml infrastructure",
    "ml infra", "inference engineer", "llm", "ai platform", "ai infrastructure",
    "platform engineer", "infrastructure engineer", "ml engineer",
    "machine learning engineer", "ai engineer", "model serving",
    "model deployment", "gpu", "ml ops",
]


def _matches_ml_title(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in _ML_KEYWORDS)


# ---------------------------------------------------------------------------
# Strategy 1 — SerpAPI Google Jobs
# ---------------------------------------------------------------------------

def _serpapi_jobs(company_name: str, api_key: str) -> bool | None:
    """
    Returns True if ML/infra job found, False if confident no results, None on error.
    """
    query = f"{company_name} ML platform engineer OR infrastructure engineer jobs"
    params = {
        "engine":   "google_jobs",
        "q":        query,
        "api_key":  api_key,
        "num":      10,
        "hl":       "en",
    }
    try:
        r = requests.get(_SERPAPI_URL, params=params,
                         headers={"User-Agent": _USER_AGENT}, timeout=15)
        if r.status_code != 200:
            return None
        data  = r.json()
        jobs  = data.get("jobs_results", [])
        if not jobs:
            return False  # Confident no results

        company_lc = company_name.lower()
        for job in jobs:
            employer = job.get("company_name", "").lower()
            title    = job.get("title", "")
            desc     = job.get("description", "")
            # Make sure it's actually this company (not a staffing firm)
            if company_lc in employer or employer in company_lc:
                if _matches_ml_title(title) or _matches_ml_title(desc[:500]):
                    return True
        return False
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Strategy 2 — LinkedIn Jobs lightweight check
# ---------------------------------------------------------------------------

def _linkedin_jobs_check(company_name: str, domain: str) -> bool | None:
    """
    Checks LinkedIn jobs page via a simple HTTP GET (no auth).
    Returns True/False/None.
    """
    # Guess company slug from domain
    slug = domain.split(".")[0].lower().replace("-", "")
    query = requests.utils.quote(
        f"{company_name} (ML engineer OR platform engineer OR infrastructure engineer)"
    )
    url = (
        f"https://www.linkedin.com/jobs/search/"
        f"?keywords={query}&f_C=&location=Worldwide"
    )
    try:
        r = requests.get(url, headers={"User-Agent": _USER_AGENT}, timeout=12)
        if r.status_code != 200:
            return None
        # Check if job listings page has ML-related content
        text = r.text[:8000].lower()
        company_lc = company_name.lower()
        # LinkedIn renders job titles in <h3> tags
        titles = re.findall(r"<h3[^>]*>(.*?)</h3>", text, re.DOTALL)
        for t in titles:
            clean = re.sub("<[^>]+>", "", t).strip()
            if company_lc in text and _matches_ml_title(clean):
                return True
        return None  # inconclusive (might be blocked)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Strategy 3 — Fallback: infer from tech stack / existing job signals
# ---------------------------------------------------------------------------

def _infer_from_row(existing_row: dict) -> bool | None:
    """
    Use existing row signals as a weak proxy.
    Returns True / None (never False — this is probabilistic).
    """
    # If company has GitHub AI repos + Cloud stack → likely hiring
    try:
        ai_repos = int(float(str(existing_row.get("github_ai_repo_count", 0))))
    except (ValueError, TypeError):
        ai_repos = 0

    tech = str(existing_row.get("tech_stack_raw", "")).lower()
    uses_llm = str(existing_row.get("uses_llm_in_prod", "")).upper() == "TRUE"
    has_k8s  = str(existing_row.get("has_kubernetes", "")).upper() == "TRUE"

    if uses_llm and has_k8s and ai_repos >= 2:
        return True  # high-confidence inference
    if uses_llm and ai_repos >= 5:
        return True

    return None  # not enough signal


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def enrich_lead(domain: str, company_name: str, existing_row: dict) -> dict:
    """
    Args:
        domain:        e.g. 'moveworks.com'
        company_name:  e.g. 'Moveworks'
        existing_row:  current row dict

    Returns:
        {"is_hiring_ml_eng": "TRUE"} or {"is_hiring_ml_eng": "FALSE"} or {}
    """
    # Skip if already set
    existing = str(existing_row.get("is_hiring_ml_eng", "")).upper()
    if existing in ("TRUE", "FALSE"):
        return {}

    serpapi_key = os.getenv("SERPAPI_KEY", "").strip()

    # Strategy 1: SerpAPI
    if serpapi_key:
        result = _serpapi_jobs(company_name, serpapi_key)
        time.sleep(0.5)   # rate limit courtesy
        if result is True:
            return {"is_hiring_ml_eng": "TRUE"}
        if result is False:
            # do a quick row-inference check before returning FALSE
            inferred = _infer_from_row(existing_row)
            if inferred:
                return {"is_hiring_ml_eng": "TRUE"}
            return {"is_hiring_ml_eng": "FALSE"}

    # Strategy 2: LinkedIn Jobs check
    result = _linkedin_jobs_check(company_name, domain)
    if result is True:
        return {"is_hiring_ml_eng": "TRUE"}

    # Strategy 3: Row inference
    inferred = _infer_from_row(existing_row)
    if inferred is True:
        return {"is_hiring_ml_eng": "TRUE"}

    # Cannot determine — leave blank (return empty so scorer yields 0 pts)
    return {}
