# P95.AI Lead Engine — Phase 6: A/B Outreach Hypotheses

**Generated:** 2026-04-18  
**Scope:** Top 20 Hot leads (score >= 92) from `data/scored_leads.csv`  
**Output:** `data/phase6_ab_variants.csv` — 40 rows (20 leads �- 2 variants each)

---

## Overview

Phase 6 tests two distinct outreach messaging frameworks across the top 20 leads.
Each lead receives both a **Variant A** and a **Variant B** message with different
psychological openers. The goal is to determine which frame generates higher
reply rates when deployed via a sequencing tool (Apollo, Outreach, or HubSpot Sequences).

---

## Variant Definitions

### Variant A — Pain-Led

> **Hypothesis:** Opening with a specific, technically credible pain point (tied to the
> lead's exact stack) creates urgency before the product pitch. CTOs who recognize their
> own infrastructure problem in the first sentence are more likely to continue reading.

**Structure:**
1. **Hook** — Name a specific, stack-matched problem (e.g. GPU underutilization on vLLM,
   token cost growth on OpenAI, idle time on Ray clusters)
2. **Solution** — One-sentence product description focused on outcome, not features
3. **Proof** — "No model changes. No re-architecture. Deploys in under a day."
4. **CTA** — Soft ask: 15-minute demo, framed as showing their numbers

**Why it might win:**  
Technical buyers (CTOs, VPs Eng) have high BS filters. Naming their exact problem
before pitching the solution signals domain expertise and earns trust. Pain + urgency
often outperforms curiosity in cold outreach to engineering leaders.

**Risk:**  
If the pain assumption is wrong (e.g. they've already solved GPU utilization), the
message misses. Also risks feeling presumptuous.

---

### Variant B — Curiosity / Social Proof

> **Hypothesis:** Leading with a concrete, quantified customer result (specific to their
> stack profile) triggers FOMO and lowers skepticism. CTOs are competitive — a peer
> company result that maps to their exact situation is more compelling than a generic pitch.

**Structure:**
1. **Hook** — A specific customer result ("a Ray-native ML platform cut GPU spend 35%..."),
   tied to a signal from the lead's stack
2. **Solution** — P95.AI framed as the mechanism behind the result
3. **Relevance bridge** — "Given [Company]'s footprint in production AI..."
4. **CTA** — Explicit calendar link for a 15-minute demo

**Why it might win:**  
Social proof reduces perceived risk. Quantified results ("35% GPU spend reduction",
"800ms → sub-200ms p95") are more concrete than problem framing. Works well with
leads who may not actively feel pain but are open to optimization.

**Risk:**  
If the result feels generic or the "customer" profile doesn't closely match, it can
feel like templated outreach. The curiosity hook depends on credibility.

---

## Stack-to-Hook Mapping

Each variant's hook is personalized based on tech stack signals detected during enrichment:

| Stack Signal | Variant A Pain Hook | Variant B Social Proof Hook |
|---|---|---|
| `vLLM` or `Triton` | GPU underutilization at 60-70% before traffic spikes | "A vLLM user went from 800ms p95 to sub-200ms, -30% GPU footprint" |
| `Ray` | GPU idle time compounds on uneven LLM serving | "A Ray-native ML platform cut GPU spend 35%, 3x concurrent requests" |
| `OpenAI` or `Anthropic` | Token costs grow faster than revenue at scale | "An enterprise SaaS cut LLM inference costs 40%, sub-200ms p95" |
| `HealthTech` vertical | — | "A HealthTech platform cut inference latency 62%, -38% GPU spend" |
| `FinTech` vertical | — | "A Series C FinTech reduced LLM serving costs 41% in 3 weeks" |
| `Logistics` vertical | — | "A logistics platform dropped inference costs 44%, tail latency halved" |
| Default | Running LLMs in prod means inference costs and latency are live problems | "An enterprise AI team cut LLM inference costs 40% in two weeks" |

---

## Lead Selection Criteria

Top 20 leads selected by `score_total` descending from `scored_leads.csv`,
filtered to `disqualified = FALSE` and `score_tier = Hot`.

| Rank | Name | Company | Title | Score | Key Signals |
|---|---|---|---|---|---|
| 1 | Vaibhav Nivargi | Moveworks | CTO | 115 | vLLM, Ray, K8s, hiring ML |
| 2 | Kevin Stumpf | Tecton | CTO | 112 | Ray, K8s, Snowflake, hiring ML |
| 3 | Braden Hancock | Snorkel AI | CTO | 112 | vLLM, WandB, K8s, hiring ML |
| 4 | Brian Rieger | Labelbox | CTO | 112 | OpenAI, K8s, hiring ML |
| 5 | Gautham Viswanathan | Workato | CTO | 110 | OpenAI, K8s, Snowflake, hiring ML |
| 6 | Tim Shi | Cresta | CTO | 107 | vLLM, K8s, hiring ML |
| 7 | Andy Beck | PathAI | CTO | 107 | OpenAI, K8s, hiring ML |
| 8 | Julien Chaumond | Hugging Face | CTO | 105 | vLLM, Ray, WandB, K8s |
| 9 | Anant Bhardwaj | Instabase | CTO | 105 | OpenAI, K8s, hiring ML |
| 10 | Ion Stoica | Anyscale | CTO | 102 | Ray, vLLM, K8s |
| 11 | Spence Green | Lilt | CTO | 100 | OpenAI, K8s, hiring ML |
| 12 | Param Reddy | Observe.AI | CTO | 100 | vLLM, K8s, hiring ML |
| 13 | Shyam Rajaram | Zendesk | VP Engineering | 98 | OpenAI, K8s, Snowflake, hiring ML |
| 14 | Naman Jain | Samsara | VP Engineering | 97 | Ray, K8s, hiring ML |
| 15 | Ajay Kulkarni | Timescale | CTO | 95 | OpenAI, K8s, Snowflake |
| 16 | Deval Shah | Chargebee | CTO | 95 | OpenAI, K8s, hiring ML |
| 17 | Eric Sammer | Imply | CTO | 93 | Ray, K8s, hiring ML |
| 18 | Nik Bhatia | Uniphore | CTO | 92 | vLLM, K8s, hiring ML |
| 19 | Sriram Raghavan | IBM Research | VP AI | 90 | vLLM, WandB, K8s |
| 20 | Shivaram Venkataraman | Databricks | VP Engineering | 88 | Ray, WandB, K8s, Snowflake |

---

## Success Metrics

To declare a winning variant, measure the following after a 2-week send window:

| Metric | Target | Winner Threshold |
|---|---|---|
| Open rate | > 50% both variants | — |
| Reply rate | > 15% for winner | +5pp over loser |
| Positive reply rate | > 8% | +3pp over loser |
| Meeting booked rate | > 5% | +2pp over loser |

**Minimum sample for significance:** 10 sends per variant (we have 20 per variant).

---

## Sequencing Recommendation

1. **Day 0** — Send Variant A or B (randomly assigned, 10 leads each)
2. **Day 3** — LinkedIn connection request with personalized note (from `phase5_outreach.csv` → `linkedin_dm`)
3. **Day 7** — Follow-up email if no reply: "Saw you're still hiring ML engineers..."
4. **Day 14** — Final bump: share a relevant inference benchmark or blog post

---

## Files

| File | Description |
|---|---|
| `data/phase6_ab_variants.csv` | 40 rows: 20 leads �- 2 variants, with full message bodies |
| `data/phase5_outreach.csv` | 50 leads with `email_body` + `linkedin_dm` for sequence step 2 |
| `data/scored_leads.csv` | Full scored lead list for expanding the test to Warm tier |

---

## Next Steps After Test

- **If A wins:** Expand pain-led messaging to all 91 Hot leads in `scored_leads.csv`
- **If B wins:** Expand social proof messaging with vertical-specific proof points
- **If no winner:** Combine hooks (lead with result, follow up with pain frame in day-7 touch)
