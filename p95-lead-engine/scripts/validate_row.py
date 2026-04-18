"""
validate_row.py — P95.AI Lead Engine schema validator
Usage: python scripts/validate_row.py path/to/your_source.csv

Checks every row against the locked schema in SCHEMA.md v1.0.
Exit code 0 = clean. Exit code 1 = violations found (do not commit).
"""

import csv
import sys
import re
import uuid
from datetime import datetime
from pathlib import Path

EXPECTED_COLUMNS = [
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

REQUIRED = {
    "lead_id","domain","company_name","source","date_sourced",
    "contact_name","contact_title","industry","employee_count",
    "employee_range","hq_country","geo_tier","disqualified"
}

VALID_SOURCES    = {"seed","apollo","linkedin","builtwith","crunchbase","github"}
VALID_INDUSTRIES = {"SaaS","FinTech","HealthTech","Ecommerce","Cybersec","Logistics","Other"}
VALID_EMP_RANGE  = {"50-200","201-500","501-1000","1001-5000"}
VALID_GEO        = {"US","EU_UK","India_seed"}
VALID_STAGE      = {"Series B","Series C","Series D","Bootstrapped","Unknown",""}
VALID_TIER       = {"Hot","Warm","Cold",""}
VALID_BOOL       = {"TRUE","FALSE",""}
VALID_AB         = {"pain_led","curiosity_led",""}
ISO_DATE_RE      = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EMAIL_RE         = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

errors = []

def err(row_num, col, msg):
    errors.append(f"  Row {row_num} | {col}: {msg}")

def validate_file(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Column contract check
        actual = list(reader.fieldnames or [])
        if actual != EXPECTED_COLUMNS:
            missing = set(EXPECTED_COLUMNS) - set(actual)
            extra   = set(actual) - set(EXPECTED_COLUMNS)
            if missing: errors.append(f"  HEADER: missing columns: {sorted(missing)}")
            if extra:   errors.append(f"  HEADER: unexpected columns: {sorted(extra)}")
            if actual != EXPECTED_COLUMNS:
                errors.append("  HEADER: column order does not match schema")

        for i, row in enumerate(reader, start=2):
            n = i  # row number for error messages

            # Required fields
            for col in REQUIRED:
                if col in row and not row[col].strip():
                    err(n, col, "required but empty")

            # lead_id — must be valid UUID v4
            v = row.get("lead_id","")
            try:
                obj = uuid.UUID(v, version=4)
                if str(obj) != v.lower():
                    raise ValueError
            except ValueError:
                err(n, "lead_id", f"not a valid UUID v4: '{v}'")

            # domain — lowercase, no protocol, no trailing slash
            v = row.get("domain","")
            if v:
                if v != v.lower():           err(n, "domain", "must be lowercase")
                if "://" in v:               err(n, "domain", "must not include protocol")
                if v.startswith("www."):     err(n, "domain", "must not include www.")
                if v.endswith("/"):          err(n, "domain", "must not have trailing slash")

            # source enum
            v = row.get("source","")
            if v and v not in VALID_SOURCES:
                err(n, "source", f"invalid value '{v}'. Must be one of {sorted(VALID_SOURCES)}")

            # date_sourced
            v = row.get("date_sourced","")
            if v and not ISO_DATE_RE.match(v):
                err(n, "date_sourced", f"must be YYYY-MM-DD, got '{v}'")

            # industry enum
            v = row.get("industry","")
            if v and v not in VALID_INDUSTRIES:
                err(n, "industry", f"invalid value '{v}'")

            # employee_count — integer >= 50
            v = row.get("employee_count","")
            if v:
                try:
                    count = int(v)
                    if count < 50:
                        err(n, "employee_count", f"must be >= 50, got {count}")
                except ValueError:
                    err(n, "employee_count", f"must be an integer, got '{v}'")

            # employee_range enum
            v = row.get("employee_range","")
            if v and v not in VALID_EMP_RANGE:
                err(n, "employee_range", f"invalid value '{v}'")

            # hq_country — 2-letter ISO
            v = row.get("hq_country","")
            if v and (len(v) != 2 or not v.isupper()):
                err(n, "hq_country", f"must be 2-letter ISO code (e.g. US), got '{v}'")

            # geo_tier enum
            v = row.get("geo_tier","")
            if v and v not in VALID_GEO:
                err(n, "geo_tier", f"invalid value '{v}'")

            # funding_stage enum
            v = row.get("funding_stage","")
            if v and v not in VALID_STAGE:
                err(n, "funding_stage", f"invalid value '{v}'")

            # last_funding_date
            v = row.get("last_funding_date","")
            if v and not ISO_DATE_RE.match(v):
                err(n, "last_funding_date", f"must be YYYY-MM-DD, got '{v}'")

            # total_funding_usd — integer if present
            v = row.get("total_funding_usd","")
            if v:
                try: int(v)
                except ValueError:
                    err(n, "total_funding_usd", f"must be integer (no commas/symbols), got '{v}'")

            # contact_linkedin URL prefix
            v = row.get("contact_linkedin","")
            if v and not v.startswith("https://linkedin.com/in/"):
                err(n, "contact_linkedin", "must start with https://linkedin.com/in/")

            # contact_email format
            v = row.get("contact_email","")
            if v and not EMAIL_RE.match(v):
                err(n, "contact_email", f"invalid email format: '{v}'")

            # email_confidence 0.0–1.0
            v = row.get("email_confidence","")
            if v:
                try:
                    f = float(v)
                    if not (0.0 <= f <= 1.0):
                        err(n, "email_confidence", f"must be 0.0–1.0, got {f}")
                except ValueError:
                    err(n, "email_confidence", f"must be float, got '{v}'")

            # boolean fields
            for col in ("uses_llm_in_prod","has_kubernetes","has_ray_or_wandb",
                        "has_snowflake","is_hiring_ml_eng","linkedin_post_30d","disqualified"):
                v = row.get(col,"")
                if v not in VALID_BOOL:
                    err(n, col, f"must be TRUE, FALSE, or blank — got '{v}'")

            # disqualified must be FALSE at source time (not blank)
            v = row.get("disqualified","")
            if v == "":
                err(n, "disqualified", "required — write FALSE at source time")

            # github_org_url
            v = row.get("github_org_url","")
            if v and not v.startswith("https://github.com/"):
                err(n, "github_org_url", "must start with https://github.com/")

            # company_linkedin
            v = row.get("company_linkedin","")
            if v and not v.startswith("https://linkedin.com/company/"):
                err(n, "company_linkedin", "must start with https://linkedin.com/company/")

            # score_tier enum
            v = row.get("score_tier","")
            if v and v not in VALID_TIER:
                err(n, "score_tier", f"invalid value '{v}'")

            # ab_variant enum
            v = row.get("ab_variant","")
            if v and v not in VALID_AB:
                err(n, "ab_variant", f"invalid value '{v}'")

            # string length checks
            if len(row.get("company_description","")) > 300:
                err(n, "company_description", "exceeds 300 char limit")
            if len(row.get("linkedin_post_topic","")) > 100:
                err(n, "linkedin_post_topic", "exceeds 100 char limit")
            if len(row.get("news_signal","")) > 200:
                err(n, "news_signal", "exceeds 200 char limit")
            if len(row.get("notes","")) > 500:
                err(n, "notes", "exceeds 500 char limit")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_row.py path/to/file.csv")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    print(f"Validating: {path}")
    validate_file(path)

    if errors:
        print(f"\nFAIL — {len(errors)} violation(s) found:\n")
        for e in errors:
            print(e)
        print("\nFix all violations before committing.")
        sys.exit(1)
    else:
        print("PASS — schema valid. Safe to commit.")
        sys.exit(0)
