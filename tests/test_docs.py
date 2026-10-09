"""data/README.md describes every column of every data file the kit reads."""
import csv

from config import DATA

DOC = (DATA / "README.md").read_text(encoding="utf-8")
FILES = ["payroll_extract.csv", "job_evaluation.csv", "transposition.csv", "readiness_checklist.csv"]


def test_every_column_is_documented() -> None:
    missing = {}
    for name in FILES:
        with (DATA / name).open(encoding="utf-8") as f:
            columns = next(csv.reader(f))
        gaps = [c for c in columns if f"`{c}`" not in DOC]
        if gaps:
            missing[name] = gaps
    assert missing == {}
