# P95.AI Lead Engine — Sourcing QA Report

**Generated:** 2026-04-19 10:05 UTC  
**Input file:** `data\raw_leads.csv`  
**Total rows:** 297 | **Active (non-disqualified):** 291

---

## Overall Count

| Metric | Actual | Target | Status |
|---|---|---|---|
| Active leads | 291 | 200 | ❌ OVER |
| Priority-persona leads | 228 | — | ✅ |

## Vertical Quota Check

| Vertical | Actual | Target | Gap | Status |
|---|---|---|---|---|
| SaaS | 97 | 45 | 0 | ❌ OVER |
| FinTech | 56 | 30 | 0 | ❌ OVER |
| HealthTech | 22 | 20 | 0 | ✅ PASS |
| Ecommerce | 15 | 15 | 0 | ✅ PASS |
| Cybersec | 15 | 15 | 0 | ✅ PASS |
| Logistics | 15 | 15 | 0 | ✅ PASS |
| Other (Flex) | 71 | 60 | 0 | ❌ OVER |

## Geographic Quota Check

| Geo Tier | Actual | Target | Gap | Status |
|---|---|---|---|---|
| US | 202 | 120 | 0 | ❌ OVER |
| EU_UK | 66 | 60 | 0 | ✅ PASS |
| India_seed | 22 | 20 | 0 | ✅ PASS |

## Source Breakdown

| Source | Count |
|---|---|
| apollo | 111 |
| linkedin | 60 |
| builtwith | 41 |
| crunchbase | 41 |
| github | 26 |
| seed | 12 |

## Duplicate Domain Check

> [!WARNING]
> 7 domain(s) appear more than once in active leads:

- `abnormal.ai`
- `doccla.com`
- `groww.in`
- `razorpay.com`
- `semrush.com`
- `thoughtspot.com`
- `xyretail.com`

## Gap-Fill Recommendations

✅ All verticals and geos are within tolerance — no gap-fill needed.

---

## Next Steps

1. **Task 2.12** — Import `data/raw_leads.csv` into Clay as `p95_leads_enriched` table
2. **Task 2.13** — Team checkpoint review of this report before Phase 3