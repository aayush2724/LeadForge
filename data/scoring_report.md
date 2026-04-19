# P95.AI Lead Engine — Scoring Report

**Generated:** 2026-04-19 06:01 UTC  
**Source:** `enriched_leads.csv`  
**Active leads scored:** 291  

---

## Tier Distribution

| Tier | Count | % of Active |
|---|---|---|
| 🔥 Hot  (80–100) | 135  | 46.4% |
| 🌡️ Warm (50–79)  | 57 | 19.6% |
| ❄️ Cold (0–49)   | 99 | 34.0% |

## Score Distribution

| Metric | Value |
|---|---|
| Mean score  | 68.2 |
| Median score | 79 |
| Min score   | 23 |
| Max score   | 96 |

## Dimension Averages (out of max)

| Dimension | Avg Score | Max |
|---|---|---|
| A — Firmographic    | 28.0 | 35 |
| B — AI/Infra signals | 18.1 | 35 |
| C — Persona          | 18.5 | 20 |
| D — Growth/intent    | 3.5 | 10 |

## Tier Breakdown by Vertical

| Vertical | Hot | Warm | Cold | Total |
|---|---|---|---|---|
| SaaS | 62 | 16 | 19 | 97 |
| FinTech | 4 | 5 | 47 | 56 |
| HealthTech | 6 | 8 | 8 | 22 |
| Ecommerce | 1 | 2 | 12 | 15 |
| Cybersec | 6 | 5 | 4 | 15 |
| Logistics | 3 | 3 | 9 | 15 |
| Other | 53 | 18 | 0 | 71 |

## 🔥 Top 20 Hot Leads

```
    company_name             contact_name    contact_title industry score_total             domain
            Ramp            Geoff Charles   VP Engineering  FinTech          83           ramp.com
            Brex            Raghav Shroff Head of Platform  FinTech          84           brex.com
        Rippling            Matt MacInnis   VP Engineering     SaaS          85       rippling.com
          Notion                Linus Lee       Head of AI     SaaS          81          notion.so
          Linear            Tuomas Artman              CTO     SaaS          80         linear.app
          Retool         Juan Camilo Ossa   VP Engineering     SaaS          83         retool.com
            Loom         Shishir Mehrotra              CTO     SaaS          82           loom.com
Weights & Biases           Chris Van Pelt              CTO     SaaS          91 weights-biases.com
           Glean          T.R. Vishwanath   VP Engineering     SaaS          85          glean.com
          Harvey         Winston Weinberg              CTO     SaaS          84          harvey.ai
          Cohere              Nick Frosst              CTO     SaaS          88         cohere.com
        Descript             Andrew Mason              CTO     SaaS          82       descript.com
   Playground AI             Suhail Doshi              CTO     SaaS          86      playground.ai
          Runway     Anastasis Germanidis              CTO     SaaS          88          runway.ml
      Midjourney               David Holz              CTO     SaaS          84            mid.com
      Observe.AI Sharath Keshava Narayana              CTO     SaaS          85         observe.ai
           Vanta       Christina Cacioppo              CTO     SaaS          85          vanta.com
             Hex            Scott Prevost              CTO     SaaS          83           hex.tech
            Pleo          Christian Ewald              CTO  FinTech          83            pleo.io
         Tessian             Simon Elisha              CTO Cybersec          83        tessian.com
```

---

## Next Steps

1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,
   and Job Postings, then re-export and re-run this script.

2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.

3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.
   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).