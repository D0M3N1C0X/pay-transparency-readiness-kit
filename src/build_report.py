"""
Writes reports/readiness_report.md (and its figures), the written read-out of the dry run.

Every number in the text comes from the same functions that feed the workbook, so the
report, the workbook and the deck cannot drift apart.
"""
import pandas as pd

import article9
import article10
import charts
import obligations
from config import BANDS, ENTITIES, JPA_THRESHOLD, MIN_CELL, REPORTS, SNAPSHOT
from workers import load_workers

FIG = REPORTS / "figures"


def pct(x, d=1):
    return "n/a" if pd.isna(x) else f"{x * 100:.{d}f}%"


def eur(x):
    return f"€{x:,.0f}"


def eur_m(x):
    return f"€{x / 1e6:.1f} million"


def day(d, month="%B"):
    return f"{d.day} {d:{month} %Y}"


def md_table(head, rows, align):
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join("---:" if a == "r" else "---" for a in align) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def driver(row) -> str:
    """What moves a flagged category's gap most."""
    if abs(row["gap_hourly"]) < JPA_THRESHOLD:
        return "Hours worked: flagged on annual pay only"
    men_total = row["hourly_total_men"]
    base_part = (row["hourly_base_men"] - row["hourly_base_women"]) / men_total
    comp_part = (row["hourly_components_men"] - row["hourly_components_women"]) / men_total
    share = lambda part: f"{part * 100:.1f} of {row['gap_hourly'] * 100:.1f} pts"
    if abs(comp_part) > abs(base_part):
        return f"Components ({share(comp_part)})"
    return f"Base pay ({share(base_part)})"


def facts(w: pd.DataFrame) -> dict:
    codes = list(ENTITIES)
    ind = article9.by_entity(w, codes)
    cats = article10.screen(w, codes, [b for _, b in BANDS])
    obl = obligations.by_entity(w)
    ready = obligations.readiness()
    sales = w[w["department"] == "Sales"].assign(rate=lambda d: d["commission"] / d["base_pay"])
    flagged = cats[cats["status"] == article10.STATUS_FLAG]
    return {"codes": codes, "ind": ind, "cats": cats, "obl": obl, "ready": ready, "flagged": flagged,
            "sales_rate": sales.groupby("gender")["rate"].mean(),
            "sales_n": sales["gender"].value_counts()}


def write(w: pd.DataFrame) -> dict:
    f = facts(w)
    codes, ind, cats, obl, ready, flagged = (f[k] for k in ("codes", "ind", "cats", "obl", "ready", "flagged"))
    FIG.mkdir(parents=True, exist_ok=True)

    (FIG / "01_gap_by_employer.svg").write_text(charts.gap_by_employer(
        [(ENTITIES[c], ind.loc["a_mean_gap_hourly", c], ind.loc["c_median_gap_hourly", c]) for c in codes]))
    (FIG / "02_quartile_bands.svg").write_text(charts.quartile_dumbbell(
        [(ENTITIES[c], ind.loc["f_q1_share_women", c], ind.loc["f_q4_share_women", c]) for c in codes]))
    cells = {(ENTITIES[r.country], r.category): (r.gap_hourly, r.gap_annual, r.status == article10.STATUS_FLAG,
                                                 bool(r.small_cell))
             for r in cats.itertuples() if r.status != article10.STATUS_ONE_SEX}
    (FIG / "03_category_screen.svg").write_text(charts.category_grid(
        [ENTITIES[c] for c in codes], [b for _, b in BANDS], cells, JPA_THRESHOLD))

    G = ind["Group"]
    first = obl["first_report"].min()
    remedy_by = obl["remedy_by"].min()
    total_cost = flagged["remedy_cost"].sum()
    counts = ready["status"].value_counts()
    rate = f["sales_rate"]
    gap_widening = G["a_mean_gap_hourly"] - G["base_mean_gap_hourly"]
    worst = ind.loc["a_mean_gap_hourly", codes].astype(float)
    hi, lo = worst.idxmax(), worst.idxmin()
    status = obligations.transposition().set_index("country")

    L = []
    add = L.append
    add("# Pay transparency readiness: where the organisation stands before its first report")
    add("")
    add(f"**Scope:** four employers - {', '.join(ENTITIES.values())} - with {G['workers']:,.0f} workers "
        f"active on {SNAPSHOT:%d %B %Y}")
    add("**Method:** Article 9 reporting items and the Article 10 screen, computed twice - in pandas and in a "
        "live Excel model - and reconciled figure by figure")
    add("**Data:** synthetic, built on the organisation analysed in "
        "[hr-people-analytics](https://github.com/D0M3N1C0X/hr-people-analytics)")
    add("")
    add("> This is a dry run, not a statutory report. It uses annualised pay of the workers present at the "
        "snapshot; the real report covers pay in the previous calendar year, under rules each Member State "
        "sets in its own transposition.")
    add("")
    add("## The answer")
    add("")
    add(f"- **Every employer reports every year, starting {day(first)}.** All four have 250 workers or more, "
        f"so the first report covers pay in 2026 (Article 9(2)).")
    add(f"- **The gender pay gap on hourly pay is {pct(G['a_mean_gap_hourly'])} across the group**, from "
        f"{pct(worst[lo])} in {ENTITIES[lo]} to {pct(worst[hi])} in {ENTITIES[hi]}. On base pay alone it is "
        f"{pct(G['base_mean_gap_hourly'])} - the figure hr-people-analytics reports - so bonuses, commission and "
        f"allowances add {gap_widening * 100:.1f} points.")
    add(f"- **{len(flagged)} of {len(cats)} categories of workers show a difference of 5% or more.** Each needs an "
        f"objective, gender-neutral justification or a remedy within six months of the report "
        f"({day(remedy_by)}); otherwise a joint pay assessment with workers' representatives follows "
        f"(Article 10).")
    add(f"- **Closing those gaps outright would cost at most {eur_m(total_cost)} a year**, before any part of "
        f"them is justified.")
    add(f"- **The organisation is not ready yet:** of 14 obligations, {counts.get('Ready', 0)} is in place, "
        f"{counts.get('Partial', 0)} are partly in place and {counts.get('Gap', 0)} are missing - pay ranges in "
        f"vacancies, published progression criteria and a route for workers' information requests among them.")
    add(f"- **The law is settled in one country of four.** {status.loc['IT', 'instrument'].split(' (')[0]} "
        f"transposes the Directive in Italy; Poland has transposed the recruitment rules only, and Germany and "
        f"Spain have not finished.")
    add("")

    add("## 1. What each employer owes, and when")
    add("")
    add(md_table(["Employer", "Workers", "Reporting", "First report", "Remedy by", "Transposition"],
                 [[r.entity, f"{r.workers:,}", r.frequency, day(r.first_report, "%b"),
                   day(r.remedy_by, "%b"), r.transposition] for r in obl.itertuples()],
                 "lrllll"))
    add("")
    add("*Remedy by: six months after the first report, the latest date to justify or close a category gap "
        "before a joint pay assessment is due. National status as checked on 16 September 2026; "
        "sources in [docs/verification.md](../docs/verification.md).*")
    add("")
    add(f"For Italy, applying a national collective agreement signed by representative unions is presumed to "
        f"comply, classification included, so the categories of workers should start from the agreement's "
        f"levels and use job evaluation to complement them, not replace them. The categories in this dry run "
        f"come from job evaluation alone, because the synthetic organisation has no collective agreement. "
        f"*[to verify on the decree text]*")
    add("")

    add("## 2. The seven reporting items")
    add("")
    rows = []
    for key, label, kind in article9.ITEMS:
        if key.startswith(("f_q2", "f_q3")) or "share_men" in key and key.startswith("f_"):
            continue
        fmt = (lambda v: f"{v:,.0f}") if kind == "count" else pct
        rows.append([label, *[fmt(ind.loc[key, c]) for c in codes], fmt(G[key])])
    add(md_table(["Item", *codes, "Group"], rows, "lrrrrr"))
    add("")
    add("*Gaps are men's pay level minus women's, as a share of men's (Article 3(1)(c)); positive means women "
        "are paid less. Items (b) and (d) are computed among workers who receive any component. The middle "
        "quartile bands and the men's shares are in the workbook. The group column is a management view, "
        "not a statutory figure.*")
    add("")
    add("![Gender pay gap by employer](figures/01_gap_by_employer.svg)")
    add("")
    add(f"The median gap sits below the mean everywhere, which says the gap is concentrated at the top of "
        f"the pay distribution. The quartile bands show why: women are {pct(G['f_q1_share_women'], 0)} of the "
        f"lowest band and {pct(G['f_q4_share_women'], 0)} of the highest.")
    add("")
    add("![Share of women in the lowest and highest pay bands](figures/02_quartile_bands.svg)")
    add("")

    add("## 3. Bonus, commission and allowances widen the gap")
    add("")
    add(f"Among workers who receive any component, women's average is {pct(G['b_mean_gap_components'])} below "
        f"men's (median {pct(G['d_median_gap_components'])}), and fewer women receive one at all: "
        f"{pct(G['e_share_women_receiving'], 0)} against {pct(G['e_share_men_receiving'], 0)}. Two mechanisms "
        f"produce most of it:")
    add("")
    share = (w["gender"] == "F").groupby(w["job_level"]).mean()
    add(f"- **Eligibility follows seniority.** Bonus starts at level L3 and car allowances at L5, while the share "
        f"of women falls from {pct(share['L1'], 0)} at L1 to {pct(share['L6'], 0)} at L6. That part is structural "
        f"and shows up again in the quartile bands.")
    add(f"- **Commission follows territory.** In Sales, commission averages {pct(rate['F'])} of base pay for women "
        f"and {pct(rate['M'])} for men. Commission rules are the same for everyone; the territories are not. "
        f"The generator allocates women territories with lower sales potential - an effect planted on purpose "
        f"and stated in [data/README.md](../data/README.md), because indirect discrimination through allocation "
        f"is exactly what an Article 10 assessment should surface.")
    add("")

    add("## 4. Categories of workers: where a justification is needed")
    add("")
    add("Categories come from a gender-neutral job evaluation: every role is scored 1-5 on skills, effort, "
        "responsibility and working conditions (Article 4(4)), and roles with similar points form a category, "
        "whatever their department. That is how a customer service team lead and a software engineer can do "
        "work of equal value - and why a category can mix functions the market pays very differently.")
    add("")
    add("![Hourly pay gap by employer and category](figures/03_category_screen.svg)")
    add("")
    drivers = {(r.country, r.category): driver(r._asdict()) for r in flagged.itertuples()}
    rows = [[ENTITIES[r.country], r.category, f"{r.women} / {r.men}", pct(r.gap_hourly), pct(r.gap_annual),
             drivers[(r.country, r.category)], eur(r.remedy_cost)]
            for r in flagged.sort_values("remedy_cost", ascending=False).itertuples()]
    by_base = sum(d.startswith("Base pay") for d in drivers.values())
    by_comp = sum(d.startswith("Components") for d in drivers.values())
    add(md_table(["Employer", "Category", "Women / men", "Hourly gap", "Annual gap", "Main driver",
                  "Cost to close, upper bound"], rows, "llrrrlr"))
    add("")
    small = cats[cats["small_cell"] == 1]
    add(f"*Cost to close: the lower-paid sex's average hourly pay lifted to the other's, for all their hours, a "
        f"year. {len(small)} categories have fewer than {MIN_CELL} workers of one sex "
        f"({', '.join(f'{ENTITIES[r.country]} {r.category}' for r in small.itertuples())}); their figures should "
        f"go only to workers' representatives, the labour inspectorate or the equality body (Article 12(3)).*")
    add("")
    add("How to read the list:")
    add("")
    add(f"- **Base pay drives {by_base} of the {len(flagged)} flags.** A gap within a category of equal value is where a justification has "
        "to be specific: experience, performance, a scarce skill priced in the market - each documented, "
        "gender-neutral and applied to everyone.")
    add(f"- **Components - bonus, commission, allowances - drive {by_comp}: look at the rules and at who they "
        f"reach.** A commission scheme or an allowance that is neutral on paper can still pay women less "
        f"through allocation or eligibility.")
    add("- **A flag on annual pay only points to hours worked.** Part-time work is a legitimate reason for a "
        "lower annual total; the hourly figure is the one to defend.")
    add("- **Gaps in either direction count.** A category where men are paid less is flagged the same way.")
    add("")

    add("## 5. Readiness: what has to be in place")
    add("")
    add(md_table(["Ref", "Article", "Requirement", "Status", "Owner"],
                 [[r.ref, r.article, r.requirement, r.status, r.owner] for r in ready.itertuples()],
                 "lllll"))
    add("")
    add("*Statuses are illustrative for the demonstration organisation. Evidence expected for each item is in "
        "the workbook's Readiness sheet.*")
    add("")

    add("## 6. The next 90 days")
    add("")
    add("1. **Agree the job evaluation with workers' representatives** in each country, starting from the Italian "
        "collective agreement's classification. Categories decide every later number.")
    add("2. **Write or rule out a justification for each flagged category**, beginning with the most expensive, "
        "and budget the remedy for the rest before the first report is filed.")
    add("3. **Review the Sales territory allocation** and any other rule that decides who can earn a component.")
    add("4. **Close the recruitment gaps now**: pay ranges in vacancies, no pay-history questions, "
        "gender-neutral titles - already law in Italy and Poland.")
    add("5. **Build the information-request route** (two-month answer) and the annual notice to workers.")
    add("6. **Rerun this model on calendar-year 2026 payroll** once each country's rules are final, and have "
        "management confirm the figures after consulting workers' representatives (Article 9(6)).")
    add("")

    add("## 7. Method, choices and limits")
    add("")
    add("- **Two engines, one answer.** Every figure is computed in pandas and again by live formulas in "
        "[the workbook](../deliverables/pay_transparency_model.xlsx); its Reconciliation sheet checks "
        "each pair, and CI recalculates the workbook with LibreOffice and fails on any mismatch.")
    add("- **Where the Directive leaves a choice, the choice is stated.** Pay includes base, bonus, commission "
        "and allowances; hourly pay uses contractual hours; components gaps (b) and (d) are among recipients; "
        "quartile bands are four equal groups by hourly pay with ties broken by row order; a category is "
        "flagged at 5% in either direction on hourly or annual pay. Full list in "
        "[docs/method.md](../docs/method.md).")
    add("- **Legal claims carry their source** and a status in [docs/verification.md](../docs/verification.md). "
        "Items marked *[to verify]* need the final national text.")
    add("- **Limits.** Synthetic data; a snapshot rather than a calendar year; leavers, leave-related pay "
        "(Article 10(2)(e)) and pay in kind beyond a car allowance are not modelled; not legal advice.")
    add("")
    (REPORTS / "readiness_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return f


def main() -> None:
    write(load_workers())
    import report_html
    report_html.build()
    print("report -> reports/readiness_report.md, reports/index.html, 3 figures")


if __name__ == "__main__":
    main()
