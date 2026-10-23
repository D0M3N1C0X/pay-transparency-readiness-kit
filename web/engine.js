// The kit's engine in the browser: a line-by-line twin of src/workers.py, src/article9.py, src/article10.py and
// src/obligations.py. tests/js/check_engine.mjs runs it on the cases pandas computed (tests/fixtures/js_vectors.json)
// and CI fails at the first difference. Nothing here touches the page or the network.

// ---- Job evaluation (Article 4(4)) -----------------------------------------------------------------
export const points = (scores, cfg) => cfg.factors.reduce((s, f) => s + Number(scores[f]) * cfg.weights[f], 0);

export function bandFor(p, cfg) {
  let label = cfg.bands[0][1];
  for (const [floor, name] of cfg.bands) if (p >= floor) label = name;
  return label;
}

// grid: [{ role, skills, effort, responsibility, working_conditions }] -> Map role -> { points, category }
export function evaluate(grid, cfg) {
  return new Map(grid.map((g) => { const p = points(g, cfg); return [g.role, { points: p, category: bandFor(p, cfg) }]; }));
}

// ---- Per-worker figures (workers.derive) ---------------------------------------------------------------
// rows: { worker_id, country, gender: "F" | "M", category, base_pay, components: [numbers], weekly_hours }
export function derive(rows, cfg) {
  const w = rows.map((r) => {
    const annual_hours = r.weekly_hours * cfg.weeks_per_year;
    let components = r.components.length ? r.components[0] : 0;
    for (const c of r.components.slice(1)) components += c;
    const total_pay = r.base_pay + components;
    return { ...r, annual_hours, components_total: components, total_pay,
      hourly_base: r.base_pay / annual_hours, hourly_components: components / annual_hours,
      hourly_total: total_pay / annual_hours, receives_components: components > 0 ? 1 : 0 };
  });
  // Quartile pay bands within each employer: four equal groups by hourly pay, ties broken by row order.
  const byCountry = new Map();
  w.forEach((r, i) => { if (!byCountry.has(r.country)) byCountry.set(r.country, []); byCountry.get(r.country).push(i); });
  for (const idx of byCountry.values()) {
    const order = [...idx].sort((a, b) => w[a].hourly_total - w[b].hourly_total || a - b);
    const n = order.length;
    order.forEach((i, k) => { w[i].quartile = Math.min(4, Math.floor((k * 4) / n) + 1); });
  }
  return w;
}

// ---- Article 9(1) --------------------------------------------------------------------------------------------
export function gap(women, men) {
  if (men === 0 || Number.isNaN(men) || Number.isNaN(women)) return NaN;
  return (men - women) / men;
}
const mean = (xs) => (xs.length ? xs.reduce((s, x) => s + x, 0) / xs.length : NaN);
function median(xs) {
  if (!xs.length) return NaN;
  const s = [...xs].sort((a, b) => a - b), k = s.length >> 1;
  return s.length % 2 ? s[k] : (s[k - 1] + s[k]) / 2;
}
const col = (rows, k) => rows.map((r) => r[k]);

export function indicators(w) {
  const f = w.filter((r) => r.gender === "F"), m = w.filter((r) => r.gender === "M");
  const fr = f.filter((r) => r.receives_components), mr = m.filter((r) => r.receives_components);
  const out = {
    workers: w.length, women: f.length, men: m.length,
    a_mean_gap_hourly: gap(mean(col(f, "hourly_total")), mean(col(m, "hourly_total"))),
    a_mean_gap_annual: gap(mean(col(f, "total_pay")), mean(col(m, "total_pay"))),
    b_mean_gap_components: gap(mean(col(fr, "components_total")), mean(col(mr, "components_total"))),
    c_median_gap_hourly: gap(median(col(f, "hourly_total")), median(col(m, "hourly_total"))),
    c_median_gap_annual: gap(median(col(f, "total_pay")), median(col(m, "total_pay"))),
    d_median_gap_components: gap(median(col(fr, "components_total")), median(col(mr, "components_total"))),
    e_share_women_receiving: f.length ? fr.length / f.length : NaN,
    e_share_men_receiving: m.length ? mr.length / m.length : NaN,
    base_mean_gap_hourly: gap(mean(col(f, "hourly_base")), mean(col(m, "hourly_base"))),
    mean_hourly_total_women: mean(col(f, "hourly_total")),
    mean_hourly_total_men: mean(col(m, "hourly_total")),
  };
  for (const q of [1, 2, 3, 4]) {
    const band = w.filter((r) => r.quartile === q);
    out[`f_q${q}_workers`] = band.length;
    out[`f_q${q}_share_women`] = band.length ? band.filter((r) => r.gender === "F").length / band.length : NaN;
    out[`f_q${q}_share_men`] = band.length ? band.filter((r) => r.gender === "M").length / band.length : NaN;
  }
  return out;
}

// One entry per employer, plus a group view that is not a statutory figure.
export function byEntity(w, countries) {
  const out = {};
  for (const c of countries) out[c] = indicators(w.filter((r) => r.country === c));
  out.Group = indicators(w);
  return out;
}

// ---- Article 9(1)(g) and the Article 10(1) screen ------------------------------------------------------------
export function categoryRow(g, cfg) {
  const f = g.filter((r) => r.gender === "F"), m = g.filter((r) => r.gender === "M");
  const row = {
    women: f.length, men: m.length,
    hourly_base_women: mean(col(f, "hourly_base")), hourly_base_men: mean(col(m, "hourly_base")),
    hourly_components_women: mean(col(f, "hourly_components")), hourly_components_men: mean(col(m, "hourly_components")),
    hourly_total_women: mean(col(f, "hourly_total")), hourly_total_men: mean(col(m, "hourly_total")),
    annual_total_women: mean(col(f, "total_pay")), annual_total_men: mean(col(m, "total_pay")),
  };
  row.gap_base = gap(row.hourly_base_women, row.hourly_base_men);
  row.gap_components = gap(row.hourly_components_women, row.hourly_components_men);
  row.gap_hourly = gap(row.hourly_total_women, row.hourly_total_men);
  row.gap_annual = gap(row.annual_total_women, row.annual_total_men);
  row.small_cell = Math.min(f.length, m.length) < cfg.min_cell ? 1 : 0;
  if (!f.length || !m.length) return { ...row, status: "one_sex", remedy_cost: 0 };
  // "a difference ... of at least 5%": either direction, on either measure of pay level
  const flagged = Math.abs(row.gap_hourly) >= cfg.threshold || Math.abs(row.gap_annual) >= cfg.threshold;
  row.status = flagged ? "flag" : "ok";
  // ceiling of the annual cost of lifting the lower-paid group's average hourly pay to the other's
  const hours = (rows) => rows.reduce((s, r) => s + r.annual_hours, 0);
  if (flagged && row.gap_hourly > 0) row.remedy_cost = (row.hourly_total_men - row.hourly_total_women) * hours(f);
  else if (flagged && row.gap_hourly < 0) row.remedy_cost = (row.hourly_total_women - row.hourly_total_men) * hours(m);
  else row.remedy_cost = 0;
  return row;
}

export function screen(w, countries, categories, cfg) {
  const rows = [];
  for (const c of countries) {
    for (const cat of categories) {
      const g = w.filter((r) => r.country === c && r.category === cat);
      if (g.length) rows.push({ country: c, category: cat, ...categoryRow(g, cfg) });
    }
  }
  return rows;
}

// ---- Obligations (Article 9(2)-(4), Article 10(1)(c)) ----------------------------------------------------------
export function sizeBand(workers, cfg) {
  const i = cfg.size_bands.findIndex(([floor]) => workers >= floor);
  const [, label, frequency, first] = cfg.size_bands[i];
  return { index: i, label, frequency, first };
}

export function addMonths(iso, months) {
  const [y, m, d] = iso.split("-").map(Number);
  const k = m - 1 + months;
  return `${y + Math.floor(k / 12)}-${String((k % 12) + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
}

// `others`: workers left out of the comparisons (sex not recorded as woman or man) still count for the size band
export function obligations(w, countries, cfg, others = {}) {
  return countries.map((c) => {
    const n = w.filter((r) => r.country === c).length + (others[c] || 0);
    const band = sizeBand(n, cfg);
    return { country: c, workers: n, size_band: band.label, band: band.index, frequency: band.frequency,
      first_report: band.first, remedy_by: band.first ? addMonths(band.first, cfg.remedy_months) : null,
      transposition: cfg.transposition[c] || null };
  });
}

// Categories in a stable order: the point bands first, in their order, then any others alphabetically.
export function categoryOrder(w, cfg) {
  const present = new Set(w.map((r) => r.category));
  const known = cfg.bands.map(([, l]) => l).filter((l) => present.has(l));
  const other = [...present].filter((c) => !known.includes(c)).sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));
  return [...known, ...other];
}

// ---- Reading values from a user's file ------------------------------------------------------------------------
// A first guess only: the page shows every code found and lets the user correct it. Single letters that mean
// different things in different exports are left out ("d" is donna in Italy and divers in Germany; "h" is hombre).
const WOMEN = new Set(["f", "female", "woman", "women", "w", "donna", "donne", "femmina", "k", "kobieta", "kobiety",
  "frau", "frauen", "weiblich", "mujer", "mujeres", "femenino"]);
const MEN = new Set(["m", "male", "man", "men", "uomo", "uomini", "maschio", "mezczyzna", "mezczyzni", "mann", "manner",
  "mannlich", "hombre", "hombres", "masculino"]);
export function sex(v) {
  const s = String(v ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/ł/g, "l").trim();
  return WOMEN.has(s) ? "F" : MEN.has(s) ? "M" : null;
}

export function number(v, decimalComma) {
  if (typeof v === "number") return v;
  let t = String(v ?? "").replace(/[\s€$£%]|zł|PLN|EUR/gi, "");
  if (t === "") return 0;
  if (decimalComma) t = t.replace(/\./g, "").replace(",", ".");
  else if (/^-?\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)) t = t.replace(/,/g, "");
  const n = Number(t);
  if (Number.isNaN(n)) throw new Error(`not a number: "${v}"`);
  return n;
}
