# P95.AI Lead Engine

**🚀� Live Landing Page / Architectural Overview:** [p95-ai-lead-engine-m8ofg.thinkroot.app](https://p95-ai-lead-engine-m8ofg.thinkroot.app/)

An end-to-end, reproducible pipeline that sources, normalises, enriches, scores, and generates personalised outreach for 291 qualified enterprise AI/ML leads — from raw data export to ready-to-send email + LinkedIn DM sequences.

---

## Table of Contents

1. [Project Overview](#project-overview)

2. [Pipeline Architecture](#pipeline-architecture)

3. [Quick Start](#quick-start)

4. [Environment Setup](#environment-setup)

5. [Pipeline Stages](#pipeline-stages)

6. [Data Schema](#data-schema)

7. [Key Outputs](#key-outputs)

8. [ICP & Scoring Framework](#icp--scoring-framework)

9. [A/B Test Design](#ab-test-design)

10. [Directory Structure](#directory-structure)

11. [Team Roles](#team-roles)

---

## Project Overview

**P95.AI** is an inference optimisation layer that cuts LLM serving costs 30–45 % with zero model changes. This repository contains the full lead-generation pipeline built to find and engage the 291 highest-fit engineering buyers (CTOs, VPs Engineering, Heads of AI) at AI-native companies running LLMs in production.

### Results at a glance

| Metric | Value |
|---|---|
| Total active leads | **291** |
| Hot tier (score >= 80) | **91** |
| Warm tier (score 60–79) | **101** |
| Cold tier (score < 60) | **99** |
| Personalised emails generated | **50** |
| LinkedIn DMs generated | **50** |
| A/B variants designed | **40** (20 leads × 2 variants) |
| Sources | Apollo · LinkedIn Sales Nav · Crunchbase · GitHub · Seed lists |

---

## Pipeline Architecture

```
Raw Sources
  │
  ├── Apollo export        → scripts/normalize_apollo.py
  ├── LinkedIn Sales Nav   → scripts/normalize_linkedin.py
  ├── Seed lists (XLS)     → scripts/normalize_seeds.py
  └── GitHub / Crunchbase  → scripts/normalize_engineer_sources.py
                                        │
                                        ▼
                          scripts/compile_leads.py
                          (dedup: domain + contact_name)
                                        │
                                        ▼
                            data/raw_leads.csv  (master)
                                        │
                                        ▼
                             scripts/prefilter.py
                         (disqualifier flags + quota check)
                                        │
                                        ▼
                       Phase 3A Automation (Enrichment)
                       → scripts/enrich_pipeline.py
                                        │
                                        ▼
                       Phase 3B Intent (Gap Fill)
                       → scripts/enrich_3b.py
                                        │
                                        ▼
                        scripts/scoring_engine.py
                     (100-point ICP score per lead)
                                        │
                                        ▼
                          data/scored_leads.csv
                       (291 active, Hot/Warm/Cold)
                                        │
                          ┌─────────────┴─────────────┐
                          ▼                           ▼
               Phase 5 Outreach                  Phase 6 A/B Test
          data/phase5_outreach.csv         data/phase6_ab_variants.csv
          (50 leads, email + DM)            (top 20 leads, 2 variants)
```

The entire pipeline can be executed via the master runner:
```bash
python pipeline.py
```

---

## Quick Start

```bash

# 1. Clone and enter the repo

git clone <repo-url>

cd hackathon

# 2. Create virtual environment

python -m venv .venv

.venv\Scripts\activate        # Windows

# source .venv/bin/activate   # Mac / Linux

# 3. Install dependencies

pip install -r requirements.txt

# 4. Configure API keys

cp .env.template .env

# Edit .env and fill in APOLLO_API_KEY, OPENAI_API_KEY, GITHUB_TOKEN

# 5. Run the full pipeline
python pipeline.py

# 6. Outputs are ready

#    data/scored_leads.csv         — 291 scored leads

#    data/phase5_outreach.csv      — 50 personalised emails + LinkedIn DMs

#    data/phase6_ab_variants.csv   — 40 A/B variant messages

```

> **Note:** All output files are pre-built and committed. You can skip directly to reviewing `data/scored_leads.csv` without running any scripts.

---

## Environment Setup

Copy `.env.template` to `.env` and fill in your keys:

```env

APOLLO_API_KEY=your_apollo_key_here

CLAY_API_KEY=your_clay_key_here

OPENAI_API_KEY=your_openai_key_here

GITHUB_TOKEN=your_github_pat_here

```

| Key | Required for | Where to get |
|---|---|---|
| `APOLLO_API_KEY` | Apollo lead sourcing | app.apollo.io †’ Settings †’ API |
| `CLAY_API_KEY` | Clay enrichment | clay.com †’ Account †’ API |
| `OPENAI_API_KEY` | GPT-4 email generation (Phase 5) | platform.openai.com |
| `GITHUB_TOKEN` | GitHub AI repo / star enrichment | github.com †’ Settings †’ Tokens |

---

## Pipeline Stages

### Stage 1 — Sourcing

| Script | Source | Output |
|---|---|---|
| `normalize_apollo.py` | Apollo.io CSV export | `data/raw/apollo_normalized.csv` |
| `normalize_linkedin.py` | LinkedIn Sales Nav pass files | `data/raw/linkedin_normalized.csv` |
| `normalize_seeds.py` | Seed XLS / CSV lists | `data/raw/seeds_normalized.csv` |
| `normalize_engineer_sources.py` | GitHub, Crunchbase, BuiltWith | `data/raw/engineer_normalized.csv` |

All scripts enforce the canonical schema defined in `data/SCHEMA.md`. Key normalisation steps:
- Standardise country †’ `geo_tier` (`US` / `EU_UK` / `APAC` / `ROW`)
- Map funding rounds to stage labels (`Series A–D`, `Bootstrapped`, etc.)
- Flag competitor keywords in company descriptions
- Deduplicate within source (domain + contact_name key)

### Stage 2 — Compilation

`compile_leads.py` merges all normalised sources into `data/raw_leads.csv`:
- Deduplication key: `(domain, contact_name)` — preserves multiple contacts per company
- Source priority order: Apollo > LinkedIn > Seeds > GitHub > Crunchbase
- Emits `data/raw_leads_rejected.csv` for any rows that failed schema validation

### Stage 3 — Pre-filter & Quota Check

`prefilter.py` applies ICP disqualifiers:
- Employee count outside 50–5000 range
- Competitor flags (`competitor_flag = TRUE`)
- Missing `uses_llm_in_prod` signal
- Missing `has_kubernetes` signal
- Geo exclusions (configurable)

`quota_check.py` validates vertical and geo distribution against targets in `icp_framework.md`.

### Stage 4 — Automated Enrichment (Phase 3A & 3B)

The pipeline uses a multi-pass automated enrichment strategy:

1. **Phase 3A (`enrich_pipeline.py`)**: 
   - **GitHub**: Finds org URLs and tech signals (Kubernetes, Ray/WandB).
   - **Apollo**: Enriches firmographics (funding, employee count) and contact technical signals.
2. **Phase 3B (`enrich_3b.py`)**:
   - **Gap Fill**: Targeted re-hits for missing funding data via Apollo and Crunchbase.
   - **Hiring Signal**: Detects `is_hiring_ml_eng` via Job Board scraping (Greenhouse/Lever) and LinkedIn Jobs.

### Stage 5 — Scoring

`scoring_engine.py` computes a 0–130 point ICP score per lead:

| Signal | Max Points |
|---|---|
| Contact title (CTO = 25, VP Eng = 20, Head/Dir = 18) | 25 |
| Uses LLM in production | 20 |
| Funding stage | 20 |
| Employee count (sweet spot 200–2000) | 15 |
| Kubernetes in stack | 8 |
| Ray / WandB in stack | 6 |
| Snowflake in stack | 3 |
| GitHub AI repos | 5 |
| GitHub stars | 4 |
| Cloud / vector stack signals | 4 |
| Geo tier (US = 8, EU/UK = 6) | 8 |
| Active ML hiring signal | 10 |
| Recency bonus (funded < 1 year) | 3 |

Output: `data/scored_leads.csv` with `score_total`, `score_tier` (`Hot`/`Warm`/`Cold`), and `score_reasons`.

### Stage 6 — Outreach Generation (Phase 5)

Personalised outreach for the top 50 Hot leads:

**Cold email** (`email_subject` + `email_body`):
- Hook based on stack signal (vLLM/Triton †’ inference angle, Ray †’ GPU efficiency, OpenAI †’ token cost)
- Hiring signal adds urgency line
- 150–200 word target, soft CTA for 15-minute demo

**LinkedIn DM** (`linkedin_dm`):
- Capped at 300 characters (connection request limit)
- Same stack-personalised hook, condensed to one punch line + ask

Script: `scripts/generate_linkedin_dms.py`

### Stage 7 — A/B Test Design (Phase 6)

Top 20 leads (score >= 88) receive two message variants each:
- **Variant A — Pain-Led:** Opens with a specific technical pain point tied to their stack
- **Variant B — Social Proof / Curiosity:** Opens with a concrete, quantified customer result

Full hypothesis documentation: `ab_test_hypotheses.md`

---

## Data Schema

All lead records conform to the schema defined in `data/SCHEMA.md`.

Core fields:

| Field | Type | Description |
|---|---|---|
| `lead_id` | UUID | Unique identifier |
| `domain` | string | Company domain (primary dedup key) |
| `company_name` | string | Company name |
| `contact_name` | string | Full name |
| `contact_title` | string | Job title |
| `contact_linkedin` | URL | LinkedIn profile URL |
| `contact_email` | email | Work email (if available) |
| `industry` | enum | `SaaS`, `HealthTech`, `FinTech`, `Logistics`, `Cybersec`, `Ecommerce`, `Other` |
| `employee_range` | enum | `50-200`, `201-500`, `501-1000`, `1001-5000` |
| `geo_tier` | enum | `US`, `EU_UK`, `APAC`, `ROW` |
| `funding_stage` | enum | `Series A` … `Series D`, `Bootstrapped`, `Unknown` |
| `uses_llm_in_prod` | bool | TRUE / FALSE |
| `tech_stack_raw` | string | Semicolon-separated stack tokens |
| `has_kubernetes` | bool | Derived from `tech_stack_raw` |
| `has_ray_or_wandb` | bool | Derived from `tech_stack_raw` |
| `is_hiring_ml_eng` | int | LinkedIn ML job postings count |
| `score_total` | int | ICP score (0–130) |
| `score_tier` | enum | `Hot`, `Warm`, `Cold` |

---

## Key Outputs

| File | Rows | Description |
|---|---|---|
| `data/raw_leads.csv` | 350+ | All normalised leads pre-filter |
| `data/raw_leads_rejected.csv` | ~60 | Disqualified leads with reasons |
| `data/enriched_leads.csv` | 291 | Post-Clay enrichment master list |
| `data/scored_leads.csv` | 291 | Scored + tiered, all signals |
| `data/scoring_report.md` | — | Score distribution + top leads summary |
| `data/sourcing_qa_report.md` | — | Vertical / geo quota validation |
| `data/phase5_outreach.csv` | 50 | Email subject, body, LinkedIn DM |
| `data/phase6_ab_variants.csv` | 40 | A/B variant messages for top 20 |
| `ab_test_hypotheses.md` | — | A/B test design + success metrics |
| `icp_framework.md` | — | Full ICP definition + scoring rubric |

---

## ICP & Scoring Framework

Full definition in [`icp_framework.md`](./icp_framework.md).

**Ideal Customer Profile:**
- **Title:** CTO, VP Engineering, Head of AI/ML, Director of Engineering
- **Company size:** 50–5,000 employees
- **Funding:** Series A through D, or bootstrapped with >$10M ARR signals
- **Must-haves:** LLMs in production + Kubernetes in stack
- **Verticals:** SaaS (primary), HealthTech, FinTech, Cybersec, Logistics
- **Geo:** US (primary), EU/UK (secondary)

**Disqualifiers:**
- Competitor companies
- Pre-revenue / pre-product
- Hardware/chip companies (different buyer)
- No discernible LLM workload

---

## A/B Test Design

See [`ab_test_hypotheses.md`](./ab_test_hypotheses.md) for full hypothesis, stack-to-hook mapping, success metrics, and sequencing plan.

**TL;DR:**
- **Variant A (Pain-Led):** Surface the exact GPU/cost pain before pitching
- **Variant B (Social Proof):** Lead with a peer company result (35–45 % cost reduction)
- **Winner declared at:** +5 pp reply rate over 2-week window, 10 sends minimum per variant

---

## Directory Structure

```
LeadForge/
├── README.md                     # This file
├── pipeline.py                   # Master pipeline runner
├── icp_framework.md              # ICP definition + scoring rubric
├── ab_test_hypotheses.md         # Phase 6 A/B test hypotheses
├── requirements.txt              # Python dependencies
├── .env.template                 # API key template (copy to .env)
│
├── data/
│   ├── SCHEMA.md                 # Canonical field definitions
│   ├── raw/                      # Per-source normalised CSVs
│   │   ├── apollo_normalized.csv
│   │   ├── linkedin_normalized.csv
│   │   ├── seeds_normalized.csv
│   │   └── engineer_normalized.csv
│   ├── raw_leads.csv             # Compiled master (pre-filter)
│   ├── raw_leads_rejected.csv    # Disqualified leads
│   ├── enriched_leads.csv        # Post-enrichment master list
│   ├── scored_leads.csv          # Scored + tiered (291 active)
│   ├── scoring_report.md         # Score distribution report
│   ├── sourcing_qa_report.md     # Quota validation report
│   ├── phase5_outreach.csv       # Email + LinkedIn DMs (top 50)
│   └── phase6_ab_variants.csv    # A/B messages (top 20 × 2)
│
├── scripts/
│   ├── normalize_apollo.py        # Stage 1: Apollo normalisation
│   ├── normalize_linkedin.py      # Stage 1: LinkedIn normalisation
│   ├── normalize_seeds.py         # Stage 1: Seed list normalisation
│   ├── normalize_engineer_sources.py # Stage 1: GitHub/Crunchbase
│   ├── normalize_gaps.py          # Stage 1: Gap-fill normalisation
│   ├── compile_leads.py           # Stage 2: Merge + dedup
│   ├── prefilter.py               # Stage 3: Disqualifier filter
│   ├── quota_check.py             # Stage 3: Vertical/geo quota
│   ├── enrich_pipeline.py         # Stage 4: Phase 3A Enrichment
│   ├── enrich_3b.py               # Stage 4: Phase 3B Intent/Gap fill
│   ├── scoring_engine.py          # Stage 5: ICP scoring
│   └── generate_linkedin_dms.py   # Stage 6: LinkedIn DM generation
│
└── docs/
    └── team_roles.md              # Team ownership matrix
```

---

## Team Roles

See [`docs/team_roles.md`](./docs/team_roles.md) for full ownership matrix.

| Role | Owner | Responsibilities |
|---|---|---|
| Data Lead | — | Normalisation, dedup, prefilter, quota |
| Research Lead | — | LinkedIn sourcing, signal enrichment |
| Outreach Lead | — | Phase 5 email + DM copy, A/B design |
| Engineering Lead | — | Scoring engine, pipeline automation |

