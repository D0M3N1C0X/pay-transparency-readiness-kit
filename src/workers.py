"""
Loads the payroll extract and derives every per-worker figure the Directive needs.

Each derived column here has a twin formula column in the workbook's Payroll sheet, built in
the same order of operations so that the two agree to the last bit.
"""
import pandas as pd

from config import BANDS, FACTOR_WEIGHTS, FACTORS, JOB_EVALUATION, PAYROLL_EXTRACT, WEEKS_PER_YEAR

COMPONENTS = ["bonus", "commission", "shift_allowance", "car_allowance"]
VARIABLE = ["bonus", "commission"]          # variable components
COMPLEMENTARY = ["shift_allowance", "car_allowance"]  # complementary components


def band_for(points: int) -> str:
    label = BANDS[0][1]
    for floor, name in BANDS:
        if points >= floor:
            label = name
    return label


def load_job_evaluation() -> pd.DataFrame:
    grid = pd.read_csv(JOB_EVALUATION)
    grid["points"] = sum(grid[f] * FACTOR_WEIGHTS[f] for f in FACTORS)
    grid["category"] = grid["points"].map(band_for)
    return grid


def load_workers() -> pd.DataFrame:
    return derive(pd.read_csv(PAYROLL_EXTRACT))


def derive(extract: pd.DataFrame) -> pd.DataFrame:
    """Every derived column, from the extract's own rows (a sample gets its own quartiles)."""
    w = extract.reset_index(drop=True)
    grid = load_job_evaluation()
    w = w.merge(grid[["role", "points", "category"]], on="role", how="left", validate="many_to_one")
    if w["category"].isna().any():
        missing = sorted(w.loc[w["category"].isna(), "role"].unique())
        raise SystemExit(f"Roles missing from the job evaluation grid: {missing}")

    w["annual_hours"] = w["weekly_hours"] * WEEKS_PER_YEAR
    comp = w[COMPONENTS[0]]
    for c in COMPONENTS[1:]:
        comp = comp + w[c]
    w["components"] = comp
    w["total_pay"] = w["base_pay"] + w["components"]
    w["hourly_base"] = w["base_pay"] / w["annual_hours"]
    w["hourly_components"] = w["components"] / w["annual_hours"]
    w["hourly_total"] = w["total_pay"] / w["annual_hours"]
    w["receives_components"] = (w["components"] > 0).astype(int)

    # Quartile pay bands (Article 3(1)(f)): four equal groups by pay level within each
    # employer. Ties are broken by row order, which the workbook reproduces with COUNTIFS.
    w["rank_in_entity"] = (w.groupby("country")["hourly_total"]
                           .rank(method="first").astype(int))
    n = w.groupby("country")["worker_id"].transform("size")
    w["quartile"] = ((w["rank_in_entity"] - 1) * 4 // n + 1).clip(upper=4)
    return w
