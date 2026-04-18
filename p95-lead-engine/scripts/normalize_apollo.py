"""
normalize_apollo.py — P95.AI Lead Engine
Merges all 4 Apollo pass CSVs, enforces schema order, strips competitors,
and writes data/raw/apollo_normalized.csv.

Usage: python scripts/normalize_apollo.py
"""

import pandas as pd
import uuid
from pathlib import Path
from datetime import date

RAW_DIR = Path("data/raw")
OUTPUT   = RAW_DIR / "apollo_normalized.csv"

PASS_FILES = [
    RAW_DIR / "apollo_pass1_us_saas_fintech.csv",
    RAW_DIR / "apollo_pass2_eu_uk.csv",
    RAW_DIR / "apollo_pass3_healthtech_cybersec.csv",
    RAW_DIR / "apollo_pass4_flex.csv",
]

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

COMPETITOR_DOMAINS = {
    "baseten.co","modal.com","anyscale.com","fireworks.ai",
    "together.ai","replicate.com","runpod.io","huggingface.co"
}


def load_passes():
    frames = []
    for f in PASS_FILES:
        if not f.exists():
            print(f"  [WARN] Missing file: {f} — skipping")
            continue
        df = pd.read_csv(f, dtype=str).fillna("")
        print(f"  Loaded {len(df):>3} rows from {f.name}")
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def ensure_schema_cols(df):
    for col in SCHEMA_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[SCHEMA_COLS]


def fix_lead_ids(df):
    """Regenerate all lead_ids as guaranteed-fresh UUID v4s (source IDs are not trusted)."""
    df["lead_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    return df


VALID_FUNDING_STAGES = {"Series B", "Series C", "Series D", "Bootstrapped", "Unknown", ""}

def normalize_funding_stage(df):
    """Map any unsupported funding stage (Series A/E/F/G/H etc.) to 'Unknown'."""
    df["funding_stage"] = df["funding_stage"].apply(
        lambda v: v if v in VALID_FUNDING_STAGES else "Unknown"
    )
    return df


def clean_score_tier(df):
    """Clear score_tier if it contains a boolean (data bleed from disqualified col)."""
    bad_mask = df["score_tier"].isin({"TRUE", "FALSE", "true", "false"})
    df.loc[bad_mask, "score_tier"] = ""
    return df


def normalize_domain(df):
    df["domain"] = (
        df["domain"]
        .str.lower()
        .str.replace(r"^https?://", "", regex=True)
        .str.replace(r"^www\.", "", regex=True)
        .str.rstrip("/")
    )
    return df


def flag_competitors(df):
    mask = df["domain"].isin(COMPETITOR_DOMAINS)
    df.loc[mask, "disqualified"]      = "TRUE"
    df.loc[mask, "disqualify_reason"] = "competitor"
    df.loc[df["disqualified"] == "", "disqualified"] = "FALSE"
    return df


def dedup(df):
    before = len(df)
    df = df.drop_duplicates(subset=["domain"], keep="first")
    dropped = before - len(df)
    if dropped:
        print(f"  Dedup: removed {dropped} duplicate domain(s)")
    return df


def fill_date_sourced(df):
    today = date.today().isoformat()
    df["date_sourced"] = df["date_sourced"].replace("", today)
    return df


def main():
    print("\n=== normalize_apollo.py ===\n")

    df = load_passes()
    if df.empty:
        print("ERROR: No data loaded. Aborting.")
        return

    print(f"\n  Total rows loaded: {len(df)}")

    df = normalize_domain(df)
    df = ensure_schema_cols(df)
    df = fix_lead_ids(df)
    df = normalize_funding_stage(df)
    df = clean_score_tier(df)
    df = flag_competitors(df)
    df = dedup(df)
    df = fill_date_sourced(df)

    # Final column order
    df = df[SCHEMA_COLS]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    total   = len(df)
    clean   = (df["disqualified"] == "FALSE").sum()
    flagged = (df["disqualified"] == "TRUE").sum()

    print(f"\n  Output: {OUTPUT}")
    print(f"  Total rows  : {total}")
    print(f"  Clean leads : {clean}")
    print(f"  Disqualified: {flagged}")
    print("\nDone. Run validate_row.py next.\n")


if __name__ == "__main__":
    main()
