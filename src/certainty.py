"""
How far the Article 10 screen can be trusted, and where a flagged gap comes from.

The Directive's test is a plain number: a difference of at least 5% in a category triggers the duty to justify
or remedy. The number is what it is, and the obligation follows from it. Three questions sit behind it that the
number alone cannot answer, and an employer preparing its justifications needs all three:

1. **Would the flag survive another year?** A category of 15 women and 9 men can show 6% one year and 2% the next
   with nothing changed. A bootstrap interval per category says which flags are solid and which are close calls.
2. **What is the gap made of?** Inside a category of work of equal value, a gap can come from women holding the
   roles the market pays less (role mix), from gender-neutral factors such as rating and part-time work, or from
   differences that remain between women and men in the same role with the same rating. The three call for
   different justifications. A decomposition splits every category's gap into those parts, exactly.
3. **Does the method find what is really there?** The data are synthetic and the two discriminatory mechanisms
   in them are known: the 2.1% residual in base pay inherited from hr-people-analytics and the poorer Sales
   territories added here. Rebuilding the payroll without them, from the same random draws, gives the ground
   truth: which flags they cause, and how much of each gap they account for. The screen and the decomposition are
   scored against it.

numpy only, for the resampling and the least squares; everything else is pandas as in the rest of the kit.
"""
import csv
import io
from collections.abc import Iterator

import numpy as np
import pandas as pd

import article10
import build_extract
from article9 import gap
from config import BANDS, ENTITIES, JPA_THRESHOLD, MIN_CELL, SEED
from workers import derive

DRAWS = 2000            # bootstrap resamples per category
LEVEL = 0.95            # interval coverage

SOLID = "Solid flag"
CLOSE = "Close call"
CLEAR = "Clearly below 5%"
NEAR = "Below 5%, could cross"


def workers(planted: bool = True) -> pd.DataFrame:
    """Every derived column, for the extract as committed or rebuilt without the planted mechanisms."""
    rows = build_extract.build(planted=planted)
    buf = io.StringIO()
    out = csv.DictWriter(buf, fieldnames=build_extract.COLUMNS, lineterminator="\n")
    out.writeheader()
    out.writerows(rows)
    buf.seek(0)
    return derive(pd.read_csv(buf))


def _cells(w: pd.DataFrame) -> Iterator[tuple[str, str, pd.DataFrame]]:
    """(country, category, rows) for every category with both sexes, in the screen's order."""
    for c in ENTITIES:
        for _, cat in BANDS:
            g = w[(w["country"] == c) & (w["category"] == cat)]
            if (g["gender"] == "F").any() and (g["gender"] == "M").any():
                yield c, cat, g


# ---- 1. Bootstrap intervals ------------------------------------------------------------------------------


def resampled_gaps(women: np.ndarray, men: np.ndarray, rng: np.random.Generator, draws: int = DRAWS) -> np.ndarray:
    """The mean gap, (men - women) / men, over `draws` resamples of each sex with replacement."""
    fw = women[rng.integers(0, len(women), (draws, len(women)))].mean(axis=1)
    fm = men[rng.integers(0, len(men), (draws, len(men)))].mean(axis=1)
    return (fm - fw) / fm


def verdict(observed: float, low: float, high: float, threshold: float = JPA_THRESHOLD) -> str:
    """Where the interval sits against the threshold, in either direction."""
    if abs(observed) >= threshold:
        solid = low >= threshold if observed > 0 else high <= -threshold
        return SOLID if solid else CLOSE
    inside = -threshold < low and high < threshold
    return CLEAR if inside else NEAR


def intervals(w: pd.DataFrame, seed: int = SEED, draws: int = DRAWS) -> pd.DataFrame:
    """Per category: the hourly and annual gaps with percentile intervals, and the verdict on the flagging one."""
    rng = np.random.default_rng(seed)
    tail = (1 - LEVEL) / 2 * 100
    rows = []
    for c, cat, g in _cells(w):
        f, m = g[g["gender"] == "F"], g[g["gender"] == "M"]
        row = {"country": c, "category": cat, "women": len(f), "men": len(m),
               "small_cell": int(min(len(f), len(m)) < MIN_CELL)}
        for name, col in (("hourly", "hourly_total"), ("annual", "total_pay")):
            sims = resampled_gaps(f[col].to_numpy(float), m[col].to_numpy(float), rng, draws)
            row[f"gap_{name}"] = gap(f[col].mean(), m[col].mean())
            row[f"low_{name}"], row[f"high_{name}"] = np.percentile(sims, [tail, 100 - tail])
            row[f"p_over_{name}"] = float((np.abs(sims) >= JPA_THRESHOLD).mean())
        # The measure that decides: hourly unless only the annual gap reaches the threshold.
        key = "annual" if (abs(row["gap_annual"]) >= JPA_THRESHOLD > abs(row["gap_hourly"])) else "hourly"
        row["measure"] = key
        row["verdict"] = verdict(row[f"gap_{key}"], row[f"low_{key}"], row[f"high_{key}"])
        rows.append(row)
    return pd.DataFrame(rows)


# ---- 2. Decomposition ------------------------------------------------------------------------------------


def _design(g: pd.DataFrame) -> tuple[np.ndarray, list[str], dict[str, list[int]]]:
    """Intercept, female, role dummies, rating dummies, part-time: the columns and which group each belongs to."""
    cols, names = [np.ones(len(g))], ["intercept"]
    groups: dict[str, list[int]] = {"role": [], "neutral": []}
    cols.append((g["gender"] == "F").to_numpy(float))
    names.append("female")
    for kind, series in (("role", g["role"]), ("neutral", g["performance_rating"].astype(str))):
        for level in sorted(series.unique())[1:]:
            groups[kind].append(len(cols))
            cols.append((series == level).to_numpy(float))
            names.append(f"{kind}:{level}")
    part = (g["weekly_hours"] < g["weekly_hours"].max()).to_numpy(float)
    if part.any() and not part.all():
        groups["neutral"].append(len(cols))
        cols.append(part)
        names.append("part_time")
    return np.column_stack(cols), names, groups


def decompose(g: pd.DataFrame, col: str = "hourly_total") -> dict:
    """
    Split the gap in mean log pay between men and women into role mix, neutral factors and the rest.

    One least-squares fit of log pay on a female indicator, role, rating and part-time, pooled over both sexes.
    With an intercept and the female indicator in the model, residuals average zero for each sex, so

        mean log pay, men - women = coef' (mean x, men - mean x, women) - coef_female

    holds exactly: the role and neutral terms are the part the characteristics account for, and minus the
    female coefficient is what remains between women and men alike on all of them. The parts are reported as
    shares of the Directive's gap, so they add up to the gap the screen reads. The unexplained part comes with a
    heteroskedasticity-robust (HC1) interval.
    """
    y = np.log(g[col].to_numpy(float))
    X, names, groups = _design(g)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    women = (g["gender"] == "F").to_numpy()
    diff = X[~women].mean(axis=0) - X[women].mean(axis=0)
    log_gap = y[~women].mean() - y[women].mean()
    parts = {k: float(sum(coef[i] * diff[i] for i in idx)) for k, idx in groups.items()}
    parts["within_role"] = float(-coef[1])

    resid = y - X @ coef
    n, k = X.shape
    rank = np.linalg.matrix_rank(X)
    bread = np.linalg.pinv(X.T @ X)
    meat = (X * resid[:, None] ** 2).T @ X
    cov = bread @ meat @ bread * n / max(n - rank, 1)
    se = float(np.sqrt(max(cov[1, 1], 0.0)))

    directive = gap(g.loc[women, col].mean(), g.loc[~women, col].mean())
    scale = directive / log_gap if log_gap else 0.0      # log points -> points of the Directive's gap
    return {"log_gap": float(log_gap), "gap": directive,
            "role": parts["role"] * scale, "neutral": parts["neutral"] * scale,
            "within_role": parts["within_role"] * scale,
            "within_low": (-coef[1] - 1.96 * se) * scale, "within_high": (-coef[1] + 1.96 * se) * scale,
            "identity_error": float(log_gap - (parts["role"] + parts["neutral"] + parts["within_role"])),
            "rank_deficient": int(rank < k)}


def decomposition(w: pd.DataFrame, col: str = "hourly_total") -> pd.DataFrame:
    return pd.DataFrame([{"country": c, "category": cat, **decompose(g, col)} for c, cat, g in _cells(w)])


def pooled(w: pd.DataFrame) -> pd.DataFrame:
    """
    The within-role gap per employer, all categories at once.

    A category holds a hundred people or so, too few to tell a 2% within-role difference from noise; an
    employer holds several hundred. Role fixes the category, so the role terms absorb every category's own
    pay level and the female term is the within-role difference averaged over the employer.
    """
    rows = []
    for c in ENTITIES:
        g = w[w["country"] == c]
        d = decompose(g)
        rows.append({"country": c, "workers": len(g), "within_role": d["within_role"],
                     "within_low": d["within_low"], "within_high": d["within_high"]})
    return pd.DataFrame(rows)


# ---- 3. Against the ground truth -------------------------------------------------------------------------


def truth(observed: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    """The screen on the payroll as it is and as it would be without the planted mechanisms, side by side."""
    codes, cats = list(ENTITIES), [b for _, b in BANDS]
    a = article10.screen(observed, codes, cats)
    b = article10.screen(clean, codes, cats)
    a = a[a["status"] != article10.STATUS_ONE_SEX]
    t = a[["country", "category", "women", "men", "gap_hourly", "gap_annual", "status"]].merge(
        b[["country", "category", "gap_hourly", "gap_annual", "status"]],
        on=["country", "category"], suffixes=("", "_clean"))
    t["planted"] = t["gap_hourly"] - t["gap_hourly_clean"]
    flag, clean_flag = t["status"] == article10.STATUS_FLAG, t["status_clean"] == article10.STATUS_FLAG
    t["cause"] = np.select([flag & ~clean_flag, flag & clean_flag, ~flag & clean_flag],
                           ["Planted mechanisms", "Structure", "Hidden by them"], "No flag either way")
    return t


def assess(w: pd.DataFrame | None = None) -> dict:
    """Everything the report section and the tests read."""
    w = workers() if w is None else w
    clean = workers(planted=False)
    iv = intervals(w)
    dec = decomposition(w)
    dec_clean = decomposition(clean)
    # The split of the gap that triggered the flag: annual pay for the categories flagged on annual pay only.
    dec_annual = decomposition(w, "total_pay")
    t = truth(w, clean)
    key = ["country", "category"]
    full = (t.merge(iv[[*key, "low_hourly", "high_hourly", "low_annual", "high_annual", "measure", "verdict",
                        "p_over_hourly", "small_cell"]], on=key)
             .merge(dec[[*key, "role", "neutral", "within_role", "within_low", "within_high"]], on=key)
             .merge(dec_clean[[*key, "within_role"]].rename(columns={"within_role": "within_clean"}), on=key))
    annual = full[[*key]].merge(dec_annual, on=key)
    pick = (full["measure"] == "annual").to_numpy()
    for k in ("role", "neutral", "within_role", "within_low", "within_high"):
        full.loc[pick, k] = annual.loc[pick, k].to_numpy()
    flagged = full[full["status"] == article10.STATUS_FLAG]
    pool = pooled(w).merge(pooled(clean)[["country", "within_role", "within_low", "within_high"]],
                           on="country", suffixes=("", "_clean"))
    return {"workers": w, "clean": clean, "full": full, "flagged": flagged, "pooled": pool,
            "false_alarms_clean": int(((dec_clean["within_low"] > 0) | (dec_clean["within_high"] < 0)).sum()),
            "cells": len(dec_clean),
            "found_observed": int(((dec["within_low"] > 0) | (dec["within_high"] < 0)).sum())}


if __name__ == "__main__":
    out = assess()
    pd.set_option("display.width", 220)
    print(out["full"][["country", "category", "women", "men", "gap_hourly", "low_hourly", "high_hourly", "verdict",
                       "gap_hourly_clean", "cause", "role", "neutral", "within_role", "within_low", "within_high",
                       "within_clean"]].round(3).to_string())
    print(out["pooled"].round(4).to_string())
    print("false alarms on the clean payroll:", out["false_alarms_clean"], "of", out["cells"])
    print("within-role gap found on the observed payroll:", out["found_observed"], "of", out["cells"])
