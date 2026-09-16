"""
Writes tidy extracts for a Tableau Public dashboard (see tableau/README.md).

Tableau Desktop is not scriptable here, so the kit ships the data and a build sheet; the
dashboard itself is assembled by hand and published to Tableau Public.
"""
import pandas as pd

import article9
import article10
from config import BANDS, ENTITIES, TABLEAU
from workers import load_workers

WORKER_COLUMNS = ["worker_id", "entity", "country", "department", "job_level", "role", "category", "points",
                  "gender", "contract_type", "work_model", "fte", "annual_hours", "base_pay", "bonus",
                  "commission", "shift_allowance", "car_allowance", "components", "total_pay", "hourly_base",
                  "hourly_total", "receives_components", "quartile"]


def write(w) -> None:
    TABLEAU.mkdir(parents=True, exist_ok=True)
    codes = list(ENTITIES)

    workers = w[WORKER_COLUMNS].copy()
    workers["sex"] = workers.pop("gender").map({"F": "Women", "M": "Men"})
    workers.round(6).to_csv(TABLEAU / "workers.csv", index=False)

    ind = article9.by_entity(w, codes)
    labels = {key: (label, kind) for key, label, kind in article9.ITEMS}
    rows = []
    for key in ind.index:
        if key not in labels:
            continue
        label, kind = labels[key]
        for col in ind.columns:
            rows.append({"employer": ENTITIES.get(col, "Group"), "code": col, "item_key": key,
                         "item": label, "kind": kind, "value": round(float(ind.loc[key, col]), 6)})
    pd.DataFrame(rows).to_csv(TABLEAU / "article9_items.csv", index=False)

    cats = article10.screen(w, codes, [b for _, b in BANDS])
    cats.insert(0, "employer", cats["country"].map(ENTITIES))
    cats.round(6).to_csv(TABLEAU / "categories.csv", index=False)


def main() -> None:
    write(load_workers())
    print("tableau extracts -> tableau/workers.csv, article9_items.csv, categories.csv")


if __name__ == "__main__":
    main()
