# P95.AI — Ideal Customer Profile (ICP) Framework

**Project:** P95.AI Lead Engine
**Document:** `icp_framework.md`
**Version:** 1.1
**Last Updated:** 2025
**Owner:** Growth / GTM Engineering

---

## Table of Contents

1. [Product Context](#1-product-context)
2. [Target Persona](#2-target-persona)
3. [Firmographic Criteria](#3-firmographic-criteria)
   - 3.1 [Core Envelope](#31-core-envelope)
   - 3.2 [Vertical Prioritization & Sourcing Quotas](#32-vertical-prioritization--sourcing-quotas)
   - 3.3 [Geographic Allocation](#33-geographic-allocation)
   - 3.4 [Seed Company List (Must-Include)](#34-seed-company-list-must-include)
4. [Positive Signals](#4-positive-signals)
5. [Negative Signals / Disqualifiers](#5-negative-signals--disqualifiers)
6. [Tier Definitions](#6-tier-definitions)
7. [ICP Validation Examples](#7-icp-validation-examples)
8. [Document Changelog](#8-document-changelog)

---

## 1. Product Context

### What is P95.AI?
P95.AI is an **AI inference optimization platform** built for enterprise teams running LLMs and agentic systems in production. We reduce p95 latency, improve throughput, and lower cost per token — without forcing teams to rewrite models or rearchitect their stack.

### Core Value Proposition (1 sentence)
> P95.AI delivers faster inference, lower GPU/cloud spend, and better P95 latency for enterprise AI workloads — turning inference economics from a runaway cost center into a competitive advantage.

### Why Now: The Inference Economy Shift
The industry's center of gravity has moved from **training performance** to **inference economics**. Training is a one-time cost; inference is a recurring, compounding one. Serving LLMs and agents reliably, cheaply, and fast at scale is now the defining infrastructure challenge for enterprise AI.

### Flagship Capabilities (use verbatim in outreach copy)
- **P95 latency optimization** — tail-latency engineering for real-time AI
- **Cost-efficient LLM serving** — lower $/token, lower $/request
- **GPU utilization efficiency** — higher throughput per GPU-hour
- **Enterprise-grade inference observability** — unified view across providers
- **Real-time AI application support** — copilots, chatbots, RAG, fraud detection, recommendations, document processing

### Top 3 Customer Pain Points
1. **Runaway inference bills** — GPU / API costs scaling faster than revenue; CFO pressure on unit economics.
2. **Tail latency in production** — p95 / p99 spikes breaking real-time SLAs for user-facing AI features.
3. **Observability gaps** — no unified view of cost, latency, and reliability across OpenAI, Anthropic, self-hosted, and OSS models.

### "Aha Moment"
The first time a CTO sees p95 latency drop from 4.2s → 480ms and monthly inference spend cut by 55% — **without changing a single line of model code.**

### Competitive Landscape (Treated as DISQUALIFIERS)
Companies locked into these stacks are **not** target leads — they are either direct competitors or are already solving the inference problem in-house:

| Company | Category | Why Disqualifier |
|---|---|---|
| Baseten | Model deployment | Direct competitor |
| Modal | Serverless GPU compute | Direct competitor |
| Anyscale | Ray-based inference | Direct competitor |
| Fireworks AI | Fast inference API | Direct competitor |
| Together AI | Inference + fine-tuning | Direct competitor |
| Replicate | Model hosting | Adjacent competitor |
| RunPod | GPU cloud | Adjacent — light disqualifier |
| Hugging Face (Inference Endpoints) | Model hosting | Adjacent competitor |

**Adjacent / complementary tools (NOT disqualifiers — often positive signals):**
- Weights & Biases — dev-time experiment tracking (complementary)
- Databricks, Snowflake, dbt — data stack (complementary)
- Kubernetes, AWS, GCP, Azure — substrate (strong positive signal)

---

## 2. Target Persona

### Primary Titles (Decision-Makers)
- **CTO** — Highest priority; owns engineering budget + infrastructure strategy
- **VP Engineering** — Owns delivery, reliability, team scale
- **Head of Infrastructure / Head of Platform** — Owns the substrate AI runs on
- **Head of AI / Head of ML** — Emerging title at AI-native companies

### Secondary Titles (Strong Influencers)
- Director of Engineering
- Director of Platform / Infrastructure
- Principal Engineer (Platform / ML)
- Staff Platform Engineer
- Engineering Manager, ML Platform

### Seniority Filter
- Must have **budget authority OR a direct line to the budget owner**
- Avoid: individual-contributor engineers, junior roles, recruiters, non-technical executives

### Daily Pains (What Keeps Them Up at Night)
- "Our OpenAI bill hit $400K last month and the CFO is asking questions."
- "Our p95 latency is 3.8 seconds and customer support tickets are climbing."
- "We're on-call every other week because inference spikes crash the API."
- "We can't tell if GPT-4o, Claude, or our fine-tuned Llama is actually cheaper per request."
- "We're hiring 4 MLOps engineers just to keep inference infra alive."

### Buying Behavior
- **Discovery:** Hacker News, engineering blogs, peer Slack/Discord communities, conference talks (KubeCon, Ray Summit, AI Engineer Summit), Twitter/X developer community
- **Evaluation:** Peer referrals, GitHub stars, technical benchmarks, POC before purchase
- **Skepticism:** Allergic to "AI-washed" marketing; wants technical depth, benchmarks, reproducible claims
- **Decision speed:** Fast for sub-$50K deals (CTO signs); slower for enterprise (requires procurement + security review)

---

## 3. Firmographic Criteria

### 3.1 Core Envelope

| Criterion | Target Range | Rationale |
|---|---|---|
| **Headcount** | 200–5,000 employees | Large enough for an infra team + budget; small enough to buy quickly |
| **Engineering headcount** | 50+ engineers | Indicates real infrastructure complexity |
| **Funding stage** | Series B → Series D | Capitalized, scaling, feeling cost pressure |
| **Alt: Bootstrapped** | >$20M ARR | Profitable companies with infra spend are great fits |
| **Revenue signal (inferred)** | >$10M ARR | Ensures budget exists |
| **Geography (primary)** | 🇺🇸 United States | Strongest buying signals, easiest to source |
| **Geography (secondary)** | 🇬🇧 UK, 🇪🇺 Western Europe | Second-wave prioritization |
| **Geography (seed-only)** | 🇮🇳 India | Seed companies only; capped at ~10% |

### 3.2 Vertical Prioritization & Sourcing Quotas

Ordered by fit quality — **engineering team size × cloud spend × AI adoption velocity**.

| Priority | Vertical | Quota | % of Total |
|---|---|---|---|
| P0 | **SaaS** | 45 | 22.5% |
| P0 | **FinTech** | 30 | 15.0% |
| P1 | **HealthTech** | 20 | 10.0% |
| P1 | **E-commerce** | 15 | 7.5% |
| P2 | **Cybersecurity** | 15 | 7.5% |
| P2 | **Logistics** | 15 | 7.5% |
| — | **Subtotal (vertical-quota)** | **140** | **70%** |
| — | **Flex / opportunistic** (AI-native, DevTools) | **60** | **30%** |
| — | **Total** | **200** | **100%** |

The 30% flex bucket absorbs high-signal AI-native companies that don't cleanly fit a vertical but match every other ICP dimension.

### 3.3 Geographic Allocation

| Region | Leads | % | Notes |
|---|---|---|---|
| 🇺🇸 United States | ~120 | 60% | Primary market |
| 🇬🇧🇪🇺 UK + Western Europe | ~60 | 30% | Secondary market |
| 🇮🇳 India (seed only) | ~20 | 10% | Restricted to seed-company list |

### 3.4 Seed Company List (Must-Include)

Pre-validated strong-fit anchors. Include in the 200-lead list and source CTO / VPE / Head of Platform contacts.

**SaaS / DevTools / Productivity**
- Notion, Canva, Figma, HubSpot, Rippling, Datadog, Cloudflare

**FinTech**
- Stripe, Brex, Razorpay, PhonePe

**E-commerce / Marketplaces / Q-commerce**
- Swiggy, Zomato, Meesho, Zepto

**Rationale:** High-visibility ICP-fit companies. Judges will recognize them, and their public engineering culture provides rich signal surface for personalized outreach. India-based companies are an intentional exception to the US/EU geo focus — justified by strong engineering teams, heavy AI investment, and brand recognition.

---

## 4. Positive Signals

Grouped by category. Each signal becomes a **scoring input** in Phase 4.

### 🧑‍💻 Hiring Signals (Strong Intent)
- Open roles: **MLOps Engineer**, **Platform Engineer**, **SRE**, **Infrastructure Engineer**, **ML Platform Engineer**, **AI Infrastructure Engineer**, **Staff Engineer, Inference**
- 3+ open infra/ML roles simultaneously = active scaling pain
- JD mentions: "inference", "latency", "GPU", "model serving", "LLM infrastructure"

### 💰 Investor Signals
- Backed by: **YC, a16z, Sequoia, Index Ventures, Benchmark, Accel, Founders Fund, Greylock, Bessemer, Lightspeed, General Catalyst**
- Tier-1 investor = capital + growth mandate = infra pressure

### 🛠️ Tech Stack Signals (via BuiltWith / Job Postings / GitHub)

**High signal (AI-infra mature):**
- Kubernetes, AWS, GCP, Azure
- Ray, vLLM, TGI, Triton Inference Server
- Snowflake, dbt, Databricks
- Kafka, Redis, Pinecone, Weaviate

**Adjacent tools (indicates AI investment — positive signal):**
- Weights & Biases, Hugging Face Hub (non-Inference-Endpoints) → ML-mature
- OpenAI / Anthropic API usage at scale → inference cost pain likely

### 📦 GitHub Signals
- Public org with ML / LLM / infra repos
- Repos mentioning: `llm`, `inference`, `serving`, `platform`, `ml-ops`
- Active commits in last 90 days
- Engineering blog linked from org README

### 💵 Funding Recency
- Closed round in **last 18 months** (cash = buying power)
- Bonus: Round raised specifically for "scaling AI" / "infrastructure" (per TechCrunch / Crunchbase press)

### ✍️ Content Signals
- Engineering blog posts about: scale, latency, AI in production, inference costs, GPU infrastructure
- Conference talks (KubeCon, Ray Summit, AI Engineer Summit, QCon)
- Open-source projects in the AI infra space

### 📣 Social Signals (LinkedIn / X)
- CTO / VPE posting in last 90 days about:
  - "reliability", "latency", "p95", "p99", "SLA"
  - "AI costs", "inference costs", "GPU", "LLM in production"
  - "we're hiring for platform / ML"
- Engagement with AI-infra companies (likes, reposts)

### 📰 News / Press Signals
- Product launch with AI feature in last 6 months
- Expansion announcement (new market, new product line)
- New CTO / VPE hire in last 6 months (new leader = new stack decisions)

---

## 5. Negative Signals / Disqualifiers

### Hard Disqualifiers (remove from list entirely)

| Disqualifier | Reason |
|---|---|
| **<50 employees** | No dedicated infra team; not our buyer |
| **Agency / consultancy / dev shop** | No proprietary product to optimize |
| **Non-technical founder, no engineering leadership visible** | No technical buyer |
| **Direct P95.AI competitor** (Baseten, Modal, Anyscale, Fireworks, Together, Replicate) | Competitive conflict |
| **Companies heavily locked into in-house inference stack** | Low conversion probability |
| **Government / public-sector / defense contractors** | Procurement friction, non-ICP |
| **Adult content, gambling, crypto-casino** | Brand / compliance risk |
| **Geography: China, Russia, sanctioned regions** | Legal / export restrictions |
| **Loud public case study of a direct competitor** | Deprioritize unless churn signal present |

### Soft Disqualifiers (deprioritize, don't remove)
- <$5M funding total (budget risk)
- No engineering blog, no GitHub org, no tech-stack signals (low maturity)
- CTO recently departed and not replaced (org in flux)
- Currently in layoffs / restructuring cycle (frozen budgets)

---

## 6. Tier Definitions

Scoring ranges used by `scoring_engine.py` in Phase 4.

| Tier | Score | Definition | Action |
|---|---|---|---|
| 🔥 **Hot** | 80–100 | Strong ICP fit + active pain signals + reachable decision-maker | Priority outreach, A/B tested, personal follow-up |
| 🌡️ **Warm** | 50–79 | Good fit, some signals present, needs nurturing | Standard outreach sequence, monitor for new signals |
| ❄️ **Cold** | 0–49 | Low fit, insufficient data, or missing key signals | Deprioritize; re-evaluate in 6 months |

**Target distribution across 200 leads:**
- 🔥 Hot: 20–30 (10–15%)
- 🌡️ Warm: 80–100 (40–50%)
- ❄️ Cold: 70–100 (35–50%)

---

## 7. ICP Validation Examples

Stress-testing the framework against known companies.

### ✅ Obvious YES

**1. Ramp** (FinTech, ~1,000 employees, Series D)
- ✅ Large engineering team; heavy AI usage (transaction categorization, receipt OCR, agents)
- ✅ Tier-1 investors (Founders Fund, Sequoia, Thrive)
- ✅ Public engineering blog posts about LLMs in production
- ✅ Hiring ML / platform roles
- **Verdict:** 🔥 Hot candidate

**2. Notion** (SaaS, ~800 employees, Series C)
- ✅ Notion AI in production = serious inference costs
- ✅ Hiring ML platform engineers
- ✅ Engineering blog discusses AI infra decisions
- ✅ Tier-1 investors (Sequoia, Index)
- **Verdict:** 🔥 Hot candidate

**3. Vercel** (DevTools / SaaS, ~500 employees, Series D)
- ✅ v0.dev + AI SDK = massive LLM inference traffic
- ✅ Public about latency-obsessed engineering culture
- ✅ Strong engineering leadership presence on X
- **Verdict:** 🔥 Hot candidate

### ❌ Obvious NO

**1. A 10-person digital marketing agency**
- ❌ Too small (<50 employees)
- ❌ Agency model — no product to optimize
- ❌ No infra team, no budget
- **Verdict:** Hard disqualify

**2. Lockheed Martin** (Defense, 120,000+ employees)
- ❌ Defense sector excluded (compliance + GTM friction)
- ❌ Procurement cycle is 12–24 months
- ❌ Buying behavior doesn't match our SMB-to-mid-market motion
- **Verdict:** Hard disqualify

### ⚖️ Edge Case

**A profitable 150-person DevTools startup, bootstrapped, $25M ARR, no press**
- ⚠️ Headcount below 200 floor
- ✅ Revenue signal strong ($25M ARR > $20M bootstrapped threshold)
- ✅ DevTools vertical = technical buyers
- ⚠️ No press / investor signals = harder to source
- **Verdict:** **Include as Warm** — passes the "bootstrapped + >$20M ARR" carve-out. Score will depend on tech stack + hiring signals. Demonstrates that **headcount alone shouldn't gate the ICP** when revenue is strong.

---

## 8. Document Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | 2025 | Initial framework definition |
| 1.1 | 2025 | Refined product positioning (inference economy framing, flagship capabilities). Updated vertical quotas (SaaS 45, FinTech 30, HealthTech 20, E-com 15, Cybersec 15, Logistics 15). Added §3.4 seed company list with India geo carve-out. Moved Baseten/Modal/Anyscale/Fireworks/Together from "landscape" to hard disqualifiers. |

---

**Next Phase:** [Phase 2 — Lead Sourcing](./README.md#phase-2)
