"""
Article 9(1)(g) and the Article 10(1) screen, per employer and category of workers.

A joint pay assessment is owed when three conditions hold together (Article 10(1)): a
difference of at least 5% in the average pay level of women and men in a category, no
justification on objective gender-neutral criteria, and no remedy within six months of
submitting the report. The data can only test the first condition. The other two are the
employer's to answer, so this screen names where the answer is needed and by when.

Italy applies the screen to "livello retributivo", fixed and continuing pay (D.lgs. 96/2026, art. 10(1)(a)),
so national_screen runs it again on that measure for the employers whose law defines one.
"""
import pandas as pd

from article9 import gap
from config import JPA_THRESHOLD, MIN_CELL, NATIONAL_MEASURE

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

    return _verdict(row, f, m, "hourly_total")


def _verdict(row: dict, f: pd.DataFrame, m: pd.DataFrame, hourly: str) -> dict:
    """Status and remedy cost, from the row's two gaps and its mean hourly pay of women and men."""
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
        row["remedy_cost"] = (row[f"{hourly}_men"] - row[f"{hourly}_women"]) * f["annual_hours"].sum()
    elif flagged and row["gap_hourly"] < 0:
        row["remedy_cost"] = (row[f"{hourly}_women"] - row[f"{hourly}_men"]) * m["annual_hours"].sum()
    else:
        row["remedy_cost"] = 0.0
    return row


def national_row(g: pd.DataFrame) -> dict:
    """The screen on fixed and continuing pay ("livello retributivo")."""
    f, m = g[g["gender"] == "F"], g[g["gender"] == "M"]
    row = {
        "women": len(f),
        "men": len(m),
        "hourly_fixed_women": _mean(f["hourly_fixed"]),
        "hourly_fixed_men": _mean(m["hourly_fixed"]),
        "annual_fixed_women": _mean(f["fixed_pay"]),
        "annual_fixed_men": _mean(m["fixed_pay"]),
    }
    row["gap_hourly"] = gap(row["hourly_fixed_women"], row["hourly_fixed_men"])
    row["gap_annual"] = gap(row["annual_fixed_women"], row["annual_fixed_men"])
    row["small_cell"] = int(min(len(f), len(m)) < MIN_CELL)
    return _verdict(row, f, m, "hourly_fixed")


def screen(w: pd.DataFrame, countries: list[str], categories: list[str]) -> pd.DataFrame:
    rows = []
    for c in countries:
        for cat in categories:
            g = w[(w["country"] == c) & (w["category"] == cat)]
            if g.empty:
                continue
            rows.append({"country": c, "category": cat, **category_row(g)})
    return pd.DataFrame(rows)


def national_screen(w: pd.DataFrame, countries: list[str], categories: list[str]) -> pd.DataFrame:
    """The screen again on the national measure, for the employers whose law defines one."""
    rows = []
    for c in countries:
        if c not in NATIONAL_MEASURE:
            continue
        for cat in categories:
            g = w[(w["country"] == c) & (w["category"] == cat)]
            if g.empty:
                continue
            rows.append({"country": c, "category": cat, **national_row(g)})
    return pd.DataFrame(rows)
