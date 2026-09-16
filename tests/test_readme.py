"""The headline numbers quoted in the README are the ones the pipeline produces."""
from pathlib import Path

import build_report
import build_workbook
from workers import load_workers

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def pct(x):
    return f"{x * 100:.1f}%"


def test_readme_quotes_current_figures(tmp_path):
    w = load_workers()
    f = build_report.facts(w)
    ind, cats, flagged, ready = f["ind"], f["cats"], f["flagged"], f["ready"]
    group = ind["Group"]
    worst = ind.loc["a_mean_gap_hourly", f["codes"]].astype(float)
    counts = ready["status"].value_counts()
    expected = [
        pct(group["a_mean_gap_hourly"]),
        pct(worst.min()),
        pct(worst.max()),
        pct(group["base_mean_gap_hourly"]),
        f"add {(group['a_mean_gap_hourly'] - group['base_mean_gap_hourly']) * 100:.1f} points",
        f"{len(flagged)} of {len(cats)} categories",
        f"{pct(f['sales_rate']['F'])} of base pay for women and {pct(f['sales_rate']['M'])} for men",
        f"€{flagged['remedy_cost'].sum() / 1e6:.1f} million",
        build_report.day(f["obl"]["remedy_by"].min()),
        f"{counts.get('Ready', 0)} is in place, {counts.get('Partial', 0)} partly, {counts.get('Gap', 0)} missing",
        f"reconciled on {len(build_workbook.build(w, tmp_path / 'm.xlsx').checks)} checks",
    ]
    missing = [e for e in expected if e not in README]
    assert not missing, f"README is out of date: {missing}"
