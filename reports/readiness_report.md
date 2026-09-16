# Pay transparency readiness: where the organisation stands before its first report

**Scope:** four employers - IT · Milan, PL · Kraków, DE · Munich, ES · Barcelona - with 3,443 workers active on 30 June 2026
**Method:** Article 9 reporting items and the Article 10 screen, computed twice - in pandas and in a live Excel model - and reconciled figure by figure
**Data:** synthetic, built on the organisation analysed in [hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics)

> This is a dry run, not a statutory report. It uses annualised pay of the workers present at the snapshot; the real report covers pay in the previous calendar year, under rules each Member State sets in its own transposition.

## The answer

- **Every employer reports every year, starting 7 June 2027.** All four have 250 workers or more, so the first report covers pay in 2026 (Article 9(2)).
- **The gender pay gap on hourly pay is 17.6% across the group**, from 14.5% in DE · Munich to 21.5% in ES · Barcelona. On base pay alone it is 15.4% - the figure hr-people-analytics reports - so bonuses, commission and allowances add 2.2 points.
- **12 of 28 categories of workers show a difference of 5% or more.** Each needs an objective, gender-neutral justification or a remedy within six months of the report (7 December 2027); otherwise a joint pay assessment with workers' representatives follows (Article 10).
- **Closing those gaps outright would cost at most €1.9 million a year**, before any part of them is justified.
- **The organisation is not ready yet:** of 14 obligations, 1 is in place, 6 are partly in place and 7 are missing - pay ranges in vacancies, published progression criteria and a route for workers' information requests among them.
- **The law is settled in one country of four.** Legislative Decree No. 96 of 7 May 2026 transposes the Directive in Italy; Poland has transposed the recruitment rules only, and Germany and Spain have not finished.

## 1. What each employer owes, and when

| Employer | Workers | Reporting | First report | Remedy by | Transposition |
|---|---:|---|---|---|---|
| IT · Milan | 1,053 | Every year | 7 Jun 2027 | 7 Dec 2027 | Transposed |
| PL · Kraków | 1,156 | Every year | 7 Jun 2027 | 7 Dec 2027 | Partly transposed |
| DE · Munich | 741 | Every year | 7 Jun 2027 | 7 Dec 2027 | Not transposed |
| ES · Barcelona | 493 | Every year | 7 Jun 2027 | 7 Dec 2027 | Draft |

*Remedy by: six months after the first report, the latest date to justify or close a category gap before a joint pay assessment is due. National status as checked on 16 September 2026; sources in [docs/verification.md](../docs/verification.md).*

For Italy, applying a national collective agreement signed by representative unions is presumed to comply, classification included, so the categories of workers should start from the agreement's levels and use job evaluation to complement them, not replace them. The categories in this dry run come from job evaluation alone, because the synthetic organisation has no collective agreement. *[to verify on the decree text]*

## 2. The seven reporting items

| Item | IT | PL | DE | ES | Group |
|---|---:|---:|---:|---:|---:|
| Workers at the snapshot | 1,053 | 1,156 | 741 | 493 | 3,443 |
| Women | 523 | 578 | 363 | 253 | 1,717 |
| Men | 530 | 578 | 378 | 240 | 1,726 |
| (a) Gender pay gap, mean hourly pay | 19.7% | 15.2% | 14.5% | 21.5% | 17.6% |
| (a) Gender pay gap, mean annual pay | 20.4% | 15.1% | 15.0% | 21.6% | 17.9% |
| (b) Gap in complementary or variable components, mean | 35.5% | 21.0% | 25.9% | 46.3% | 31.1% |
| (c) Median gender pay gap, hourly pay | 16.9% | 12.5% | 11.3% | 18.9% | 15.6% |
| (c) Median gender pay gap, annual pay | 19.7% | 13.7% | 13.2% | 19.4% | 16.7% |
| (d) Median gap in complementary or variable components | 26.0% | 15.7% | 16.2% | 42.7% | 24.6% |
| (e) Women receiving complementary or variable components | 56.0% | 55.5% | 54.5% | 54.9% | 55.4% |
| (e) Men receiving complementary or variable components | 62.1% | 64.2% | 63.5% | 65.8% | 63.6% |
| (f) Women in quartile pay band 1 (lowest) | 62.9% | 58.8% | 54.3% | 66.1% | 60.1% |
| (f) Women in quartile pay band 4 (highest) | 31.6% | 36.0% | 37.3% | 30.1% | 34.1% |
| Context: gap on base pay alone, mean hourly | 17.5% | 13.6% | 12.6% | 17.7% | 15.4% |

*Gaps are men's pay level minus women's, as a share of men's (Article 3(1)(c)); positive means women are paid less. Items (b) and (d) are computed among workers who receive any component. The middle quartile bands and the men's shares are in the workbook. The group column is a management view, not a statutory figure.*

![Gender pay gap by employer](figures/01_gap_by_employer.svg)

The median gap sits below the mean everywhere, which says the gap is concentrated at the top of the pay distribution. The quartile bands show why: women are 60% of the lowest band and 34% of the highest.

![Share of women in the lowest and highest pay bands](figures/02_quartile_bands.svg)

## 3. Bonus, commission and allowances widen the gap

Among workers who receive any component, women's average is 31.1% below men's (median 24.6%), and fewer women receive one at all: 55% against 64%. Two mechanisms produce most of it:

- **Eligibility follows seniority.** Bonus starts at level L3 and car allowances at L5, while the share of women falls from 57% at L1 to 30% at L6. That part is structural and shows up again in the quartile bands.
- **Commission follows territory.** In Sales, commission averages 12.6% of base pay for women and 15.1% for men. Commission rules are the same for everyone; the territories are not. The generator allocates women territories with lower sales potential - an effect planted on purpose and stated in [data/README.md](../data/README.md), because indirect discrimination through allocation is exactly what an Article 10 assessment should surface.

## 4. Categories of workers: where a justification is needed

Categories come from a gender-neutral job evaluation: every role is scored 1-5 on skills, effort, responsibility and working conditions (Article 4(4)), and roles with similar points form a category, whatever their department. That is how a customer service team lead and a software engineer can do work of equal value - and why a category can mix functions the market pays very differently.

![Hourly pay gap by employer and category](figures/03_category_screen.svg)

| Employer | Category | Women / men | Hourly gap | Annual gap | Main driver | Cost to close, upper bound |
|---|---|---:|---:|---:|---|---:|
| IT · Milan | Cat B | 147 / 106 | 7.4% | 8.4% | Base pay (7.9 of 7.4 pts) | €331,912 |
| PL · Kraków | Cat D | 125 / 133 | 5.7% | 6.1% | Base pay (5.9 of 5.7 pts) | €262,744 |
| DE · Munich | Cat E | 47 / 65 | 6.0% | 6.3% | Base pay (5.9 of 6.0 pts) | €254,265 |
| PL · Kraków | Cat F | 37 / 56 | 8.0% | 7.0% | Base pay (6.3 of 8.0 pts) | €222,454 |
| PL · Kraków | Cat E | 49 / 87 | 7.9% | 7.5% | Base pay (6.8 of 7.9 pts) | €188,889 |
| ES · Barcelona | Cat D | 56 / 52 | 6.9% | 7.1% | Base pay (4.8 of 6.9 pts) | €173,333 |
| ES · Barcelona | Cat F | 5 / 24 | -5.2% | -7.1% | Base pay (-5.7 of -5.2 pts) | €107,053 |
| ES · Barcelona | Cat B | 64 / 48 | 5.3% | 5.5% | Base pay (5.2 of 5.3 pts) | €97,880 |
| IT · Milan | Cat G | 7 / 20 | 10.5% | 10.5% | Components (5.4 of 10.5 pts) | €95,319 |
| IT · Milan | Cat A | 72 / 55 | 4.1% | 5.4% | Hours worked: flagged on annual pay only | €85,246 |
| ES · Barcelona | Cat E | 28 / 41 | 5.0% | 4.4% | Components (2.8 of 5.0 pts) | €82,584 |
| ES · Barcelona | Cat G | 4 / 9 | 2.4% | 7.1% | Hours worked: flagged on annual pay only | €12,024 |

*Cost to close: the lower-paid sex's average hourly pay lifted to the other's, for all their hours, a year. 2 categories have fewer than 5 workers of one sex (DE · Munich Cat G, ES · Barcelona Cat G); their figures should go only to workers' representatives, the labour inspectorate or the equality body (Article 12(3)).*

How to read the list:

- **Base pay drives 8 of the 12 flags.** A gap within a category of equal value is where a justification has to be specific: experience, performance, a scarce skill priced in the market - each documented, gender-neutral and applied to everyone.
- **Components - bonus, commission, allowances - drive 2: look at the rules and at who they reach.** A commission scheme or an allowance that is neutral on paper can still pay women less through allocation or eligibility.
- **A flag on annual pay only points to hours worked.** Part-time work is a legitimate reason for a lower annual total; the hourly figure is the one to defend.
- **Gaps in either direction count.** A category where men are paid less is flagged the same way.

## 5. Readiness: what has to be in place

| Ref | Article | Requirement | Status | Owner |
|---|---|---|---|---|
| R01 | Art. 4(1)-(4) | Pay structures allow equal work and work of equal value to be compared, on objective gender-neutral criteria that include skills, effort, responsibility and working conditions | Partial | Reward |
| R02 | Art. 5(1) | Applicants receive the initial pay or its range, and the relevant collective agreement provisions, before the interview | Gap | Talent Acquisition |
| R03 | Art. 5(2) | Applicants are not asked about their pay history | Partial | Talent Acquisition |
| R04 | Art. 5(3) | Vacancy notices and job titles are gender-neutral and recruitment is non-discriminatory | Partial | Talent Acquisition |
| R05 | Art. 6(1) | Workers can easily access the criteria that set pay, pay levels and pay progression | Gap | Reward |
| R06 | Art. 7(1) and 7(4) | Workers can request their own pay level and the average pay by sex for their category, answered in writing within two months | Gap | HR Operations |
| R07 | Art. 7(3) | Workers are told every year of their right to request that information | Gap | HR Operations |
| R08 | Art. 7(5) | No contract term stops workers disclosing their pay for the purpose of equal pay | Partial | Legal |
| R09 | Art. 8 | Information for workers and applicants is accessible to persons with disabilities | Gap | HR Operations |
| R10 | Art. 9(1) | The seven reporting items can be produced for each employer from payroll data | Ready | People Analytics |
| R11 | Art. 9(6) | Management confirms the accuracy of the report after consulting workers' representatives, who can see the method | Gap | HR Director |
| R12 | Art. 9(9) | Pay gaps by category of workers are provided to all workers and their representatives | Gap | HR Operations |
| R13 | Art. 10 | A process exists to justify or remedy category gaps of 5% or more within six months, and to run a joint pay assessment with workers' representatives if not | Partial | Reward |
| R14 | Art. 12 | Personal data used for transparency is processed under the GDPR, only for equal pay, with small categories protected | Partial | Data Protection |

*Statuses are illustrative for the demonstration organisation. Evidence expected for each item is in the workbook's Readiness sheet.*

## 6. The next 90 days

1. **Agree the job evaluation with workers' representatives** in each country, starting from the Italian collective agreement's classification. Categories decide every later number.
2. **Write or rule out a justification for each flagged category**, beginning with the most expensive, and budget the remedy for the rest before the first report is filed.
3. **Review the Sales territory allocation** and any other rule that decides who can earn a component.
4. **Close the recruitment gaps now**: pay ranges in vacancies, no pay-history questions, gender-neutral titles - already law in Italy and Poland.
5. **Build the information-request route** (two-month answer) and the annual notice to workers.
6. **Rerun this model on calendar-year 2026 payroll** once each country's rules are final, and have management confirm the figures after consulting workers' representatives (Article 9(6)).

## 7. Method, choices and limits

- **Two engines, one answer.** Every figure is computed in pandas and again by live formulas in [the workbook](../deliverables/pay_transparency_model.xlsx); its Reconciliation sheet checks each pair, and CI recalculates the workbook with LibreOffice and fails on any mismatch.
- **Where the Directive leaves a choice, the choice is stated.** Pay includes base, bonus, commission and allowances; hourly pay uses contractual hours; components gaps (b) and (d) are among recipients; quartile bands are four equal groups by hourly pay with ties broken by row order; a category is flagged at 5% in either direction on hourly or annual pay. Full list in [docs/method.md](../docs/method.md).
- **Legal claims carry their source** and a status in [docs/verification.md](../docs/verification.md). Items marked *[to verify]* need the final national text.
- **Limits.** Synthetic data; a snapshot rather than a calendar year; leavers, leave-related pay (Article 10(2)(e)) and pay in kind beyond a car allowance are not modelled; not legal advice.

