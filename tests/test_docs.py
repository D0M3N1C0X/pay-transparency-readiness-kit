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


def test_catalogue_is_current_and_complete() -> None:
    """docs/catalogue.md is generated from the code and the workbook: if either changes, it must be rebuilt."""
    import article9
    import build_catalogue
    text = build_catalogue.text()
    assert (DATA.parent / "docs" / "catalogue.md").read_text(encoding="utf-8") == text
    covered = {k for card in build_catalogue.CARDS for k in card["keys"]}
    statutory = {k for k, _, _ in article9.ITEMS if k[:2] in ("a_", "b_", "c_", "d_", "e_") or "share_women" in k}
    assert statutory <= covered
