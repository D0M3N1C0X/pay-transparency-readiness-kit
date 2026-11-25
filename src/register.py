"""
The justification register: one row per flagged category, with what has to be proved, by whom and by when.

A justification is only as good as the record behind it. For each category the screen flags, the register states
what drives the gap (from the split in src/certainty.py and the base-or-components reading of item (g)), the
evidence that kind of gap needs, the function that owns it, a review date halfway to the remedy deadline, and how
solid the flag is: its interval and whether it stays flagged on the reference year. The status and evidence
columns are left for the employer to fill in; nothing here decides that a gap is justified.

Writes reports/justification_register.csv.
"""
import pandas as pd

import article10
import certainty
import obligations
import reference_year
from config import ENTITIES, REPORTS

OUT = REPORTS / "justification_register.csv"

# What each kind of gap has to be justified with, and who holds the evidence.
EVIDENCE = {
    "Role mix": ("Market pay data for each role in the category, dated and sourced; the job evaluation scores that "
                 "put the roles together; hiring and promotion records showing how women and men came to hold the "
                 "lower- and higher-paid roles", "Reward"),
    "Same role": ("For each worker in the roles concerned: starting pay, every increase and the criterion applied "
                  "(experience at hire, tenure, a documented skill); if no objective criterion explains the "
                  "difference, a remedy", "Reward with line managers"),
    "Rating and part-time": ("The rating distribution by sex with the calibration record; the rules that link pay "
                             "to rating and to hours", "HR business partners"),
    "Time worked": ("Contractual hours and periods employed, by sex; confirmation that hourly rates do not differ, "
                    "since the flag is on annual pay only", "HR operations"),
}
COMPONENTS_EVIDENCE = ("The rules of each component (bonus, commission, allowances) and how its basis is allocated: "
                       "territories, targets, eligibility; who received what, by sex", "Sales operations and Reward")
COLUMNS = ["ref", "employer", "category", "women", "men", "measure", "gap", "interval_95", "flag_strength",
           "flagged_on_reference_year", "main_driver", "pay_element", "evidence_needed", "owner", "cost_ceiling_eur",
           "review_by", "remedy_by", "status", "evidence_held", "decision"]


def driver(r: pd.Series) -> str:
    if r["measure"] == "annual":
        return "Time worked"
    parts = {"Role mix": r["role"], "Same role": r["within_role"], "Rating and part-time": r["neutral"]}
    return max(parts, key=lambda k: abs(parts[k]))


def element(row: pd.Series) -> str:
    """Base pay or components: which moves the hourly gap more (item (g))."""
    men = row["hourly_total_men"]
    base = (row["hourly_base_men"] - row["hourly_base_women"]) / men
    comp = (row["hourly_components_men"] - row["hourly_components_women"]) / men
    return "Components" if abs(comp) > abs(base) else "Base pay"


def build(w: pd.DataFrame) -> pd.DataFrame:
    a = certainty.assess(w)
    flagged = a["flagged"].set_index(["country", "category"])
    screen = article10.screen(w, list(ENTITIES), sorted({c for _, c in flagged.index}))
    screen = screen.set_index(["country", "category"])
    ref = reference_year.compare(w)
    still = set(ref["kept"])
    duties = obligations.by_entity(w).set_index("country")
    rows = []
    order = flagged.assign(cost=screen.loc[flagged.index, "remedy_cost"]).sort_values("cost", ascending=False)
    for i, ((c, cat), r) in enumerate(order.iterrows(), start=1):
        s = screen.loc[(c, cat)]
        kind = driver(r)
        pay = element(s)
        evidence, owner = EVIDENCE[kind]
        if pay == "Components" and kind != "Time worked":
            names = [*owner.split(" with "), *COMPONENTS_EVIDENCE[1].split(" and ")]
            evidence = f"{evidence}. {COMPONENTS_EVIDENCE[0]}"
            owner = ", ".join(dict.fromkeys(names))
        gap_v = r[f"gap_{r['measure']}"]
        first, deadline = duties.loc[c, "first_report"], duties.loc[c, "remedy_by"]
        rows.append({
            "ref": f"J{i:02d}", "employer": ENTITIES[c], "category": cat, "women": int(r["women"]),
            "men": int(r["men"]), "measure": r["measure"], "gap": round(float(gap_v), 4),
            "interval_95": f"{r['low_' + r['measure']] * 100:.1f}% to {r['high_' + r['measure']] * 100:.1f}%",
            "flag_strength": r["verdict"], "flagged_on_reference_year": "Yes" if (c, cat) in still else "No",
            "main_driver": kind, "pay_element": pay, "evidence_needed": evidence, "owner": owner,
            "cost_ceiling_eur": int(round(float(s["remedy_cost"]))),
            "review_by": obligations.add_months(first, 3).isoformat(), "remedy_by": deadline.isoformat(),
            "status": "Open", "evidence_held": "", "decision": "",
        })
    return pd.DataFrame(rows, columns=COLUMNS)


def write(w: pd.DataFrame) -> pd.DataFrame:
    reg = build(w)
    reg.to_csv(OUT, index=False, lineterminator="\n")
    return reg


