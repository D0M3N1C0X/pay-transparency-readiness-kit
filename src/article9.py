"""
Article 9(1): the seven pay-gap reporting items, per employer.

Definitions follow Article 3(1): a gap is the difference between men's and women's pay level
expressed as a share of men's, and "pay level" is both gross annual pay and the corresponding
gross hourly pay, so items (a) and (c) are reported both ways. Where the Directive leaves a
choice open, the choice is named in docs/method.md.
"""
import math

import pandas as pd


def gap(women: float, men: float) -> float:
    """(men - women) / men. Positive means women are paid less."""
    if men == 0 or math.isnan(men) or math.isnan(women):
        return float("nan")
    return (men - women) / men


def _stat(s: pd.Series, how: str) -> float:
    if s.empty:
        return float("nan")
    return float(s.mean() if how == "mean" else s.median())


def indicators(w: pd.DataFrame) -> dict:
    """The Article 9(1) items (a)-(f) for one employer (or for the group view)."""
    f, m = w[w["gender"] == "F"], w[w["gender"] == "M"]
    fr, mr = f[f["receives_components"] == 1], m[m["receives_components"] == 1]
    out = {
        "workers": len(w),
        "women": len(f),
        "men": len(m),
        # (a) gender pay gap, on total pay
        "a_mean_gap_hourly": gap(_stat(f["hourly_total"], "mean"), _stat(m["hourly_total"], "mean")),
        "a_mean_gap_annual": gap(_stat(f["total_pay"], "mean"), _stat(m["total_pay"], "mean")),
        # (b) gap in complementary or variable components, among those who receive them
        "b_mean_gap_components": gap(_stat(fr["components"], "mean"), _stat(mr["components"], "mean")),
        # (c) median gender pay gap
        "c_median_gap_hourly": gap(_stat(f["hourly_total"], "median"), _stat(m["hourly_total"], "median")),
        "c_median_gap_annual": gap(_stat(f["total_pay"], "median"), _stat(m["total_pay"], "median")),
        # (d) median gap in components, among those who receive them
        "d_median_gap_components": gap(_stat(fr["components"], "median"), _stat(mr["components"], "median")),
        # (e) share of each sex receiving components
        "e_share_women_receiving": len(fr) / len(f) if len(f) else float("nan"),
        "e_share_men_receiving": len(mr) / len(m) if len(m) else float("nan"),
        # context, not a reporting item: the gap on base pay alone
        "base_mean_gap_hourly": gap(_stat(f["hourly_base"], "mean"), _stat(m["hourly_base"], "mean")),
        "mean_hourly_total_women": _stat(f["hourly_total"], "mean"),
        "mean_hourly_total_men": _stat(m["hourly_total"], "mean"),
    }
    # (f) share of women and men in each quartile pay band
    for q in (1, 2, 3, 4):
        band = w[w["quartile"] == q]
        out[f"f_q{q}_workers"] = len(band)
        out[f"f_q{q}_share_women"] = (band["gender"] == "F").mean() if len(band) else float("nan")
        out[f"f_q{q}_share_men"] = (band["gender"] == "M").mean() if len(band) else float("nan")
    return out


# Labels in reporting order, shared by the workbook, the report and the deck.
ITEMS = [
    ("workers", "Workers at the snapshot", "count"),
    ("women", "Women", "count"),
    ("men", "Men", "count"),
    ("a_mean_gap_hourly", "(a) Gender pay gap, mean hourly pay", "pct"),
    ("a_mean_gap_annual", "(a) Gender pay gap, mean annual pay", "pct"),
    ("b_mean_gap_components", "(b) Gap in complementary or variable components, mean", "pct"),
    ("c_median_gap_hourly", "(c) Median gender pay gap, hourly pay", "pct"),
    ("c_median_gap_annual", "(c) Median gender pay gap, annual pay", "pct"),
    ("d_median_gap_components", "(d) Median gap in complementary or variable components", "pct"),
    ("e_share_women_receiving", "(e) Women receiving complementary or variable components", "pct"),
    ("e_share_men_receiving", "(e) Men receiving complementary or variable components", "pct"),
    *[(f"f_q{q}_share_women", f"(f) Women in quartile pay band {q}{' (lowest)' if q == 1 else ' (highest)' if q == 4 else ''}", "pct")
      for q in (1, 2, 3, 4)],
    *[(f"f_q{q}_share_men", f"(f) Men in quartile pay band {q}{' (lowest)' if q == 1 else ' (highest)' if q == 4 else ''}", "pct")
      for q in (1, 2, 3, 4)],
    ("base_mean_gap_hourly", "Context: gap on base pay alone, mean hourly", "pct"),
]


def by_entity(w: pd.DataFrame, countries: list[str]) -> pd.DataFrame:
    """One column per employer, plus a non-statutory group view."""
    cols = {c: indicators(w[w["country"] == c]) for c in countries}
    cols["Group"] = indicators(w)
    return pd.DataFrame(cols)
