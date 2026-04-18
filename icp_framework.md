# P95.AI — Ideal Customer Profile (ICP) Framework

**Project:** P95.AI Lead Engine
**Document:** `icp_framework.md`
**Version:** 1.0
**Last Updated:** 2025
**Owner:** Growth / GTM Engineering

---

## Table of Contents

1. [Product Context](#1-product-context)
2. [Target Persona](#2-target-persona)
3. [Firmographic Criteria](#3-firmographic-criteria)
4. [Positive Signals](#4-positive-signals)
5. [Negative Signals / Disqualifiers](#5-negative-signals--disqualifiers)
6. [Tier Definitions](#6-tier-definitions)
7. [ICP Validation Examples](#7-icp-validation-examples)

---

## 1. Product Context

### What is P95.AI?
P95.AI is an **AI inference performance and cost optimization platform** that helps engineering teams run LLM and ML workloads faster, cheaper, and more reliably in production.

### Core Value Proposition (1 sentence)
> P95.AI cuts AI inference costs by 40–70% and tail latency (p95/p99) by 3–10x, without forcing teams to rewrite their models or rearchitect their stack.

### Top 3 Customer Pain Points We Solve
1. **Runaway inference bills** — GPU costs scaling linearly (or worse) with usage; CFO pressure on unit economics.
2. **Tail latency in production** — p95/p99 spikes breaking SLAs for user-facing AI features (chat, search, agents).
3. **Reliability & observability gaps** — No unified view of model performance across providers (OpenAI, Anthropic, self-hosted, OSS).

### "Aha Moment"
The first time a CTO sees their p95 latency drop from 4.2s to 480ms — and their monthly OpenAI bill drop by 55% — **without changing a single line of model code.**

### Competitive Landscape
Competitors and adjacent players we track (also useful as **signal**: if a prospect uses these, they're AI-infra-mature and buying in this category):

| Company | Category | Relationship |
|---|---|---|
| Baseten | Model deployment | Overlap — possible disqualifier if deeply integrated |
| Modal | Serverless GPU compute | Adjacent — often complementary |
| Anyscale (Ray) | Distributed ML compute | Adjacent — infra layer below us |
| Fireworks AI | Fast inference API | Direct competitor |
| Together AI | Inference + fine-tuning | Direct competitor |
| Replicate | Model hosting | Adjacent — developer-focused |
| RunPod | GPU cloud | Infra layer — complementary |
| Weights & Biases | ML experiment tracking | Adjacent — dev-time, not prod-time |
| Hugging Face (Inference Endpoints) | Model hub + hosting | Adjacent / competitor |

> **Rule of thumb:** Presence of these tools = strong buy signal (company is AI-infra-mature). Deep lock-in with Fireworks/Together = possible disqualifier unless they're feeling cost pain.

---

## 2. Target Persona

### Primary Titles (Decision-Makers)
- **CTO** — Highest priority; owns eng budget + infra strategy
- **VP Engineering** — Owns delivery, reliability, team scale
- **Head of Infrastructure / Head of Platform** — Owns the substrate AI runs on
- **Head of AI / Head of ML** — Emerging title at AI-native companies

### Secondary Titles (Strong Influencers)
- Director of Engineering
- Director of Platform / Infrastructure
- Principal Engineer (Platform/ML)
- Staff Platform Engineer
- Engineering Manager, ML Platform

### Seniority Filter
- Must have **budget authority OR direct line to the budget owner**
- Avoid: IC engineers, junior roles, recruiters, non-technical execs

### Daily Pains (What Keeps Them Up at Night)
- "Our OpenAI bill hit $400K last month and the CFO is asking questions."
- "Our p95 latency is 3.8 seconds and customer support tickets are climbing."
- "We're on-call every other week because inference spikes crash the API."
- "We can't tell if GPT-4o, Claude, or our fine-tuned Llama is actually cheaper per request."
- "We're hiring 4 MLOps engineers just to keep inference infra alive."

### Buying Behavior
- **Discovery:** Hacker News, engineering blogs, peer Slack/Discord communities, conference talks (KubeCon, Ray Summit, AI Engineer Summit), Twitter/X dev community
- **Evaluation:** Peer referrals, GitHub stars, technical benchmarks, POC before purchase
- **Skepticism:** Allergic to "AI-washed" marketing; wants technical depth, benchmarks, reproducible claims
- **Decision speed:** Fast for sub-$50K deals (CTO signs); slower for enterprise (requires procurement + security review)

---

## 3. Firmographic Criteria

### Core Envelope

| Criterion | Target Range | Rationale |
|---|---|---|
| **Headcount** | 200–5,000 employees | Large enough to have infra team + budget; small enough to buy fast |
| **Engineering headcount** | 50+ engineers | Indicates real infra complexity |
| **Funding stage** | Series B → Series D | Capitalized, scaling, feeling cost pressure |
| **Alt: Bootstrapped** | >$20M ARR | Profitable cos with infra spend are great fits |
| **Revenue signal (inferred)** | >$10M ARR | Ensures budget exists |
| **Geography (primary)** | 🇺🇸 United States | Strongest buying signals, easiest to source |
| **Geography (secondary)** | 🇬🇧 UK, 🇪🇺 Western Europe | Second-wave prioritization |

### Vertical Prioritization

Ordered by fit quality — **engineering team size × cloud spend × AI adoption velocity**:

| Priority | Vertical | Why It's a Fit |
|---|---|---|
| **P0** | **SaaS** | Largest eng teams, heaviest cloud usage, AI features shipping fast |
| **P0** | **FinTech** | High spending power, strict latency SLAs, fraud/AI use cases |
| **P1** | **HealthTech** | Growing AI adoption (diagnostics, notes, agents), compliance-driven infra |
| **P1** | **E-commerce** | Search/recommendation/personalization are heavy inference workloads |
| **P2** | **Cybersecurity** | ML-heavy (anomaly detection), but often self-hosted infra preferences |
| **P2** | **Logistics** | Optimization + vision models; smaller eng teams but high-value use cases |

**Quota allocation for sourcing (200 leads):**
- SaaS: 70 leads (35%)
- FinTech: 50 leads (25%)
- HealthTech: 30 leads (15%)
- E-commerce: 25 leads (12.5%)
- Cybersecurity: 15 leads (7.5%)
- Logistics: 10 leads (5%)

### Geo Allocation
- US: **~70%** (~140 leads)
- UK + EU: **~30%** (~60 leads)

---

## 4. Positive Signals

Grouped by category. Each signal becomes a **scoring input** in Phase 4.

### 🧑‍💻 Hiring Signals (Strong Intent)
- Open roles for: **MLOps Engineer**, **Platform Engineer**, **SRE**, **Infrastructure Engineer**, **ML Platform Engineer**, **AI Infrastructure Engineer**, **Staff Engineer, Inference**
- 3+ open infra/ML roles simultaneously = active scaling pain
- JD mentions: "inference", "latency", "GPU", "model serving", "LLM infrastructure"

### 💰 Investor Signals
- Backed by: **YC, a16z, Sequoia, Index Ventures, Benchmark, Accel, Founders Fund, Greylock, Bessemer, Lightspeed, General Catalyst**
- Tier-1 investor = capital + growth mandate = infra pressure

### 🛠️ Tech Stack Signals (Detected via BuiltWith / Job Postings / GitHub)
**High signal (AI-infra mature):**
- Kubernetes, AWS, GCP, Azure
- Ray, vLLM, TGI, Triton Inference Server
- Snowflake, dbt, Databricks
- Kafka, Redis, Pinecone, Weaviate

**Adjacent tools (indicates AI investment):**
- Using Baseten, Modal, Anyscale, Fireworks, Together, RunPod → **AI-native, already buying in category** = excellent signal
- Using Weights & Biases, Hugging Face → ML-mature

### 📦 GitHub Signals
- Public org with ML / LLM / infra repos
- Repos mentioning: `llm`, `inference`, `serving`, `platform`, `ml-ops`
- Active commits in last 90 days
- Engineering blog linked from org README

### 💵 Funding Recency
- Closed round in **last 18 months** (cash = buying power)
- Bonus: Round raised specifically for "scaling AI" / "infrastructure" (per TechCrunch/Crunchbase press)

### ✍️ Content Signals
- Engineering blog posts about: scale, latency, AI in production, inference costs, GPU infrastructure
- Conference talks (KubeCon, Ray Summit, AI Engineer Summit, QCon)
- Open-source projects in the AI infra space

### 📣 Social Signals (LinkedIn / X)
- CTO / VPE posting in last 90 days about:
  - "reliability", "latency", "p95", "p99", "SLA"
  - "AI costs", "inference costs", "GPU", "LLM in production"
  - "we're hiring for platform/ML"
- Engagement with AI infra companies (likes, reposts)

### 📰 News / Press Signals
- Product launch with AI feature in last 6 months
- Expansion announcement (new market, new product line)
- New CTO / VPE hire in last 6 months (new leader = new stack decisions)

---

## 5. Negative Signals / Disqualifiers

**Hard disqualifiers (remove from list entirely):**

| Disqualifier | Reason |
|---|---|
| **<50 employees** | No dedicated infra team, not our buyer |
| **Agency / consultancy / dev shop** | No proprietary product to optimize |
| **Non-technical founder, no eng leadership visible** | No technical buyer |
| **Defense / military contractors** | GTM + compliance friction |
| **Adult content, gambling, crypto-casino** | Brand / compliance risk |
| **Geography: China, Russia, sanctioned regions** | Legal / export restrictions |
| **Already public case study of a direct competitor** | E.g., loud Fireworks/Together customer — deprioritize unless churn signal |

**Soft disqualifiers (deprioritize, don't remove):**
- <$5M funding total (budget risk)
- No engineering blog, no GitHub org, no tech stack signals (low maturity)
- CTO recently departed and not replaced (org in flux)
- Currently in layoffs / restructuring cycle (frozen budgets)

---

## 6. Tier Definitions

Scoring ranges used by `scoring_engine.py` (Phase 4).

| Tier | Score | Definition | Action |
|---|---|---|---|
| 🔥 **Hot** | 80–100 | Strong ICP fit + active pain signals + reachable decision-maker | Priority outreach, A/B tested, personal follow-up |
| 🌡️ **Warm** | 50–79 | Good fit, some signals present, needs nurturing | Standard outreach sequence, monitor for new signals |
| ❄️ **Cold** | 0–49 | Low fit, insufficient data, or missing key signals | Deprioritize; re-evaluate in 6 months |

**Tier distribution target (of 200 leads):**
- 🔥 Hot: 20–30 (10–15%)
- 🌡️ Warm: 80–100 (40–50%)
- ❄️ Cold: 70–100 (35–50%)

---

## 7. ICP Validation Examples

Stress-testing the framework against known companies.

### ✅ Obvious YES

**1. Ramp** (FinTech, ~1,000 employees, Series D)
- ✅ Large eng team, heavy AI usage (transaction categorization, receipt OCR, agents)
- ✅ Known investors (Founders Fund, Sequoia, Thrive)
- ✅ Public engineering blog posts about LLMs in production
- ✅ Hiring ML/platform roles
- **Verdict:** 🔥 Hot candidate

**2. Notion** (SaaS, ~800 employees, Series C)
- ✅ Notion AI in production = serious inference costs
- ✅ Hiring ML platform engineers
- ✅ Engineering blog discusses AI infra decisions
- ✅ Tier-1 investors (Sequoia, Index)
- **Verdict:** 🔥 Hot candidate

**3. Vercel** (DevTools/SaaS, ~500 employees, Series D)
- ✅ v0.dev + AI SDK = massive LLM inference traffic
- ✅ Public about latency-obsessed engineering culture
- ✅ Strong eng leadership presence on X
- **Verdict:** 🔥 Hot candidate

### ❌ Obvious NO

**1. A 10-person digital marketing agency**
- ❌ Too small (<50 employees)
- ❌ Agency model — no product to optimize
- ❌ No infra team, no budget
- **Verdict:** Hard disqualify

**2. Lockheed Martin** (Defense, 120,000+ employees)
- ❌ Defense sector excluded (compliance, GTM friction)
- ❌ Procurement cycle is 12–24 months
- ❌ Buying behavior doesn't match our SMB-to-mid-market motion
- **Verdict:** Hard disqualify

### ⚖️ Edge Case

**A profitable 150-person DevTools startup, bootstrapped, $25M ARR, no press**
- ⚠️ Headcount below 200 floor
- ✅ Revenue signal strong ($25M ARR > $20M bootstrapped threshold)
- ✅ DevTools vertical = technical buyers
- ⚠️ No press / investor signals = harder to source
- **Verdict:** **Include as Warm** — passes the "bootstrapped + >$20M ARR" carve-out. Score will depend on tech stack + hiring signals. A reminder that **headcount alone shouldn't gate the ICP** when revenue is strong.

---

## Document Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025 | Initial framework definition |

---

**Next Phase:** [Phase 2 — Lead Sourcing](./README.md#phase-2)
