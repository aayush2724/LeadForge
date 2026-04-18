"""
apollo_enricher.py — P95.AI Lead Engine Phase 3A
=================================================
Enriches each lead using Apollo.io's Organisation Enrich API.

Endpoint: POST https://api.apollo.io/v1/organizations/enrich
Docs:     https://apolloio.github.io/apollo-api-docs/?shell#organization-enrichment

Fields populated (where Apollo returns data):
  tech_stack_raw       — comma-joined list of detected technologies
  has_kubernetes       — TRUE/FALSE (detected in tech stack)
  has_ray_or_wandb     — TRUE/FALSE
  has_snowflake        — TRUE/FALSE
  uses_llm_in_prod     — TRUE/FALSE (heuristic from tech stack + description)
  employee_count       — integer (overrides blank values only)
  funding_stage        — series / bootstrapped label
  last_funding_date    — YYYY-MM-DD (if present)
  total_funding_usd    — integer
  company_description  — one-line summary (overrides blank values only)

Rate limits (free / basic Apollo plans): ~50 requests / minute.
We use a 1.3-second delay between calls to stay well under.
"""

import os
import re
import time
import requests

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "").strip()

_BASE_URL = "https://api.apollo.io/v1/organizations/enrich"
_DELAY = 1.3  # seconds between requests

# --------------------------------------------------------------------------- #
#  Tech-stack keyword maps                                                      #
# --------------------------------------------------------------------------- #

_KUBE_KW = {"kubernetes", "k8s", "helm", "kube"}
_RAY_KW  = {"ray", "wandb", "weights & biases", "weights and biases"}
_SNOW_KW = {"snowflake"}
_LLM_KW  = {
    "openai", "anthropic", "langchain", "hugging face", "huggingface",
    "llm", "vllm", "triton inference", "tgi", "text generation inference",
    "bedrock", "azure openai", "vertex ai", "cohere", "mistral",
}

# Funding-stage normalisation map
_STAGE_MAP = {
    "seed":          "Seed",
    "series_a":      "Series A",
    "series_b":      "Series B",
    "series_c":      "Series C",
    "series_d":      "Series D",
    "series_e":      "Series D",   # lump E+ into D for our schema
    "series_f":      "Series D",
    "ipo":           "Public",
    "private_equity":"Series D",
    "bootstrapped":  "Bootstrapped",
    "angel":         "Seed",
    "pre_seed":      "Seed",
    "":              "Unknown",
}


# --------------------------------------------------------------------------- #
#  Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _normalise_stage(raw: str) -> str:
    key = (raw or "").lower().replace(" ", "_").replace("-", "_")
    return _STAGE_MAP.get(key, "Unknown")


def _parse_funding_amount(raw) -> int:
    """Convert Apollo's funding string/int to a plain integer USD."""
    if raw is None:
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    # remove $, commas, M/B suffixes
    s = str(raw).replace(",", "").replace("$", "").strip().upper()
    try:
        if s.endswith("B"):
            return int(float(s[:-1]) * 1_000_000_000)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        return int(float(s))
    except ValueError:
        return 0


def _flag(tech_list: list[str], keywords: set) -> str:
    """Return 'TRUE' if any keyword appears in the tech list, else 'FALSE'."""
    lowered = {t.lower() for t in tech_list}
    return "TRUE" if any(kw in lowered for kw in keywords) else "FALSE"


def _llm_in_prod(tech_list: list[str], description: str) -> str:
    """Heuristic: TRUE if we see clear LLM-serving tech or description mentions it."""
    text = " ".join(tech_list).lower() + " " + (description or "").lower()
    llm_signals = list(_LLM_KW) + [
        "inference", "model serving", "ai api", "generative ai", "gen ai",
        "large language", "foundation model",
    ]
    return "TRUE" if any(sig in text for sig in llm_signals) else "FALSE"


# --------------------------------------------------------------------------- #
#  API call                                                                     #
# --------------------------------------------------------------------------- #

def _call_apollo(domain: str) -> dict | None:
    """
    POST to Apollo org enrich endpoint.
    Returns the parsed JSON dict (full response), or None on failure.
    """
    try:
        resp = requests.post(
            _BASE_URL,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
            },
            json={"api_key": APOLLO_API_KEY, "domain": domain},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 422:
            # Unprocessable — domain not found in Apollo
            return None
        if resp.status_code == 429:
            print(f"      [RATE LIMIT 429] sleeping 60s …")
            time.sleep(60)
            return _call_apollo(domain)   # single retry
        print(f"      [APOLLO {resp.status_code}] {domain}")
        return None
    except requests.exceptions.RequestException as exc:
        print(f"      [APOLLO NETWORK ERROR] {exc}")
        return None


# --------------------------------------------------------------------------- #
#  Signal extraction                                                            #
# --------------------------------------------------------------------------- #

def _extract(data: dict) -> dict:
    """Pull the fields we care about from Apollo's response envelope."""
    org = data.get("organization") or {}

    # --- tech stack ---
    raw_techs: list = org.get("technologies", []) or []
    # Apollo may return list of strings or list of dicts with "name" key
    tech_names: list[str] = []
    for t in raw_techs:
        if isinstance(t, str):
            tech_names.append(t)
        elif isinstance(t, dict):
            n = t.get("name") or t.get("uid") or ""
            if n:
                tech_names.append(n)

    tech_str = ", ".join(tech_names)

    # --- funding ---
    stage_raw = org.get("latest_funding_stage", "")
    funding_date = org.get("latest_funding_round_date", "") or ""
    if funding_date:
        # Apollo sometimes returns full datetime — trim to date
        funding_date = funding_date[:10]

    total_funding = _parse_funding_amount(org.get("total_funding"))

    # --- description ---
    description = (org.get("short_description") or "")[:300]

    # --- employee count ---
    emp = org.get("estimated_num_employees")
    emp_int = int(emp) if emp else 0

    return {
        "tech_stack_raw":    tech_str,
        "has_kubernetes":    _flag(tech_names, _KUBE_KW),
        "has_ray_or_wandb":  _flag(tech_names, _RAY_KW),
        "has_snowflake":     _flag(tech_names, _SNOW_KW),
        "uses_llm_in_prod":  _llm_in_prod(tech_names, description),
        "funding_stage":     _normalise_stage(stage_raw),
        "last_funding_date": funding_date,
        "total_funding_usd": total_funding,
        "company_description": description,
        "employee_count":    emp_int,
    }


# --------------------------------------------------------------------------- #
#  Public entry point                                                           #
# --------------------------------------------------------------------------- #

def enrich_lead(domain: str, existing_row: dict) -> dict:
    """
    Main entry point called by enrich_pipeline.py per unique domain.

    `existing_row` is the current row dict so we don't clobber already-populated
    fields with empty Apollo values.

    Returns a dict of fields to merge back into the dataframe.
    Only non-empty values are returned (caller decides merge strategy).
    """
    time.sleep(_DELAY)

    raw = _call_apollo(domain)
    if not raw:
        return {}

    extracted = _extract(raw)

    # --- selective merge: don't clobber existing good data with blanks ---
    updates: dict = {}
    for field, value in extracted.items():
        existing = str(existing_row.get(field, "")).strip()
        new_val  = str(value).strip() if value else ""

        # Always update tech_stack_raw (append / replace blank)
        if field == "tech_stack_raw":
            if new_val:
                updates[field] = new_val
            continue

        # For integer fields: only set if currently 0/blank
        if field in ("employee_count", "total_funding_usd"):
            if not existing or existing == "0":
                if value and int(float(str(value))) > 0:
                    updates[field] = int(float(str(value)))
            continue

        # For all other fields: set if currently blank
        if (not existing or existing.lower() in ("", "unknown", "false")) and new_val:
            updates[field] = new_val

    return updates
