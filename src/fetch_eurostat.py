"""
The official gender pay gap the employer will be read against: Eurostat, earn_gr_gpgr2.

The unadjusted gender pay gap by NACE Rev. 2 activity, structure of earnings survey methodology: the difference
between men's and women's average gross hourly earnings as a share of men's, in enterprises with 10 employees or
more, part-timers included, paid overtime in and non-regular payments out (Eurostat metadata, earn_grgpg2_esms).
The same formula as Article 9(1)(a) on hourly pay; the pay counted differs, and src/benchmark.py says how.

Fetching and parsing are split, so the parser is tested on a captured payload and the pipeline never needs the
network: run this file to refresh data/eurostat_gpg.csv, then commit it with the date it was read.

    python src/fetch_eurostat.py
"""
import csv
import json
import sys
import urllib.request
from datetime import date

from config import DATA

DATASET = "earn_gr_gpgr2"
URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/" + DATASET
GEOS = ["EU27_2020", "IT", "PL", "DE", "ES"]
# The business economy, and the three sections closest to this employer's mix of functions: customer service and
# operations (N, administrative and support services), technology (J, information and communication) and the
# finance, HR and sales functions of a professional services firm (M).
NACE = ["B-S_X_O", "J", "M", "N"]
SINCE = 2018
OUT = DATA / "eurostat_gpg.csv"
COLUMNS = ["geo", "nace_r2", "year", "gap_pct", "flag", "dataset_updated", "read_on"]


def fetch() -> dict:
    query = "&".join(["format=JSON", "lang=en", f"sinceTimePeriod={SINCE}", *[f"geo={g}" for g in GEOS],
                      *[f"nace_r2={n}" for n in NACE]])
    with urllib.request.urlopen(f"{URL}?{query}", timeout=60) as r:
        return json.load(r)


def parse(payload: dict, read_on: date) -> list[dict]:
    """JSON-stat 2.0 to one row per geo, activity and year; a missing value is left out, its absence reported."""
    dims, sizes = payload["id"], payload["size"]
    index = {k: payload["dimension"][k]["category"]["index"] for k in dims}
    values, status = payload.get("value", {}), payload.get("status", {})
    updated = payload.get("updated", "")[:10]
    rows = []
    for geo in GEOS:
        for nace in NACE:
            for year in sorted(index["time"]):
                pick = {"freq": "A", "unit": "PC", "geo": geo, "nace_r2": nace, "time": year}
                pos = 0
                for k, n in zip(dims, sizes, strict=True):
                    if pick[k] not in index[k]:
                        pos = None
                        break
                    pos = pos * n + index[k][pick[k]]
                if pos is None or str(pos) not in values:
                    continue
                rows.append({"geo": geo, "nace_r2": nace, "year": int(year), "gap_pct": values[str(pos)],
                             "flag": status.get(str(pos), ""), "dataset_updated": updated,
                             "read_on": read_on.isoformat()})
    return rows


def write(rows: list[dict]) -> None:
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows = parse(fetch(), date.today())
    if not rows:
        sys.exit(f"{DATASET} returned no values for {GEOS} x {NACE}: nothing written")
    write(rows)
    missing = [(g, n) for g in GEOS for n in NACE if not any(r["geo"] == g and r["nace_r2"] == n for r in rows)]
    print(f"{DATASET}: {len(rows)} values -> {OUT.relative_to(OUT.parents[1])}"
          + (f"; no values for {missing}" if missing else ""))


if __name__ == "__main__":
    main()
