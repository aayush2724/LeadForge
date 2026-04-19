"""
quota_check.py — P95.AI Lead Engine  |  Task 2.11
Validates that the active (non-disqualified) leads in raw_leads.csv
meet the vertical and geographic quotas defined in icp_framework.md.

Produces:
  - data/sourcing_qa_report.md  (full QA report with pass/fail table + gap analysis)
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

INPUT  = Path("data/raw_leads.csv")
REPORT = Path("data/sourcing_qa_report.md")

# ── Target Quotas (from icp_framework.md §3.2 & §3.3) ───────────────────────

VERTICAL_QUOTAS = {
    "SaaS":      45,
    "FinTech":   30,
    "HealthTech": 20,
    "Ecommerce": 15,
    "Cybersec":  15,
    "Logistics": 15,
    # Flex / Other: 60
}
TOTAL_TARGET = 200
FLEX_TARGET  = 60   # "Other" bucket

GEO_QUOTAS = {
    "US":          120,
    "EU_UK":        60,
    "India_seed":   20,
}


# ── Report Generator ─────────────────────────────────────────────────────────

def status(actual: int, target: int, tolerance: float = 0.15) -> str:
    """Return ✅ PASS / ⚠️ LOW / ❌ OVER based on ±15% tolerance."""
    if actual < target * (1 - tolerance):
        return "⚠️  LOW"
    if actual > target * (1 + tolerance):
        return "❌ OVER"
    return "✅ PASS"


def main():
    df = pd.read_csv(INPUT, dtype=str)
    total_rows = len(df)

    # Only check ACTIVE (non-disqualified) leads
    active = df[df["disqualified"].str.upper() != "TRUE"].copy()
    active_count = len(active)

    # ── Vertical breakdown ────────────────────────────────────────────────────
    vertical_counts = active["industry"].value_counts().to_dict()

    # ── Geo breakdown ─────────────────────────────────────────────────────────
    geo_counts = active["geo_tier"].value_counts().to_dict()

    # ── Source breakdown ──────────────────────────────────────────────────────
    source_counts = active["source"].value_counts().to_dict()

    # ── Duplicate domain check ────────────────────────────────────────────────
    dup_domains = active[active.duplicated(subset=["domain"], keep=False)]["domain"].unique()

    # ── Personas check ────────────────────────────────────────────────────────
    priority_titles = [
        "CTO", "VP Engineering", "Head of Platform", "Head of AI", "Head of ML",
        "Head of Infrastructure", "VP Eng"
    ]
    def is_priority(title: str) -> bool:
        if pd.isna(title): return False
        t = str(title).lower()
        return any(pt.lower() in t for pt in priority_titles)

    active["is_priority_persona"] = active["contact_title"].apply(is_priority)
    priority_count = active["is_priority_persona"].sum()

    # ── Compute gaps ──────────────────────────────────────────────────────────
    gaps = {}
    for vertical, target in VERTICAL_QUOTAS.items():
        actual = vertical_counts.get(vertical, 0)
        gap = target - actual
        if gap > 0:
            gaps[vertical] = gap

    geo_gaps = {}
    for geo, target in GEO_QUOTAS.items():
        actual = geo_counts.get(geo, 0)
        gap = target - actual
        if gap > 0:
            geo_gaps[geo] = gap

    # ── Write report ──────────────────────────────────────────────────────────
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines.append(f"# P95.AI Lead Engine — Sourcing QA Report")
    lines.append(f"")
    lines.append(f"**Generated:** {now}  ")
    lines.append(f"**Input file:** `{INPUT}`  ")
    lines.append(f"**Total rows:** {total_rows} | **Active (non-disqualified):** {active_count}")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Overall
    overall_status = status(active_count, TOTAL_TARGET)
    lines.append(f"## Overall Count")
    lines.append(f"")
    lines.append(f"| Metric | Actual | Target | Status |")
    lines.append(f"|---|---|---|---|")
    lines.append(f"| Active leads | {active_count} | {TOTAL_TARGET} | {overall_status} |")
    lines.append(f"| Priority-persona leads | {priority_count} | — | {'✅' if priority_count > 0 else '❌'} |")
    lines.append(f"")

    # Vertical
    lines.append(f"## Vertical Quota Check")
    lines.append(f"")
    lines.append(f"| Vertical | Actual | Target | Gap | Status |")
    lines.append(f"|---|---|---|---|---|")
    for vertical, target in VERTICAL_QUOTAS.items():
        actual = vertical_counts.get(vertical, 0)
        gap = max(0, target - actual)
        st = status(actual, target)
        lines.append(f"| {vertical} | {actual} | {target} | {gap} | {st} |")

    # Flex / Other
    flex_actual = vertical_counts.get("Other", 0)
    flex_gap = max(0, FLEX_TARGET - flex_actual)
    lines.append(f"| Other (Flex) | {flex_actual} | {FLEX_TARGET} | {flex_gap} | {status(flex_actual, FLEX_TARGET)} |")
    lines.append(f"")

    # Geo
    lines.append(f"## Geographic Quota Check")
    lines.append(f"")
    lines.append(f"| Geo Tier | Actual | Target | Gap | Status |")
    lines.append(f"|---|---|---|---|---|")
    for geo, target in GEO_QUOTAS.items():
        actual = geo_counts.get(geo, 0)
        gap = max(0, target - actual)
        st = status(actual, target)
        lines.append(f"| {geo} | {actual} | {target} | {gap} | {st} |")
    lines.append(f"")

    # Source
    lines.append(f"## Source Breakdown")
    lines.append(f"")
    lines.append(f"| Source | Count |")
    lines.append(f"|---|---|")
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {src} | {cnt} |")
    lines.append(f"")

    # Duplicates
    lines.append(f"## Duplicate Domain Check")
    lines.append(f"")
    if len(dup_domains) == 0:
        lines.append(f"✅ No duplicate domains found in active leads.")
    else:
        lines.append(f"> [!WARNING]")
        lines.append(f"> {len(dup_domains)} domain(s) appear more than once in active leads:")
        lines.append(f"")
        for d in sorted(dup_domains):
            lines.append(f"- `{d}`")
    lines.append(f"")

    # Gap-fill recommendations
    all_gaps = {**{f"Vertical:{k}": v for k, v in gaps.items()},
                **{f"Geo:{k}": v for k, v in geo_gaps.items()}}

    lines.append(f"## Gap-Fill Recommendations")
    lines.append(f"")
    if not all_gaps:
        lines.append(f"✅ All verticals and geos are within tolerance — no gap-fill needed.")
    else:
        lines.append(f"> [!IMPORTANT]")
        lines.append(f"> The following gaps need to be filled before moving to Phase 3:")
        lines.append(f"")
        lines.append(f"| Dimension | Gap |")
        lines.append(f"|---|---|")
        for dim, gap in sorted(all_gaps.items(), key=lambda x: -x[1]):
            lines.append(f"| {dim} | {gap} leads needed |")
        lines.append(f"")
        lines.append(f"**Action:** Re-run the relevant sourcing tasks (2.3–2.8) "
                     f"targeting the under-quota segments, then re-run `scripts/compile_leads.py` "
                     f"and `scripts/prefilter.py` before proceeding.")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Next Steps")
    lines.append(f"")
    lines.append(f"1. **Task 2.12** — Import `data/raw_leads.csv` into Clay as `p95_leads_enriched` table")
    lines.append(f"2. **Task 2.13** — Team checkpoint review of this report before Phase 3")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"QA report written to {REPORT}")

    # Console summary
    print(f"\n--- Quota Check Summary ------------------------------------")
    print(f"  Active leads: {active_count} / {TOTAL_TARGET} target")
    print(f"  Vertical gaps: {list(gaps.keys()) if gaps else 'None'}")
    print(f"  Geo gaps:      {list(geo_gaps.keys()) if geo_gaps else 'None'}")
    print(f"  Duplicate domains: {len(dup_domains)}")


if __name__ == "__main__":
    main()
