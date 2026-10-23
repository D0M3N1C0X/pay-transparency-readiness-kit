// strumenti-design 1.0.0 · table.js
// Turns a file the user picked (CSV or Excel) into rows of objects, and matches its columns to the ones a tool
// needs. Everything runs in the page: the file is read with the browser's own File API and never uploaded.
//
//   readTable(file)                       -> { headers, rows, decimalComma, sheet }
//   parseCsv(text)                        -> { headers, rows, decimalComma }
//   matchColumns(headers, fields, saved)  -> { mapping, missing }
//   rememberMapping(key, headers, mapping) / savedMapping(key, headers)

import { readXlsx } from "./xlsx.js";

export const normalise = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
  .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");

export function parseCsv(text) {
  text = text.replace(/^﻿/, "");
  const first = text.split(/\r?\n/, 1)[0];
  const sep = (first.match(/;/g) || []).length > (first.match(/,/g) || []).length ? ";" : ",";
  const records = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === sep) { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.some((v) => v !== "")) records.push(row);
      row = [];
    } else field += ch;
  }
  row.push(field);
  if (row.some((v) => v !== "")) records.push(row);
  const headers = (records.shift() || []).map((h) => h.trim());
  const rows = records.map((r) => Object.fromEntries(headers.map((h, i) => [h, (r[i] ?? "").trim()])));
  return { headers, rows, decimalComma: sep === ";" };
}

export async function readTable(file, { sheet } = {}) {
  const name = (file.name || "").toLowerCase();
  if (name.endsWith(".xlsx") || name.endsWith(".xlsm")) {
    const sheets = await readXlsx(await file.arrayBuffer());
    const chosen = sheets.find((s) => s.name === sheet) || sheets.find((s) => s.rows.length > 1) || sheets[0];
    if (!chosen) throw new Error("empty workbook");
    const [head = [], ...body] = chosen.rows;
    const headers = head.map((h) => String(h ?? "").trim());
    const rows = body.filter((r) => r.some((v) => v !== "" && v !== null))
      .map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i] ?? ""])));
    return { headers, rows, decimalComma: false, sheet: chosen.name, sheets: sheets.map((s) => s.name) };
  }
  if (name.endsWith(".xls")) throw new Error("old .xls format: save the file as .xlsx or CSV");
  return { ...parseCsv(await file.text()), sheet: null, sheets: [] };
}

// fields: [{ key, required, aliases: [...] }]. A header matches a field when its normalised form equals the key or
// one of the aliases. Saved choices win over guesses.
export function matchColumns(headers, fields, saved = {}) {
  const byNorm = new Map(headers.map((h) => [normalise(h), h]));
  const mapping = {};
  for (const f of fields) {
    if (saved[f.key] && headers.includes(saved[f.key])) { mapping[f.key] = saved[f.key]; continue; }
    const hit = [f.key, ...(f.aliases || [])].map(normalise).find((n) => byNorm.has(n));
    if (hit) mapping[f.key] = byNorm.get(hit);
  }
  const missing = fields.filter((f) => f.required && !mapping[f.key]).map((f) => f.key);
  return { mapping, missing };
}

// Renames each row's columns to the tool's own keys; fields left unmapped are simply absent.
export const applyMapping = (rows, mapping) => rows.map((r) =>
  Object.fromEntries(Object.entries(mapping).filter(([, h]) => h).map(([k, h]) => [k, r[h]])));

const storageKey = (key, headers) => `strumenti.colonne.${key}.${normalise([...headers].sort().join("|")).slice(0, 180)}`;
export function savedMapping(key, headers) {
  try { return JSON.parse(localStorage.getItem(storageKey(key, headers)) || "{}"); } catch { return {}; }
}
export function rememberMapping(key, headers, mapping) {
  try { localStorage.setItem(storageKey(key, headers), JSON.stringify(mapping)); } catch { /* private mode: fine */ }
}

export function download(bytes, filename, type) {
  const url = URL.createObjectURL(new Blob([bytes], { type }));
  const a = Object.assign(document.createElement("a"), { href: url, download: filename });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
