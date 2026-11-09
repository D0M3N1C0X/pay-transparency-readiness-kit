// strumenti-design 1.1.1 · table.js
// Turns a file the user picked (CSV or Excel) into rows of objects, and matches its columns to the ones a tool
// needs. Everything runs in the page: the file is read with the browser's own File API and never uploaded.
//
//   readTable(file)                       -> { headers, rows, decimalComma, sheet }
//   parseCsv(text)                        -> { headers, rows, decimalComma }
//   matchColumns(headers, fields, saved)  -> { mapping, missing }
//   rememberMapping(key, headers, mapping) / savedMapping(key, headers); choices stay in memory only

import { readXlsx } from "./xlsx.js";

export const normalise = (s) => String(s ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[łŁ]/g, "l").toLowerCase()
  .replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");

function assertHeaders(headers, rows) {
  const seen = new Map();
  const issues = [];
  const width = rows.reduce((max, row) => Math.max(max, row.length), headers.length);
  for (let index = 0; index < width; index += 1) {
    const header = String(headers[index] ?? "").trim();
    const key = normalise(header);
    if (!key) {
      if (rows.some((row) => row[index] !== "" && row[index] !== null && row[index] !== undefined)) {
        issues.push(`blank column header at position ${index + 1} contains data`);
      }
      continue;
    }
    if (seen.has(key)) {
      issues.push(`duplicate or ambiguous column headers: "${seen.get(key)}" and "${header}" normalize to the same name`);
    } else seen.set(key, header);
  }
  if (issues.length) throw new Error(issues.join("; "));
}

function recognizedFields(headers, fields = []) {
  const available = new Set(headers.map(normalise).filter(Boolean));
  return fields.filter((field) => [field.key, ...(field.aliases || [])]
    .some((candidate) => available.has(normalise(candidate)))).length;
}

function candidateForSheet(sheet, fields) {
  let best = null;
  const maxPopulatedRows = 100;
  let examined = 0;
  for (let index = 0; index < sheet.rows.length && examined < maxPopulatedRows; index += 1) {
    const row = sheet.rows[index] || [];
    if (!row.some((value) => value !== "" && value !== null && value !== undefined)) continue;
    examined += 1;
    const headers = row.map((value) => String(value ?? "").trim());
    const recognized = recognizedFields(headers, fields);
    const width = headers.filter((header) => normalise(header)).length;
    if (!best || recognized > best.recognized || (recognized === best.recognized && width > best.width)) {
      best = { sheet, headerIndex: index, headers, recognized, width };
    }
  }
  return best;
}

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
  assertHeaders(headers, records);
  const rows = records.map((r) => Object.fromEntries(headers.map((h, i) => [h, (r[i] ?? "").trim()])));
  return { headers, rows, decimalComma: decimalMark(rows, sep === ";") };
}

// Is the decimal mark a comma? Read it from the numbers themselves: a semicolon file can still write 1539.70,
// and a comma file can write "1539,70" in quotes. Only when the numbers do not tell (no decimals at all) does
// the separator decide: semicolon files come from Italian, Polish or German Excel, which use the comma.
export function decimalMark(rows, fallback) {
  let comma = 0, dot = 0;
  for (const r of rows.slice(0, 500)) {
    for (const v of Object.values(r)) {
      const s = String(v).trim().replace(/[\s€$£%]/g, "");
      if (/^-?\d{1,3}(\.\d{3})+,\d+$/.test(s) || /^-?\d+,\d+$/.test(s) && !/^-?\d{1,3}(,\d{3})+$/.test(s)) comma++;
      else if (/^-?\d{1,3}(,\d{3})+\.\d+$/.test(s) || /^-?\d+\.\d+$/.test(s) && !/^-?\d{1,3}(\.\d{3})+$/.test(s)) dot++;
    }
  }
  return comma === dot ? fallback : comma > dot;
}

export async function readTable(file, { sheet, fields } = {}) {
  const name = (file.name || "").toLowerCase();
  if (name.endsWith(".xlsx") || name.endsWith(".xlsm")) {
    const sheets = await readXlsx(await file.arrayBuffer());
    if (!sheets.length) throw new Error("empty workbook");

    let chosen;
    if (sheet) {
      const selected = sheets.find((item) => item.name === sheet);
      if (!selected) throw new Error(`worksheet "${sheet}" not found`);
      chosen = candidateForSheet(selected, fields);
      if (!chosen) throw new Error(`worksheet "${sheet}" is empty`);
    } else {
      const hiddenSheets = sheets.filter((item) => item.state === "hidden" || item.state === "veryHidden");
      const visibleSheets = sheets.filter((item) => item.state !== "hidden" && item.state !== "veryHidden");
      const candidates = visibleSheets.map((item) => candidateForSheet(item, fields)).filter(Boolean);
      const hiddenCandidates = hiddenSheets.map((item) => candidateForSheet(item, fields)).filter(Boolean);
      if (!candidates.length) {
        if (hiddenCandidates.some((candidate) => candidate.recognized > 0)) {
          throw new Error("matching payroll data is in a hidden worksheet; unhide it and retry");
        }
        throw new Error("empty workbook");
      }
      if (!fields?.length) {
        chosen = candidates.find((candidate) => candidate.sheet.rows.length > 1) || candidates[0];
      } else {
        const mostRecognized = Math.max(...candidates.map((candidate) => candidate.recognized));
        const bestHidden = hiddenCandidates.reduce((best, candidate) => Math.max(best, candidate.recognized), 0);
        if (bestHidden > mostRecognized) {
          throw new Error("the strongest matching payroll data is in a hidden worksheet; unhide it and retry");
        }
        if (mostRecognized > 0) {
          const matches = candidates.filter((candidate) => candidate.recognized === mostRecognized);
          if (matches.length > 1) {
            throw new Error(`multiple worksheets match the file's expected columns: ${matches.map((candidate) => candidate.sheet.name).join(", ")}; keep only the worksheet you want to import and retry`);
          }
          [chosen] = matches;
        } else {
          const widest = Math.max(...candidates.map((candidate) => candidate.width));
          const matches = candidates.filter((candidate) => candidate.width === widest);
          if (matches.length > 1) {
            throw new Error(`multiple worksheets have equally plausible headers: ${matches.map((candidate) => candidate.sheet.name).join(", ")}; keep one data worksheet`);
          }
          [chosen] = matches;
        }
      }
    }

    const body = chosen.sheet.rows.slice(chosen.headerIndex + 1)
      .filter((row) => row.some((value) => value !== "" && value !== null && value !== undefined));
    assertHeaders(chosen.headers, body);
    const rows = body.map((row) => Object.fromEntries(chosen.headers.map((header, index) => [header, row[index] ?? ""])));
    return { headers: chosen.headers, rows, decimalComma: false, sheet: chosen.sheet.name, sheets: sheets.map((item) => item.name) };
  }
  if (name.endsWith(".xls")) throw new Error("old .xls format: save the file as .xlsx or CSV");
  return { ...parseCsv(await file.text()), sheet: null, sheets: [] };
}

// fields: [{ key, required, aliases: [...] }]. A header matches a field when its normalised form equals the key or
// one of the aliases. Saved choices win over guesses.
export function matchColumns(headers, fields, saved = {}) {
  const mapping = {};
  const ambiguous = {};
  let recognized = 0;
  for (const f of fields) {
    const accepted = new Set([f.key, ...(f.aliases || [])].map(normalise).filter(Boolean));
    const hits = headers.filter((header) => accepted.has(normalise(header)));
    if (hits.length) recognized += 1;
    if (Object.hasOwn(saved, f.key) && saved[f.key] === "") continue;
    if (saved[f.key] && headers.includes(saved[f.key])) { mapping[f.key] = saved[f.key]; continue; }
    if (hits.length === 1) mapping[f.key] = hits[0];
    else if (hits.length > 1) ambiguous[f.key] = hits;
  }
  const missing = fields.filter((f) => f.required && !mapping[f.key]).map((f) => f.key);
  return { mapping, missing, ambiguous, recognized };
}

// Renames each row's columns to the tool's own keys; fields left unmapped are simply absent.
export const applyMapping = (rows, mapping) => rows.map((r) =>
  Object.fromEntries(Object.entries(mapping).filter(([, h]) => h).map(([k, h]) => [k, r[h]])));

const mappings = new Map();
const mappingKey = (key, headers) => key + "." + normalise([...headers].sort().join("|")).slice(0, 180);
export function savedMapping(key, headers) { return mappings.get(mappingKey(key, headers)) || {}; }
export function rememberMapping(key, headers, mapping) { mappings.set(mappingKey(key, headers), { ...mapping }); }
export function clearMappings() { mappings.clear(); }

export function download(bytes, filename, type) {
  const url = URL.createObjectURL(new Blob([bytes], { type }));
  const a = Object.assign(document.createElement("a"), { href: url, download: filename });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
