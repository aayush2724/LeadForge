# P95.AI Lead Engine — Scoring Report

**Generated:** 2026-04-19 05:29 UTC  
**Source:** `enriched_leads.csv`  
**Active leads scored:** 291  

---

## Tier Distribution

| Tier | Count | % of Active |
|---|---|---|
| 🔥 Hot  (80–100) | 143  | 49.1% |
| 🌡️ Warm (50–79)  | 80 | 27.5% |
| ❄️ Cold (0–49)   | 68 | 23.4% |

## Score Distribution

| Metric | Value |
|---|---|
| Mean score  | 70.6 |
| Median score | 79 |
| Min score   | 27 |
| Max score   | 96 |

## Dimension Averages (out of max)

| Dimension | Avg Score | Max |
|---|---|---|
| A — Firmographic    | 28.0 | 35 |
| B — AI/Infra signals | 20.4 | 35 |
| C — Persona          | 18.5 | 20 |
| D — Growth/intent    | 3.6 | 10 |

## Tier Breakdown by Vertical

| Vertical | Hot | Warm | Cold | Total |
|---|---|---|---|---|
| SaaS | 63 | 24 | 10 | 97 |
| FinTech | 4 | 16 | 36 | 56 |
| HealthTech | 7 | 11 | 4 | 22 |
| Ecommerce | 1 | 4 | 10 | 15 |
| Cybersec | 6 | 8 | 1 | 15 |
| Logistics | 4 | 4 | 7 | 15 |
| Other | 58 | 13 | 0 | 71 |

## 🔥 Top 20 Hot Leads

```
    company_name             contact_name    contact_title industry score_total             domain
            Ramp            Geoff Charles   VP Engineering  FinTech          83           ramp.com
            Brex            Raghav Shroff Head of Platform  FinTech          91           brex.com
        Rippling            Matt MacInnis   VP Engineering     SaaS          88       rippling.com
          Notion                Linus Lee       Head of AI     SaaS          84          notion.so
          Linear            Tuomas Artman              CTO     SaaS          89         linear.app
          Retool         Juan Camilo Ossa   VP Engineering     SaaS          86         retool.com
            Loom         Shishir Mehrotra              CTO     SaaS          91           loom.com
        Scale AI            Brad Lightcap   VP Engineering     SaaS          83           scale.ai
Weights & Biases           Chris Van Pelt              CTO     SaaS          95 weights-biases.com
           Glean          T.R. Vishwanath   VP Engineering     SaaS          90          glean.com
          Harvey         Winston Weinberg              CTO     SaaS          87          harvey.ai
          Cohere              Nick Frosst              CTO     SaaS          95         cohere.com
        Descript             Andrew Mason              CTO     SaaS          95       descript.com
   Playground AI             Suhail Doshi              CTO     SaaS          86      playground.ai
          Runway     Anastasis Germanidis              CTO     SaaS          95          runway.ml
      Midjourney               David Holz              CTO     SaaS          89            mid.com
      Observe.AI Sharath Keshava Narayana              CTO     SaaS          85         observe.ai
           Vanta       Christina Cacioppo              CTO     SaaS          85          vanta.com
             Hex            Scott Prevost              CTO     SaaS          86           hex.tech
            Pleo          Christian Ewald              CTO  FinTech          86            pleo.io
```

---

## Next Steps

1. **Task 3B (if not done)** — Run Clay enrichment blocks for BuiltWith, Crunchbase,
   and Job Postings, then re-export and re-run this script.

2. **Phase 4 / Task 4.1** — Review Top 20 Hot leads and approve for outreach.

3. **Phase 5** — Write personalised outreach emails & LinkedIn messages for Hot tier.
   Run `python scripts/outreach_writer.py` (Phase 5 script — not yet built).