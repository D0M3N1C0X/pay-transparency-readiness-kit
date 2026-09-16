# Method

How every number in the kit is produced, and every choice the Directive leaves open. The
definitions quoted come from Directive (EU) 2023/970, Article 3(1), checked against the text
in the Official Journal (see [verification.md](verification.md)).

## Population and period

| Choice | This kit | Why, and what changes in a real report |
|---|---|---|
| Employer | One legal entity per Member State | Reporting duties fall on the employer, and each country's transposition sets its own rules. The group view is for management only. |
| Workers | Everyone active on 30 June 2026 | A dry run needs a stable population. The statutory report covers "the previous calendar year" (Article 9(2)-(4)); national rules decide how leavers and joiners count. |
| Pay | Annualised: base pay at the contracted FTE plus a year of each component | The real report uses pay actually paid in the calendar year. |
| Size band | Head count at the snapshot | The Directive counts workers; national law may specify how (average over the year, FTE). |

## Pay and pay level

- **Pay** (Article 3(1)(a)) is the basic wage plus "complementary or variable components". The
  kit models four components: bonus and commission (variable), shift allowance and car
  allowance (complementary). Pay in kind other than a car allowance, overtime and leave-related
  pay are not modelled.
- **Pay level** (Article 3(1)(b)) is "gross annual pay and the corresponding gross hourly pay",
  so items (a) and (c) are reported both ways.
- **Hourly pay** = annual pay ÷ annual contractual hours, where annual hours = weekly
  contractual hours × 52. The synthetic organisation has a 40-hour full-time week in every
  country; part-time workers are on 32 hours.

## The Article 9(1) items

| Item | Computed as |
|---|---|
| (a) Gender pay gap | (mean pay of men − mean pay of women) ÷ mean pay of men, on hourly and on annual total pay |
| (b) Gap in complementary or variable components | the same formula on annual components, **among workers who receive any** |
| (c) Median gender pay gap | the same formula on medians |
| (d) Median gap in components | medians of annual components, among recipients |
| (e) Share receiving components | women with any component ÷ women; the same for men |
| (f) Quartile pay bands | workers ranked by hourly total pay within the employer and cut into four equal groups; share of women and of men in each |
| (g) Gap by category of workers | per category: gap on hourly base pay, on hourly components (averaged over all workers in the category) and on total pay |

**Open choices, stated:**

- *Items (b) and (d): recipients only.* The Directive does not say whether workers without any
  component count as zero. Averaging over recipients describes how much people are paid when
  they are paid a component; item (e) then says how many receive one. This follows the UK
  bonus-gap convention. Check national guidance before filing.
- *Quartile ties.* Four equal groups need a rule for equal pay at a cut point. The kit breaks
  ties by row order. The workbook reproduces this with a `SUMPRODUCT` rank rather than
  `COUNTIFS`, because a `"<"&value` criterion converts the value to 15-digit text and can count
  a number as smaller than itself.
- *Direction.* A positive gap means women are paid less. The screen treats a gap of 5% or more
  in either direction the same way, because Article 10(1)(a) speaks of "a difference".

## Categories of workers

A category is "workers performing the same work or work of equal value grouped in a
non-arbitrary manner" on the criteria of Article 4(4): skills, effort, responsibility and working
conditions.

- Every role (department × level) is scored 1 to 5 on the four criteria in
  [`data/job_evaluation.csv`](../data/job_evaluation.csv), with a written rationale per role.
- Points = 35 × skills + 15 × effort + 35 × responsibility + 15 × working conditions, so a role
  scores 100 to 500. Whole-number weights keep points exact in Python and Excel; with decimal
  weights a role worth 340 points computes as 339.999… and drops a category.
- Roles are grouped into seven point bands (A to G, limits in `src/config.py`). The bands cross
  departments on purpose: an entry-level customer service role and a mid-level engineering role
  can do work of equal value.
- Two choices guard against the bias the Directive warns about ("relevant soft skills shall
  not be undervalued"): customer service scores high on effort for sustained emotional load, and
  HR scores extra responsibility for confidential data and legal compliance.
- **In Italy the national collective agreement comes first.** D.Lgs. 96/2026 presumes that
  applying a representative collective agreement complies, classification included; job
  evaluation complements the agreement's levels. The synthetic organisation has no agreement,
  so its categories come from job evaluation alone.

## The Article 10 screen

A joint pay assessment is owed when all three conditions of Article 10(1) hold. The data can
only test the first:

| Condition | Where it is handled |
|---|---|
| (a) a difference of at least 5% in any category | computed: flagged if the hourly **or** annual gap is 5% or more in either direction |
| (b) not justified on objective, gender-neutral criteria | a blank justification column in the workbook, one row per category |
| (c) not remedied within six months of the report | a Yes/No column; the deadline is the first report date plus six months |

**Cost to close, upper bound:** for a flagged category, the gap in mean hourly pay × the annual
hours of the lower-paid sex. It prices lifting that group's average to the other's. It is a
ceiling: any justified part of a gap reduces it, and a flag raised by annual pay alone is mostly
about hours worked, not hourly rates.

**Disclosure control:** where a category has fewer than five workers of one sex, an average can
reveal one person's pay. Article 12(3) lets Member States limit such figures to workers'
representatives, the labour inspectorate and the equality body. The Directive sets no number;
five matches the confidentiality threshold in
[engagement-survey-analytics](https://github.com/D0M3N1C0X/engagement-survey-analytics).

## Two engines, one answer

Every figure is computed twice:

1. **pandas** (`src/article9.py`, `src/article10.py`), which feeds the report, the deck and the
   Tableau extracts;
2. **live Excel formulas** in `deliverables/pay_transparency_model.xlsx`, which a client can
   change.

`src/build_workbook.py` writes the pandas value next to each formula on the Reconciliation
sheet, and the sheet checks every pair to one part in a billion (460 checks). Two engines then
evaluate the formulas:

- **LibreOffice**, in CI, on the full workbook (`src/check_workbook.py`);
- the pure-Python **`formulas`** package, in the test suite, on a 100-worker sample, including a
  test that a single wrong value is caught.

The workbook uses only functions that Excel, LibreOffice and Numbers all evaluate, with no
dynamic arrays. Medians are classic array formulas (`MEDIAN(IF(...))`).

## Reproducibility

Everything is rebuilt by `python src/run_all.py` from a fixed seed. CI regenerates all outputs
and fails if a text output changes; for the Office files it compares the unzipped contents,
because compressed bytes can differ between zlib builds while the content does not.
