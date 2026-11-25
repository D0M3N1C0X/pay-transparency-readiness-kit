"""
The payroll for a reference year: what each worker was actually paid over twelve months, leavers and joiners in.

The statutory report does not look at the people on the payroll on one day. It looks at pay paid over the
previous calendar year, to everyone who was paid in it: the people who left in March, the ones who joined in
October. The snapshot extract cannot show what that does to the figures; this file can.

It is written in the browser tool's actual-pay layout (web/template_payroll.csv): amounts actually paid and each
worker's own contractual hours for the period, so the same file runs through the page.

Rules, stated in data/README.md:

- **Who:** everyone employed on at least one day between REFERENCE_START and REFERENCE_END. The 3,443 workers of
  the snapshot keep the annual rates of payroll_extract.csv; the leavers get theirs from the same rules, with a
  random stream of their own (seed + 1), so the snapshot extract does not move.
- **Base pay, commission, allowances:** the annual rate times the share of the period employed.
- **Bonus:** the 2025 bonus is paid on BONUS_PAYDAY to workers employed that day, pro rata to their days of
  service in 2025. Leavers before payday get none; joiners of 2026 get none.
- **Hours:** contractual weekly hours times 52 times the share of the period employed.

Standard library only, so the file is byte-identical on every Python version.
"""
import csv
import random
from datetime import date

from build_extract import annual_row, verify_source
from config import (
    BONUS_PAYDAY,
    PAYROLL_EXTRACT,
    PAYROLL_PERIOD,
    REFERENCE_END,
    REFERENCE_START,
    SEED,
    SOURCE_EMPLOYEES,
    WEEKS_PER_YEAR,
)

COLUMNS = ["worker_id", "country", "role", "gender", "weekly_hours", "annual_hours", "base_pay", "payroll_total",
           "bonus", "commission", "shift_allowance", "car_allowance", "period_status"]
PRO_RATA = ["base_pay", "commission", "shift_allowance", "car_allowance"]
PERIOD_DAYS = (REFERENCE_END - REFERENCE_START).days + 1


def employed(hire: date, leave: date | None, start: date, end: date) -> int:
    """Days employed between start and end, both included; the exit date is the last day worked."""
    first = max(hire, start)
    last = min(leave, end) if leave else end
    return max(0, (last - first).days + 1)


def status(hire: date, leave: date | None) -> str:
    joined, left = hire > REFERENCE_START, leave is not None and leave < REFERENCE_END
    return {(False, False): "whole period", (True, False): "joined", (False, True): "left",
            (True, True): "joined and left"}[(joined, left)]


def build() -> list[dict]:
    verify_source()
    with SOURCE_EMPLOYEES.open(newline="") as f:
        source = sorted(csv.DictReader(f), key=lambda r: r["employee_id"])
    with PAYROLL_EXTRACT.open(newline="") as f:
        snapshot = {r["worker_id"]: r for r in csv.DictReader(f)}

    leavers_rng = random.Random(SEED + 1)
    rows = []
    for e in source:
        hire = date.fromisoformat(e["hire_date"])
        leave = date.fromisoformat(e["exit_date"]) if e["exit_date"] else None
        worker_id = e["employee_id"].replace("E", "W")
        # A leaver's rates come from the same rules, drawn for every leaver, paid in the period or not.
        rate = snapshot[worker_id] if leave is None else annual_row(e, leavers_rng)
        days = employed(hire, leave, REFERENCE_START, REFERENCE_END)
        if days == 0:
            continue
        share = days / PERIOD_DAYS
        row = {k: round(float(rate[k]) * share) for k in PRO_RATA}
        on_payday = hire <= BONUS_PAYDAY and (leave is None or leave >= BONUS_PAYDAY)
        service_2025 = employed(hire, leave, date(2025, 1, 1), date(2025, 12, 31)) / 365
        row["bonus"] = int(round(float(rate["bonus"]) * service_2025 / 10)) * 10 if on_payday else 0
        weekly = int(rate["weekly_hours"])
        rows.append({
            "worker_id": worker_id, "country": rate["country"], "role": rate["role"], "gender": rate["gender"],
            "weekly_hours": weekly, "annual_hours": round(weekly * WEEKS_PER_YEAR * share, 2),
            **{k: row[k] for k in ("base_pay",)},
            "payroll_total": row["base_pay"] + row["bonus"] + row["commission"] + row["shift_allowance"]
            + row["car_allowance"],
            "bonus": row["bonus"], "commission": row["commission"], "shift_allowance": row["shift_allowance"],
            "car_allowance": row["car_allowance"], "period_status": status(hire, leave),
        })
    return rows


def main() -> None:
    rows = build()
    with PAYROLL_PERIOD.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"reference year: {len(rows):,} workers paid -> {PAYROLL_PERIOD.relative_to(PAYROLL_PERIOD.parents[1])}")


if __name__ == "__main__":
    main()
