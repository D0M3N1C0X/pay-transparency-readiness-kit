# Engagement playbook: a pay transparency readiness assessment

How this kit would run with a real client, step by step: who does what, what each step hands over, and the check
that has to pass before the next one starts. The steps follow the order the kit itself computes things; the weeks
are a plan for a mid-sized group, to be fitted to the client.

## Roles

| Role | Who | Owns |
|---|---|---|
| **Consultant** | The person running the assessment | Method, computation, findings, the board briefing |
| **Reward lead** | The client's head of reward or compensation | Pay codes, job architecture, decisions on gaps |
| **Payroll** | The client's payroll team or provider | The extract, and what each pay code means |
| **Employment law** | In-house counsel or external advisor | National transposition, justification wording |
| **Workers' representatives** | Works council or unions, where they exist | Consultation on job evaluation and on any joint pay assessment |
| **Board sponsor** | The executive who signs the report | Decisions on budget and timeline |

## Steps

| Week | Step | Who leads | Hands over | Gate before the next step |
|---|---|---|---|---|
| 0 | **Scope.** Legal entities, headcount by entity, size band and first reporting date, transposition status per country | Consultant, employment law | The obligations table (sheet Obligations) | Every entity has a size band and a date |
| 1 | **Data request.** Actual base pay and component totals paid from 1 January to 31 December, annual contractual hours per worker, pseudonymous IDs, and a pay-code map; average weekly hours may be included as context | Payroll, reward lead | A client-controlled Excel/CSV extract and pay-code map | Headcount, annual hours and total pay reconcile to payroll; each pay code maps to an exact payroll column and HR/Compensation approves whether it is fixed and continuing, variable or one-off. Optional weekly hours are reviewed as context. Read both files in the [browser tool](https://d0m3n1c0x.github.io/pay-transparency-readiness-kit/tool/) on the client's own machine; use [the pilot data contract](pilot-data-contract.md) and do not place real data in GitHub |
| 2 | **Job evaluation.** Confirm the categories with HR and workers' representatives. In Italy start from the applicable CCNL classification; the browser grid is exploratory only | Reward lead, with workers' representatives | Client-approved categories or an exploratory grid with a rationale per role | No score band is treated as a legal category without review |
| 3 | **Compute.** The Article 9 items and the Article 10 screen, in Python and in the Excel model | Consultant | The report, the workbook, the [catalogue](catalogue.md) | Every reconciliation row matches; small cells marked |
| 4 | **Justify or price.** For each flagged category, an objective, gender-neutral reason or a cost to close; the readiness checklist | Reward lead, employment law | The Categories sheet filled in (the browser tool's download has a justification, owner and due date per flag); sheet Readiness | Each flag has a reason, a cost, or an owner |
| 5 | **Brief the board.** The answer, the cost ceiling, the 90-day plan | Consultant, board sponsor | `board_briefing.pptx` | A decision on budget and owners |

## What a step must never do

- **Change a number to fit a story.** Figures come from the extract through code; the two engines must agree.
- **Justify after the fact.** A reason written after the gap is known is a weak reason; it has to rest on criteria
  that were already in use.
- **Publish small cells.** Where a category has fewer than five workers of one sex, the figure goes to workers'
  representatives and authorities only (Article 12(3)).

## What the client keeps

The model, with the extract and the job evaluation in it, so next year's report is a refresh rather than a new
project; the method and verification register; and the list of what was assumed, in [method.md](method.md) and
[verification.md](verification.md).
