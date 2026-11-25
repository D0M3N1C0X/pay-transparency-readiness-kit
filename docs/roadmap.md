# Roadmap

What comes next, in order of value to an employer preparing its first report. Dates are intentions.

| # | What | Why it matters | What it needs | When |
|---|---|---|---|---|
| 1 | **Tableau Public dashboard** from the three files in `tableau/` | Leadership reads a dashboard, not a workbook | The build sheet in `tableau/README.md` | November 2026 |
| 2 | **Statutory-year mode**: done for the twelve months to the snapshot (report section 7); still to do, a calendar year once the source records one, with pay history instead of current rates | The real report covers the previous calendar year, not a snapshot | A pay history per worker | 2027 |
| 3 | **National variants** as Poland, Germany and Spain adopt their acts | Thresholds, dates and the bodies to report to differ by country | The final texts, read at the source and entered in `data/transposition.csv` | As each act is adopted |
| 4 | **Justification register**: evidence per flagged category, with owner and review date | A justification is only as good as the record behind it | The browser tool already records a reason per flag, and its download has owner and due-date columns to fill in; still to add: the evidence and a review date | Q1 2027 |
| 5 | **Right to information** (Article 7): a response template per worker request | Workers can ask for the average pay of their category once national law applies | The categories already built here | Q1 2027 |
| 6 | **Pay ranges in job adverts** (Article 5) | Recruitment transparency comes first in time | Already built in [equal-value-pay-ranges](https://github.com/D0M3N1C0X/equal-value-pay-ranges): link the two | Q1 2027 |

What has already changed is in the [CHANGELOG](../CHANGELOG.md).
