# P95.AI Lead Engine — Scoring Report

**Generated:** 2026-04-19 10:04 UTC  
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
| Mean score  | 65.2 |
| Median score | 74 |
| Min score   | 23 |
| Max score   | 91 |

## Dimension Averages (out of max)

| Dimension | Avg Score | Max |
|---|---|---|
| A — Firmographic    | 28.0 | 35 |
| B — AI/Infra signals | 18.1 | 35 |
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
        Rippling            Matt MacInnis VP Engineering       SaaS          80       rippling.com
Weights & Biases           Chris Van Pelt            CTO       SaaS          86 weights-biases.com
           Glean          T.R. Vishwanath VP Engineering       SaaS          80          glean.com
          Cohere              Nick Frosst            CTO       SaaS          83         cohere.com
   Playground AI             Suhail Doshi            CTO       SaaS          81      playground.ai
          Runway     Anastasis Germanidis            CTO       SaaS          83          runway.ml
      Observe.AI Sharath Keshava Narayana            CTO       SaaS          80         observe.ai
           Vanta       Christina Cacioppo            CTO       SaaS          80          vanta.com
   Privia Health       Bertie Sherrington            CTO HealthTech          80      privia.health
          PathAI                Andy Beck            CTO HealthTech          86         pathai.com
       Darktrace           Jack Stockdale            CTO   Cybersec          80      darktrace.com
   Orca Security                 Avi Shua            CTO   Cybersec          80      orca.security
        Flexport            Sanne Manders            CTO  Logistics          80       flexport.com
      Mistral AI         Guillaume Lample            CTO      Other          82         mistral.ai
   Perplexity AI             Denis Yarats            CTO      Other          84      perplexity.ai
       CoreWeave            Brian Venturo            CTO      Other          83      coreweave.com
           Comet           Gideon Mendels            CTO      Other          84           comet.ml
        Adept AI               David Luan            CTO      Other          81           adept.ai
          Replit              Amjad Masad            CTO      Other          81         replit.com
        Labelbox             Brian Rieger            CTO      Other          86       labelbox.com
```

---

## Next Steps

1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,
   and Job Postings, then re-export and re-run this script.

2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.

3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.
   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).