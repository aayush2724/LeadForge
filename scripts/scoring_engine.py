"""
scoring_engine.py — P95.AI Lead Engine Phase 3C
================================================
Scores every active lead 0–100 across four weighted dimensions and
assigns Hot / Warm / Cold tiers as defined in icp_framework.md §6.

Scoring model (100 pts total)
──────────────────────────────
  Dimension A — Firmographic       35 pts
  Dimension B — AI / Infra signals 35 pts
  Dimension C — Contact persona    20 pts
  Dimension D — Growth / intent    10 pts

Reads:   data/enriched_leads.csv   (Phase 3A output)
         Falls back to data/raw_leads.csv if enriched file not found.

Writes:  data/scored_leads.csv     (all 43 original columns + score_total + score_tier)
         data/scoring_report.md    (full analytics breakdown)

Usage
-----
    python scripts/scoring_engine.py
"""

import sys
import re
import pandas as pd
from pathlib import Path
from datetime import date, datetime

ROOT      = Path(__file__).resolve().parent.parent
DATA_DIR  = ROOT / "data"
ENRICHED  = DATA_DIR / "enriched_leads.csv"
RAW       = DATA_DIR / "raw_leads.csv"
OUTPUT    = DATA_DIR / "scored_leads.csv"
REPORT    = DATA_DIR / "scoring_report.md"


# =========================================================================== #
#   DIMENSION A — Firmographic  (max 35 pts)                                   #
# =========================================================================== #

def _score_firmographic(row: pd.Series) -> tuple[int, list[str]]:
    pts  = 0
    why  = []

    # ── Employee count (15 pts) ───────────────────────────────────────────
    try:
        emp = int(float(str(row.get("employee_count", 0))))
    except (ValueError, TypeError):
        emp = 0

    if 200 <= emp <= 5000:
        pts += 15; why.append(f"emp {emp} in sweet spot (+15)")
    elif 50 <= emp < 200:
        pts += 8;  why.append(f"emp {emp} small but viable (+8)")
    elif emp > 5000:
        pts += 6;  why.append(f"emp {emp} large enterprise (+6)")
    else:
        why.append(f"emp {emp} unknown/below floor (+0)")

    # ── Funding stage (12 pts) ────────────────────────────────────────────
    stage = str(row.get("funding_stage", "")).strip()
    stage_scores = {
        "Series D": 12, "Series C": 12, "Series B": 10,
        "Series A": 7,  "Bootstrapped": 8, "Seed": 4,
        "Public": 6,    "Unknown": 2,
    }
    s_pts = stage_scores.get(stage, 2)
    pts += s_pts
    why.append(f"funding '{stage}' (+{s_pts})")

    # ── Geography (8 pts) ─────────────────────────────────────────────────
    geo = str(row.get("geo_tier", "")).strip()
    geo_scores = {"US": 8, "EU_UK": 6, "India_seed": 4}
    g_pts = geo_scores.get(geo, 0)
    pts += g_pts
    why.append(f"geo '{geo}' (+{g_pts})")

    return min(pts, 35), why


# =========================================================================== #
#   DIMENSION B — AI / Infra signals  (max 35 pts)                             #
# =========================================================================== #

def _score_ai_signals(row: pd.Series) -> tuple[int, list[str]]:
    pts = 0
    why = []

    def flag(col: str) -> bool:
        return str(row.get(col, "")).strip().upper() == "TRUE"

    # Uses LLM in production (12 pts) — highest signal
    if flag("uses_llm_in_prod"):
        pts += 12; why.append("uses_llm_in_prod=TRUE (+12)")

    # Kubernetes (8 pts)
    if flag("has_kubernetes"):
        pts += 8; why.append("has_kubernetes=TRUE (+8)")

    # Ray / W&B (6 pts)
    if flag("has_ray_or_wandb"):
        pts += 6; why.append("has_ray_or_wandb=TRUE (+6)")

    # Snowflake (3 pts — data maturity signal)
    if flag("has_snowflake"):
        pts += 3; why.append("has_snowflake=TRUE (+3)")

    # GitHub AI repo count (up to 5 pts)
    try:
        ai_repos = int(float(str(row.get("github_ai_repo_count", 0))))
    except (ValueError, TypeError):
        ai_repos = 0
    if ai_repos >= 5:
        pts += 5; why.append(f"github AI repos ≥5 (+5)")
    elif ai_repos >= 1:
        pts += 3; why.append(f"github AI repos {ai_repos} (+3)")

    # GitHub stars on top AI repo (up to 4 pts)
    try:
        stars = int(float(str(row.get("github_stars_top_repo", 0))))
    except (ValueError, TypeError):
        stars = 0
    if stars >= 1000:
        pts += 4; why.append(f"github stars ≥1K (+4)")
    elif stars >= 100:
        pts += 2; why.append(f"github stars {stars} (+2)")

    # Tech stack bonus — scan tech_stack_raw for extra signals (up to 4 pts)
    tech = str(row.get("tech_stack_raw", "")).lower()
    extra = 0
    CLOUD_KW  = ["aws", "gcp", "azure", "google cloud"]
    VECTOR_KW = ["pinecone", "weaviate", "qdrant", "chroma", "pgvector"]
    if any(k in tech for k in CLOUD_KW):
        extra += 2
    if any(k in tech for k in VECTOR_KW):
        extra += 2
    if extra:
        pts += extra; why.append(f"cloud/vector stack signals (+{extra})")

    return min(pts, 35), why


# =========================================================================== #
#   DIMENSION C — Contact persona  (max 20 pts)                                #
# =========================================================================== #

# Title patterns in priority order
_TITLE_RULES: list[tuple[int, list[str]]] = [
    (20, ["cto", "chief technology officer"]),
    (18, ["vp engineering", "vp of engineering", "vice president engineering",
          "vice president of engineering"]),
    (17, ["head of infrastructure", "head of platform", "head of ai",
          "head of ml", "head of machine learning", "head of mlops"]),
    (16, ["head of engineering"]),
    (14, ["director of engineering", "director of platform",
          "director of infrastructure", "director of ai", "director of ml"]),
    (12, ["principal engineer", "staff engineer", "distinguished engineer"]),
    (10, ["engineering manager", "manager of engineering",
          "ml platform", "ml infra", "mlops lead"]),
    (8,  ["senior engineer", "lead engineer", "tech lead"]),
]

def _score_persona(row: pd.Series) -> tuple[int, list[str]]:
    title = str(row.get("contact_title", "")).lower().strip()
    why   = []

    for pts, patterns in _TITLE_RULES:
        if any(p in title for p in patterns):
            why.append(f"title '{row.get('contact_title', '')}' (+{pts})")
            return pts, why

    why.append(f"title '{row.get('contact_title', '')}' not in priority list (+2)")
    return 2, why


# =========================================================================== #
#   DIMENSION D — Growth / intent signals  (max 10 pts)                        #
# =========================================================================== #

def _score_growth(row: pd.Series) -> tuple[int, list[str]]:
    pts = 0
    why = []

    # Hiring ML/platform engineers (5 pts)
    if str(row.get("is_hiring_ml_eng", "")).upper() == "TRUE":
        pts += 5; why.append("is_hiring_ml_eng=TRUE (+5)")

    # Recent funding (within 18 months = 548 days)
    funding_date_str = str(row.get("last_funding_date", "")).strip()
    if funding_date_str and len(funding_date_str) >= 10:
        try:
            fdate = datetime.strptime(funding_date_str[:10], "%Y-%m-%d").date()
            days_ago = (date.today() - fdate).days
            if days_ago <= 548:
                pts += 3; why.append(f"funded {days_ago}d ago (+3)")
            elif days_ago <= 730:
                pts += 1; why.append(f"funded {days_ago}d ago (+1)")
        except ValueError:
            pass

    # LinkedIn activity in last 30 days (2 pts)
    if str(row.get("linkedin_post_30d", "")).upper() == "TRUE":
        pts += 2; why.append("linkedin_post_30d=TRUE (+2)")

    return min(pts, 10), why


# =========================================================================== #
#   Tier assignment                                                             #
# =========================================================================== #

def _tier(score: int) -> str:
    if score >= 80: return "Hot"
    if score >= 50: return "Warm"
    return "Cold"


# =========================================================================== #
#   Main                                                                        #
# =========================================================================== #

def score_row(row: pd.Series) -> pd.Series:
    a, why_a = _score_firmographic(row)
    b, why_b = _score_ai_signals(row)
    c, why_c = _score_persona(row)
    d, why_d = _score_growth(row)

    total = a + b + c + d
    # CSV is loaded with dtype=str — cast all written values to str
    row["score_total"] = str(total)
    row["score_tier"]  = _tier(total)
    row["notes"]       = " | ".join(why_a + why_b + why_c + why_d)[:500]
    return row


def run():
    print("\n" + "=" * 65)
    print("  P95.AI Lead Engine — Phase 3C Scoring Engine")
    print("=" * 65)

    # ── Load ────────────────────────────────────────────────────────────────
    src = ENRICHED if ENRICHED.exists() else RAW
    print(f"\n  Input: {src.name}")

    df = pd.read_csv(src, dtype=str).fillna("")
    print(f"  Rows: {len(df)}")

    # ── Score active leads only ─────────────────────────────────────────────
    active_mask = df["disqualified"].str.upper() != "TRUE"
    active = df[active_mask].copy()
    disq   = df[~active_mask].copy()

    print(f"  Scoring {len(active)} active leads …\n")
    active = active.apply(score_row, axis=1)

    # ── Merge and sort ──────────────────────────────────────────────────────
    disq["score_total"] = 0
    disq["score_tier"]  = "Disqualified"

    result = pd.concat([active, disq], ignore_index=True)
    result["score_total"] = pd.to_numeric(result["score_total"], errors="coerce").fillna(0).astype(int)
    result = result.sort_values("score_total", ascending=False).reset_index(drop=True)

    result.to_csv(OUTPUT, index=False)
    print(f"  [OK] Saved -> {OUTPUT.name}")

    # ── Analytics ──────────────────────────────────────────────────────────
    hot  = active[active["score_tier"] == "Hot"]
    warm = active[active["score_tier"] == "Warm"]
    cold = active[active["score_tier"] == "Cold"]

    # Dimension averages
    dim_rows: list[dict] = []
    for _, row in active.iterrows():
        a, _ = _score_firmographic(row)
        b, _ = _score_ai_signals(row)
        c, _ = _score_persona(row)
        d, _ = _score_growth(row)
        dim_rows.append({"A": a, "B": b, "C": c, "D": d})
    dim_df = pd.DataFrame(dim_rows)

    # Top 20 hot leads
    top20 = active[active["score_tier"] == "Hot"].head(20)[
        ["company_name", "contact_name", "contact_title", "industry",
         "score_total", "domain"]
    ].to_string(index=False)

    # ── Scoring report ──────────────────────────────────────────────────────
    report = [
        "# P95.AI Lead Engine — Scoring Report",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC  ",
        f"**Source:** `{src.name}`  ",
        f"**Active leads scored:** {len(active)}  ",
        "",
        "---",
        "",
        "## Tier Distribution",
        "",
        "| Tier | Count | % of Active |",
        "|---|---|---|",
        f"| 🔥 Hot  (80–100) | {len(hot)}  | {100*len(hot)/max(len(active),1):.1f}% |",
        f"| 🌡️ Warm (50–79)  | {len(warm)} | {100*len(warm)/max(len(active),1):.1f}% |",
        f"| ❄️ Cold (0–49)   | {len(cold)} | {100*len(cold)/max(len(active),1):.1f}% |",
        "",
        "## Score Distribution",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Mean score  | {active['score_total'].astype(int).mean():.1f} |",
        f"| Median score | {active['score_total'].astype(int).median():.0f} |",
        f"| Min score   | {active['score_total'].astype(int).min()} |",
        f"| Max score   | {active['score_total'].astype(int).max()} |",
        "",
        "## Dimension Averages (out of max)",
        "",
        "| Dimension | Avg Score | Max |",
        "|---|---|---|",
        f"| A — Firmographic    | {dim_df['A'].mean():.1f} | 35 |",
        f"| B — AI/Infra signals | {dim_df['B'].mean():.1f} | 35 |",
        f"| C — Persona          | {dim_df['C'].mean():.1f} | 20 |",
        f"| D — Growth/intent    | {dim_df['D'].mean():.1f} | 10 |",
        "",
        "## Tier Breakdown by Vertical",
        "",
        "| Vertical | Hot | Warm | Cold | Total |",
        "|---|---|---|---|---|",
    ]

    for vert in ["SaaS", "FinTech", "HealthTech", "Ecommerce", "Cybersec", "Logistics", "Other"]:
        v = active[active["industry"] == vert]
        vh = len(v[v["score_tier"] == "Hot"])
        vw = len(v[v["score_tier"] == "Warm"])
        vc = len(v[v["score_tier"] == "Cold"])
        if len(v) > 0:
            report.append(f"| {vert} | {vh} | {vw} | {vc} | {len(v)} |")

    report += [
        "",
        "## 🔥 Top 20 Hot Leads",
        "",
        "```",
        top20,
        "```",
        "",
        "---",
        "",
        "## Next Steps",
        "",
        "1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,",
        "   and Job Postings, then re-export and re-run this script.",
        "",
        "2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.",
        "",
        "3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.",
        "   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).",
    ]

    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(f"  [OK] Report -> {REPORT.name}")

    # ── Console summary ─────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print(f"  [HOT]  (80-100): {len(hot):>4}  ({100*len(hot)/max(len(active),1):.1f}%)")
    print(f"  [WARM] (50-79) : {len(warm):>4}  ({100*len(warm)/max(len(active),1):.1f}%)")
    print(f"  [COLD] (0-49)  : {len(cold):>4}  ({100*len(cold)/max(len(active),1):.1f}%)")
    print(f"{'=' * 65}")
    print(f"  Mean score: {active['score_total'].astype(int).mean():.1f}")
    print(f"\n  Next: review data/scoring_report.md -> Phase 4\n")


if __name__ == "__main__":
    run()
