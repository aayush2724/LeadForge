# P95.AI Lead Engine — Scoring Report

**Generated:** 2026-04-18 20:33 UTC  
**Source:** `enriched_leads.csv`  
**Active leads scored:** 291  

---

## Tier Distribution

| Tier | Count | % of Active |
|---|---|---|
| 🔥 Hot  (80–100) | 135  | 46.4% |
| 🌡️ Warm (50–79)  | 58 | 19.9% |
| ❄️ Cold (0–49)   | 98 | 33.7% |

## Score Distribution

| Metric | Value |
|---|---|
| Mean score  | 68.7 |
| Median score | 79 |
| Min score   | 25 |
| Max score   | 96 |

## Dimension Averages (out of max)

| Dimension | Avg Score | Max |
|---|---|---|
| A — Firmographic    | 28.0 | 35 |
| B — AI/Infra signals | 18.6 | 35 |
| C — Persona          | 18.5 | 20 |
| D — Growth/intent    | 3.5 | 10 |

## Tier Breakdown by Vertical

| Vertical | Hot | Warm | Cold | Total |
|---|---|---|---|---|
| SaaS | 62 | 17 | 18 | 97 |
| FinTech | 4 | 5 | 47 | 56 |
| HealthTech | 6 | 8 | 8 | 22 |
| Ecommerce | 1 | 2 | 12 | 15 |
| Cybersec | 6 | 5 | 4 | 15 |
| Logistics | 3 | 3 | 9 | 15 |
| Other | 53 | 18 | 0 | 71 |

## 🔥 Top 20 Hot Leads

```
    company_name             contact_name  contact_title   industry score_total             domain
       Moveworks          Vaibhav Nivargi            CTO       SaaS          95      moveworks.com
          Tecton             Kevin Stumpf            CTO      Other          95          tecton.ai
      Snorkel AI           Braden Hancock            CTO      Other          95         snorkel.ai
        Labelbox             Brian Rieger            CTO      Other          91       labelbox.com
         Workato      Gautham Viswanathan            CTO       SaaS          90        workato.com
          Cresta                  Tim Shi            CTO       SaaS          95         cresta.com
          PathAI                Andy Beck            CTO HealthTech          91         pathai.com
       Instabase           Anant Bhardwaj            CTO       SaaS          95      instabase.com
          Runway     Anastasis Germanidis            CTO       SaaS          88          runway.ml
          OctoAI                Luis Ceze            CTO      Other          93         octoml.com
   Perplexity AI             Denis Yarats            CTO      Other          89      perplexity.ai
        Fivetran            Fraser Harris            CTO       SaaS          94       fivetran.com
         Kore.ai               Raj Koneru            CTO       SaaS          92            kore.ai
           Vanta       Christina Cacioppo            CTO       SaaS          85          vanta.com
          Aisera           Muddu Sudhakar            CTO       SaaS          90         aisera.com
            Ramp            Geoff Charles VP Engineering    FinTech          83           ramp.com
           Glean          T.R. Vishwanath VP Engineering       SaaS          85          glean.com
Weights & Biases           Chris Van Pelt            CTO       SaaS          91 weights-biases.com
      Observe.AI Sharath Keshava Narayana            CTO       SaaS          85         observe.ai
            Miro       Robert Blenkinsopp            CTO       SaaS          85           miro.com
```

---

## Next Steps

1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,
   and Job Postings, then re-export and re-run this script.

2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.

3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.
   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).