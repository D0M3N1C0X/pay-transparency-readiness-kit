"""The reference-year payroll: who is in it, what each worker is paid, and how the figures compare."""
from datetime import date

import pandas as pd
import pytest

import build_period
import certainty
import reference_year
from config import BONUS_PAYDAY, PAYROLL_EXTRACT, PAYROLL_PERIOD, WEEKS_PER_YEAR
from workers import load_workers


@pytest.fixture(scope="module")
def period():
    return pd.read_csv(PAYROLL_PERIOD)


@pytest.mark.parametrize("hire, leave, days", [
    (date(2020, 1, 1), None, 365),
    (date(2026, 6, 30), None, 1),
    (date(2020, 1, 1), date(2025, 7, 1), 1),
    (date(2025, 10, 1), date(2025, 10, 31), 31),
    (date(2026, 7, 1), None, 0),
])
def test_days_employed(hire, leave, days):
    assert build_period.employed(hire, leave, date(2025, 7, 1), date(2026, 6, 30)) == days


def test_the_committed_file_is_current(period):
    rebuilt = pd.DataFrame(build_period.build())
    pd.testing.assert_frame_equal(rebuilt, period, check_dtype=False)


def test_whole_period_workers_are_paid_their_snapshot_rates(period):
    snap = pd.read_csv(PAYROLL_EXTRACT).set_index("worker_id")
    whole = period[period["period_status"] == "whole period"].set_index("worker_id")
    for col in ("base_pay", "commission", "shift_allowance", "car_allowance"):
        assert (whole[col] == snap.loc[whole.index, col]).all(), col
    assert (whole["annual_hours"] == whole["weekly_hours"] * WEEKS_PER_YEAR).all()


def test_totals_and_hours(period):
    parts = period[["base_pay", "bonus", "commission", "shift_allowance", "car_allowance"]].sum(axis=1)
    assert (period["payroll_total"] == parts).all()
    assert (period["annual_hours"] > 0).all()
    assert (period["annual_hours"] <= period["weekly_hours"] * WEEKS_PER_YEAR).all()


def test_nobody_gone_before_payday_gets_a_bonus(period):
    src = pd.read_csv(build_period.SOURCE_EMPLOYEES, parse_dates=["hire_date", "exit_date"])
    src["worker_id"] = src["employee_id"].str.replace("E", "W")
    gone = src[(src["exit_date"] < pd.Timestamp(BONUS_PAYDAY)) | (src["hire_date"] > pd.Timestamp("2025-12-31"))]
    assert (period.set_index("worker_id").loc[gone["worker_id"], "bonus"] == 0).all()


def test_every_worker_paid_in_the_period_is_in_the_file(period):
    assert len(period) == 4000
    assert period["worker_id"].is_unique


def test_the_new_flags_were_close_to_the_line():
    r = reference_year.compare(load_workers())
    assert r["new"], "the reference year should move some flags"
    assert all(v in (certainty.NEAR, certainty.CLOSE) for v in r["new_verdicts"].values())
    assert sum(r["counts"].values()) == 4000
