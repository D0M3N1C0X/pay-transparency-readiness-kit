# Data

All synthetic. No real person's pay is in this repository.

## Where it comes from

| File | Made by | What it is |
|---|---|---|
| `source/employees.csv` | copied from [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics) at commit `201495b` | The 4,000-employee organisation analysed there, seed 42. SHA-256 `3727232…7da79c`, pinned in `src/config.py` and checked on every build. |
| `payroll_extract.csv` | `src/build_extract.py`, seed 2026 | The payroll extract a client would send: the 3,443 workers active on 30 June 2026, with four pay components added. |
| `job_evaluation.csv` | written by hand | The scored role grid: 36 roles × the four Article 4(4) criteria, with a rationale per role. |
| `transposition.csv` | written by hand from the sources in [docs/verification.md](../docs/verification.md) | National status, 16 September 2026. |
| `readiness_checklist.csv` | written by hand | Fourteen obligations from Articles 4 to 12, with illustrative statuses. |

Reusing the organisation from hr-people-analytics is deliberate: that project found a 15.4% gap
in base salary and said a real Article 9 report would also need bonuses and allowances. This
kit adds them, and its test suite checks that the base-pay gap still comes out at 15.4%.

## `payroll_extract.csv`, one row per worker

| Column | Description |
|---|---|
| `worker_id` | `W00001` format; the same number as `employee_id` in the source |
| `entity`, `country`, `site` | Employer (one per Member State) and location |
| `department`, `job_level`, `role` | Function, level L1-L6, and the two combined, which keys into the job evaluation |
| `gender` | `F` / `M`, as the Directive reports women and men |
| `contract_type`, `work_model` | Permanent or fixed-term; on-site, hybrid or remote |
| `fte`, `weekly_hours` | 1.0 → 40 hours, 0.8 → 32 hours |
| `performance_rating` | 1-5, drives the bonus payout |
| `base_pay` | Annual gross base pay actually due: the source's full-time salary × FTE, EUR |
| `bonus` | Annual bonus, EUR (variable) |
| `commission` | Annual sales commission, EUR (variable) |
| `shift_allowance` | Annual shift allowance, EUR (complementary) |
| `car_allowance` | Annual car allowance, EUR (complementary) |

Every amount is in EUR, the Polish entity included; a real Polish extract would be in PLN.

## How the components are generated

| Component | Rule | Parameters |
|---|---|---|
| Bonus | base pay × target by level × payout by rating × noise (sd 6%), rounded to €10 | target 0% at L1-L2, 5% L3, 8% L4, 12% L5, 20% L6; payout 0 / 0.5 / 1 / 1.25 / 1.5 for ratings 1-5 |
| Commission | Sales only: base pay × 15% × territory potential × noise (sd 10%) | potential drawn around 1.0 for men and **0.82 for women** (sd 0.18, clipped to 0.3-1.8) |
| Shift allowance | on-site Operations and Customer Service staff at L1-L3: monthly amount × 12 × FTE | €110 IT, €70 PL, €150 DE, €100 ES |
| Car allowance | L5-L6 | €6,000 IT, €4,200 PL, €7,200 DE, €5,400 ES a year |

Each worker gets three random draws whatever their role, so changing one rule never shifts the
random numbers of anyone else.

## What is planted, stated openly

| Mechanism | Where it comes from | What should find it |
|---|---|---|
| Vertical segregation: women 57% of L1, 30% of L6 | inherited from hr-people-analytics | quartile bands, item (f) |
| A small residual base-pay effect within level and country | inherited | category gaps driven by base pay |
| **Lower-potential territories for women in Sales** | added here | components gap (b), commission as a share of base pay, category gaps driven by components |
| Eligibility for bonus and car allowance rises with level | added here | the share receiving components, item (e) |
| Part-time work at random (about 8% of workers), unrelated to sex | inherited | hourly and annual gaps differing by category |

The territory effect is the one an Article 10 assessment exists to surface: a commission rule
that is identical for everyone and still pays women less, through how the territories are
assigned.
