"""The data, the job evaluation, the obligations and the cross-checks between outputs."""
import csv
import hashlib
from datetime import date

import pytest

import build_extract
import obligations
from article9 import by_entity
from config import FACTOR_WEIGHTS, PAYROLL_EXTRACT, SOURCE_EMPLOYEES, SOURCE_SHA256
from workers import load_job_evaluation, load_workers


@pytest.fixture(scope="module")
def workers():
    return load_workers()


def test_source_matches_the_pinned_checksum():
    assert hashlib.sha256(SOURCE_EMPLOYEES.read_bytes()).hexdigest() == SOURCE_SHA256


def test_extract_is_rebuilt_byte_for_byte():
    rows = build_extract.build()
    with PAYROLL_EXTRACT.open(newline="") as f:
        committed = list(csv.DictReader(f))
    assert len(rows) == len(committed) == 3443
    assert [{k: str(v) for k, v in r.items()} for r in rows] == committed


def test_planted_commission_effect_is_there(workers):
    sales = workers[workers["department"] == "Sales"]
    rate = (sales["commission"] / sales["base_pay"]).groupby(sales["gender"]).mean()
    assert rate["F"] < rate["M"] - 0.015


def test_weights_sum_to_100_and_points_are_whole():
    assert sum(FACTOR_WEIGHTS.values()) == 100
    grid = load_job_evaluation()
    assert grid["points"].between(100, 500).all()
    assert grid["points"].dtype.kind == "i"


def test_points_rise_with_level_inside_every_department():
    grid = load_job_evaluation().sort_values(["department", "job_level"])
    for dept, g in grid.groupby("department"):
        assert g["points"].is_monotonic_increasing, dept


def test_every_role_in_the_extract_is_evaluated(workers):
    assert workers["category"].notna().all()


@pytest.mark.parametrize("n, band, first", [
    (99, "Fewer than 100", None), (100, "100 to 149", date(2031, 6, 7)), (149, "100 to 149", date(2031, 6, 7)),
    (150, "150 to 249", date(2027, 6, 7)), (249, "150 to 249", date(2027, 6, 7)),
    (250, "250 or more", date(2027, 6, 7)),
])
def test_size_bands_follow_article_9(n, band, first):
    label, _, first_report = obligations.size_band(n)
    assert (label, first_report) == (band, first)


def test_remedy_deadline_is_six_months_after_the_report():
    assert obligations.add_months(date(2027, 6, 7), 6) == date(2027, 12, 7)


def test_base_pay_gap_reconciles_with_hr_people_analytics(workers):
    # hr-people-analytics reports a 15.4% mean gap on base salary for the same 3,443 people.
    # Hourly base pay divides every full-time-equivalent salary by the same 2,080 hours, so the
    # two figures must agree.
    group = by_entity(workers, ["IT", "PL", "DE", "ES"])["Group"]
    assert round(group["base_mean_gap_hourly"] * 100, 1) == 15.4
