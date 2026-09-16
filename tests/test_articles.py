"""Article 9 and Article 10 on hand-checked examples."""
import math

import pandas as pd
import pytest

import article9
import article10
from workers import derive


def frame(rows):
    """rows: (country, gender, base, components, weekly_hours, category)."""
    df = pd.DataFrame(rows, columns=["country", "gender", "base_pay", "components", "weekly_hours", "category"])
    df["annual_hours"] = df["weekly_hours"] * 52
    df["total_pay"] = df["base_pay"] + df["components"]
    df["hourly_base"] = df["base_pay"] / df["annual_hours"]
    df["hourly_components"] = df["components"] / df["annual_hours"]
    df["hourly_total"] = df["total_pay"] / df["annual_hours"]
    df["receives_components"] = (df["components"] > 0).astype(int)
    df["quartile"] = 1
    return df


def test_gap_is_a_share_of_mens_pay():
    assert article9.gap(90, 100) == pytest.approx(0.10)
    assert article9.gap(110, 100) == pytest.approx(-0.10)
    assert math.isnan(article9.gap(90, 0))


def test_mean_and_median_gaps():
    w = frame([
        ("IT", "F", 20800, 0, 40, "A"), ("IT", "F", 41600, 0, 40, "A"), ("IT", "F", 62400, 0, 40, "A"),
        ("IT", "M", 41600, 0, 40, "A"), ("IT", "M", 62400, 0, 40, "A"),
    ])
    out = article9.indicators(w)
    # hourly: women 10, 20, 30 (mean 20, median 20); men 20, 30 (mean 25, median 25)
    assert out["a_mean_gap_hourly"] == pytest.approx(0.20)
    assert out["c_median_gap_hourly"] == pytest.approx(0.20)


def test_hourly_and_annual_gaps_differ_with_part_time():
    # Same hourly pay, but the woman works four days: no hourly gap, a 20% annual gap.
    w = frame([("IT", "F", 33280, 0, 32, "A"), ("IT", "M", 41600, 0, 40, "A")])
    out = article9.indicators(w)
    assert out["a_mean_gap_hourly"] == pytest.approx(0.0)
    assert out["a_mean_gap_annual"] == pytest.approx(0.20)


def test_component_gaps_are_among_recipients():
    w = frame([
        ("IT", "F", 40000, 1000, 40, "A"), ("IT", "F", 40000, 0, 40, "A"),
        ("IT", "M", 40000, 2000, 40, "A"), ("IT", "M", 40000, 2000, 40, "A"),
    ])
    out = article9.indicators(w)
    assert out["b_mean_gap_components"] == pytest.approx(0.5)   # 1000 vs 2000, the zero is not averaged in
    assert out["e_share_women_receiving"] == pytest.approx(0.5)
    assert out["e_share_men_receiving"] == pytest.approx(1.0)


def test_quartiles_are_equal_groups_with_ties_broken_by_row_order():
    rows = [("IT", "F" if i % 2 else "M", 41600, 0, 40, "Cat A") for i in range(8)]  # eight identical salaries
    extract = pd.DataFrame(rows, columns=["country", "gender", "base_pay", "bonus", "weekly_hours", "category"])
    extract = extract.drop(columns="category").assign(
        worker_id=[f"W{i}" for i in range(8)], role="Customer Service L1", commission=0, shift_allowance=0,
        car_allowance=0)
    w = derive(extract)
    assert w["quartile"].tolist() == [1, 1, 2, 2, 3, 3, 4, 4]


def test_screen_flags_either_direction_and_annual_only():
    women_paid_less = article10.category_row(frame([("IT", "F", 37960, 0, 40, "A"), ("IT", "M", 40000, 0, 40, "A")]))
    assert women_paid_less["status"] == article10.STATUS_FLAG            # 5.1%
    men_paid_less = article10.category_row(frame([("IT", "F", 42200, 0, 40, "A"), ("IT", "M", 40000, 0, 40, "A")]))
    assert men_paid_less["gap_hourly"] < 0 and men_paid_less["status"] == article10.STATUS_FLAG
    annual_only = article10.category_row(frame([("IT", "F", 33280, 0, 32, "A"), ("IT", "M", 41600, 0, 40, "A")]))
    assert abs(annual_only["gap_hourly"]) < 0.05 and annual_only["status"] == article10.STATUS_FLAG
    below = article10.category_row(frame([("IT", "F", 39000, 0, 40, "A"), ("IT", "M", 40000, 0, 40, "A")]))
    assert below["status"] == article10.STATUS_OK and below["remedy_cost"] == 0


def test_screen_one_sex_and_small_cells():
    one_sex = article10.category_row(frame([("IT", "M", 40000, 0, 40, "A")] * 6))
    assert one_sex["status"] == article10.STATUS_ONE_SEX and one_sex["small_cell"] == 1
    rows = [("IT", "F", 40000, 0, 40, "A")] * 4 + [("IT", "M", 40000, 0, 40, "A")] * 10
    assert article10.category_row(frame(rows))["small_cell"] == 1
    rows = [("IT", "F", 40000, 0, 40, "A")] * 5 + [("IT", "M", 40000, 0, 40, "A")] * 10
    assert article10.category_row(frame(rows))["small_cell"] == 0


def test_remedy_cost_lifts_the_lower_paid_sex_for_all_their_hours():
    # Women 20/h, men 25/h, two women on 2,080 hours: 5 x 4,160 = 20,800.
    w = frame([("IT", "F", 41600, 0, 40, "A"), ("IT", "F", 41600, 0, 40, "A"), ("IT", "M", 52000, 0, 40, "A")])
    assert article10.category_row(w)["remedy_cost"] == pytest.approx(20800)
