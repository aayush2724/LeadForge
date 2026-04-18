"""
enrich_pipeline.py — P95.AI Lead Engine Phase 3A
=================================================
Orchestrates the full automated enrichment pass.

Reads:   data/raw_leads.csv            (291 active leads)
Writes:  data/enriched_leads.csv       (same schema + filled signal columns)
         data/enrichment_run_log.md    (per-domain result log)

Workflow
--------
1. Load raw_leads.csv, filter out disqualified rows.
2. Deduplicate by domain — each company's GitHub & Apollo are only hit ONCE,
   then the signals are broadcast to all contacts at that company.
3. Run GitHub enricher  → fills github_* / has_kubernetes / has_ray_or_wandb
4. Run Apollo enricher  → fills tech_stack_raw / uses_llm_in_prod / funding / etc.
5. Merge signals back into every row for that domain.
6. Save enriched_leads.csv and a markdown run log.

Usage
-----
    python scripts/enrich_pipeline.py

Estimated runtime: ~15–25 minutes for 291 leads (API rate limits).
Progress is printed live to console.
"""

import os
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# ── load .env ──────────────────────────────────────────────────────────────
load_dotenv()

# ── path setup ─────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent
DATA_DIR  = ROOT / "data"
INPUT     = DATA_DIR / "raw_leads.csv"
OUTPUT    = DATA_DIR / "enriched_leads.csv"
LOG_PATH  = DATA_DIR / "enrichment_run_log.md"

# add scripts/ to path so enrichers package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from enrichers.github_enricher import enrich_lead as github_enrich
from enrichers.apollo_enricher import enrich_lead as apollo_enrich

# --------------------------------------------------------------------------- #
#  Helpers                                                                      #
# --------------------------------------------------------------------------- #

BOOL_COLS = [
    "uses_llm_in_prod", "has_kubernetes", "has_ray_or_wandb",
    "has_snowflake", "is_hiring_ml_eng", "linkedin_post_30d",
]


def _employee_range(count) -> str:
    try:
        n = int(float(str(count)))
    except (ValueError, TypeError):
        return ""
    if n <= 200:
        return "50-200"
    if n <= 500:
        return "201-500"
    if n <= 1000:
        return "501-1000"
    return "1001-5000"


def _progress(current: int, total: int, domain: str, status: str):
    pct = int(100 * current / total)
    bar = "#" * (pct // 5) + "-" * (20 - pct // 5)
    print(f"  [{bar}] {pct:3d}%  ({current}/{total})  {domain[:35]:<35}  {status}")


# --------------------------------------------------------------------------- #
#  Main pipeline                                                                #
# --------------------------------------------------------------------------- #

def run():
    start_ts = datetime.now(timezone.utc)
    print("\n" + "=" * 65)
    print("  P95.AI Lead Engine — Phase 3A Enrichment Pipeline")
    print("=" * 65)

    # ── 1. Load ────────────────────────────────────────────────────────────
    if not INPUT.exists():
        print(f"\n[ERROR] {INPUT} not found. Run compile_leads.py first.\n")
        sys.exit(1)

    df = pd.read_csv(INPUT, dtype=str).fillna("")
    total_rows = len(df)
    print(f"\n  Loaded {total_rows} rows from {INPUT.name}")

    # Filter disqualified
    active = df[df["disqualified"].str.upper() != "TRUE"].copy()
    disq   = df[df["disqualified"].str.upper() == "TRUE"].copy()
    print(f"  Active: {len(active)} | Disqualified (skipped): {len(disq)}")

    # ── 2. Deduplicate domains ─────────────────────────────────────────────
    unique_domains = active["domain"].unique().tolist()
    print(f"  Unique domains to enrich: {len(unique_domains)}")
    print(f"\n  Starting enrichment — estimated time: {len(unique_domains) * 4 // 60:.0f}–{len(unique_domains) * 6 // 60:.0f} min\n")

    # Cache: domain → {field: value}
    domain_signals: dict[str, dict] = {}

    log_rows: list[dict] = []

    for idx, domain in enumerate(unique_domains, start=1):
        # Representative row for this domain (first occurrence)
        rep_mask = active["domain"] == domain
        rep_row  = active[rep_mask].iloc[0].to_dict()
        company  = rep_row.get("company_name", domain)

        gh_updates   = {}
        apo_updates  = {}
        gh_status    = "⬜ skip"
        apo_status   = "⬜ skip"

        # ── GitHub ─────────────────────────────────────────────────────
        try:
            gh_updates = github_enrich(
                domain       = domain,
                company_name = company,
                existing_org_url = rep_row.get("github_org_url", ""),
            )
            gh_status = "✅ ok" if gh_updates else "❌ not found"
        except Exception as exc:
            gh_status = f"💥 {str(exc)[:40]}"

        # ── Apollo ─────────────────────────────────────────────────────
        try:
            apo_updates = apollo_enrich(
                domain       = domain,
                existing_row = rep_row,
            )
            apo_status = "✅ ok" if apo_updates else "❌ not found"
        except Exception as exc:
            apo_status = f"💥 {str(exc)[:40]}"

        # Merge signals
        merged = {**gh_updates, **apo_updates}
        domain_signals[domain] = merged

        log_rows.append({
            "domain":     domain,
            "company":    company,
            "gh_status":  gh_status,
            "apo_status": apo_status,
            "fields_set": len(merged),
        })

        _progress(idx, len(unique_domains), domain,
                  f"GH:{gh_status}  APO:{apo_status}  +{len(merged)} fields")

    # ── 3. Merge signals back into every row ──────────────────────────────
    print("\n  Merging signals into dataframe …")

    for col, val in {d: v for d, v in domain_signals.items()}.items():
        pass  # just validating dict is built

    def apply_signals(row):
        signals = domain_signals.get(row["domain"], {})
        for field, value in signals.items():
            # Only update if field is currently blank/FALSE/0
            existing = str(row.get(field, "")).strip()
            if existing in ("", "0", "FALSE", "Unknown", "unknown"):
                # Cast to str — DataFrame is loaded with dtype=str throughout
                row[field] = str(value) if value is not None else ""
        # Recompute employee_range if employee_count was updated
        if row.get("employee_count") and not row.get("employee_range"):
            row["employee_range"] = _employee_range(row["employee_count"])
        return row

    active = active.apply(apply_signals, axis=1)

    # Normalise bool columns to uppercase TRUE/FALSE
    for col in BOOL_COLS:
        if col in active.columns:
            active[col] = active[col].apply(
                lambda x: "TRUE" if str(x).strip().upper() in ("TRUE", "1", "YES") else
                          ("FALSE" if str(x).strip().upper() in ("FALSE", "0", "NO") else x)
            )

    # Recombine active + disqualified
    enriched_df = pd.concat([active, disq], ignore_index=True)

    # -- 4. Save ------------------------------------------------------------
    enriched_df.to_csv(OUTPUT, index=False)
    print(f"  [OK] Saved enriched dataset -> {OUTPUT}")
    print(f"     Rows: {len(enriched_df)} | Columns: {len(enriched_df.columns)}")

    # -- 5. Run log ---------------------------------------------------------
    end_ts  = datetime.now(timezone.utc)
    elapsed = int((end_ts - start_ts).total_seconds())
    mins, secs = divmod(elapsed, 60)

    gh_ok  = sum(1 for r in log_rows if "✅" in r["gh_status"])
    apo_ok = sum(1 for r in log_rows if "✅" in r["apo_status"])

    log_md = [
        "# P95.AI Lead Engine — Enrichment Run Log",
        "",
        f"**Run date:** {end_ts.strftime('%Y-%m-%d %H:%M')} UTC  ",
        f"**Duration:** {mins}m {secs}s  ",
        f"**Input:** `data/raw_leads.csv` ({total_rows} rows)  ",
        f"**Output:** `data/enriched_leads.csv` ({len(enriched_df)} rows)  ",
        f"**Unique domains processed:** {len(unique_domains)}  ",
        "",
        "## Summary",
        "",
        f"| Enricher | Domains hit | Success | Not found |",
        f"|---|---|---|---|",
        f"| GitHub   | {len(unique_domains)} | {gh_ok} | {len(unique_domains) - gh_ok} |",
        f"| Apollo   | {len(unique_domains)} | {apo_ok} | {len(unique_domains) - apo_ok} |",
        "",
        "## Per-Domain Results",
        "",
        "| Domain | Company | GitHub | Apollo | Fields Set |",
        "|---|---|---|---|---|",
    ]
    for r in log_rows:
        log_md.append(
            f"| `{r['domain']}` | {r['company']} | {r['gh_status']} | {r['apo_status']} | {r['fields_set']} |"
        )

    log_md += [
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. **Task 3B** — Run these 3 Clay enrichment blocks on `p95_leads_enriched`:",
        "   - **BuiltWith** → populates `tech_stack_raw` gaps",
        "   - **Crunchbase** → confirms `funding_stage` + `last_funding_date`",
        "   - **Find Job Postings** → sets `is_hiring_ml_eng`",
        "   After Clay, export the table back as CSV and place it at `data/enriched_leads.csv`.",
        "",
        "2. **Task 3C** — Run `python scripts/scoring_engine.py` to score all 291 leads.",
    ]

    LOG_PATH.write_text("\n".join(log_md), encoding="utf-8")
    print(f"  [OK] Run log -> {LOG_PATH.name}")

    print(f"\n{'=' * 65}")
    print(f"  Phase 3A Complete  ({mins}m {secs}s)")
    print(f"  GitHub enriched: {gh_ok}/{len(unique_domains)} domains")
    print(f"  Apollo enriched: {apo_ok}/{len(unique_domains)} domains")
    print(f"{'=' * 65}\n")
    print("  Next: run scoring_engine.py  OR  complete Clay 3B first\n")


if __name__ == "__main__":
    run()
