"""
normalize_aayush.py — P95.AI Lead Engine
Normalizes Aayush's three source files (BuiltWith, Crunchbase, GitHub),
deduplicates against existing leads, and writes:
  data/raw/aayush_normalized.csv

Usage: python scripts/normalize_aayush.py
"""

import csv
import uuid
import re
import pandas as pd
from pathlib import Path
from datetime import date

SOURCES = [
    Path("data/raw/builtwith_raw.csv"),
    Path("data/raw/crunchbase_raw.csv"),
    Path("data/raw/github_raw.csv"),
]

EXISTING_NORMALIZED = [
    Path("data/raw/apollo_normalized.csv"),
    Path("data/raw/seeds_normalized.csv"),
]

OUTPUT = Path("data/raw/aayush_normalized.csv")

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

VALID_SOURCES    = {"seed","apollo","linkedin","builtwith","crunchbase","github"}
VALID_INDUSTRIES = {"SaaS","FinTech","HealthTech","Ecommerce","Cybersec","Logistics","Other"}
VALID_EMP_RANGE  = {"50-200","201-500","501-1000","1001-5000"}
VALID_GEO        = {"US","EU_UK","India_seed"}
VALID_STAGE      = {"Series B","Series C","Series D","Bootstrapped","Unknown",""}
VALID_BOOL       = {"TRUE","FALSE",""}

COMPETITOR_DOMAINS = {
    "baseten.co","modal.com","anyscale.com","fireworks.ai","together.ai",
    "replicate.com","runpod.io","huggingface.co","modal.run",
}


def load_existing_domains() -> set:
    domains = set()
    for f in EXISTING_NORMALIZED:
        if f.exists():
            df = pd.read_csv(f, dtype=str, usecols=["domain"]).fillna("")
            domains |= set(df["domain"].str.lower().str.strip())
    return domains


def clean(v: str) -> str:
    v = str(v).strip() if v and str(v) != "nan" else ""
    if re.fullmatch(r'["\s]+', v):
        return ""
    return v


def norm_domain(v: str) -> str:
    return (v.lower()
            .replace("https://","").replace("http://","")
            .replace("www.","")
            .rstrip("/"))


def map_emp_range(count_str: str) -> str:
    try:
        n = int(float(count_str))
    except (ValueError, TypeError):
        return "201-500"
    if n <= 200:  return "50-200"
    if n <= 500:  return "201-500"
    if n <= 1000: return "501-1000"
    return "1001-5000"


def map_geo(raw: str, country: str) -> str:
    if raw in VALID_GEO:            return raw
    if raw in {"India","India_seed"}: return "India_seed"
    if country == "IN":             return "India_seed"
    if country in {"GB","DE","FR","SE","DK","IE","ES","NL","BE","CH","CZ","IL","HK","SG","AU","CA"}:
        return "EU_UK"
    if country == "US":             return "US"
    return "EU_UK"


def norm_funding(v: str) -> str:
    return v if v in VALID_STAGE else "Unknown"


def norm_linkedin(url: str, prefix: str) -> str:
    if not url: return ""
    url = url.replace("https://www.linkedin.com","https://linkedin.com")
    url = re.sub(r"https:/(?=[^/])","https://",url)
    url = re.sub(r"//+","/",url.replace("https:/","https://"))
    url = url.rstrip("/")
    return url if url.startswith(prefix) else ""


def norm_source(v: str) -> str:
    v = v.lower().strip()
    if "builtwith" in v: return "builtwith"
    if "crunchbase" in v: return "crunchbase"
    if "github" in v: return "github"
    if "apollo" in v: return "apollo"
    if "linkedin" in v: return "linkedin"
    if "seed" in v: return "seed"
    return v if v in VALID_SOURCES else "builtwith"


def norm_industry(v: str) -> str:
    return v if v in VALID_INDUSTRIES else "Other"


def main():
    print("\n=== normalize_aayush.py ===\n")
    existing = load_existing_domains()
    print(f"  Existing domains (apollo + seeds): {len(existing)}")

    out_rows   = []
    seen_now   = set()   # track within this batch
    stats      = {"loaded":0,"dupes_existing":0,"dupes_batch":0,"competitors":0,"written":0}

    for src_file in SOURCES:
        if not src_file.exists():
            print(f"  [WARN] Missing: {src_file} — skipping")
            continue

        df = pd.read_csv(src_file, dtype=str).fillna("")
        print(f"  Loading {len(df):>3} rows from {src_file.name}")
        stats["loaded"] += len(df)

        for _, raw in df.iterrows():
            row = {k: clean(v) for k, v in raw.items()}

            domain = norm_domain(row.get("domain",""))
            row["domain"] = domain

            # Skip existing
            if domain in existing:
                stats["dupes_existing"] += 1
                continue

            # Skip within-batch duplicates
            if domain in seen_now:
                stats["dupes_batch"] += 1
                continue
            seen_now.add(domain)

            # Fresh UUID
            row["lead_id"] = str(uuid.uuid4())

            # Enums
            row["source"]       = norm_source(row.get("source",""))
            row["industry"]     = norm_industry(row.get("industry",""))
            row["employee_range"] = map_emp_range(row.get("employee_count",""))
            row["geo_tier"]     = map_geo(row.get("geo_tier",""), row.get("hq_country",""))
            row["funding_stage"]= norm_funding(row.get("funding_stage",""))

            # LinkedIn URLs
            row["contact_linkedin"] = norm_linkedin(row.get("contact_linkedin",""), "https://linkedin.com/in/")
            row["company_linkedin"] = norm_linkedin(row.get("company_linkedin",""), "https://linkedin.com/company/")

            # Date fallback
            if not row.get("date_sourced"):
                row["date_sourced"] = date.today().isoformat()

            # Competitor flagging
            if domain in COMPETITOR_DOMAINS:
                row["disqualified"]      = "TRUE"
                row["disqualify_reason"] = "competitor"
                stats["competitors"] += 1
            elif row.get("disqualified","").upper() not in {"TRUE","FALSE"}:
                row["disqualified"] = "FALSE"

            # Boolean field cleanup
            for col in ("uses_llm_in_prod","has_kubernetes","has_ray_or_wandb",
                        "has_snowflake","is_hiring_ml_eng","linkedin_post_30d"):
                v = row.get(col,"").upper()
                row[col] = v if v in {"TRUE","FALSE"} else ""

            # score_tier bleed protection
            if row.get("score_tier","").upper() in {"TRUE","FALSE"}:
                row["score_tier"] = ""

            # Ensure all columns
            for col in SCHEMA_COLS:
                if col not in row:
                    row[col] = ""

            out_rows.append({c: row.get(c,"") for c in SCHEMA_COLS})
            stats["written"] += 1

    # Write
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_COLS)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"\n  Rows loaded       : {stats['loaded']}")
    print(f"  Dupes (existing)  : {stats['dupes_existing']}")
    print(f"  Dupes (batch)     : {stats['dupes_batch']}")
    print(f"  Competitors flagged: {stats['competitors']}")
    print(f"  Rows written      : {stats['written']}")
    print(f"  Output            : {OUTPUT}")
    print("\nDone. Run validate_row.py next.\n")


if __name__ == "__main__":
    main()
