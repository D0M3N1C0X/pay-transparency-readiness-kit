# Changelog

What changed in each release. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). What comes next is
in [docs/roadmap.md](docs/roadmap.md).

## [Unreleased]

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

[Unreleased]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.2.1
[1.2.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.0.0
