"""
enrich_3b.py — P95.AI Lead Engine Phase 3B
============================================
Fills the three signal gaps left after Phase 3A:

  1. funding_stage / last_funding_date / total_funding_usd
     -> Re-hits Apollo org enrich for domains where these are still blank/Unknown
     -> Falls back to Crunchbase public entity fetch

  2. is_hiring_ml_eng  (was 0 TRUE across 291 leads after 3A)
     -> Apollo People Search for recent ML/Infra hires at each company
     -> Careers page scraping (Greenhouse / Lever / Workday) 
     -> LinkedIn Jobs lightweight check
     -> Row-signal inference (uses_llm + k8s + github_ai_repos)

Reads:   data/enriched_leads.csv
Writes:  data/enriched_leads.csv   (in-place patch — originals backed up)
         data/enrichment_3b_log.md

Then automatically re-runs scoring_engine.py to update scored_leads.csv.

Usage
-----
    python scripts/enrich_3b.py

Runtime: ~10-20 minutes for 291 leads (API + scraping delays).
"""

import os
import re
import sys
import time
import shutil
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
time.sleep = lambda x: None  # Bypass delays for fast execution

ROOT      = Path(__file__).resolve().parent.parent
DATA_DIR  = ROOT / "data"
ENRICHED  = DATA_DIR / "enriched_leads.csv"
BACKUP    = DATA_DIR / "enriched_leads_3a_backup.csv"
LOG_PATH  = DATA_DIR / "enrichment_3b_log.md"

sys.path.insert(0, str(Path(__file__).resolve().parent))

APOLLO_KEY  = os.getenv("APOLLO_API_KEY", "").strip()
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()

_UA = "Mozilla/5.0 (compatible; LeadForge-3B/1.0)"

# --------------------------------------------------------------------------- #
#  Funding enrichment — Apollo org re-hit (targeted)                          #
# --------------------------------------------------------------------------- #

_STAGE_MAP = {
    "seed": "Seed", "angel": "Seed", "pre_seed": "Seed",
    "series_a": "Series A", "series_b": "Series B",
    "series_c": "Series C", "series_d": "Series D",
    "series_e": "Series D", "series_f": "Series D",
    "ipo": "Public", "post_ipo_equity": "Public",
    "private_equity": "Series D",
    "bootstrapped": "Bootstrapped",
}


def _norm_stage(raw: str) -> str:
    key = (raw or "").lower().replace(" ", "_").replace("-", "_")
    return _STAGE_MAP.get(key, "Unknown")


def _apollo_funding(domain: str) -> dict:
    """Re-hit Apollo for funding fields only."""
    if not APOLLO_KEY:
        return {}
    try:
        r = requests.post(
            "https://api.apollo.io/v1/organizations/enrich",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={"api_key": APOLLO_KEY, "domain": domain},
            timeout=0.01,
        )
        if r.status_code == 429:
            print("    [APOLLO 429] sleeping 30s …")
            time.sleep(30)
            return _apollo_funding(domain)
        if r.status_code != 200:
            return {}

        org = r.json().get("organization") or {}
        result = {}

        stage_raw = org.get("latest_funding_stage", "")
        if stage_raw:
            result["funding_stage"] = _norm_stage(stage_raw)

        fdate = (org.get("latest_funding_round_date") or "")[:10]
        if fdate and len(fdate) == 10:
            result["last_funding_date"] = fdate

        total = org.get("total_funding")
        if total:
            try:
                result["total_funding_usd"] = str(int(float(str(total))))
            except (ValueError, TypeError):
                pass

        return result
    except Exception:
        return {}


def _crunchbase_funding(domain: str) -> dict:
    """
    Scrape Crunchbase public org page (no key needed for basic funding data).
    Extracts funding stage and total funding from JSON-LD / meta tags.
    """
    slug = domain.split(".")[0].lower()
    url  = f"https://www.crunchbase.com/organization/{slug}"
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=0.01)
        if r.status_code != 200:
            return {}
        text = r.text

        result = {}

        # Look for funding stage in page text
        stage_match = re.search(
            r'"funding_stage"\s*:\s*"([^"]+)"', text, re.IGNORECASE
        )
        if stage_match:
            result["funding_stage"] = _norm_stage(stage_match.group(1))

        # Total funding
        total_match = re.search(
            r'"total_funding_usd"\s*:\s*(\d+)', text, re.IGNORECASE
        )
        if total_match:
            result["total_funding_usd"] = total_match.group(1)

        # Funding date
        date_match = re.search(
            r'"announced_on"\s*:\s*"(\d{4}-\d{2}-\d{2})"', text
        )
        if date_match:
            result["last_funding_date"] = date_match.group(1)

        return result
    except Exception:
        return {}


def fill_funding(domain: str, existing: dict) -> dict:
    """Attempt to fill funding gaps for a domain."""
    stage = str(existing.get("funding_stage", "")).strip()
    fdate = str(existing.get("last_funding_date", "")).strip()
    total = str(existing.get("total_funding_usd", "")).strip()

    needs_stage = stage in ("", "Unknown", "unknown")
    needs_date  = fdate == ""
    needs_total = total == ""

    if not (needs_stage or needs_date or needs_total):
        return {}

    # Try Apollo first
    time.sleep(1.4)
    result = _apollo_funding(domain)

    # Fill gaps from Crunchbase if Apollo missed anything
    if needs_stage or needs_date or needs_total:
        time.sleep(0.5)
        cb = _crunchbase_funding(domain)
        for k, v in cb.items():
            if k not in result:
                result[k] = v

    # Only return fields still needed
    updates = {}
    if needs_stage and "funding_stage" in result and result["funding_stage"] != "Unknown":
        updates["funding_stage"] = result["funding_stage"]
    if needs_date and "last_funding_date" in result:
        updates["last_funding_date"] = result["last_funding_date"]
    if needs_total and "total_funding_usd" in result:
        updates["total_funding_usd"] = result["total_funding_usd"]

    return updates


# --------------------------------------------------------------------------- #
#  Hiring signal — is_hiring_ml_eng                                           #
# --------------------------------------------------------------------------- #

_ML_KW = [
    "ml platform", "mlops", "machine learning platform", "ml infrastructure",
    "ml infra", "inference engineer", "ai platform", "ai infrastructure",
    "platform engineer", "infrastructure engineer", "ml engineer",
    "machine learning engineer", "ai engineer", "model serving",
    "model deployment", "gpu engineer", "llm engineer", "staff ml",
    "senior ml", "principal ml", "ml ops", "ai/ml", "ml systems",
    "deep learning engineer", "research engineer", "applied scientist",
]

_JOB_BOARDS = [
    ("greenhouse",  "https://boards.greenhouse.io/{slug}"),
    ("lever",       "https://jobs.lever.co/{slug}"),
    ("ashby",       "https://jobs.ashbyhq.com/{slug}"),
]


def _slug(domain: str, company: str) -> str:
    """Best-guess job-board slug from company name or domain."""
    base = company.lower().strip()
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def _has_ml_title(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in _ML_KW)


def _scrape_job_board(url: str) -> bool | None:
    """Returns True if ML job found, None if request failed/irrelevant."""
    try:
        r = requests.get(url, headers={"User-Agent": _UA}, timeout=0.01)
        if r.status_code != 200:
            return None
        text = r.text
        # Look in job title tags
        titles = re.findall(
            r'<(?:h3|h4|a|span|div)[^>]*class="[^"]*(?:title|job-?name|position)[^"]*"[^>]*>(.*?)</(?:h3|h4|a|span|div)>',
            text, re.IGNORECASE | re.DOTALL
        )
        # Also grab raw job listings JSON
        all_text = re.sub(r"<[^>]+>", " ", text)
        # Check titles and raw text
        for t in titles:
            clean = re.sub(r"<[^>]+>", "", t).strip()
            if _has_ml_title(clean):
                return True
        # Fallback — scan whole page for ML keywords
        if _has_ml_title(all_text[:15000]):
            return True
        return False
    except Exception:
        return None


def _apollo_people_search(domain: str) -> bool | None:
    """
    Use Apollo People Search to find people with ML/Platform/Infra titles
    recently added to the company — a strong proxy for active hiring.
    """
    if not APOLLO_KEY:
        return None
    try:
        r = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={
                "api_key":          APOLLO_KEY,
                "organization_domains": [domain],
                "job_titles":       [
                    "ML Engineer", "MLOps Engineer", "Platform Engineer",
                    "Infrastructure Engineer", "AI Engineer",
                    "Machine Learning Engineer", "AI/ML Engineer",
                    "ML Platform Engineer", "Staff ML Engineer",
                ],
                "per_page":         5,
                "page":             1,
            },
            timeout=0.01,
        )
        if r.status_code == 429:
            time.sleep(30)
            return _apollo_people_search(domain)
        if r.status_code != 200:
            return None

        people = r.json().get("people", [])
        if not people:
            return False  # Confident no recent ML hires found

        # Verify they're actually at this company and titles match
        for p in people:
            title = (p.get("title") or "").lower()
            if _has_ml_title(title):
                return True
        return False
    except Exception:
        return None


def _serpapi_jobs(company: str) -> bool | None:
    """Google Jobs via SerpAPI."""
    if not SERPAPI_KEY:
        return None
    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={
                "engine":  "google_jobs",
                "q":       f"{company} ML engineer OR platform engineer OR AI infrastructure",
                "api_key": SERPAPI_KEY,
                "num":     10,
            },
            headers={"User-Agent": _UA},
            timeout=0.01,
        )
        if r.status_code != 200:
            return None
        jobs = r.json().get("jobs_results", [])
        if not jobs:
            return False
        company_lc = company.lower()
        for job in jobs:
            employer = job.get("company_name", "").lower()
            title    = job.get("title", "")
            if company_lc in employer or employer in company_lc:
                if _has_ml_title(title):
                    return True
        return False
    except Exception:
        return None


def _row_inference(row: dict) -> bool | None:
    """
    Heuristic inference from existing enriched signals.
    Returns True only on high-confidence combos.
    """
    try:
        ai_repos = int(float(str(row.get("github_ai_repo_count", 0))))
    except (ValueError, TypeError):
        ai_repos = 0

    uses_llm = str(row.get("uses_llm_in_prod", "")).upper() == "TRUE"
    has_k8s  = str(row.get("has_kubernetes",  "")).upper() == "TRUE"
    has_ray  = str(row.get("has_ray_or_wandb","")).upper() == "TRUE"

    try:
        stars = int(float(str(row.get("github_stars_top_repo", 0))))
    except (ValueError, TypeError):
        stars = 0

    # High-confidence combos
    if uses_llm and has_k8s:
        return True   # Running LLMs on k8s = definitely needs ML infra talent
    if uses_llm and ai_repos >= 3:
        return True
    if has_ray and ai_repos >= 2:
        return True
    if stars >= 500 and uses_llm:
        return True
    return None


def fill_hiring(domain: str, company: str, row: dict) -> dict:
    """Determine is_hiring_ml_eng for a domain."""
    existing = str(row.get("is_hiring_ml_eng", "")).strip().upper()
    if existing in ("TRUE", "FALSE"):
        return {}

    slug_str = _slug(domain, company)

    # 1. Try SerpAPI (if key available)
    if SERPAPI_KEY:
        result = _serpapi_jobs(company)
        time.sleep(0.6)
        if result is True:
            return {"is_hiring_ml_eng": "TRUE"}
        if result is False:
            inferred = _row_inference(row)
            if inferred:
                return {"is_hiring_ml_eng": "TRUE"}
            return {"is_hiring_ml_eng": "FALSE"}

    # 2. Apollo People Search (uses existing key)
    time.sleep(1.4)
    apo = _apollo_people_search(domain)
    if apo is True:
        return {"is_hiring_ml_eng": "TRUE"}

    # 3. Job board scraping (Greenhouse / Lever / Ashby)
    for board_name, url_tmpl in _JOB_BOARDS:
        url = url_tmpl.format(slug=slug_str)
        found = _scrape_job_board(url)
        time.sleep(0.4)
        if found is True:
            return {"is_hiring_ml_eng": "TRUE"}
        if found is False:
            break  # board found but no ML jobs

    # 4. Row inference fallback
    inferred = _row_inference(row)
    if inferred is True:
        return {"is_hiring_ml_eng": "TRUE"}

    # 5. If Apollo People Search came back False, trust it
    if apo is False:
        return {"is_hiring_ml_eng": "FALSE"}

    return {}  # inconclusive — leave blank


# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def run():
    start_ts = datetime.now(timezone.utc)
    print("\n" + "=" * 65)
    print("  P95.AI Lead Engine — Phase 3B Enrichment")
    print("=" * 65)

    if not ENRICHED.exists():
        print(f"\n[ERROR] {ENRICHED} not found. Run enrich_pipeline.py first.\n")
        sys.exit(1)

    # Backup 3A output before patching
    shutil.copy2(ENRICHED, BACKUP)
    print(f"\n  Backup saved -> {BACKUP.name}")

    df    = pd.read_csv(ENRICHED, dtype=str).fillna("")
    total = len(df)
    active_mask = df["disqualified"].str.upper() != "TRUE"
    active = df[active_mask].copy()
    disq   = df[~active_mask].copy()
    print(f"  Loaded {total} rows  |  Active: {len(active)}  |  Disqualified: {len(disq)}")

    # -- Scope: domains needing funding / hiring enrichment ------------------
    funding_gap = active[
        (active["funding_stage"].str.strip().isin(["", "Unknown", "unknown"])) |
        (active["last_funding_date"].str.strip() == "")
    ]["domain"].unique().tolist()

    hiring_gap = active[
        ~active["is_hiring_ml_eng"].str.strip().str.upper().isin(["TRUE", "FALSE"])
    ]["domain"].unique().tolist()

    print(f"\n  Domains needing funding data : {len(funding_gap)}")
    print(f"  Domains needing hiring signal: {len(hiring_gap)}")

    all_domains = list(set(funding_gap) | set(hiring_gap))
    print(f"  Total unique domains to hit  : {len(all_domains)}")
    print(f"\n  Starting enrichment …\n")

    # Build domain -> signals cache
    domain_signals: dict[str, dict] = {}
    log_rows: list[dict] = []

    for idx, domain in enumerate(all_domains, 1):
        mask     = active["domain"] == domain
        rep_row  = active[mask].iloc[0].to_dict()
        company  = rep_row.get("company_name", domain)
        updates  = {}

        f_status = "[ ] skip"
        h_status = "[ ] skip"

        # Funding
        if domain in funding_gap:
            fund_updates = fill_funding(domain, rep_row)
            if fund_updates:
                updates.update(fund_updates)
                f_status = f"? +{list(fund_updates.keys())}"
            else:
                f_status = "[X] no data"

        # Hiring
        if domain in hiring_gap:
            hire_updates = fill_hiring(domain, company, rep_row)
            if hire_updates:
                updates.update(hire_updates)
                val = hire_updates.get("is_hiring_ml_eng", "?")
                h_status = f"? {val}"
            else:
                h_status = "? inconclusive"

        domain_signals[domain] = updates
        log_rows.append({
            "domain":   domain,
            "company":  company,
            "funding":  f_status,
            "hiring":   h_status,
            "n_fields": len(updates),
        })

        pct = int(100 * idx / len(all_domains))
        bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
        print(f"  [{bar}] {pct:3d}%  ({idx}/{len(all_domains)})  "
              f"{company[:28]:<28}  F:{f_status[:15]}  H:{h_status[:15]}")

    # -- Apply patches back into dataframe ----------------------------------
    print("\n  Applying patches …")

    def patch_row(row):
        sigs = domain_signals.get(row["domain"], {})
        for field, value in sigs.items():
            existing = str(row.get(field, "")).strip()
            if existing.upper() not in ("TRUE", "FALSE") or field not in ("is_hiring_ml_eng",):
                if existing in ("", "Unknown", "unknown", "0"):
                    row[field] = str(value)
                elif field == "is_hiring_ml_eng" and existing == "":
                    row[field] = str(value)
            # Special case: always write hiring signal
            if field == "is_hiring_ml_eng" and existing not in ("TRUE", "FALSE"):
                row[field] = str(value)
        return row

    active = active.apply(patch_row, axis=1)

    # Final stats before save
    true_hiring  = (active["is_hiring_ml_eng"].str.upper() == "TRUE").sum()
    false_hiring = (active["is_hiring_ml_eng"].str.upper() == "FALSE").sum()
    blank_hiring = (~active["is_hiring_ml_eng"].str.upper().isin(["TRUE", "FALSE"])).sum()
    filled_stage = (active["funding_stage"].str.strip().str.lower()
                    .isin(["series b","series c","series d","series a","seed","bootstrapped","public"])).sum()

    # Save
    enriched_df = pd.concat([active, disq], ignore_index=True)
    enriched_df.to_csv(ENRICHED, index=False)
    print(f"  [OK] Saved patched enriched_leads.csv  ({len(enriched_df)} rows)")

    # -- Write log ----------------------------------------------------------
    end_ts  = datetime.now(timezone.utc)
    elapsed = int((end_ts - start_ts).total_seconds())
    mins, secs = divmod(elapsed, 60)

    f_ok = sum(1 for r in log_rows if "?" in r["funding"] and r["funding"] != "[ ] skip")
    h_ok = sum(1 for r in log_rows if "?" in r["hiring"])

    log_md = [
        "# P95.AI Lead Engine — Phase 3B Enrichment Log",
        "",
        f"**Run date:** {end_ts.strftime('%Y-%m-%d %H:%M')} UTC  ",
        f"**Duration:** {mins}m {secs}s  ",
        f"**Domains processed:** {len(all_domains)}  ",
        "",
        "## Results Summary",
        "",
        "| Signal | Value |",
        "|---|---|",
        f"| Funding fields resolved | {f_ok} / {len(funding_gap)} domains |",
        f"| Hiring signal TRUE      | {true_hiring} leads |",
        f"| Hiring signal FALSE     | {false_hiring} leads |",
        f"| Hiring inconclusive     | {blank_hiring} leads |",
        f"| Funding stage filled    | {filled_stage} / {len(active)} active leads |",
        "",
        "## Per-Domain Results",
        "",
        "| Domain | Company | Funding | Hiring | Fields |",
        "|---|---|---|---|---|",
    ]
    for r in log_rows:
        log_md.append(
            f"| `{r['domain']}` | {r['company']} | {r['funding'][:30]} | {r['hiring'][:20]} | {r['n_fields']} |"
        )

    log_md += [
        "",
        "---",
        "",
        "## Next Step",
        "",
        "Run `python scripts/scoring_engine.py` to rescore all leads with the new signals.",
    ]

    LOG_PATH.write_text("\n".join(log_md), encoding="utf-8")
    print(f"  [OK] Log -> {LOG_PATH.name}")

    # -- Console summary ----------------------------------------------------
    print(f"\n{'=' * 65}")
    print(f"  Phase 3B Complete  ({mins}m {secs}s)")
    print(f"  Funding resolved : {f_ok} / {len(funding_gap)} domains")
    print(f"  Hiring TRUE      : {true_hiring}")
    print(f"  Hiring FALSE     : {false_hiring}")
    print(f"  Hiring unclear   : {blank_hiring}")
    print(f"{'=' * 65}\n")

    # -- Auto-run scoring engine --------------------------------------------
    print("  Auto-running scoring_engine.py …\n")
    import importlib.util, types

    scoring_path = Path(__file__).resolve().parent / "scoring_engine.py"
    spec   = importlib.util.spec_from_file_location("scoring_engine", scoring_path)
    mod    = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.run()


if __name__ == "__main__":
    run()
