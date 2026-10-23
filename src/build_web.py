"""
Writes what the browser tool needs (web/inputs.json and two template files) and the cases its JavaScript is
checked against (tests/fixtures/js_vectors.json): the sample payroll and random variants of it, each with the
results computed here by pandas. tests/js/check_engine.mjs recomputes every case with web/engine.js and fails at
the first difference, so the page and the pipeline cannot drift apart.
"""
import json
import math
import random

import pandas as pd

import article9
import article10
import obligations
from config import (
    BANDS,
    ENTITIES,
    FACTOR_WEIGHTS,
    FACTORS,
    FULL_TIME_WEEKLY_HOURS,
    JPA_THRESHOLD,
    MIN_CELL,
    PAYROLL_EXTRACT,
    REMEDY_MONTHS,
    ROOT,
    SIZE_BANDS,
    WEEKS_PER_YEAR,
)
from workers import COMPONENTS, derive, load_job_evaluation

WEB = ROOT / "web"
VECTORS = ROOT / "tests" / "fixtures" / "js_vectors.json"
# The columns the tool reads from a payroll file; the components are whichever pay columns the user ticks.
COLUMNS = ["worker_id", "country", "role", "gender", "weekly_hours", "base_pay", *COMPONENTS]
STATUS = {article10.STATUS_ONE_SEX: "one_sex", article10.STATUS_FLAG: "flag", article10.STATUS_OK: "ok"}


def cfg() -> dict:
    status = obligations.transposition().set_index("country")
    return {
        "full_time_weekly_hours": FULL_TIME_WEEKLY_HOURS, "weeks_per_year": WEEKS_PER_YEAR,
        "threshold": JPA_THRESHOLD, "min_cell": MIN_CELL, "remedy_months": REMEDY_MONTHS,
        "factors": FACTORS, "weights": FACTOR_WEIGHTS, "bands": [[floor, label] for floor, label in BANDS],
        "size_bands": [[floor, label, frequency, first.isoformat() if first else None]
                       for floor, label, frequency, first in SIZE_BANDS],
        "entities": ENTITIES, "components": COMPONENTS,
        "transposition": {c: {k: str(r[k]) for k in ("status", "instrument", "reporting", "notes", "checked_on")}
                          for c, r in status.iterrows()},
    }


def _clean(x: object) -> object:
    """NaN is not JSON: it becomes null, and the JavaScript check reads null as 'no value'."""
    if isinstance(x, float) and math.isnan(x):
        return None
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_clean(v) for v in x]
    return x


def write_inputs() -> None:
    WEB.mkdir(exist_ok=True)
    (WEB / "inputs.json").write_text(json.dumps(cfg(), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    extract = pd.read_csv(PAYROLL_EXTRACT)
    extract[COLUMNS].head(3).to_csv(WEB / "template_payroll.csv", index=False)
    grid = load_job_evaluation()[["role", *FACTORS]]
    grid.head(3).to_csv(WEB / "template_job_evaluation.csv", index=False)


def expected(extract: pd.DataFrame) -> dict:
    """What the pipeline says for one payroll extract: the seven items per employer, the category screen and the
    reporting obligations."""
    w = derive(extract)
    countries = [c for c in ENTITIES if (w["country"] == c).any()]
    items = article9.by_entity(w, countries)
    screen = article10.screen(w, countries, [label for _, label in BANDS])
    screen["status"] = screen["status"].map(STATUS)
    duties = obligations.by_entity(w)
    duties = duties[duties["country"].isin(countries)]
    return _clean({
        "items": {col: {k: float(v) for k, v in items[col].items()} for col in items.columns},
        "screen": screen[["country", "category", "women", "men", "gap_base", "gap_components", "gap_hourly",
                          "gap_annual", "small_cell", "status", "remedy_cost"]].to_dict("records"),
        "quartiles": w[["worker_id", "quartile"]].values.tolist(),
        "obligations": [{"country": r.country, "workers": int(r.workers), "size_band": r.size_band,
                         "first_report": r.first_report.isoformat() if r.first_report else None,
                         "remedy_by": r.remedy_by.isoformat() if r.remedy_by else None}
                        for r in duties.itertuples(index=False)],
    })


def write_vectors(n: int = 6, seed: int = 9) -> int:
    base = pd.read_csv(PAYROLL_EXTRACT)[COLUMNS]
    rng = random.Random(seed)
    cases = [{"rows": None, "patch": [], **expected(base)}]
    for k in range(n):
        rows = sorted(rng.sample(range(len(base)), rng.randint(300, 900)))
        if k == 0:                          # a small employer: size bands, small cells and one-sex categories
            spain = [i for i in rows if base.loc[i, "country"] == "ES"]
            rows = [i for i in rows if base.loc[i, "country"] != "ES"] + spain[:7]
            rows.sort()
        x = base.loc[rows].reset_index(drop=True)
        x[["weekly_hours", "base_pay", *COMPONENTS]] = x[["weekly_hours", "base_pay", *COMPONENTS]].astype(float)
        patch = []
        for _ in range(rng.randint(5, 25)):
            i, col = rng.randrange(len(x)), rng.choice(["base_pay", "bonus", "commission", "weekly_hours"])
            v = (rng.choice([20, 24, 30, 36]) if col == "weekly_hours"
                 else round(float(x.loc[i, col]) * rng.choice([0.5, 0.9, 1.07, 1.5]) + rng.choice([0, 0.5]), 2))
            x.loc[i, col] = v
            patch.append([i, col, v])
        cases.append({"rows": rows, "patch": patch, **expected(x)})
    VECTORS.parent.mkdir(exist_ok=True)
    VECTORS.write_text(json.dumps({"cfg": cfg(), "grid": load_job_evaluation()[["role", *FACTORS]].to_dict("records"),
                                   "base": base.to_dict("records"), "cases": cases},
                                  ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return len(cases)


def main() -> None:
    write_inputs()
    print(f"tool -> web/inputs.json; {write_vectors()} cases -> tests/fixtures/js_vectors.json")


if __name__ == "__main__":
    main()
