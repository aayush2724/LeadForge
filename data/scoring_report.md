# P95.AI Lead Engine — Scoring Report

**Generated:** 2026-04-18 19:06 UTC  
**Source:** `enriched_leads.csv`  
**Active leads scored:** 291  

---

## Tier Distribution

| Tier | Count | % of Active |
|---|---|---|
| 🔥 Hot  (80–100) | 91  | 31.3% |
| 🌡️ Warm (50–79)  | 101 | 34.7% |
| ❄️ Cold (0–49)   | 99 | 34.0% |

## Score Distribution

| Metric | Value |
|---|---|
| Mean score  | 65.7 |
| Median score | 74 |
| Min score   | 25 |
| Max score   | 91 |

## Dimension Averages (out of max)

| Dimension | Avg Score | Max |
|---|---|---|
| A — Firmographic    | 28.0 | 35 |
| B — AI/Infra signals | 18.6 | 35 |
| C — Persona          | 18.5 | 20 |
| D — Growth/intent    | 0.5 | 10 |

## Tier Breakdown by Vertical

| Vertical | Hot | Warm | Cold | Total |
|---|---|---|---|---|
| SaaS | 40 | 38 | 19 | 97 |
| FinTech | 1 | 8 | 47 | 56 |
| HealthTech | 5 | 9 | 8 | 22 |
| Ecommerce | 1 | 2 | 12 | 15 |
| Cybersec | 5 | 6 | 4 | 15 |
| Logistics | 2 | 4 | 9 | 15 |
| Other | 37 | 34 | 0 | 71 |

## 🔥 Top 20 Hot Leads

```
    company_name             contact_name  contact_title   industry score_total             domain
       Moveworks          Vaibhav Nivargi            CTO       SaaS          90      moveworks.com
          Tecton             Kevin Stumpf            CTO      Other          90          tecton.ai
      Snorkel AI           Braden Hancock            CTO      Other          90         snorkel.ai
        Labelbox             Brian Rieger            CTO      Other          86       labelbox.com
         Workato      Gautham Viswanathan            CTO       SaaS          85        workato.com
          Cresta                  Tim Shi            CTO       SaaS          90         cresta.com
          PathAI                Andy Beck            CTO HealthTech          86         pathai.com
       Instabase           Anant Bhardwaj            CTO       SaaS          90      instabase.com
          Runway     Anastasis Germanidis            CTO       SaaS          83          runway.ml
          OctoAI                Luis Ceze            CTO      Other          88         octoml.com
   Perplexity AI             Denis Yarats            CTO      Other          84      perplexity.ai
        Fivetran            Fraser Harris            CTO       SaaS          89       fivetran.com
         Kore.ai               Raj Koneru            CTO       SaaS          87            kore.ai
           Vanta       Christina Cacioppo            CTO       SaaS          80          vanta.com
          Aisera           Muddu Sudhakar            CTO       SaaS          85         aisera.com
           Glean          T.R. Vishwanath VP Engineering       SaaS          80          glean.com
Weights & Biases           Chris Van Pelt            CTO       SaaS          86 weights-biases.com
      Observe.AI Sharath Keshava Narayana            CTO       SaaS          80         observe.ai
            Miro       Robert Blenkinsopp            CTO       SaaS          80           miro.com
          Writer           Waseem Alshikh            CTO       SaaS          91       brainware.io
```

---

## Next Steps

1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,
   and Job Postings, then re-export and re-run this script.

2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.

3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.
   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).