"""
Phase 5 completion: Generate LinkedIn DMs for top 50 leads
and add linkedin_dm column to data/phase5_outreach.csv
"""

import csv
import os

# ── DM templates (≤300 chars each — LinkedIn connection request limit) ──────────

def build_dm(row):
    first = row["contact_name"].split()[0]
    company = row["company_name"]
    title = row["contact_title"]
    stack = row["tech_stack_raw"]
    hiring = str(row.get("is_hiring_ml_eng", "")).strip()

    # Pick hook based on stack signals
    stack_parts = [s.strip() for s in stack.split(";") if s.strip()] if stack else []

    if any(t in stack_parts for t in ["vLLM", "Triton"]):
        hook = f"Saw {company} is running vLLM/Triton in prod - inference performance is clearly on your radar."
    elif "Ray" in stack_parts:
        hook = f"Noticed {company} runs Ray for distributed ML - GPU efficiency at scale is a real challenge."
    elif any(t in stack_parts for t in ["OpenAI", "Anthropic"]):
        hook = f"Saw {company} is using OpenAI/Anthropic in prod - at scale, inference costs compound fast."
    elif "Kubernetes" in stack_parts:
        hook = f"Running LLMs on Kubernetes at {company}'s scale means inference overhead is a real cost."
    else:
        hook = f"Impressed by {company}'s AI infrastructure - inference cost and latency are key levers at scale."

    # Hiring signal
    try:
        hiring_val = float(hiring)
        hiring_line = " You're also hiring ML engineers, which tells me inference demand is growing." if hiring_val > 0 else ""
    except (ValueError, TypeError):
        hiring_line = ""

    dm = (
        f"Hi {first} - {hook}{hiring_line} "
        f"I'm building P95.AI, an inference optimization layer that cuts LLM serving costs 30-45% with zero model changes. "
        f"Would you be open to a quick chat?"
    )

    # Trim to 300 chars if needed (LinkedIn DM limit for connection requests)
    if len(dm) > 300:
        dm = dm[:297] + "..."

    return dm


def main():
    input_path = os.path.join("data", "phase5_outreach.csv")
    output_path = os.path.join("data", "phase5_outreach.csv")
    temp_path   = os.path.join("data", "phase5_outreach_tmp.csv")

    rows = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames[:]
        rows = list(reader)

    # Add linkedin_dm column if not already present
    if "linkedin_dm" not in fieldnames:
        fieldnames.append("linkedin_dm")

    dm_count = 0
    for row in rows:
        if "linkedin_dm" not in row or not row["linkedin_dm"]:
            row["linkedin_dm"] = build_dm(row)
            dm_count += 1

    # Write to temp then replace
    with open(temp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    os.replace(temp_path, output_path)

    print(f"[OK] Phase 5 complete.")
    print(f"   Total leads:  {len(rows)}")
    print(f"   DMs generated: {dm_count}")
    print(f"   Columns now: {fieldnames}")
    print(f"   Output: {output_path}")

    # Preview top 3
    print("\n--- Sample DMs ---")
    for row in rows[:3]:
        print(f"\n[{row['contact_name']} @ {row['company_name']}]")
        print(f"  DM ({len(row['linkedin_dm'])} chars): {row['linkedin_dm']}")


if __name__ == "__main__":
    main()
