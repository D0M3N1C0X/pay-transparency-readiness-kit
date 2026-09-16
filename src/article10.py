"""
Article 9(1)(g) and the Article 10(1) screen, per employer and category of workers.

A joint pay assessment is owed when three conditions hold together (Article 10(1)): a
difference of at least 5% in the average pay level of women and men in a category, no
justification on objective gender-neutral criteria, and no remedy within six months of
submitting the report. The data can only test the first condition. The other two are the
employer's to answer, so this screen names where the answer is needed and by when.
"""
import pandas as pd

from article9 import gap
from config import JPA_THRESHOLD, MIN_CELL

STATUS_ONE_SEX = "No comparison: one sex only"
STATUS_FLAG = "Justify or remedy"
STATUS_OK = "Below 5%"


def _mean(s: pd.Series) -> float:
    return float(s.mean()) if len(s) else float("nan")


def category_row(g: pd.DataFrame) -> dict:
    f, m = g[g["gender"] == "F"], g[g["gender"] == "M"]
    row = {
        "women": len(f),
        "men": len(m),
        "hourly_base_women": _mean(f["hourly_base"]),
        "hourly_base_men": _mean(m["hourly_base"]),
        "hourly_components_women": _mean(f["hourly_components"]),
        "hourly_components_men": _mean(m["hourly_components"]),
        "hourly_total_women": _mean(f["hourly_total"]),
        "hourly_total_men": _mean(m["hourly_total"]),
        "annual_total_women": _mean(f["total_pay"]),
        "annual_total_men": _mean(m["total_pay"]),
    }
    row["gap_base"] = gap(row["hourly_base_women"], row["hourly_base_men"])
    row["gap_components"] = gap(row["hourly_components_women"], row["hourly_components_men"])
    row["gap_hourly"] = gap(row["hourly_total_women"], row["hourly_total_men"])
    row["gap_annual"] = gap(row["annual_total_women"], row["annual_total_men"])
    row["small_cell"] = int(min(len(f), len(m)) < MIN_CELL)

    if len(f) == 0 or len(m) == 0:
        row["status"] = STATUS_ONE_SEX
        row["remedy_cost"] = 0.0
        return row
    # "a difference ... of at least 5%": either direction, on either measure of pay level.
    flagged = abs(row["gap_hourly"]) >= JPA_THRESHOLD or abs(row["gap_annual"]) >= JPA_THRESHOLD
    row["status"] = STATUS_FLAG if flagged else STATUS_OK
    # Upper bound of the annual cost of closing the hourly gap by lifting the lower-paid
    # group's average to the other's, before any part of the gap is justified.
    if flagged and row["gap_hourly"] > 0:
        row["remedy_cost"] = (row["hourly_total_men"] - row["hourly_total_women"]) * f["annual_hours"].sum()
    elif flagged and row["gap_hourly"] < 0:
        row["remedy_cost"] = (row["hourly_total_women"] - row["hourly_total_men"]) * m["annual_hours"].sum()
    else:
        row["remedy_cost"] = 0.0
    return row


def screen(w: pd.DataFrame, countries: list[str], categories: list[str]) -> pd.DataFrame:
    rows = []
    for c in countries:
        for cat in categories:
            g = w[(w["country"] == c) & (w["category"] == cat)]
            if g.empty:
                continue
            rows.append({"country": c, "category": cat, **category_row(g)})
    return pd.DataFrame(rows)
