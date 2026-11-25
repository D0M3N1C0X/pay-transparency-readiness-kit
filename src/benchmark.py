"""
The employer's gap set against the official figures it will be compared with (data/eurostat_gpg.csv).

Eurostat's gap and Article 9(1)(a) share a formula, (men - women) / men on mean hourly pay, but not the pay:
the structure of earnings survey counts regular earnings and paid overtime and leaves non-regular payments out,
so the employer's figure is computed both ways, with and without the annual bonus. Commission and allowances are
paid monthly here and count as regular.

The employer has no single activity code: its customer service and operations staff look like section N, its
technology staff like J, its finance, HR and sales functions like a professional services firm, M. So it is read
against the business economy, the figure a newspaper will quote, and against those three sections.
"""
import pandas as pd

from article9 import gap
from config import DATA, ENTITIES

SOURCE = DATA / "eurostat_gpg.csv"
SECTIONS = {"J": "Information and communication", "M": "Professional, scientific and technical",
            "N": "Administrative and support services"}
ECONOMY = "B-S_X_O"


def load() -> pd.DataFrame:
    return pd.read_csv(SOURCE, keep_default_na=False, dtype={"flag": str})


def compare(w: pd.DataFrame) -> dict:
    g = load()
    year = int(g["year"].max())
    latest = g[g["year"] == year].set_index(["geo", "nace_r2"])["gap_pct"] / 100
    flags = g[g["year"] == year].set_index(["geo", "nace_r2"])["flag"]
    rows = []
    for c in ENTITIES:
        x = w[w["country"] == c]
        f, m = x["gender"] == "F", x["gender"] == "M"
        regular = (x["total_pay"] - x["bonus"]) / x["annual_hours"]
        sections = {s: float(latest.get((c, s), float("nan"))) for s in SECTIONS}
        rows.append({
            "country": c,
            "article9": gap(x.loc[f, "hourly_total"].mean(), x.loc[m, "hourly_total"].mean()),
            "regular": gap(regular[f].mean(), regular[m].mean()),
            "economy": float(latest[(c, ECONOMY)]),
            **{f"sec_{s}": v for s, v in sections.items()},
            "sec_low": min(sections.values()), "sec_high": max(sections.values()),
            "provisional": bool((flags.loc[c] == "p").any()) if c in flags.index.get_level_values(0) else False,
        })
    t = pd.DataFrame(rows)
    t["times_economy"] = t["regular"] / t["economy"]
    t["inside_sections"] = (t["regular"] >= t["sec_low"]) & (t["regular"] <= t["sec_high"])
    trend = (g[(g["nace_r2"] == ECONOMY)].pivot(index="geo", columns="year", values="gap_pct") / 100)
    return {"table": t, "year": year, "eu": float(latest[("EU27_2020", ECONOMY)]), "trend": trend,
            "updated": g["dataset_updated"].iloc[0], "read_on": g["read_on"].iloc[0]}
