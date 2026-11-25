"""The Eurostat parser on a captured payload, and the comparison built on the committed file."""
import json
from datetime import date
from pathlib import Path

import pandas as pd

import benchmark
import fetch_eurostat
from workers import load_workers

PAYLOAD = json.loads((Path(__file__).parent / "fixtures" / "eurostat_gpg_payload.json").read_text())


def test_parse_reads_every_value_with_its_flag():
    rows = fetch_eurostat.parse(PAYLOAD, date(2026, 11, 25))
    got = {(r["geo"], r["nace_r2"], r["year"]): (r["gap_pct"], r["flag"]) for r in rows}
    assert got[("IT", "B-S_X_O", 2024)] == (5.3, "p")
    assert got[("PL", "J", 2024)] == (24.0, "")
    assert ("EU27_2020", "J", 2024) not in got          # Eurostat publishes no EU figure by section here
    assert len(rows) == sum(1 for v in PAYLOAD["value"])


def test_parse_reports_nothing_rather_than_inventing():
    empty = dict(PAYLOAD, value={})
    assert fetch_eurostat.parse(empty, date(2026, 11, 25)) == []


def test_the_committed_file_matches_the_payload():
    rows = fetch_eurostat.parse(PAYLOAD, date(2026, 11, 25))
    committed = pd.read_csv(fetch_eurostat.OUT, keep_default_na=False)
    assert len(committed) == len(rows)
    assert committed["gap_pct"].tolist() == [r["gap_pct"] for r in rows]


def test_regular_pay_leaves_the_bonus_out():
    w = load_workers()
    t = benchmark.compare(w)["table"].set_index("country")
    x = w[w["country"] == "IT"]
    regular = (x["base_pay"] + x["commission"] + x["shift_allowance"] + x["car_allowance"]) / x["annual_hours"]
    f, m = regular[x["gender"] == "F"].mean(), regular[x["gender"] == "M"].mean()
    assert abs(t.loc["IT", "regular"] - (m - f) / m) < 1e-12
    assert (t["regular"] < t["article9"]).all()
