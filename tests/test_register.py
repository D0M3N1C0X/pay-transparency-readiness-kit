"""The justification register and the Article 7 reply."""
from datetime import date

import pandas as pd
import pytest

import article7
import register
from config import MIN_CELL
from workers import load_workers


@pytest.fixture(scope="module")
def w():
    return load_workers()


@pytest.fixture(scope="module")
def reg(w):
    return register.build(w)


def test_one_row_per_flag_most_expensive_first(reg):
    assert len(reg) == 12
    assert reg["ref"].is_unique
    assert reg["cost_ceiling_eur"].is_monotonic_decreasing


def test_the_committed_register_is_current(reg):
    committed = pd.read_csv(register.OUT, keep_default_na=False)
    assert committed["ref"].tolist() == reg["ref"].tolist()
    assert committed["evidence_needed"].tolist() == reg["evidence_needed"].tolist()


def test_annual_only_flags_are_about_time_worked(reg):
    assert (reg.loc[reg["measure"] == "annual", "main_driver"] == "Time worked").all()


def test_nothing_is_decided_for_the_employer(reg):
    assert (reg["status"] == "Open").all()
    assert (reg["decision"] == "").all() and (reg["evidence_held"] == "").all()


def test_review_comes_before_the_deadline(reg):
    assert (pd.to_datetime(reg["review_by"]) < pd.to_datetime(reg["remedy_by"])).all()


def test_article7_figures_are_the_category_averages(w):
    a = article7.answer(w, "W00013", date(2027, 7, 1))
    peers = w[(w["country"] == "IT") & (w["category"] == a["category"])]
    assert a["women_hourly"] == pytest.approx(peers.loc[peers["gender"] == "F", "hourly_total"].mean())
    assert a["men_annual"] == pytest.approx(peers.loc[peers["gender"] == "M", "total_pay"].mean())
    assert (a["answer_by"] - a["received"]).days <= 62


def test_article7_holds_back_small_categories(w):
    counts = w.groupby(["country", "category", "gender"]).size().unstack(fill_value=0)
    country, cat = counts[counts.min(axis=1) < MIN_CELL].index[0]
    worker = w.loc[(w["country"] == country) & (w["category"] == cat), "worker_id"].iloc[0]
    a = article7.answer(w, worker, date(2027, 7, 1))
    assert not a["shown"] and "women_hourly" not in a
    for lang in ("en", "it"):
        text = article7.letter(a, lang)
        assert "€" in text                       # the worker's own pay is always given
        assert text.count("€") == 2              # and nobody else's


def test_article7_examples_are_current(w, tmp_path, monkeypatch):
    monkeypatch.setattr(article7, "EXAMPLES", tmp_path / "a7.md")
    article7.write_examples(w)
    assert (tmp_path / "a7.md").read_text() == (article7.ROOT / "docs" / "article7-response.md").read_text()
