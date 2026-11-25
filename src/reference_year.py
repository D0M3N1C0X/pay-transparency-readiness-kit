"""
The figures on a reference year instead of a snapshot: who was paid, not who is on the payroll today.

Reads data/payroll_reference_year.csv (src/build_period.py) the way the browser tool reads an actual-pay file:
each worker's own contractual hours for the period are the denominator of hourly pay, passed to derive() as
annual hours / 52, the convention web/app.js uses. Then the same Article 9 items and Article 10 screen run on it
and are set against the snapshot's.
"""
import pandas as pd

import article9
import article10
import certainty
from config import BANDS, ENTITIES, JPA_THRESHOLD, PAYROLL_PERIOD, WEEKS_PER_YEAR
from workers import derive

LEFT = ("left", "joined and left")


def load_period() -> pd.DataFrame:
    p = pd.read_csv(PAYROLL_PERIOD)
    p["weekly_hours"] = p["annual_hours"] / WEEKS_PER_YEAR
    return derive(p)


def _flags(screen: pd.DataFrame) -> set[tuple[str, str]]:
    return set(map(tuple, screen.loc[screen["status"] == article10.STATUS_FLAG, ["country", "category"]].values))


def _gap(x: pd.DataFrame, col: str = "hourly_total") -> float:
    return article9.gap(x.loc[x["gender"] == "F", col].mean(), x.loc[x["gender"] == "M", col].mean())


def compare(snapshot: pd.DataFrame, period: pd.DataFrame | None = None) -> dict:
    period = load_period() if period is None else period
    codes, cats = list(ENTITIES), [b for _, b in BANDS]
    ind_s, ind_p = article9.by_entity(snapshot, codes), article9.by_entity(period, codes)
    scr_s, scr_p = article10.screen(snapshot, codes, cats), article10.screen(period, codes, cats)
    fs, fp = _flags(scr_s), _flags(scr_p)
    flagged_p = scr_p[scr_p["status"] == article10.STATUS_FLAG]
    annual_only = flagged_p[flagged_p["gap_hourly"].abs() < JPA_THRESHOLD]
    verdicts = certainty.intervals(snapshot).set_index(["country", "category"])["verdict"]
    new = sorted(fp - fs)
    leavers = period[period["period_status"].isin(LEFT)]
    stayers = period[~period["period_status"].isin(LEFT)]
    kept_cost = flagged_p[[tuple(k) in fs for k in flagged_p[["country", "category"]].values]]["remedy_cost"].sum()
    return {
        "period": period, "ind_s": ind_s, "ind_p": ind_p, "scr_s": scr_s, "scr_p": scr_p,
        "kept": sorted(fs & fp), "dropped": sorted(fs - fp), "new": new,
        "new_verdicts": {k: verdicts.get(k, "") for k in new},
        "annual_only": sorted(map(tuple, annual_only[["country", "category"]].values)),
        "cost_s": float(scr_s.loc[scr_s["status"] == article10.STATUS_FLAG, "remedy_cost"].sum()),
        "cost_p": float(flagged_p["remedy_cost"].sum()),
        "counts": period["period_status"].value_counts().to_dict(),
        "women_share_left": float((leavers["gender"] == "F").mean()),
        "gap_leavers": _gap(leavers), "gap_stayers": _gap(stayers),
        "kept_cost_share": float(kept_cost / flagged_p["remedy_cost"].sum()),
    }
