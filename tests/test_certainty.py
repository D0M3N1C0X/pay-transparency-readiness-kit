"""The certainty module: the counterfactual payroll, the exact decomposition, the intervals, the verdicts."""
import math

import numpy as np
import pandas as pd
import pytest

import build_extract
import certainty
from config import PAYROLL_EXTRACT


@pytest.fixture(scope="module")
def assessed():
    return certainty.assess()


def test_the_planted_build_is_the_committed_extract():
    committed = pd.read_csv(PAYROLL_EXTRACT)
    rebuilt = certainty.workers(planted=True)
    pd.testing.assert_frame_equal(rebuilt[committed.columns], committed)


def test_the_counterfactual_changes_only_womens_pay():
    planted = pd.DataFrame(build_extract.build())
    clean = pd.DataFrame(build_extract.build(planted=False))
    men = planted["gender"] == "M"
    pd.testing.assert_frame_equal(planted[men], clean[men])
    women = ~men
    keep = [c for c in planted.columns if c not in ("base_pay", "bonus", "commission", "shift_allowance")]
    pd.testing.assert_frame_equal(planted.loc[women, keep], clean.loc[women, keep])
    assert (clean.loc[women, "base_pay"] > planted.loc[women, "base_pay"]).all()
    sales = women & (planted["department"] == "Sales")
    assert clean.loc[sales, "commission"].mean() > planted.loc[sales, "commission"].mean() * 1.15


def frame(rows):
    """rows: (gender, role, rating, weekly_hours, hourly)."""
    df = pd.DataFrame(rows, columns=["gender", "role", "performance_rating", "weekly_hours", "hourly_total"])
    return df


def test_the_decomposition_adds_up_exactly():
    rng = np.random.default_rng(1)
    rows = []
    for i in range(400):
        g = "F" if i % 3 else "M"
        role = ["A", "B", "C"][(i * 7) % 3 if g == "M" else (i % 5) % 3]
        pay = {"A": 20, "B": 25, "C": 32}[role] * (0.97 if g == "F" else 1.0) * math.exp(rng.normal(0, 0.05))
        rows.append((g, role, 1 + i % 5, 40 if i % 11 else 32, pay))
    d = certainty.decompose(frame(rows))
    assert abs(d["identity_error"]) < 1e-12
    assert d["role"] + d["neutral"] + d["within_role"] == pytest.approx(d["gap"], abs=1e-12)
    # The within-role effect is 3% of pay, about 3 log points, recovered within its interval.
    within_log = d["within_role"] / d["gap"] * d["log_gap"]
    assert within_log == pytest.approx(-math.log(0.97), abs=0.015)
    assert d["within_low"] < d["within_role"] < d["within_high"]


def test_no_within_role_gap_when_only_the_role_differs():
    rows = [("F", "A", 3, 40, 20.0)] * 30 + [("F", "B", 3, 40, 30.0)] * 10 + \
           [("M", "A", 3, 40, 20.0)] * 10 + [("M", "B", 3, 40, 30.0)] * 30
    d = certainty.decompose(frame(rows))
    assert d["within_role"] == pytest.approx(0.0, abs=1e-12)
    assert d["role"] == pytest.approx(d["gap"], abs=1e-12)


def test_resampling_a_constant_gives_a_constant():
    rng = np.random.default_rng(0)
    sims = certainty.resampled_gaps(np.full(7, 90.0), np.full(5, 100.0), rng, draws=50)
    assert np.allclose(sims, 0.10)


@pytest.mark.parametrize("obs, low, high, expected", [
    (0.08, 0.06, 0.10, certainty.SOLID),
    (0.08, 0.02, 0.12, certainty.CLOSE),
    (-0.08, -0.12, -0.06, certainty.SOLID),
    (-0.08, -0.12, 0.01, certainty.CLOSE),
    (0.01, -0.03, 0.04, certainty.CLEAR),
    (0.03, -0.01, 0.07, certainty.NEAR),
    (-0.03, -0.07, 0.01, certainty.NEAR),
])
def test_verdicts(obs, low, high, expected):
    assert certainty.verdict(obs, low, high) == expected


def test_intervals_contain_the_observed_gap(assessed):
    full = assessed["full"]
    assert ((full["low_hourly"] <= full["gap_hourly"]) & (full["gap_hourly"] <= full["high_hourly"])).all()


def test_every_flag_has_a_cause_and_the_counts_hold(assessed):
    f = assessed["flagged"]
    assert len(f) == 12
    assert set(f["cause"]) <= {"Planted mechanisms", "Structure"}


def test_the_pooled_estimate_finds_the_planted_effect_and_nothing_without_it(assessed):
    p = assessed["pooled"]
    assert (p["within_low"] > 0).all()
    assert ((p["within_low_clean"] < 0) & (p["within_high_clean"] > 0)).all()
    # The planted base-pay residual alone is about 2.3% of a woman's salary; the estimate is in that range.
    assert p["within_role"].between(0.01, 0.035).all()


def test_false_alarms_on_the_clean_payroll_are_rare(assessed):
    assert assessed["false_alarms_clean"] <= 0.1 * assessed["cells"]
