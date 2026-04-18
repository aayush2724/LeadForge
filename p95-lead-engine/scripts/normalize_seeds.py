"""
normalize_seeds.py — P95.AI Lead Engine
Cleans the raw seeds CSV (Janaki's Research Lead output) and writes
data/raw/seeds_normalized.csv conformant to SCHEMA.md v1.0.

Issues fixed:
  - '""" """' placeholder values → empty string
  - Non-schema employee_range values → mapped to nearest valid bucket
  - geo_tier 'India' → 'India_seed'
  - contact_linkedin with 'www.' prefix → stripped
  - Double-slash in company_linkedin URLs → fixed
  - Domains deduplicated against apollo_normalized.csv (skip if already present)
  - Fresh UUID v4s assigned to all rows
  - funding_stage blanks → 'Unknown'

Usage: python scripts/normalize_seeds.py
"""

import csv
import uuid
import re
import pandas as pd
from pathlib import Path
from datetime import date

RAW_FILE        = Path("data/raw/seeds_raw.csv")
APOLLO_NORM     = Path("data/raw/apollo_normalized.csv")
OUTPUT          = Path("data/raw/seeds_normalized.csv")

SCHEMA_COLS = [
    "lead_id","domain","company_name","source","source_url","date_sourced",
    "contact_name","contact_title","contact_linkedin","contact_email","email_confidence",
    "industry","employee_count","employee_range","hq_country","hq_city","geo_tier",
    "funding_stage","last_funding_date","total_funding_usd","arr_estimate_usd",
    "company_linkedin","company_description","uses_llm_in_prod","tech_stack_raw",
    "has_kubernetes","has_ray_or_wandb","has_snowflake","github_org_url",
    "github_ai_repo_count","github_stars_top_repo","is_hiring_ml_eng",
    "linkedin_post_30d","linkedin_post_topic","news_signal",
    "score_total","score_tier","disqualified","disqualify_reason",
    "outreach_email_v1","outreach_linkedin_v1","ab_variant","notes"
]

VALID_FUNDING_STAGES = {"Series B", "Series C", "Series D", "Bootstrapped", "Unknown", ""}

# Map any raw employee_range value to the nearest valid schema bucket
def map_emp_range(raw: str, count: str) -> str:
    try:
        n = int(count)
    except (ValueError, TypeError):
        n = 0

    if n <= 200:   return "50-200"
    if n <= 500:   return "201-500"
    if n <= 1000:  return "501-1000"
    return "1001-5000"


def clean_value(v: str) -> str:
    """Strip the '\"\"\" \"\"\"' placeholder pattern → empty string."""
    v = v.strip()
    # Matches: """ """ or " " or variants with quotes around whitespace
    if re.fullmatch(r'["\s]+', v):
        return ""
    # Also catch literal string '" "' written as value
    if v in {'""" """', '" "', '""', "''' '''"}:
        return ""
    return v


def normalize_linkedin_url(url: str, prefix: str) -> str:
    """Ensure LinkedIn URLs use https://linkedin.com (not www.)."""
    if not url:
        return url
    url = url.replace("https://www.linkedin.com", "https://linkedin.com")
    url = re.sub(r"//+", "/", url.replace("https:/", "https://"))
    if url and not url.startswith(prefix):
        return ""
    return url.rstrip("/")


def map_geo_tier(raw: str, hq_country: str) -> str:
    raw = raw.strip()
    if raw in {"US"}:                    return "US"
    if raw in {"EU_UK"}:                 return "EU_UK"
    if raw in {"India_seed", "India"}:   return "India_seed"
    if hq_country == "IN":               return "India_seed"
    if hq_country in {"GB","DE","FR","SE","DK","IE","ES","NL","BE","CH"}:
        return "EU_UK"
    if hq_country == "US":               return "US"
    return "EU_UK"   # default for remaining (AU/CA etc.) — treat as secondary


def normalize_funding(v: str) -> str:
    return v if v in VALID_FUNDING_STAGES else ("Unknown" if v else "Unknown")


def load_apollo_domains() -> set:
    if APOLLO_NORM.exists():
        df = pd.read_csv(APOLLO_NORM, dtype=str, usecols=["domain"]).fillna("")
        return set(df["domain"].str.lower().str.strip())
    return set()


def main():
    print("\n=== normalize_seeds.py ===\n")

    apollo_domains = load_apollo_domains()
    print(f"  Apollo domains loaded for dedup check: {len(apollo_domains)}")

    rows_in  = 0
    rows_out = 0
    dupes    = 0
    out_rows = []

    with open(RAW_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            rows_in += 1
            # Clean every value
            row = {k: clean_value(v) for k, v in raw.items()}

            # Domain normalization
            domain = (row.get("domain","")
                      .lower()
                      .replace("https://","").replace("http://","")
                      .replace("www.","")
                      .rstrip("/"))
            row["domain"] = domain

            # Skip if already in Apollo (dedup across sources)
            if domain in apollo_domains:
                print(f"  [DEDUP] {domain} already in apollo_normalized — skipping")
                dupes += 1
                continue

            # Fresh UUID
            row["lead_id"] = str(uuid.uuid4())

            # employee_range → map to valid bucket
            row["employee_range"] = map_emp_range(
                row.get("employee_range",""), row.get("employee_count","")
            )

            # geo_tier
            row["geo_tier"] = map_geo_tier(
                row.get("geo_tier",""), row.get("hq_country","")
            )

            # LinkedIn URL normalization
            row["contact_linkedin"] = normalize_linkedin_url(
                row.get("contact_linkedin",""), "https://linkedin.com/in/"
            )
            row["company_linkedin"] = normalize_linkedin_url(
                row.get("company_linkedin",""), "https://linkedin.com/company/"
            )

            # funding_stage
            row["funding_stage"] = normalize_funding(row.get("funding_stage",""))

            # date_sourced fallback
            if not row.get("date_sourced"):
                row["date_sourced"] = date.today().isoformat()

            # disqualified must be FALSE at source time
            if row.get("disqualified","").upper() not in {"TRUE","FALSE"}:
                row["disqualified"] = "FALSE"

            # Ensure all schema columns exist
            for col in SCHEMA_COLS:
                if col not in row:
                    row[col] = ""

            out_rows.append({c: row.get(c,"") for c in SCHEMA_COLS})
            rows_out += 1

    # Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_COLS)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\n  Rows in           : {rows_in}")
    print(f"  Dupes skipped     : {dupes}")
    print(f"  Rows written      : {rows_out}")
    print(f"  Output            : {OUTPUT}")
    print("\nDone. Run validate_row.py next.\n")


if __name__ == "__main__":
    main()
