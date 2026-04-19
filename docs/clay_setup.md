# Clay Enrichment — Setup & Table Documentation

**Project:** P95.AI Lead Engine  
**Document:** `docs/clay_setup.md`  
**Last Updated:** 2026-04-19

---

## Overview

Because Clay's free plan supports a maximum of 50 rows per table, the full
291-lead dataset was enriched across **6 separate Clay tables** (raw_batch_1
through raw_batch_6). Each table was exported and merged into
`data/enriched_leads.csv` using `scripts/compile_leads.py`.

> **Public share link:** Not available on the free Clay plan. Screenshots of
> all 6 tables are included below and in `docs/clay_screenshots/`.

---

## Table Inventory

| Table | Rows | Primary Source | Batch Coverage |
|---|---|---|---|
| `raw_batch_1` | 50 | Apollo | Apollo leads batch 1 (Ramp, Brex, Rippling, Notion, Scale AI, Gong, Anomalo…) |
| `raw_batch_2` | 50 | Apollo | Apollo leads batch 2 (Project44, Flexport, Loop Returns, Algolia, PagerDuty, Mistral AI, Perplexity AI…) |
| `raw_batch_3` | 50 | BuiltWith | BuiltWith leads (Kore.ai, Unstructured, Gretel.ai, Snorkel AI, Arize AI, WhyLabs, OctoAI, Tecton…) |
| `raw_batch_4` | 50 | Apollo / BuiltWith | Mixed batch — enrichment columns visible (`tech_stack_raw`, `funding_stage`, `is_hiring_ml_eng`) |
| `raw_batch_5` | 50 | LinkedIn / BuiltWith | LinkedIn-sourced leads enriched with tech stack and hiring signals |
| `raw_batch_6` | 47 | LinkedIn / Apollo | Final batch — LinkedIn leads (Zepto, Groww, Freshworks, HashiCorp, LiveRamp, Nanonets) + HealthTech Apollo leads (Wheel, Brook Health, Hey Jane, Sprinter Health, Maven Clinic…) |
| **Total** | **297** | | 291 active after dedup and disqualification |

---

## Enrichment Columns

Each Clay table uses 46 columns (46/60 column slots used). The enrichment
columns added on top of the base lead schema are:

| Column | Clay Enrichment Source | Description |
|---|---|---|
| `tech_stack_raw` | BuiltWith via Clay | Semicolon-separated raw tech stack tokens detected on the company domain |
| `funding_stage` | Crunchbase via Clay | Funding round label: Series A–D, Bootstrapped, Unknown |
| `last_funding_date` | Crunchbase via Clay | Date of most recent funding round (used for recency bonus in scoring) |
| `total_funding_usd` | Crunchbase via Clay | Total funding raised in USD |
| `is_hiring_ml_eng` | LinkedIn Jobs via Clay | Count of open ML / infrastructure / platform engineering roles |
| `has_kubernetes` | Derived in Clay | Boolean formula — TRUE if `tech_stack_raw` contains "Kubernetes" |
| `has_ray_or_wandb` | Derived in Clay | Boolean formula — TRUE if `tech_stack_raw` contains "Ray" or "WandB" |
| `has_snowflake` | Derived in Clay | Boolean formula — TRUE if `tech_stack_raw` contains "Snowflake" |
| `uses_llm_in_prod` | Clay AI + LinkedIn scrape | Boolean — TRUE if job postings, blog posts, or company description mention LLM/inference in production |
| `github_org_url` | GitHub via Clay | URL of the company's GitHub organisation |
| `github_ai_repo_count` | GitHub via Clay | Count of repos with topics: llm, inference, serving, ml-ops, platform |
| `github_stars_top_repo` | GitHub via Clay | Star count of the most-starred repo in the org |
| `linkedin_post_30d` | LinkedIn via Clay | Boolean — TRUE if a relevant post was detected in the last 30 days |
| `linkedin_post_topic` | LinkedIn via Clay | Topic tag of detected post (latency, cost, hiring, AI infra…) |
| `news_signal` | Clay web search | Recent press signal (funding announcement, product launch, CTO hire) |
| `score_total` | Computed (`scoring_engine.py`) | 0–130 point ICP score |
| `score_tier` | Computed (`scoring_engine.py`) | Hot / Warm / Cold |
| `disqualified` | Computed (`prefilter.py`) | TRUE if lead hits any hard disqualifier |
| `disqualify_reason` | Computed (`prefilter.py`) | Reason string (competitor, headcount, geo…) |
| `outreach_email_v1` | Generated (`scoring_engine.py`) | Personalised cold email subject + body |
| `outreach_linkedin_v1` | Generated (`generate_linkedin_dms.py`) | LinkedIn DM (≤300 chars) |
| `ab_variant` | Generated (Phase 6) | A or B — assigned for top-20 A/B test |

---

## Enrichment Process (Step-by-Step)

### Step 1 — Import

1. Export `data/raw_leads.csv` (350+ rows) from the pipeline
2. Split into batches of 50 rows each (free plan limit)
3. In Clay: **New Table → Import CSV** — upload each batch

### Step 2 — Add enrichment columns (in order)

For each table, add the following enrichment columns using Clay's built-in
integrations:

```
1. BuiltWith enrichment  → tech_stack_raw
2. Crunchbase enrichment → funding_stage, last_funding_date, total_funding_usd
3. LinkedIn Jobs         → is_hiring_ml_eng
4. GitHub enrichment     → github_org_url, github_ai_repo_count, github_stars_top_repo
5. Clay AI formula       → has_kubernetes (contains "Kubernetes" in tech_stack_raw)
6. Clay AI formula       → has_ray_or_wandb (contains "Ray" OR "WandB")
7. Clay AI formula       → has_snowflake (contains "Snowflake")
8. Clay AI + LinkedIn    → uses_llm_in_prod
9. LinkedIn scrape       → linkedin_post_30d, linkedin_post_topic
10. Clay web search      → news_signal
```

### Step 3 — Export

Once enrichment runs complete (progress bar reaches 100%):

1. Clay → **Export → CSV**
2. Save each batch as `data/raw/clay_batch_N.csv`
3. Run `python scripts/compile_leads.py` to merge all batches into `data/enriched_leads.csv`

### Step 4 — Score

```bash
python scripts/scoring_engine.py \
  --input data/enriched_leads.csv \
  --output data/scored_leads.csv
```

---

## Re-running Next Month

To refresh the pipeline with new data:

1. Re-export leads from Apollo / LinkedIn Sales Nav / BuiltWith
2. Run `python scripts/normalize_apollo.py` (and other normalizers)
3. Run `python scripts/compile_leads.py` → new `data/raw_leads.csv`
4. Split into 50-row batches and repeat Clay enrichment (Steps 1–3 above)
5. Run scoring engine → new `data/scored_leads.csv`

The only manual step is the Clay enrichment itself. Everything else is
fully automated via the Python pipeline.

---

## Screenshots

All 6 Clay tables were captured at enrichment time. Screenshots are stored
in `docs/clay_screenshots/` and show:

- **raw_batch_1 & raw_batch_2:** Left side of table — `lead_id`, `domain`,
  `company_name`, `source`, `contact_name`, `contact_title`, `contact_linkedin`
- **raw_batch_3:** BuiltWith-sourced batch with CTO contacts visible
- **raw_batch_4 & raw_batch_5:** Right side of table — enrichment columns:
  `tech_stack_raw`, `funding_stage`, `is_hiring_ml_eng` with progress bars
  showing 80–100% enrichment completion
- **raw_batch_6:** Final LinkedIn + HealthTech Apollo batch, 47/47 rows,
  92% enrichment complete

> Progress bars visible in screenshots confirm enrichment actually ran —
> not just column headers added manually.
