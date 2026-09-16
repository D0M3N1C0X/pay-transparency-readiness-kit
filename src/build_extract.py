"""
Turns the organisation from hr-people-analytics into the payroll extract a client would send.

The source table has base salary only - its report says so and stops there. Article 9 also
asks about complementary and variable components, so this step adds four of them with
documented rules. One effect is planted on purpose and declared in data/README.md: women in
Sales are given territories with lower sales potential, which lowers their commission.

Standard library only, so the extract is byte-identical on every Python version.
"""
import csv
import hashlib
import random

from config import (BONUS_PAYOUT, BONUS_TARGET, CAR_ALLOWANCE_ANNUAL, COMMISSION_RATE, ENTITIES,
                    FULL_TIME_WEEKLY_HOURS, PAYROLL_EXTRACT, SEED, SHIFT_ALLOWANCE_MONTHLY,
                    SOURCE_EMPLOYEES, SOURCE_SHA256)

COLUMNS = ["worker_id", "entity", "country", "site", "department", "job_level", "role", "gender",
           "contract_type", "work_model", "fte", "weekly_hours", "performance_rating",
           "base_pay", "bonus", "commission", "shift_allowance", "car_allowance"]

# Mean territory potential by sex in Sales (1.0 = average territory). The planted effect.
TERRITORY_MEAN = {"M": 1.0, "F": 0.82}


def verify_source() -> None:
    digest = hashlib.sha256(SOURCE_EMPLOYEES.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(f"{SOURCE_EMPLOYEES} does not match the pinned checksum.\n"
                         f"expected {SOURCE_SHA256}\nfound    {digest}\n"
                         "Copy the file again from the commit named in src/config.py.")


def round_to(x: float, step: int = 10) -> int:
    return int(round(x / step)) * step


def build() -> list[dict]:
    verify_source()
    with SOURCE_EMPLOYEES.open(newline="") as f:
        active = [r for r in csv.DictReader(f) if not r["exit_date"]]
    active.sort(key=lambda r: r["employee_id"])

    rng = random.Random(SEED)
    rows = []
    for e in active:
        # Three draws per worker whatever their role, so adding a rule never shifts the
        # random stream of everyone after them.
        bonus_noise, territory_draw, commission_noise = rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1)

        country, level, dept, gender = e["country"], e["job_level"], e["department"], e["gender"]
        fte = float(e["fte"])
        base = round(float(e["base_salary_eur"]) * fte)   # the source salary is full-time equivalent
        rating = int(e["performance_rating"])

        bonus = 0
        if BONUS_TARGET[level] > 0:
            bonus = round_to(base * BONUS_TARGET[level] * BONUS_PAYOUT[rating]
                             * max(0.0, 1 + 0.06 * bonus_noise))

        commission = 0
        if dept == "Sales":
            potential = min(1.8, max(0.3, TERRITORY_MEAN[gender] + 0.18 * territory_draw))
            commission = round_to(base * COMMISSION_RATE * potential
                                  * max(0.0, 1 + 0.10 * commission_noise))

        shift = 0
        if dept in ("Operations", "Customer Service") and level in ("L1", "L2", "L3") \
                and e["work_model"] == "Onsite":
            shift = round(SHIFT_ALLOWANCE_MONTHLY[country] * 12 * fte)

        car = CAR_ALLOWANCE_ANNUAL[country] if level in ("L5", "L6") else 0

        rows.append({
            "worker_id": e["employee_id"].replace("E", "W"),
            "entity": ENTITIES[country],
            "country": country,
            "site": e["site"],
            "department": dept,
            "job_level": level,
            "role": f"{dept} {level}",
            "gender": gender,
            "contract_type": e["contract_type"],
            "work_model": e["work_model"],
            "fte": e["fte"],
            "weekly_hours": round(FULL_TIME_WEEKLY_HOURS * fte),
            "performance_rating": rating,
            "base_pay": base,
            "bonus": bonus,
            "commission": commission,
            "shift_allowance": shift,
            "car_allowance": car,
        })
    return rows


def main() -> None:
    rows = build()
    with PAYROLL_EXTRACT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"payroll extract: {len(rows):,} workers -> {PAYROLL_EXTRACT.relative_to(PAYROLL_EXTRACT.parents[1])}")


if __name__ == "__main__":
    main()
