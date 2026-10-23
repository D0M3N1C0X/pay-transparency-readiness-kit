// Recomputes with web/engine.js every case that pandas computed, and exits with 1 at the first difference.
import { readFileSync } from "node:fs";
import { evaluate, derive, byEntity, national, screen, obligations, categoryOrder, sex, number, addMonths } from "../../web/engine.js";

const V = JSON.parse(readFileSync(new URL("../fixtures/js_vectors.json", import.meta.url)));
const close = (a, b) => (b === null ? a === null || Number.isNaN(a)
  : typeof b === "number" ? Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b)) : a === b);
let checks = 0, failures = 0;
const expect = (ok, what) => { checks++; if (!ok) { failures++; if (failures <= 20) console.error("difference:", what); } };

const roles = evaluate(V.grid, V.cfg);
const comps = V.cfg.components;
const fixed = comps.map((x) => V.cfg.fixed_components.includes(x));
V.cases.forEach((c, k) => {
  const rows = (c.rows ? c.rows.map((i) => ({ ...V.base[i] })) : V.base.map((r) => ({ ...r })));
  for (const [i, f, v] of c.patch) rows[i][f] = v;
  const w = derive(rows.map((r) => ({ worker_id: r.worker_id, country: r.country, gender: r.gender,
    category: roles.get(r.role).category, base_pay: r.base_pay, components: comps.map((x) => r[x]), fixed,
    weekly_hours: r.weekly_hours })), V.cfg);
  const countries = Object.keys(V.cfg.entities).filter((x) => w.some((r) => r.country === x));
  const items = byEntity(w, countries);
  for (const [entity, values] of Object.entries(c.items))
    for (const [key, v] of Object.entries(values)) expect(close(items[entity]?.[key], v), `case ${k} ${entity} ${key}: ${items[entity]?.[key]} vs ${v}`);
  const s = screen(w, countries, categoryOrder(w, V.cfg), V.cfg);
  expect(s.length === c.screen.length, `case ${k}: ${s.length} categories vs ${c.screen.length}`);
  for (const e of c.screen) {
    const a = s.find((r) => r.country === e.country && r.category === e.category) || {};
    for (const [key, v] of Object.entries(e)) expect(close(a[key], v), `case ${k} ${e.country} ${e.category} ${key}: ${a[key]} vs ${v}`);
  }
  const q = new Map(w.map((r) => [r.worker_id, r.quartile]));
  expect(c.quartiles.every(([id, v]) => q.get(id) === v), `case ${k}: quartile bands`);
  // Italy's narrower measure: the items, the quartile bands and the screen again on fixed and continuing pay
  const nat = national(w, countries, V.cfg);
  expect(Object.keys(nat).length === Object.keys(c.national_items).length, `case ${k}: national employers`);
  for (const [entity, values] of Object.entries(c.national_items))
    for (const [key, v] of Object.entries(values)) expect(close(nat[entity]?.[key], v), `case ${k} national ${entity} ${key}: ${nat[entity]?.[key]} vs ${v}`);
  const qf = new Map(w.map((r) => [r.worker_id, r.quartile_fixed]));
  expect(c.quartiles_fixed.every(([id, v]) => qf.get(id) === v), `case ${k}: quartile bands on fixed pay`);
  const ns = screen(w, countries, categoryOrder(w, V.cfg), V.cfg, "national");
  expect(ns.length === c.national_screen.length, `case ${k}: ${ns.length} national categories vs ${c.national_screen.length}`);
  for (const e of c.national_screen) {
    const a = ns.find((r) => r.country === e.country && r.category === e.category) || {};
    for (const [key, v] of Object.entries(e)) expect(close(a[key], v), `case ${k} national ${e.country} ${e.category} ${key}: ${a[key]} vs ${v}`);
  }
  const o = obligations(w, countries, V.cfg);
  for (const e of c.obligations) {
    const a = o.find((r) => r.country === e.country) || {};
    for (const [key, v] of Object.entries(e)) expect(close(a[key], v), `case ${k} obligations ${e.country} ${key}: ${a[key]} vs ${v}`);
  }
});
// Reading values the way payroll exports write them
for (const [v, s] of [["F", "F"], ["donna", "F"], ["Kobieta", "F"], ["M", "M"], ["Uomo", "M"], ["Mężczyzna", "M"], ["X", null], ["", null],
  ["d", null], ["h", null], ["Mujeres", "F"], ["Hombres", "M"], ["Frauen", "F"]])
  expect(sex(v) === s, `sex(${v}) = ${sex(v)}`);
for (const [v, comma, n] of [["1.234,50", true, 1234.5], ["1,234.50", false, 1234.5], ["€ 32 000", false, 32000], ["", false, 0], [41000, false, 41000]])
  expect(number(v, comma) === n, `number(${v}) = ${number(v, comma)}`);
expect(obligations([{ country: "IT" }], ["IT"], V.cfg, { IT: 150 })[0].band === 1, "size band counts everyone");
expect(number("80%", false) === 80, "number strips the percent sign");
for (const [d, m, r] of [["2027-06-07", 6, "2027-12-07"], ["2027-09-30", 4, "2028-01-30"], ["2031-06-07", 6, "2031-12-07"]])
  expect(addMonths(d, m) === r, `addMonths(${d}, ${m}) = ${addMonths(d, m)}`);
console.log(`${checks - failures} of ${checks} values agree with pandas in ${V.cases.length} cases`);
process.exit(failures ? 1 : 0);
