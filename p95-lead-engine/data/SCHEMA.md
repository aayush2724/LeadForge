# P95.AI Lead Engine — Clay Table Schema v1.0

**Owner:** Harshita (Data Lead)  
**Status:** Locked — do not alter column names or types without team sync  
**Dedup key:** `domain` (lowercase, no protocol, e.g. `stripe.com`)

All 6 source CSVs (tasks 2.3–2.8) must include every column below.  
Use empty string `""` for any optional field you cannot populate — **never omit columns.**

---

## Group A — Identity (required at source time)

| Column | Type | Required | Rule |
|---|---|---|---|
| `lead_id` | string | Y | UUID v4, unique per row, generated at row creation |
| `domain` | string | Y | Lowercase, no protocol/path. E.g. `stripe.com`. Primary dedup key. |
| `company_name` | string | Y | Non-empty, title case |
| `source` | enum | Y | `seed` \| `apollo` \| `linkedin` \| `builtwith` \| `crunchbase` \| `github` |
| `source_url` | string | N | Full URL to the Apollo/LinkedIn/CB record |
| `date_sourced` | date | Y | ISO 8601 `YYYY-MM-DD` |

## Group B — Contact (required at source time)

| Column | Type | Required | Rule |
|---|---|---|---|
| `contact_name` | string | Y | Full name, non-empty |
| `contact_title` | string | Y | E.g. `CTO`, `VP Engineering`, `Head of Platform` |
| `contact_linkedin` | string | N | Must start with `https://linkedin.com/in/` |
| `contact_email` | string | N | Populated in Phase 3 enrichment — blank at source time |
| `email_confidence` | float | N | 0.0–1.0, Phase 3 only |

## Group C — Company profile

| Column | Type | Required | Rule |
|---|---|---|---|
| `industry` | enum | Y | `SaaS` \| `FinTech` \| `HealthTech` \| `Ecommerce` \| `Cybersec` \| `Logistics` \| `Other` |
| `employee_count` | integer | Y | >= 50 |
| `employee_range` | enum | Y | `50-200` \| `201-500` \| `501-1000` \| `1001-5000` |
| `hq_country` | string | Y | ISO 3166-1 alpha-2 (e.g. `US`, `GB`, `IN`) |
| `hq_city` | string | N | Free text |
| `geo_tier` | enum | Y | `US` \| `EU_UK` \| `India_seed` |
| `funding_stage` | enum | N | `Series B` \| `Series C` \| `Series D` \| `Bootstrapped` \| `Unknown` |
| `last_funding_date` | date | N | ISO 8601, blank if unknown |
| `total_funding_usd` | integer | N | Raw integer, no commas/symbols |
| `arr_estimate_usd` | string | N | Free text range, e.g. `>$20M` |
| `company_linkedin` | string | N | Must start with `https://linkedin.com/company/` |
| `company_description` | string | N | Max 300 chars. One-line summary. |

## Group D — AI/infra signals

| Column | Type | Required | Rule |
|---|---|---|---|
| `uses_llm_in_prod` | boolean | N | `TRUE` \| `FALSE` \| blank |
| `tech_stack_raw` | string | N | Comma-separated technologies from BuiltWith |
| `has_kubernetes` | boolean | N | `TRUE` \| `FALSE` \| blank |
| `has_ray_or_wandb` | boolean | N | `TRUE` \| `FALSE` \| blank |
| `has_snowflake` | boolean | N | `TRUE` \| `FALSE` \| blank |
| `github_org_url` | string | N | Must start with `https://github.com/` |
| `github_ai_repo_count` | integer | N | Count of public AI/infra repos |
| `github_stars_top_repo` | integer | N | Stars on most popular AI/infra repo |
| `is_hiring_ml_eng` | boolean | N | Phase 3 enrichment — blank at source time |
| `linkedin_post_30d` | boolean | N | `TRUE` \| `FALSE`. Contact posted on LI in last 30 days. |
| `linkedin_post_topic` | string | N | Max 100 chars |
| `news_signal` | string | N | Max 200 chars. Phase 3 enrichment — blank at source time. |

## Group E — Scoring & outreach (all blank at source time)

| Column | Type | Required | Rule |
|---|---|---|---|
| `score_total` | integer | N | 0–100. Computed in Phase 4. |
| `score_tier` | enum | N | `Hot` (80–100) \| `Warm` (50–79) \| `Cold` (0–49) |
| `disqualified` | boolean | Y | Write `FALSE` at source time. Set by `prefilter.py` in Task 2.10. |
| `disqualify_reason` | string | N | E.g. `competitor`, `too_small`, `wrong_geo` |
| `outreach_email_v1` | string | N | Phase 5 — blank at source time |
| `outreach_linkedin_v1` | string | N | Phase 5 — blank at source time |
| `ab_variant` | enum | N | `pain_led` \| `curiosity_led`. Phase 6, top 20 only. |
| `notes` | string | N | Free text, max 500 chars |

---

## Rules for all source files

1. Column order must match this schema exactly
2. Use `""` (empty string) for any optional field you cannot populate — never skip columns
3. `domain` is always lowercase with no `https://`, `www.`, or trailing slashes
4. Booleans: write `TRUE` or `FALSE` (uppercase), never `1/0` or `yes/no`
5. Dates: always `YYYY-MM-DD`
6. `disqualified` must always be written as `FALSE` at source time — Task 2.10 handles rejections
7. Run `scripts/validate_row.py your_file.csv` locally before committing

---

## Column order (for CSV headers)

```
lead_id,domain,company_name,source,source_url,date_sourced,contact_name,contact_title,contact_linkedin,contact_email,email_confidence,industry,employee_count,employee_range,hq_country,hq_city,geo_tier,funding_stage,last_funding_date,total_funding_usd,arr_estimate_usd,company_linkedin,company_description,uses_llm_in_prod,tech_stack_raw,has_kubernetes,has_ray_or_wandb,has_snowflake,github_org_url,github_ai_repo_count,github_stars_top_repo,is_hiring_ml_eng,linkedin_post_30d,linkedin_post_topic,news_signal,score_total,score_tier,disqualified,disqualify_reason,outreach_email_v1,outreach_linkedin_v1,ab_variant,notes
```
