"""
Writes reports/readiness_report.md (and its figures), the written read-out of the dry run.

Every number in the text comes from the same functions that feed the workbook, so the
report, the workbook and the deck cannot drift apart.
"""
import pandas as pd

import article9
import article10
import benchmark
import certainty
import charts
import obligations
import reference_year
from config import (
    BANDS,
    BONUS_PAYDAY,
    EIGE_WEIGHTS,
    ENTITIES,
    FIXED_COMPONENTS,
    JPA_THRESHOLD,
    MIN_CELL,
    REFERENCE_END,
    REFERENCE_START,
    REPORTS,
    SNAPSHOT,
)
from workers import load_job_evaluation, load_workers

FIG = REPORTS / "figures"


def pct(x, d=1) -> str:
    return "n/a" if pd.isna(x) else f"{x * 100:.{d}f}%"


def eur(x) -> str:
    return f"€{x:,.0f}"


def eur_m(x) -> str:
    return f"€{x / 1e6:.1f} million"


def day(d, month="%B") -> str:
    return f"{d.day} {d:{month} %Y}"


def md_table(head, rows, align) -> str:
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


def weights_test(w: pd.DataFrame, cats: pd.DataFrame) -> dict:
    """The categories and the screen again with the EU guidelines' default factor weights."""
    ours, eige = load_job_evaluation(), load_job_evaluation(EIGE_WEIGHTS)
    moved = ours.merge(eige[["role", "points", "category"]], on="role", suffixes=("", "_eige"))
    moved = moved[moved["category"] != moved["category_eige"]]
    w2 = w.assign(category=w["role"].map(eige.set_index("role")["category"]))
    other = article10.screen(w2, list(ENTITIES), [b for _, b in BANDS])
    flags = lambda s: set(map(tuple, s.loc[s["status"] == article10.STATUS_FLAG, ["country", "category"]].values))
    return {"roles": moved, "workers": int(w["role"].isin(moved["role"]).sum()), "n_roles": len(ours),
            "only_ours": sorted(flags(cats) - flags(other)), "only_eige": sorted(flags(other) - flags(cats)),
            "flags_eige": len(flags(other)),
            "cost_eige": float(other.loc[other["status"] == article10.STATUS_FLAG, "remedy_cost"].sum())}


def facts(w: pd.DataFrame) -> dict:
    codes = list(ENTITIES)
    ind = article9.by_entity(w, codes)
    cats = article10.screen(w, codes, [b for _, b in BANDS])
    obl = obligations.by_entity(w)
    ready = obligations.readiness()
    sales = w[w["department"] == "Sales"].assign(rate=lambda d: d["commission"] / d["base_pay"])
    flagged = cats[cats["status"] == article10.STATUS_FLAG]
    nat = article9.national(w, codes)
    ncats = article10.national_screen(w, codes, [b for _, b in BANDS])
    return {"codes": codes, "ind": ind, "cats": cats, "obl": obl, "ready": ready, "flagged": flagged,
            "nat": nat, "ncats": ncats, "weights": weights_test(w, cats),
            "sales_rate": sales.groupby("gender")["rate"].mean(),
            "sales_n": sales["gender"].value_counts()}


def italy(add, w, ind, nat, cats, ncats) -> None:
    """Section 5: the Milan figures again on the measure the Italian decree uses."""
    fixed = " and ".join(c.replace("_", " ") + "s" for c in FIXED_COMPONENTS)
    add("## 5. Italy measures the gap on fixed pay")
    add("")
    add("The Italian decree does not compute the gaps on total pay. Its items (a) and (c), its quartile bands and "
        "its 5% test for a joint pay assessment all use *livello retributivo*: annual and hourly pay made of the "
        "fixed and continuing elements, leaving out individual non-structural components granted on a personal, "
        "discretionary or temporary basis, not generalised within the category of workers and based on individual "
        "objective criteria (D.lgs. 96/2026, art. 3(1)(b), art. 9(1), art. 10(1)(a)). The Directive has no such "
        "notion. Here it is read as base pay plus the " + fixed + " this employer pays by a general rule; "
        "bonus and commission are left out.")
    add("")
    keys = [("a_mean_gap_hourly", "(a) Gender pay gap, mean hourly pay"), ("a_mean_gap_annual", "(a) Gender pay gap, mean annual pay"),
            ("c_median_gap_hourly", "(c) Median gender pay gap, hourly pay"), ("c_median_gap_annual", "(c) Median gender pay gap, annual pay"),
            ("f_q4_share_women", "(f) Women in the highest quartile pay band")]
    add(md_table(["Milan", "Directive: total pay", "Italy: livello retributivo", "Difference"],
                 [[label, pct(ind.loc[k, "IT"]), pct(nat.loc[k, "IT"]),
                   f"{(nat.loc[k, 'IT'] - ind.loc[k, 'IT']) * 100:+.1f} pts".replace("-", "−")] for k, label in keys], "lrrr"))
    add("")
    d = cats[cats["country"] == "IT"].set_index("category")
    n = ncats[ncats["country"] == "IT"].set_index("category")
    show = [c for c in n.index if n.loc[c, "status"] == article10.STATUS_FLAG or d.loc[c, "status"] == article10.STATUS_FLAG]
    add(md_table(["Category", "Hourly gap, total pay", "Hourly gap, livello retributivo", "Annual gap, livello retributivo",
                  "Status, Italy", "Cost to close, Italy"],
                 [[c, pct(d.loc[c, "gap_hourly"]), pct(n.loc[c, "gap_hourly"]), pct(n.loc[c, "gap_annual"]),
                   n.loc[c, "status"], eur(n.loc[c, "remedy_cost"])] for c in show], "lrrrlr"))
    add("")
    changed = [c for c in n.index if n.loc[c, "status"] != d.loc[c, "status"]]
    shift = n["gap_hourly"] - d["gap_hourly"]
    up, down = shift.idxmax(), shift.idxmin()
    cost_d = d.loc[d["status"] == article10.STATUS_FLAG, "remedy_cost"].sum()
    cost_n = n.loc[n["status"] == article10.STATUS_FLAG, "remedy_cost"].sum()
    add("What changes, and why it matters for the justification:")
    add("")
    if changed:
        add(f"- **{len(changed)} categor{'y changes' if len(changed) == 1 else 'ies change'} status** between the two "
            f"measures: {', '.join(changed)}.")
    else:
        add("- **The same categories are flagged under both measures**, so the Milan employer's to-do list does not "
            "change. What has to be justified does.")
    if shift[down] < 0:
        add(f"- **In {down}, the hourly gap falls from {pct(d.loc[down, 'gap_hourly'])} to {pct(n.loc[down, 'gap_hourly'])}** "
            f"once bonus and commission are left out: {-shift[down] * 100:.1f} of its points sit outside the Italian "
            f"5% test, but they stay in items (b) and (d) and in any equal-pay claim.")
    if shift[up] > 0:
        add(f"- **In {up}, the hourly gap rises from {pct(d.loc[up, 'gap_hourly'])} to {pct(n.loc[up, 'gap_hourly'])}**: "
            f"bonus and commission partly offset a gap in fixed pay, and the decree takes that offset away. The "
            f"justification has to be about fixed pay.")
    add(f"- **The cost ceiling for Milan moves from {eur(cost_d)} to {eur(cost_n)} a year.**")
    add("- **Keep both measures on file.** The Directive sets the floor and the Commission is checking national "
        "laws for conformity; if the narrower definition does not survive, the total-pay figures are the ones "
        "that count. Whether an individual superminimo or a role allowance is \"fixed and continuing\" is the open "
        "question; the ministerial decrees on the data to collect (art. 9(4)(b)) are the likelier place for an answer.")
    add("- **The excluded components stay visible.** Item (g) still breaks each category's gap down into ordinary "
        "base pay and complementary or variable components (art. 9(1)(g)), and items (b) and (d) report the "
        "components on their own.")
    add("")


def certainty_section(add, w) -> dict:
    """Section 6: how solid each flag is, what it is made of, and how the method scores against the known truth."""
    a = certainty.assess(w)
    full, flagged, pool = a["full"], a["flagged"].copy(), a["pooled"]
    key = lambda r, col: r[f"{col}_{r['measure']}"] if col in ("low", "high") else r[f"gap_{r['measure']}"]
    flagged["shown"] = flagged.apply(lambda r: key(r, "gap"), axis=1)
    flagged["shown_low"] = flagged.apply(lambda r: key(r, "low"), axis=1)
    flagged["shown_high"] = flagged.apply(lambda r: key(r, "high"), axis=1)
    flagged["shown_clean"] = flagged.apply(lambda r: r[f"gap_{r['measure']}_clean"], axis=1)
    flagged = flagged.sort_values("shown", ascending=False)
    (FIG / "04_flag_intervals.svg").write_text(charts.flag_intervals(
        [(f"{ENTITIES[r.country]} {r.category}" + (" †" if r.measure == "annual" else ""), r.shown, r.shown_low,
          r.shown_high, r.cause == "Planted mechanisms") for r in flagged.itertuples()], JPA_THRESHOLD))

    solid = int((flagged["verdict"] == certainty.SOLID).sum())
    below = full[full["status"] != article10.STATUS_FLAG]
    near = int((below["verdict"] == certainty.NEAR).sum())
    causes = flagged["cause"].value_counts()
    planted_n, structure_n = int(causes.get("Planted mechanisms", 0)), int(causes.get("Structure", 0))
    hidden = full[full["cause"] == "Hidden by them"]
    leads = flagged["role"].abs() >= flagged[["within_role", "neutral"]].abs().max(axis=1)
    role_led = int(leads.sum())
    structural = flagged["cause"] == "Structure"
    role_led_structural = int((leads & structural).sum())
    found = a["found_observed"]
    false_alarms, cells = a["false_alarms_clean"], a["cells"]
    rng_obs = f"{pct(pool['within_role'].min())} to {pct(pool['within_role'].max())}"
    rng_clean = f"{pct(pool['within_role_clean'].min())} to {pct(pool['within_role_clean'].max())}"
    clear_obs = int((pool["within_low"] > 0).sum())
    clear_clean = int(((pool["within_low_clean"] > 0) | (pool["within_high_clean"] < 0)).sum())

    add("## 6. How far the flags can be trusted")
    add("")
    add("The 5% test reads a number, and the duty follows from the number: an interval does not lift it. But an "
        "employer deciding where to spend its justification effort needs three things the number cannot say: "
        "whether the flag would survive a year of hiring and leaving, what the gap is made of, and whether the "
        "method finds what is really there. The data are synthetic, so the third can be answered for once: the "
        "payroll is rebuilt from the same random draws without the two discriminatory mechanisms planted in it "
        "(the 2.1% base-pay residual from hr-people-analytics and the poorer Sales territories), and every result "
        "below is scored against that ground truth.")
    add("")
    add("![Flagged categories with their intervals](figures/04_flag_intervals.svg)")
    add("")
    add(f"- **{'None' if solid == 0 else solid} of the {len(flagged)} flags {'is' if solid <= 1 else 'are'} clear of "
        f"the 5% line.** Resampling the workers in post {certainty.DRAWS:,} times, every flagged category's 95% "
        "interval reaches below 5%: with one or two hundred people in a category, a handful of hires or exits "
        f"moves the figure across the threshold. {near} of the {len(below)} categories below 5% could cross it the "
        "same way. Prepare a justification for the flagged categories and keep the evidence for those near the "
        "line: next year's report may move them.")
    add(f"- **{planted_n} of the {len(flagged)} flags are caused by the planted mechanisms; {structure_n} would be "
        f"there without them.** {role_led_structural} of the {structure_n} structural ones come mostly from women "
        "holding the lower-paid roles inside a category of equal value, which is what Article 4 asks an employer "
        "to justify, whatever its cause."
        + (f" One effect runs the other way: in {', '.join(f'{ENTITIES[r.country]} {r.category}' for r in hidden.itertuples())}"
           f" men would be paid {pct(-hidden['gap_hourly_clean'].iloc[0])} less without the mechanisms, a flag they hide."
           if len(hidden) else ""))
    add(f"- **Role mix leads in {role_led} of the {len(flagged)} flags.** Each category's gap splits exactly into "
        "the part role mix accounts for, the part gender-neutral factors (rating, part-time) account for, and what "
        "remains between women and men in the same role with the same rating. The first needs a justification "
        "for paying roles of equal value differently; the last needs one for paying the same work differently, "
        "and is the harder to give.")
    add(f"- **Category by category, a within-role gap of about 2% is too small to see; employer by employer it is "
        f"not.** The within-role part is clearly above zero in {found} of {cells} categories, and in {false_alarms} "
        f"of {cells} on the payroll without the mechanisms, about the one in twenty chance alone gives. Pooled over "
        f"each employer it is {rng_obs}, clearly above zero in {clear_obs} of 4 employers; without the mechanisms "
        f"it is {rng_clean}, clear of zero in {clear_clean}. The method finds the planted effect where there are "
        "enough people to find it and finds nothing where there is nothing: argue the justification per category, "
        "set the pay policy per employer.")
    add("")
    rows = [[ENTITIES[r.country], r.category + (" †" if r.measure == "annual" else "") + (" *" if r.small_cell else ""),
             f"{r.women} / {r.men}",
             pct(r.shown), f"{pct(r.shown_low)} to {pct(r.shown_high)}", pct(r.role), pct(r.neutral),
             f"{pct(r.within_role)} ({pct(r.within_low)} to {pct(r.within_high)})", pct(r.shown_clean),
             r.cause] for r in flagged.itertuples()]
    add(md_table(["Employer", "Category", "Women / men", "Gap", "95% interval", "Role mix", "Rating, part-time",
                  "Same role (95%)", "Gap without planted mechanisms", "Ground truth"], rows, "llrrrrrrrl"))
    add("")
    add("*Gap and interval: the measure that triggered the flag (hourly, or annual where marked †). Role mix, "
        "rating and part-time, and same role: the split of the hourly gap, from one least-squares fit per category "
        "of log pay on sex, role, rating and part-time, scaled to the gap shown so the three add up to it; "
        "the same-role interval is heteroskedasticity-robust. Rating counts as gender-neutral only if the ratings "
        "are; tenure is not in the extract, so differences in it sit in the same-role part. Gap without planted "
        "mechanisms: the same measure, on the payroll rebuilt from the same random draws without them. "
        f"\\* Fewer than {MIN_CELL} of one sex: for workers' representatives and the authorities only (Article 12(3)). "
        "Code: src/certainty.py.*")
    add("")
    return a


def reference_section(add, w) -> dict:
    """Section 7: the same figures on pay actually paid over a year, leavers and joiners included."""
    r = reference_year.compare(w)
    codes = list(ENTITIES)
    s_ind, p_ind, scr_p = r["ind_s"], r["ind_p"], r["scr_p"]
    cells = {(ENTITIES[x.country], x.category): (x.gap_hourly, x.gap_annual, x.status == article10.STATUS_FLAG,
                                                 bool(x.small_cell))
             for x in scr_p.itertuples() if x.status != article10.STATUS_ONE_SEX}
    (FIG / "05_reference_year_screen.svg").write_text(charts.category_grid(
        [ENTITIES[c] for c in codes], [b for _, b in BANDS], cells, JPA_THRESHOLD))
    n = r["counts"]
    total = sum(n.values())
    name = lambda pair: f"{ENTITIES[pair[0]]} {pair[1]}"
    n_flags = len(r["kept"]) + len(r["new"])
    could = sum(v == certainty.NEAR for v in r["new_verdicts"].values())
    clear = sum(v == certainty.CLEAR for v in r["new_verdicts"].values())
    first, last = REFERENCE_START, REFERENCE_END

    add("## 7. The reference year: leavers and joiners")
    add("")
    add("The statutory report does not look at the people on the payroll on one day: it covers pay paid over the "
        "previous calendar year to everyone who was paid in it, the worker who left in March and the one who "
        "joined in October. hr-people-analytics records exits from "
        f"{day(first)} to {day(last)}, so those twelve months are the only full year the data can show; the "
        "mechanics are the calendar year's. The payroll for them, "
        "[data/payroll_reference_year.csv](../data/payroll_reference_year.csv), has the amounts actually paid and "
        "each worker's own contractual hours for the period, in the browser tool's actual-pay layout; the page gives "
        "the same answer on it as pandas.")
    add("")
    add(f"**{total:,} workers were paid in the period**: {n.get('whole period', 0):,} for all of it, "
        f"{n.get('joined', 0):,} who joined, {n.get('left', 0):,} who left and {n.get('joined and left', 0):,} who did "
        "both. Base pay, commission and allowances are paid for the days employed; the 2025 bonus is paid on "
        f"{day(BONUS_PAYDAY)} to the workers still there, pro rata to their service in 2025.")
    add("")
    keys = [("a_mean_gap_hourly", "(a) Mean gap, hourly pay"), ("a_mean_gap_annual", "(a) Mean gap, annual pay"),
            ("c_median_gap_hourly", "(c) Median gap, hourly pay"), ("c_median_gap_annual", "(c) Median gap, annual pay")]
    add(md_table(["Item", *[f"{c} snapshot / year" for c in codes], "Group snapshot / year"],
                 [[label, *[f"{pct(s_ind.loc[k, c])} / {pct(p_ind.loc[k, c])}" for c in [*codes, "Group"]]]
                  for k, label in keys], "lrrrrr"))
    add("")
    add(f"- **The hourly gap is {pct(p_ind.loc['a_mean_gap_hourly', 'Group'])} over the year against "
        f"{pct(s_ind.loc['a_mean_gap_hourly', 'Group'])} at the snapshot.** The people who left had a smaller gap "
        f"between them ({pct(r['gap_leavers'])}) than the people who stayed or joined ({pct(r['gap_stayers'])}).")
    add(f"- **{n_flags} categories are flagged instead of {len(r['kept']) + len(r['dropped'])}, and only "
        f"{len(r['kept'])} are the same.** {', '.join(map(name, r['dropped']))} drop out; "
        f"{', '.join(map(name, r['new']))} come in. "
        + (f"All {len(r['new'])} newcomers" if could == len(r["new"]) else f"{could} of the {len(r['new'])} newcomers")
        + " were marked *could cross* in section 6"
        + (", and none was clearly below 5%: the interval says which categories to watch." if clear == 0 else
           f"; {clear} {'was' if clear == 1 else 'were'} clearly below 5%."))
    add(f"- **{len(r['annual_only'])} of the {n_flags} flags come from annual pay alone.** Someone paid for four "
        "months has a low annual total whatever their rate, so where women and men joined or left in different "
        "numbers, the annual gap moves with turnover, not with pay: the median annual gap falls from "
        f"{pct(s_ind.loc['c_median_gap_annual', 'Group'])} to {pct(p_ind.loc['c_median_gap_annual', 'Group'])}. "
        "The Directive defines pay level as annual and hourly pay but does not say how to count a part-year "
        "worker's annual pay. The kit reports it as paid, as the browser's actual-pay mode does, and reads an "
        "annual-only flag as a question of time worked to explain, not a rate to remedy; national guidance may "
        "settle it otherwise.")
    m2 = lambda x: f"€{x / 1e6:.2f} million"
    add(f"- **The cost ceiling is {m2(r['cost_p'])} a year instead of {m2(r['cost_s'])}.** The {len(r['kept'])} "
        f"flags that stay carry {pct(r['kept_cost_share'], 0)} of it: the expensive categories are the stable ones.")
    add("")
    add("![The category screen on the reference year](figures/05_reference_year_screen.svg)")
    add("")
    return r


def benchmark_section(add, w) -> dict:
    """Section 8: the employer against the official figures it will be read against."""
    b = benchmark.compare(w)
    t, year = b["table"], b["year"]
    (FIG / "06_benchmark.svg").write_text(charts.benchmark(
        [(ENTITIES[r.country], r.regular, r.economy, r.sec_low, r.sec_high) for r in t.itertuples()], year))
    above = t[t["regular"] > t["sec_high"]]
    below = t[t["regular"] < t["sec_low"]]
    inside = t[t["inside_sections"]]
    worst = t.loc[t["times_economy"].idxmax()]
    name = lambda c: ENTITIES[c]
    low_nat = t[t["economy"] < b["eu"]]
    ratios = pd.concat([low_nat["sec_J"] / low_nat["economy"], low_nat["sec_M"] / low_nat["economy"]])
    add("## 8. Against the official figures")
    add("")
    add("Once the report is published, the employer's gap will be set against the national one. Eurostat publishes "
        "it from the structure of earnings survey with the same formula as item (a): the difference between men's "
        "and women's mean gross hourly earnings, as a share of men's. The pay counted differs: the survey leaves "
        "non-regular payments out, so the employer's figure is shown here without its annual bonus. Values for "
        f"{year} (provisional where Eurostat marks them so), dataset updated {day(pd.Timestamp(b['updated']))}, read on "
        f"{day(pd.Timestamp(b['read_on']))}; [data/eurostat_gpg.csv](../data/eurostat_gpg.csv), refreshed by "
        "src/fetch_eurostat.py.")
    add("")
    add("![The employer against Eurostat](figures/06_benchmark.svg)")
    add("")
    add(md_table(["Employer", "Item (a), hourly", "Regular pay only", f"National {year}",
                  *[f"{k}: {v}" for k, v in benchmark.SECTIONS.items()]],
                 [[ENTITIES[r.country], pct(r.article9), pct(r.regular), pct(r.economy),
                   *[pct(getattr(r, f"sec_{k}")) for k in benchmark.SECTIONS]] for r in t.itertuples()], "lrrrrrr"))
    add("")
    add(f"- **Against the national figure the employer looks bad**: in {name(worst.country)} its gap is "
        f"{worst.times_economy:.1f} times the national {pct(worst.economy)}. That is the comparison a journalist or a "
        "works council will make first.")
    add(f"- **Against the sectors it resembles it is ordinary in {len(inside)} of 4 countries** "
        f"({', '.join(map(name, inside['country']))}). National figures average over sectors that pay women and men "
        "very differently and employ them in different numbers: where the national figure is below the EU's "
        f"{pct(b['eu'])} ({', '.join(map(name, low_nat['country']))}), the gap inside information and communication "
        f"and professional services is {ratios.min():.1f} to {ratios.max():.1f} times the national one. "
        "[where-pay-transparency-bites](https://github.com/D0M3N1C0X/where-pay-transparency-bites) shows the same "
        "for all 27 Member States: the published figure understates the gap inside sectors, most of all where it "
        "looks small.")
    if len(above):
        add(f"- **{', '.join(map(name, above['country']))} is above every sector it resembles** "
            f"({pct(above['regular'].iloc[0])} against at most {pct(above['sec_high'].iloc[0])}): the one employer "
            "whose gap the sector cannot explain, and the one to prepare the strongest narrative for.")
    if len(below):
        add(f"- **{', '.join(map(name, below['country']))} is below both** its national figure and its sectors, so "
            "a good number there is still worth explaining: it is where the reasons are easiest to show.")
    add("- **Put both comparisons in the report's narrative.** The Directive asks for the figures, not a benchmark; "
        "but the first question after publication will be how they compare, and an answer prepared in advance "
        "reads better than one given afterwards.")
    add("")
    add("*Sections: J information and communication (the technology staff), M professional, scientific and "
        "technical activities (finance, HR, sales), N administrative and support services (customer service, "
        "operations). The employer has no single activity code; the three are a reading aid, not its "
        "classification. The synthetic organisation's segregation was not set country by country, so read the "
        "comparison as the method a real employer would apply, not as a finding about Milan or Barcelona.*")
    add("")
    return b


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
    checked = pd.to_datetime(status["checked_on"]).max()
    nat, ncats = f["nat"], f["ncats"]

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
    add("> This is a dry run, not a statutory report. Sections 1 to 6 use annualised pay of the workers present "
        "at the snapshot; section 7 reruns the figures on pay actually paid over twelve months, leavers and "
        "joiners included, as the real report will on the previous calendar year, under rules each Member State "
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
    if "IT" in nat:
        add(f"- **Italy measures the gap on fixed pay, and the Milan figures change.** The decree counts only "
            f"fixed and continuing pay (livello retributivo): the Milan gap is {pct(nat.loc['a_mean_gap_hourly', 'IT'])} "
            f"on that measure against {pct(ind.loc['a_mean_gap_hourly', 'IT'])} on total pay. The same categories "
            f"are flagged; what each one has to justify is not the same (section 5).")
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
        f"before a joint pay assessment is due. National status as checked on {day(checked)}; "
        "sources in [docs/verification.md](../docs/verification.md).*")
    add("")
    add("For Italy, applying a national collective agreement signed by the unions comparatively most representative "
        "at national level is presumed to comply, classification included, unless individual discriminatory pay "
        "treatment is shown (D.lgs. 96/2026, art. 4(1)); the agreement's levels are "
        "the reference for comparing work of equal value; an employer's own job evaluation may complement them "
        "if its criteria are objective and gender-neutral (art. 4(4)). So the categories of workers should start "
        "from the agreement's levels and use job evaluation to refine them, not replace them. The categories in "
        "this dry run come from job evaluation alone, because the synthetic organisation has no collective "
        "agreement.")
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
    wt = f["weights"]
    roles = ", ".join(wt["roles"]["role"])
    name = lambda pair: f"{ENTITIES[pair[0]]} {pair[1]}"
    add("**How much the categories depend on the weights.** The EU-wide guidelines on gender-neutral job evaluation "
        "(European Commission and EIGE, March 2026) come with preset, illustrative weights of 40% skills, 35% responsibility, 15% "
        "effort and 10% working conditions; this kit uses 35/35/15/15. With the guidelines' weights, "
        f"{len(wt['roles'])} of {wt['n_roles']} roles change category ({roles}), moving {wt['workers']:,} workers; "
        f"{wt['flags_eige']} categories are flagged instead of {len(flagged)}"
        + (f" ({', '.join(map(name, wt['only_ours']))} drop out" if wt["only_ours"] else "")
        + (f"; {', '.join(map(name, wt['only_eige']))} come{'s' if len(wt['only_eige']) == 1 else ''} in)" if wt["only_eige"] else ")" if wt["only_ours"] else "")
        + f", and the cost ceiling is {eur_m(wt['cost_eige'])} instead of {eur_m(flagged['remedy_cost'].sum())}. "
        "The weights are a negotiated choice, not a technical one: agree them with workers' representatives "
        "before anyone sees the pay figures, and test them on women- and men-dominated roles, as the guidelines "
        "ask. The comparison with the guidelines' method is in "
        "[docs/job-evaluation-eige.md](../docs/job-evaluation-eige.md).")
    add("")

    if "IT" in nat:
        italy(add, w, ind, nat, cats, ncats)

    f["certainty"] = certainty_section(add, w)
    f["reference"] = reference_section(add, w)
    f["benchmark"] = benchmark_section(add, w)

    add("## 9. Readiness: what has to be in place")
    add("")
    add(md_table(["Ref", "Article", "Requirement", "Status", "Owner"],
                 [[r.ref, r.article, r.requirement, r.status, r.owner] for r in ready.itertuples()],
                 "lllll"))
    add("")
    add("*Statuses are illustrative for the demonstration organisation. Evidence expected for each item is in "
        "the workbook's Readiness sheet.*")
    add("")

    add("## 10. The next 90 days")
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

    add("## 11. Method, choices and limits")
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
    add("- **Limits.** Synthetic data; the reference year is the twelve months to the snapshot rather than a "
        "calendar year, with each worker's current pay rate applied to the whole of it; leave-related pay "
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
