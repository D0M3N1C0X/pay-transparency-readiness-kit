# Changelog

What changed in each release. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). What comes next is
in [docs/roadmap.md](docs/roadmap.md).

## [Unreleased]

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

[Unreleased]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.2.0
[1.1.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.1.0
[1.0.0]: https://github.com/D0M3N1C0X/pay-transparency-readiness-kit/releases/tag/v1.0.0
