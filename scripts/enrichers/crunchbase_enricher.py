"""
crunchbase_enricher.py — Phase 3B
==================================
Hits the Crunchbase Basic (free-tier) API to pull:
  - funding_stage        (Series B / Series C / Series D / Bootstrapped / IPO / etc.)
  - last_funding_date    (ISO 8601 YYYY-MM-DD)
  - total_funding_usd    (integer)

Uses the /entities/organizations/{permalink} endpoint.
Falls back to a domain-based search when a direct permalink isn't known.

Returns a dict of fields to update (only non-empty values).
Returns {} on any failure — caller is responsible for swallowing errors.
"""

import os
import re
import time
import requests
from datetime import datetime

# Crunchbase Basic API (no key required for read-only public data, but key
# raises rate limit from 200 → 3000 req/day)
_CB_BASE    = "https://api.crunchbase.com/api/v4"
_USER_AGENT = "LeadForge-P95-Enricher/1.0"

# Map CB round types → our funding_stage enum
_ROUND_MAP: dict[str, str] = {
    "seed":                      "Seed",
    "angel":                     "Seed",
    "pre_seed":                  "Seed",
    "series_a":                  "Series A",
    "series_b":                  "Series B",
    "series_c":                  "Series C",
    "series_d":                  "Series D",
    "series_e":                  "Series D",   # lump D+
    "series_f":                  "Series D",
    "series_g":                  "Series D",
    "series_unknown":            "Unknown",
    "venture":                   "Unknown",
    "convertible_note":          "Seed",
    "corporate_round":           "Unknown",
    "debt_financing":            "Unknown",
    "equity_crowdfunding":       "Seed",
    "grant":                     "Unknown",
    "initial_coin_offering":     "Unknown",
    "post_ipo_equity":           "Public",
    "post_ipo_debt":             "Public",
    "secondary_market":          "Public",
    "private_equity":            "Unknown",
    "undisclosed":               "Unknown",
    "bootstrapped":              "Bootstrapped",
    "non_equity_assistance":     "Unknown",
}


def _domain_to_permalink(domain: str) -> str:
    """
    Strip TLD noise and return a best-guess Crunchbase org permalink.
    E.g. 'moveworks.com' → 'moveworks'
    """
    clean = domain.lower().strip()
    clean = re.sub(r"^www\.", "", clean)
    clean = re.sub(r"\.[a-z]{2,}$", "", clean)   # strip TLD
    clean = re.sub(r"\.[a-z]{2,}$", "", clean)    # strip second-level .co.uk etc.
    clean = re.sub(r"[^a-z0-9-]", "-", clean)
    return clean.strip("-")


def _search_org(domain: str, api_key: str) -> str | None:
    """
    Use CB autocomplete to find the org permalink for a domain.
    Returns permalink string or None.
    """
    url = f"{_CB_BASE}/autocompletes"
    params = {
        "query":        domain.split(".")[0],
        "collection_ids": "organizations",
        "limit":        5,
        "user_key":     api_key,
    }
    try:
        r = requests.get(url, params=params,
                         headers={"User-Agent": _USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return None
        items = r.json().get("entities", [])
        if not items:
            return None
        # prefer exact domain match in identifier
        for item in items:
            slug = item.get("identifier", {}).get("permalink", "")
            if slug:
                return slug
        return None
    except Exception:
        return None


def _get_org_funding(permalink: str, api_key: str) -> dict:
    """
    Fetch an org's entity card and extract funding fields.
    """
    url = f"{_CB_BASE}/entities/organizations/{permalink}"
    params = {
        "user_key": api_key,
        "field_ids": "funding_rounds,last_funding_type,last_funding_at,total_funding_usd",
    }
    try:
        r = requests.get(url, params=params,
                         headers={"User-Agent": _USER_AGENT}, timeout=12)
        if r.status_code == 404:
            return {}
        if r.status_code != 200:
            return {}

        props = r.json().get("properties", {})
        result: dict = {}

        # funding_stage from last_funding_type
        raw_type = props.get("last_funding_type", "")
        if raw_type:
            result["funding_stage"] = _ROUND_MAP.get(raw_type.lower(), "Unknown")

        # last_funding_date
        raw_date = props.get("last_funding_at", "")
        if raw_date:
            # CB returns ISO 8601 date strings already
            try:
                result["last_funding_date"] = datetime.strptime(
                    raw_date[:10], "%Y-%m-%d"
                ).strftime("%Y-%m-%d")
            except ValueError:
                pass

        # total_funding_usd
        total = props.get("total_funding_usd")
        if total is not None:
            try:
                result["total_funding_usd"] = str(int(total))
            except (ValueError, TypeError):
                pass

        return result

    except Exception:
        return {}


def enrich_lead(domain: str, existing_row: dict) -> dict:
    """
    Public interface — called by enrich_3b.py.

    Args:
        domain:       e.g. 'moveworks.com'
        existing_row: current row dict (used to skip already-filled fields)

    Returns:
        dict of {field: value} for fields that were blank / Unknown.
        Returns {} if nothing useful was found.
    """
    api_key = os.getenv("CRUNCHBASE_API_KEY", "").strip()

    # Without a key we still get limited public data from the autocomplete
    # endpoint, but entity cards require a key.  Accept either CB key name.
    if not api_key:
        api_key = os.getenv("CB_API_KEY", "").strip()

    updates: dict = {}

    # Skip if all three target fields are already populated and not Unknown
    stage = str(existing_row.get("funding_stage", "")).strip()
    fdate = str(existing_row.get("last_funding_date", "")).strip()
    total = str(existing_row.get("total_funding_usd", "")).strip()

    needs_stage = stage in ("", "Unknown", "unknown")
    needs_date  = fdate == ""
    needs_total = total == ""

    if not (needs_stage or needs_date or needs_total):
        return {}  # nothing to fill

    # --- Strategy 1: known permalink via domain guess ----------------------
    permalink = _domain_to_permalink(domain)

    if api_key:
        result = _get_org_funding(permalink, api_key)
        if not result:
            # Strategy 2: autocomplete search
            found = _search_org(domain, api_key)
            if found and found != permalink:
                time.sleep(0.3)
                result = _get_org_funding(found, api_key)
    else:
        # No API key — try unauthenticated entity fetch (often 403/429 but worth trying)
        result = _get_org_funding(permalink, api_key="")

    # Only write fields that are currently blank/Unknown
    if needs_stage and "funding_stage" in result:
        updates["funding_stage"] = result["funding_stage"]

    if needs_date and "last_funding_date" in result:
        updates["last_funding_date"] = result["last_funding_date"]

    if needs_total and "total_funding_usd" in result:
        updates["total_funding_usd"] = result["total_funding_usd"]

    return updates
