"""
prefilter.py — P95.AI Lead Engine  |  Task 2.10
Applies hard disqualifier rules from icp_framework.md to raw_leads.csv.

Produces:
  - data/raw_leads.csv           (updated: disqualified=TRUE + disqualify_reason filled)
  - data/raw_leads_rejected.csv  (audit trail of all rejected rows)
"""

import pandas as pd
from pathlib import Path

INPUT  = Path("data/raw_leads.csv")
OUTPUT = Path("data/raw_leads.csv")
AUDIT  = Path("data/raw_leads_rejected.csv")

# ── Hard Disqualifier Rules (from icp_framework.md §5) ──────────────────────

# Competitor domains — direct or adjacent disqualifiers
COMPETITOR_DOMAINS = {
    "baseten.co", "modal.com", "modal.run", "anyscale.com", "fireworks.ai",
    "together.ai", "replicate.com", "runpod.io", "huggingface.co",
}

# Sectors that are hard-disqualified
DISQUALIFIED_INDUSTRIES = {
    # none from the ICP enum are fully disqualified; we use domain/keyword checks below
}

# Employee count floor
MIN_EMPLOYEES = 50

# Geo hard-disqualifiers (ISO 3166-1 alpha-2)
BANNED_COUNTRIES = {"CN", "RU", "KP", "IR", "SY", "CU", "BY"}

# Keywords in company_description / company_name signaling disqualifying sectors
DISQUALIFIED_KEYWORDS = [
    "adult content", "gambling", "casino", "crypto casino",
    "defense contractor", "government contractor",
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def check_row(row: pd.Series) -> str | None:
    """
    Returns a disqualify_reason string if the row should be disqualified,
    or None if the row passes all checks.
    """
    # Already flagged upstream (e.g. from normalize script)
    if str(row.get("disqualified", "")).strip().upper() == "TRUE":
        reason = str(row.get("disqualify_reason", "competitor")).strip()
        return reason if reason else "flagged_upstream"

    domain = str(row.get("domain", "")).strip().lower()
    employees = row.get("employee_count", "")
    country = str(row.get("hq_country", "")).strip().upper()
    description = str(row.get("company_description", "")).lower()
    name = str(row.get("company_name", "")).lower()

    # 1. Competitor domain
    if domain in COMPETITOR_DOMAINS:
        return "competitor"

    # 2. Employee count too small
    try:
        if int(float(str(employees))) < MIN_EMPLOYEES:
            return "too_small"
    except (ValueError, TypeError):
        pass  # missing employee_count — don't disqualify on this alone

    # 3. Banned geography
    if country in BANNED_COUNTRIES:
        return "banned_geo"

    # 4. Disqualifying sector keywords in description or name
    combined = description + " " + name
    for kw in DISQUALIFIED_KEYWORDS:
        if kw in combined:
            return "disqualified_sector"

    return None  # passes all checks


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    df = pd.read_csv(INPUT, dtype=str)
    total = len(df)
    print(f"Loaded {total} rows from {INPUT}")

    reasons = []
    for _, row in df.iterrows():
        reasons.append(check_row(row))

    disqualified_mask = pd.Series([r is not None for r in reasons])
    reason_values     = pd.Series([r if r is not None else "" for r in reasons])

    # Update columns
    df["disqualified"]      = disqualified_mask.map({True: "TRUE", False: "FALSE"})
    df["disqualify_reason"] = reason_values

    # Split
    rejected = df[disqualified_mask].copy()
    kept     = df[~disqualified_mask].copy()

    # Save
    df.to_csv(OUTPUT, index=False)         # full file (with flags)
    rejected.to_csv(AUDIT, index=False)    # audit trail

    print(f"\n--- Prefilter Summary -----------------------------------")
    print(f"  Total rows:       {total:>4}")
    print(f"  Kept (active):    {len(kept):>4}")
    print(f"  Disqualified:     {len(rejected):>4}")

    if len(rejected):
        print(f"\n  Breakdown by reason:")
        for reason, count in rejected["disqualify_reason"].value_counts().items():
            print(f"    {reason:<30} {count}")

    print(f"\n  Output -> {OUTPUT}")
    print(f"  Audit  -> {AUDIT}")


if __name__ == "__main__":
    main()
