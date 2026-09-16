"""
What each employer owes, and when: Article 9(2)-(4) size bands, the national status of
transposition, and the illustrative readiness checklist.
"""
import pandas as pd

from config import DATA, ENTITIES, REMEDY_MONTHS, SIZE_BANDS


def size_band(workers: int) -> tuple[str, str, object]:
    for floor, label, frequency, first in SIZE_BANDS:
        if workers >= floor:
            return label, frequency, first
    raise ValueError(workers)


def add_months(d, months: int):
    y, m = divmod(d.month - 1 + months, 12)
    return d.replace(year=d.year + y, month=m + 1)


def by_entity(w: pd.DataFrame) -> pd.DataFrame:
    status = pd.read_csv(DATA / "transposition.csv").set_index("country")
    rows = []
    for c, name in ENTITIES.items():
        n = int((w["country"] == c).sum())
        band, frequency, first = size_band(n)
        rows.append({
            "country": c,
            "entity": name,
            "workers": n,
            "size_band": band,
            "frequency": frequency,
            "first_report": first,
            "remedy_by": add_months(first, REMEDY_MONTHS) if first else None,
            "transposition": status.loc[c, "status"],
            "instrument": status.loc[c, "instrument"],
        })
    return pd.DataFrame(rows)


def readiness() -> pd.DataFrame:
    return pd.read_csv(DATA / "readiness_checklist.csv").fillna("")


def transposition() -> pd.DataFrame:
    return pd.read_csv(DATA / "transposition.csv")
