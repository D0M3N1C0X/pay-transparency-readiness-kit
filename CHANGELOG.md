# Changelog

What changed in each release. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). What comes next is
in [docs/roadmap.md](docs/roadmap.md).

## [Unreleased]

### Added

- **The workbook gets two sheets**: Register (the justification register, its gaps and costs linked to Categories,
  its dates to Obligations, status, evidence and decision for the employer to fill in) and Benchmark (each
  employer's gap on regular pay, live from a new Payroll column, against Eurostat's figures). Reconciliation
  checks: 511 → 547, all matching after a LibreOffice recalculation. New cover with the results of this release.

- **Justification register and right to information** (report section 9): `reports/justification_register.csv`
  gives each flagged category a reference, its main driver (role mix, same role, rating and part-time, or time
  worked) and pay element, the evidence that kind of gap needs, an owner, a review date halfway to the remedy
  deadline, its interval and whether it stays flagged on the reference year; status and decision are left blank.
  `src/article7.py` answers a worker's Article 7 request from the same categories, in Italian and English, and
  holds averages back where one sex has fewer than five workers ([docs/article7-response.md](docs/article7-response.md)).

- **Against the official figures** (report section 8, `src/benchmark.py`, `src/fetch_eurostat.py`): each
  employer's gap on regular pay set against Eurostat's 2024 gender pay gap for its country's business economy and
  for sections J, M and N, real data with the date they were read. Milan and Kraków are 3.4 and 3.5 times their
  national figure and inside their sectors' range; Barcelona is above every sector it resembles; Munich is below
  both. Two entries in the verification register (E01, E02).

- **The reference year** (report section 7, `src/build_period.py`, `src/reference_year.py`): pay actually paid
  from 1 July 2025 to 30 June 2026 to the 4,000 workers employed in it, leavers and joiners included, in
  `data/payroll_reference_year.csv`, in the browser tool's actual-pay layout. 15 categories are flagged instead of
  12 and only 8 are the same; all 7 newcomers were marked *could cross* in section 6. 7 of the 15 flags come from
  annual pay alone, which moves with turnover. The browser engine is checked on the file too (4,457 → 5,009
  values).

- **How far the flags can be trusted** (report section 6, `src/certainty.py`): a bootstrap interval for every
  category's gap; an exact split of each gap into role mix, rating and part-time, and what remains between women
  and men in the same role; and both scored against the ground truth, the payroll rebuilt from the same random
  draws without the two planted mechanisms. None of the 12 flags is clear of the 5% line; 6 are caused by the
  planted mechanisms and 6 would be there without them, and one category's gap against men is hidden by them. The
  same-role gap is about 2% in every employer and indistinguishable from zero once the mechanisms are removed.

- **Actual-pay browser mode**: captures the completed calendar year, requires amounts actually paid and worker-specific annual contractual hours, validates pseudonymous ID uniqueness, omits the source filename from exported reports, and records the basis and year in the print view and workbook. Annualized contract amounts remain labelled simulations.
- **Pilot data contract** for a local Italian-company payroll run, including pseudonymous IDs, minimum columns, CCNL category review, storage behavior and calculation limits.
- **Pay-code dictionary import** in the browser: validates pay codes against exact payroll column headers, pre-fills component and fixed-continuing classes, and records the map in the downloaded workbook.

### Changed

- Payroll files, column mappings, role scores and notes now remain in page memory and can be cleared with one action. Existing local storage keys for old scores, notes and mappings are removed on page load; the language choice is preserved.
- The role-scoring grid is labelled exploratory; Italy-specific copy points HR to the applicable CCNL classification.

## [1.3.1] - 2026-10-24

### Fixed

After an independent review of v1.3.0:

- **Italian law, stated as the decree states it**: the full definition of *livello retributivo* (art. 3(1)(b));
  the collective-agreement presumption is rebuttable and needs unions comparatively most representative at national
  level (art. 4(1)); the open question on fixed pay points to the ministerial decrees on data (art. 9(4)(b)), not to
  the guidance on equal value (art. 4(6)); item (g) keeps base pay and components apart.
- **Browser tool**: loading a job evaluation grid no longer resets the components ticked on the payroll file; a column
  chosen for a field is no longer also counted as a component.
- **Checks**: the JavaScript is now also tested on changed allowances, an employer without Italian workers and an
  Italian entity of nine (3,821 → 4,452 values); weekly hours of zero are rejected in Python as they are on the page.

## [1.3.0] - 2026-10-24

### Added

- **Italy's narrower measure.** D.lgs. 96/2026 computes the gaps, the quartile bands and the 5% test on
  *livello retributivo*, fixed and continuing pay, not on total pay. The Milan employer now gets both: an Italy sheet
  in the workbook (live formulas, reconciled), section 5 of the report, slide 8 of the deck, and an Italy panel in
  the browser tool, which asks which of the client's components are fixed. Reconciliation checks: 460 → 511; values
  the browser tool is checked on: 3,177 → 3,821.
- **The weights tested against the EU guidelines.** The categories and the screen rerun with the illustrative
  weights of the European Commission and EIGE guidelines on gender-neutral job evaluation (March 2026), and a note
  setting the kit's grid against their method: [docs/job-evaluation-eige.md](docs/job-evaluation-eige.md).

### Changed

- The Italian decree read in the Gazzetta Ufficiale: size bands, the collective-agreement presumption and the
  monitoring body move from "to verify" to verified, with article numbers ([verification register](docs/verification.md),
  N01-N04, N11-N14).
- The report dates the legal status from `data/transposition.csv` instead of a fixed 16 September.

## [1.2.1] - 2026-10-23

### Fixed

- **Gender codes:** the tool shows every code found in the file and asks which means woman and which man,
  instead of guessing: in Spanish exports M can mean *mujer*, in German ones d means *divers*.
- **Size band:** workers not recorded as woman or man are left out of the comparisons but counted for the
  employer's size (Article 9(2)-(4)).
- **Small categories:** averages, gaps and cost are kept back in the table, the chart and the download, and left
  out of the total cost, which would otherwise give them away. The note no longer claims more than it does.
- The category table and the download show the gap in complementary and variable pay, item (g) in full.
- Role scores and justifications are remembered per file, so one client's never appear in another's results.
- National transposition rechecked on 23 October 2026 (no adoption in Poland, Germany or Spain); `checked_on` in
  `data/transposition.csv`, left at 16 September after the 9 October recheck, now carries the date.
- A currency choice for the amounts; semicolon CSV files with dot decimals are read correctly (design base 1.1.0);
  "80%" as a full-time share; country names in Polish, German and Spanish; the group view resets with one
  country; print shows the results only.

## [1.2.0] - 2026-10-23

### Added

- **[Browser tool](https://d0m3n1c0x.github.io/pay-transparency-readiness-kit/tool/)**: the assessment on a client's own payroll file, Excel or CSV, without Python and
  without the file leaving the computer. Columns matched by name; categories from the file or from roles scored on
  the four Article 4(4) criteria; the seven items per employer; the category screen with a justification per flag
  and the cost ceiling; reporting dates by size and national status; small categories' averages kept back
  (Article 12(3)); an Excel download; English and Italian. `web/engine.js` is checked against pandas on 3,170
  values in CI (`tests/js/check_engine.mjs`).
- [Catalogue of reporting items](docs/catalogue.md): one card per Article 9(1) item and one for the Article 10
  screen, with results, workbook formulas, choices and what a statutory report adds. Generated from the code and
  the workbook, kept current by a test.
- [Engagement playbook](docs/engagement-playbook.md): how the assessment runs with a client, step by step.
- [Architecture](docs/architecture.md): the flow, how the two engines stay equal, how to run it on real data.
- `data/README.md` documents every column of every data file, checked by a test.
- Lint and return types in CI, test coverage measured with a floor.
- The published report counts visits with GoatCounter, no cookies.

### Changed

- National transposition rechecked on 9 October 2026: no change for Poland, Germany or Spain.

## [1.1.0] - 2026-10-09

### Changed

- Reconciliation, LibreOffice recalculation and byte-stable files now come from
  [excel-twin](https://github.com/D0M3N1C0X/excel-twin); all 460 checks still match.

## [1.0.0] - 2026-09-30

First complete release: Article 9 reporting items, the Article 10 screen, a live Excel model reconciled with
pandas on 460 checks, a board briefing, a written report and a verification register.

[Unreleased]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/compare/v1.3.1...HEAD
[1.2.1]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.2.1
[1.2.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.0.0
