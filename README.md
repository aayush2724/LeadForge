# LeadForge — AI-Powered Lead Scoring, Enrichment & Outreach

An end-to-end, reproducible pipeline that sources, normalises, enriches, scores, and generates personalised outreach for 291 qualified enterprise AI/ML leads — from raw data export to ready-to-send email + LinkedIn DM sequences.

**Built for:** P95.AI — an AI inference optimization platform  
**Target buyer:** CTOs, VPs Engineering, Heads of AI at companies running LLMs in production  
**GitHub:** https://github.com/aayush2724/LeadForge

---

## Results at a Glance

| Metric | Value |
|---|---|
| Total active leads | **291** |
| Hot tier (score 65+) | **135** |
| Warm tier (score 40–64) | **57** |
| Cold tier (score <40) | **99** |
| Personalised emails generated | **50** |
| LinkedIn DMs generated | **50** |
| A/B variants designed | **40** (top 20 leads × 2 variants) |
| Pipeline stages | **9** (11/11 passing) |
| Sources | Apollo · LinkedIn Sales Nav · Crunchbase · GitHub · BuiltWith · Seed lists |

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Pipeline Architecture](#pipeline-architecture)
4. [ICP Framework](#icp-framework)
5. [Lead Scoring Model](#lead-scoring-model)
6. [Outreach Generation](#outreach-generation)
7. [A/B Testing Strategy](#ab-testing-strategy)
8. [Tech Stack](#tech-stack)
9. [Quick Start](#quick-start)
10. [Automated Pipeline (n8n)](#automated-pipeline-n8n)
11. [Data Sourcing Guide](#data-sourcing-guide)
12. [Directory Structure](#directory-structure)

---

## Project Overview

LeadForge is an intelligent lead qualification and personalised outreach system built for P95.AI. It combines multi-platform lead sourcing, Clay-powered enrichment, a 9-signal ICP scoring rubric, and GPT-4o outreach generation into a single reproducible Python pipeline — fully automated via n8n.

The system produces a fully enriched, scored, and outreach-ready lead database that can be re-run monthly with fresh data using one command:

```bash
python pipeline.py
```

Or triggered end-to-end in a single click using the n8n workflow.

---

## Problem Statement

P95.AI has a powerful product — an AI inference optimization layer that cuts LLM serving costs 30–45% with zero model changes. The challenge is finding and reaching the right enterprise buyers efficiently.

**Three core problems:**

1. **No signal, no context** — Raw lead lists lack tech stack data, hiring signals, and buying intent. Without enrichment, every outreach message is a guess.

2. **Manual qualification doesn't scale** — Human lead scoring is slow, inconsistent, and expensive. SDRs spend 70%+ of their time researching instead of selling.

3. **Generic outreach fails** — Non-personalised cold emails get ignored, flagged as spam, and permanently damage sender reputation. A CTO running Ray for distributed ML won't respond to a generic pitch.

LeadForge solves all three with a data-driven, signal-aware pipeline.

---

## Pipeline Architecture

```
Raw Sources
    │
    ├── Apollo.io export        → scripts/normalize_apollo.py
    ├── LinkedIn Sales Nav      → scripts/normalize_linkedin.py
    ├── Seed lists              → scripts/normalize_seeds.py
    └── GitHub / Crunchbase /   → scripts/normalize_engineer_sources.py
        BuiltWith
                │
                ▼
    scripts/compile_leads.py
    (merge + dedup by domain)
                │
                ▼
    scripts/prefilter.py
    (hard disqualifiers + competitor detection)
                │
                ▼
    scripts/quota_check.py
    (vertical + geo distribution validation)
                │
                ▼
    Clay enrichment (manual import)
    → data/enriched_leads.csv
                │
                ▼
    scripts/enrich_3b.py
    (hiring signals + funding patch)
                │
                ▼
    scripts/scoring_engine.py
    (115-point ICP score per lead)
                │
                ▼
    data/scored_leads.csv
    (291 active, Hot/Warm/Cold)
                │
        ┌───────┴───────┐
        ▼               ▼
Phase 5 Outreach    Phase 6 A/B Test
phase5_outreach.csv  phase6_ab_variants.csv
(50 leads)           (top 20 × 2 variants)
```

### Stage Summary

| Stage | Script | Output |
|---|---|---|
| 1. Normalize Apollo | `normalize_apollo.py` | `data/raw/apollo_normalized.csv` |
| 2. Normalize LinkedIn | `normalize_linkedin.py` | `data/raw/linkedin_normalized.csv` |
| 3. Normalize Seeds | `normalize_seeds.py` | `data/raw/seeds_normalized.csv` |
| 4. Normalize Engineer Sources | `normalize_engineer_sources.py` | `data/raw/engineer_normalized.csv` |
| 5. Merge + Dedupe | `compile_leads.py` | `data/raw_leads.csv` (297 rows) |
| 6. Pre-filter | `prefilter.py` | `data/raw_leads_rejected.csv` |
| 7. Quota Check | `quota_check.py` | `data/sourcing_qa_report.md` |
| 8. Enrichment Patch | `enrich_3b.py` | `data/enriched_leads.csv` |
| 9. Lead Scoring | `scoring_engine.py` | `data/scored_leads.csv` |
| 10. Outreach Generation | `generate_linkedin_dms.py` | `data/phase5_outreach.csv` |

---

## ICP Framework

Full definition in [`icp_framework.md`](icp_framework.md).

**Target Persona:**
- Title: CTO, VP Engineering, Head of AI/ML, Director of Engineering
- Company size: 200–5,000 employees
- Funding: Series B through D, or bootstrapped with >$20M ARR
- Must-haves: LLMs in production + cloud infrastructure
- Verticals: SaaS (primary), FinTech, HealthTech, Cybersec, Logistics
- Geo: US (primary), EU/UK (secondary), India seed-only

**Hard Disqualifiers:**
- Competitor platforms: Baseten, Modal, Anyscale, Fireworks, Together, Replicate, RunPod, HuggingFace
- Under 50 employees
- Government or defense
- No discernible LLM workload

**Tier Thresholds:**
- Hot: 65+ points
- Warm: 40–64 points
- Cold: under 40 points

---

## Lead Scoring Model

Each lead is scored 0–115 across 9 signals:

| Signal | Max Points | Logic |
|---|---|---|
| Contact title | 25 | CTO=25, VP Eng=20, Head/Dir=18 |
| Uses LLM in production | 20 | TRUE=20 |
| Funding stage | 20 | Series C=20, Series B=15, Series D=12 |
| Employee count | 15 | 501–2000=15, 201–500=12, 2001–5000=10 |
| Active ML hiring | 10 | Hiring ML engineers detected |
| Kubernetes in stack | 8 | TRUE=8 |
| Geo tier | 8 | US=8, EU/UK=6, India=4 |
| Ray / WandB in stack | 6 | TRUE=6 |
| GitHub AI repos | 3 | Active public AI/infra repos |

**Top scoring lead:** Vaibhav Nivargi — Moveworks CTO — **115/115**

---

## Outreach Generation

Personalised outreach for the top 50 Hot leads using per-lead signal context.

**Cold email structure:**
- Hook based on detected tech stack signal (Ray → GPU efficiency, Kubernetes → infra scale)
- Hiring signal adds urgency line
- 150–200 word target, soft CTA for 15-minute demo

**LinkedIn DM structure:**
- Capped at 300 characters
- Same stack-personalised hook, condensed to one punch line + ask

**Sample email — Vaibhav Nivargi, Moveworks:**
```
Subject: GPU efficiency at Moveworks scale

Hi Vaibhav,

Noticed Moveworks runs Ray for distributed ML — GPU efficiency at scale
is a real challenge. You're also hiring ML engineers, which tells me
inference demand is growing.

I'm building P95.AI, an inference optimization layer that cuts LLM
serving costs 30–45% with zero model changes.

Worth a 15-minute call to see if it fits your stack?
```

---

## A/B Testing Strategy

Top 20 leads (score 88+) receive two message variants each.

| | Variant A — Pain-Led | Variant B — Social Proof |
|---|---|---|
| Hook | Specific GPU/cost pain tied to their stack | Peer company quantified result |
| Subject example | "Your Ray cluster is probably leaving 30% GPU capacity on the table" | "How a Series C AI company cut inference costs 40% in 3 weeks" |
| Target reply rate | 12% | 10% |
| Target open rate | 45% | 50% |
| Hypothesis | High-urgency, problem-aware buyers respond better | Curious/research-mode buyers engage with social proof |

Full hypothesis documentation: [`ab_test_hypotheses.md`](ab_test_hypotheses.md)

**Winner declared at:** +5pp reply rate over 2-week window, minimum 10 sends per variant.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Pipeline scripting, data processing |
| pandas | Data normalization, dedup, scoring |
| Clay.com | Lead enrichment backbone — tech stack, hiring, funding, LinkedIn signals |
| Apollo.io | Primary lead sourcing (80 leads) |
| LinkedIn Sales Navigator | High-recency contact sourcing (60 leads) |
| Crunchbase | Funding and firmographic data |
| GitHub API | Engineering signal detection — AI/infra repos |
| BuiltWith | Tech stack detection — Kubernetes, Snowflake, Ray, WandB |
| GPT-4o (OpenAI) | Personalised outreach generation |
| n8n | Full pipeline automation and orchestration |
| python-dotenv | API key management |
| tqdm + rich | Progress tracking and CLI output |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/aayush2724/LeadForge
cd LeadForge

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.template .env
# Edit .env and add your keys

# 5. Run the full pipeline
python pipeline.py
```

> **Note:** All output files are pre-built and committed. You can skip directly to reviewing `data/scored_leads.csv` without running any scripts.

### Required API Keys

| Key | Required for | Where to get |
|---|---|---|
| `APOLLO_API_KEY` | Apollo sourcing | app.apollo.io → Settings → API |
| `OPENAI_API_KEY` | GPT-4o outreach generation | platform.openai.com |
| `GITHUB_TOKEN` | GitHub AI repo enrichment | github.com → Settings → Tokens |
| `CLAY_API_KEY` | Clay enrichment | clay.com → Account → API |

---

## Automated Pipeline (n8n)

The full pipeline is automated via n8n, allowing one-click end-to-end execution without touching the command line.

### Setup

**Step 1 — Install n8n**
```bash
npm install -g n8n
```

**Step 2 — Set environment variable**

On Windows (run PowerShell as Administrator):
```powershell
[System.Environment]::SetEnvironmentVariable("NODE_FUNCTION_ALLOW_BUILTIN", "child_process", "User")
[System.Environment]::SetEnvironmentVariable("NODE_FUNCTION_ALLOW_EXTERNAL", "child_process", "User")
```

On Mac/Linux:
```bash
export NODE_FUNCTION_ALLOW_BUILTIN=child_process
export NODE_FUNCTION_ALLOW_EXTERNAL=child_process
```

**Step 3 — Start n8n from the project root**
```bash
cd LeadForge
n8n start
```

**Step 4 — Import the workflow**
- Open `http://localhost:5678`
- Go to Workflows → Import
- Select `workflows/leadforge_pipeline.json`

**Step 5 — Execute**
- Click **Execute Workflow**
- All 12 pipeline nodes run in sequence automatically

### Workflow Nodes

```
Manual Trigger
      ↓
Compile Leads           ← compile_leads.py
      ↓
Normalize Apollo        ← normalize_apollo.py
      ↓
Normalize LinkedIn      ← normalize_linkedin.py
      ↓
Normalize Seeds         ← normalize_seeds.py
      ↓
Normalize Gaps          ← normalize_gaps.py
      ↓
Enrich Pipeline         ← enrich_pipeline.py
      ↓
Prefilter Competitors   ← prefilter.py
      ↓
Score Leads             ← scoring_engine.py
      ↓
Validate Emails         ← validate_emails.py
      ↓
Generate LinkedIn DMs   ← generate_linkedin_dms.py
      ↓
Sanity Check            ← validate_row.py
```

Each node outputs `{ success: true, output: "..." }` — visible in the n8n execution log for full auditability.

---

## Data Sourcing Guide

Lead sourcing from Apollo.io and LinkedIn Sales Navigator requires manual CSV export due to platform API restrictions on free/standard plans. All exported files are included in `data/raw/` so the full pipeline can be re-run without re-sourcing.

### To re-source fresh leads:

**Apollo.io (target: 80 leads)**
- Go to apollo.io → Search → People
- Job titles: CTO, VP Engineering, Head of AI, Director of Engineering
- Headcount: 200–5,000
- Industries: Computer Software, Financial Services, Healthcare
- Keywords: machine learning, LLM, AI inference, GPU, generative AI
- Exclude: baseten.co, modal.com, anyscale.com, fireworks.ai, together.ai, replicate.com
- Export CSV → save to `data/raw/apollo_pass1_*.csv`

**LinkedIn Sales Navigator (target: 60 leads)**
- Go to Sales Navigator → Lead Filters
- Same job titles as above
- Seniority: VP, CXO, Director
- Headcount: 200–5,000
- Activity: Posted on LinkedIn
- Geography: US, UK, Germany, France, Netherlands, India
- Save list → export → save to `data/raw/linkedin_pass*.csv`

**After re-sourcing:**
```bash
python pipeline.py
```

---

## Key Output Files

| File | Rows | Description |
|---|---|---|
| `data/raw_leads.csv` | 297 | All normalised leads pre-filter |
| `data/raw_leads_rejected.csv` | 6 | Disqualified leads with reasons |
| `data/enriched_leads.csv` | 297 | Post-Clay enrichment master list |
| `data/scored_leads.csv` | 291 | Scored + tiered, all signals |
| `data/scoring_report.md` | — | Score distribution + top leads |
| `data/sourcing_qa_report.md` | — | Vertical/geo quota validation |
| `data/phase5_outreach.csv` | 50 | Email subject, body, LinkedIn DM |
| `data/phase6_ab_variants.csv` | 40 | A/B variant messages for top 20 |
| `ab_test_hypotheses.md` | — | A/B test design + success metrics |
| `icp_framework.md` | — | Full ICP definition + scoring rubric |

---

## Directory Structure

```
LeadForge/
├── README.md
├── icp_framework.md
├── ab_test_hypotheses.md
├── requirements.txt
├── .env.template
├── pipeline.py
│
├── workflows/
│   └── leadforge_pipeline.json     ← n8n workflow (import to re-run)
│
├── data/
│   ├── SCHEMA.md
│   ├── raw/
│   │   ├── apollo_normalized.csv
│   │   ├── linkedin_normalized.csv
│   │   ├── seeds_normalized.csv
│   │   └── engineer_normalized.csv
│   ├── raw_leads.csv
│   ├── raw_leads_rejected.csv
│   ├── enriched_leads.csv
│   ├── scored_leads.csv
│   ├── scoring_report.md
│   ├── sourcing_qa_report.md
│   ├── phase5_outreach.csv
│   └── phase6_ab_variants.csv
│
├── scripts/
│   ├── normalize_apollo.py
│   ├── normalize_linkedin.py
│   ├── normalize_seeds.py
│   ├── normalize_engineer_sources.py
│   ├── normalize_gaps.py
│   ├── compile_leads.py
│   ├── prefilter.py
│   ├── quota_check.py
│   ├── enrich_3b.py
│   ├── enrich_pipeline.py
│   ├── scoring_engine.py
│   ├── generate_linkedin_dms.py
│   ├── validate_emails.py
│   └── validate_row.py
│
└── docs/
    └── team_roles.md
```
