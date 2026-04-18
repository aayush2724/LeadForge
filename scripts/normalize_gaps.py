"""
normalize_gaps.py — P95.AI Lead Engine
Normalizes the 4 raw Apollo gap-fill exports into the master schema.
"""

import pandas as pd
import uuid
import os
from pathlib import Path
from datetime import date

RAW_DIR = Path("data/raw")
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

GAP_FILES = {
    "healthtech_people_gap.csv": "HealthTech",
    "ecommerce_people_gap.csv": "Ecommerce",
    "logistics_people_gap.csv": "Logistics",
    "cyber_people_gap.csv": "Cybersec"
}

EU_UK_COUNTRIES = {
    "United Kingdom", "Germany", "France", "Netherlands", "Sweden", "Denmark", 
    "Belgium", "Austria", "Ireland", "Italy", "Spain", "Norway", "Finland", "Switzerland"
}

def get_geo_tier(country):
    if country == "United States":
        return "US"
    if country in EU_UK_COUNTRIES:
        return "EU_UK"
    if country == "India":
        return "India_seed"
    return "Other"

def normalize_domain(url):
    if not url or pd.isna(url): return ""
    domain = str(url).lower().strip()
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = domain.split("/")[0]
    return domain

def process_file(filename, industry_tag):
    input_path = RAW_DIR / filename
    output_path = RAW_DIR / filename.replace("_people_gap.csv", "_normalized_gap.csv")
    
    if not input_path.exists():
        print(f"  [SKIP] {filename} not found.")
        return None

    df = pd.read_csv(input_path, dtype=str).fillna("")
    print(f"  Processing {filename} ({len(df)} rows)...")

    out_df = pd.DataFrame(columns=SCHEMA_COLS)
    
    out_df["lead_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
    out_df["domain"] = df["Website"].apply(normalize_domain)
    out_df["company_name"] = df["Company Name"]
    out_df["source"] = "apollo"
    out_df["date_sourced"] = date.today().isoformat()
    out_df["contact_name"] = df["First Name"] + " " + df["Last Name"]
    out_df["contact_title"] = df["Title"]
    out_df["contact_linkedin"] = df["Person Linkedin Url"]
    out_df["contact_email"] = df["Email"]
    out_df["email_confidence"] = df["Email Confidence"]
    out_df["industry"] = industry_tag
    out_df["employee_count"] = df["# Employees"]
    out_df["hq_country"] = df["Country"]
    out_df["hq_city"] = df["City"]
    out_df["geo_tier"] = df["Country"].apply(get_geo_tier)
    out_df["funding_stage"] = df["Latest Funding"]
    out_df["last_funding_date"] = df["Last Raised At"]
    out_df["total_funding_usd"] = df["Total Funding"]
    out_df["arr_estimate_usd"] = df["Annual Revenue"]
    out_df["company_linkedin"] = df["Company Linkedin Url"]
    out_df["company_description"] = df["Keywords"]
    out_df["tech_stack_raw"] = df["Technologies"]
    out_df["disqualified"] = "FALSE"
    
    # Ensure all columns exist
    for col in SCHEMA_COLS:
        if col not in out_df.columns:
            out_df[col] = ""
            
    out_df = out_df[SCHEMA_COLS]
    out_df.to_csv(output_path, index=False)
    print(f"  Saved to {output_path.name}")
    return output_path

def main():
    print("\n=== normalize_gaps.py ===\n")
    processed = []
    for f, tag in GAP_FILES.items():
        res = process_file(f, tag)
        if res: processed.append(res)
    
    print(f"\nDone. Normalized {len(processed)} gap files.\n")

if __name__ == "__main__":
    main()
