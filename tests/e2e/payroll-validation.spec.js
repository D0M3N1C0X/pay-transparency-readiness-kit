import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { readXlsx } from "../../web/design/xlsx.js";

const BASE_URL = "http://127.0.0.1:4173";
const PAYROLL_HEADERS = [
  "worker_id", "gender", "base_pay", "category", "country", "annual_hours",
  "weekly_hours", "fixed_allowance", "bonus", "one_off", "commission"
];

function syntheticPayrollRows({ women = 5, men = 5, category = "Professional" } = {}) {
  const rows = [PAYROLL_HEADERS];
  const groups = [
    ["F", "SYN-F", women, "40000,00", "2080", "2000,00", "5000,00", "1000,00", "100,00"],
    ["M", "SYN-M", men, "21000,00", "1040", "1000,00", "0,00", "0,00", "200,00"]
  ];
  for (const [gender, prefix, count, base, annualHours, fixed, bonus, oneOff, commission] of groups) {
    for (let index = 1; index <= count; index += 1) {
      rows.push([
        prefix + "-" + String(index).padStart(2, "0"), gender, base, category, "IT",
        annualHours, "40", fixed, bonus, oneOff, commission
      ]);
    }
  }
  return rows;
}

function payrollCsv(rows) {
  return rows.map((row) => row.join(";")).join("\n") + "\n";
}

function payCodeCsv() {
  return [
    "pay_code;column_header;description;classification",
    "001;fixed_allowance;Contractual fixed allowance;fixed_continuing",
    "002;bonus;Annual bonus;variable",
    "003;one_off;One-time amount;one_off",
    ""
  ].join("\n");
}

function completePayCodeCsv() {
  return [
    "pay_code;column_header;description;classification",
    "001;fixed_allowance;Contractual fixed allowance;fixed_continuing",
    "002;bonus;Annual bonus;variable",
    "003;one_off;One-time amount;one_off",
    "004;commission;Sales commission;variable",
    ""
  ].join("\n");
}

function payrollRowsWithGrossTotal() {
  const rows = syntheticPayrollRows().map((row) => [...row]);
  const amountColumns = ["base_pay", "fixed_allowance", "bonus", "one_off", "commission"].map((name) => rows[0].indexOf(name));
  rows[0].push("gross_total_paid");
  for (const row of rows.slice(1)) {
    const total = amountColumns.reduce((sum, index) => sum + Number(row[index].replace(",", ".")), 0);
    row.push(total.toFixed(2).replace(".", ","));
  }
  return rows;
}

function watchPage(page) {
  const requests = [];
  const errors = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (url.protocol === "http:" || url.protocol === "https:") {
      requests.push({ origin: url.origin, method: request.method() });
    }
  });
  page.on("pageerror", (error) => errors.push(error.message));
  return { requests, errors };
}

async function openApp(page) {
  const observed = watchPage(page);
  await page.goto("/index.html?lang=en");
  return observed;
}

async function uploadPayroll(page, rows, annualHoursExpected = true) {
  await page.locator("#file-paghe").setInputFiles({
    name: "synthetic-payroll-validation.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(payrollCsv(rows), "utf8")
  });
  await expect(page.locator('#mappa select[data-key="annual_hours"]'))
    .toHaveValue(annualHoursExpected ? "annual_hours" : "");
}

async function uploadXlsxPayroll(page, filename) {
  await page.locator("#file-paghe").setInputFiles("test-results/e2e-fixtures/" + filename);
}

async function uploadPayCodeMap(page, complete = false) {
  const csv = complete ? completePayCodeCsv() : payCodeCsv();
  const expected = complete ? 4 : 3;
  await page.locator("#file-codici").setInputFiles({
    name: "synthetic-pay-codes.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(csv, "utf8")
  });
  await expect(page.locator("#codici-sub")).toContainText(`Loaded ${expected} pay-code entries`);
}

async function loadValidPayroll(page, rows = syntheticPayrollRows()) {
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await uploadPayCodeMap(page);
  return observed;
}

async function expectLocalRequests(observed) {
  expect(observed.requests.every((entry) => entry.origin === BASE_URL && entry.method === "GET")).toBe(true);
  expect(observed.errors).toEqual([]);
}

async function expectRowError(page, messages) {
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  for (const message of messages) await expect(page.locator("#errore")).toContainText(message);
  await expect(page.locator("#risultati")).toBeHidden();
}

const rowValidationCases = [
  {
    name: "duplicate pseudonymous worker IDs",
    messages: ["Row 3", "duplicate pseudonymous worker ID"],
    mutate(rows) { rows[2][0] = rows[1][0]; }
  },
  {
    name: "a missing pseudonymous worker ID",
    messages: ["Row 2", "pseudonymous worker ID missing"],
    mutate(rows) { rows[1][0] = ""; }
  },
  {
    name: "zero annual contractual hours",
    messages: ["Row 2", "contractual hours missing or zero"],
    mutate(rows) { rows[1][5] = "0"; }
  },
  {
    name: "negative annual contractual hours",
    messages: ["Row 2", "contractual hours missing or zero"],
    mutate(rows) { rows[1][5] = "-1"; }
  },
  {
    name: "malformed base pay",
    messages: ["Row 2", "not a number: not-money"],
    mutate(rows) { rows[1][2] = "not-money"; }
  },
  {
    name: "infinite base pay",
    messages: ["Row 2", "not a number: Infinity"],
    mutate(rows) { rows[1][2] = "Infinity"; }
  },
  {
    name: "missing base pay",
    messages: ["Row 2", "base pay missing"],
    mutate(rows) { rows[1][2] = ""; }
  },
  {
    name: "a missing worker category",
    messages: ["Row 2", "no category"],
    mutate(rows) { rows[1][3] = ""; }
  }
];

for (const scenario of rowValidationCases) {
  test("rejects " + scenario.name + " with a row-specific message", async ({ page }) => {
    const rows = syntheticPayrollRows();
    scenario.mutate(rows);
    const observed = await openApp(page);
    await uploadPayroll(page, rows);
    await uploadPayCodeMap(page);
    await expectRowError(page, scenario.messages);
    await expectLocalRequests(observed);
  });
}

test("requires annual-hours mapping before an actual-pay run", async ({ page }) => {
  const rows = syntheticPayrollRows();
  const annualHoursIndex = rows[0].indexOf("annual_hours");
  const withoutAnnualHours = rows.map((row) => row.filter((_, index) => index !== annualHoursIndex));
  const observed = await openApp(page);
  await uploadPayroll(page, withoutAnnualHours, false);
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeDisabled();
  await expect(page.locator("#colonne-sub")).toContainText("marked in red");
  await expectLocalRequests(observed);
});

test("rejects a non-finite mapped component during pay-code map validation", async ({ page }) => {
  const rows = syntheticPayrollRows();
  rows[1][7] = "Infinity";
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await page.locator("#file-codici").setInputFiles({
    name: "synthetic-pay-codes.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(payCodeCsv(), "utf8")
  });
  await expect(page.locator("#errore")).toContainText("fixed_allowance");
  await expect(page.locator("#errore")).toContainText("not numeric");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});

test("treats a blank mapped component amount as zero", async ({ page }) => {
  const rows = syntheticPayrollRows();
  rows[1][9] = "";
  const observed = await loadValidPayroll(page, rows);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#errore")).toBeHidden();
  await expectLocalRequests(observed);
});

test("keeps category statistics below the five-person threshold out of the table and Excel export", async ({ page }) => {
  const rows = syntheticPayrollRows({ women: 4, men: 4, category: "Confidential cohort" });
  const observed = await loadValidPayroll(page, rows);
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#nota-piccole")).toContainText("fewer than 5 women or men");

  const visibleRow = page.locator("#tab-categorie tr").nth(1);
  const visibleCells = await visibleRow.locator("td").allTextContents();
  expect(visibleCells[0]).toBe("Confidential cohort");
  expect(visibleCells[1]).toBe("4");
  expect(visibleCells[2]).toBe("4");
  for (const index of [3, 4, 5, 6, 7, 8]) expect(visibleCells[index]).toContain("kept back");
  expect(visibleCells[10]).toContain("kept back");
  await expect(page.locator("#grafico-categorie")).not.toContainText("Confidential cohort");

  const downloadPromise = page.waitForEvent("download");
  await page.locator("#scarica-xlsx").click();
  const download = await downloadPromise;
  const filePath = await download.path();
  expect(filePath).toBeTruthy();
  const bytes = await readFile(filePath);
  const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const sheets = await readXlsx(arrayBuffer);
  const categories = sheets.find((sheet) => sheet.name === "Categories");
  expect(categories).toBeTruthy();
  const exportedRow = categories.rows.find((row) => row[1] === "Confidential cohort");
  expect(exportedRow).toBeTruthy();
  expect(exportedRow.slice(4, 10).every((value) => value === "kept back")).toBe(true);
  expect(exportedRow[11]).toBe("kept back");
  await expectLocalRequests(observed);
});

test("counts workers with unclassified gender toward employer size but excludes them from comparisons", async ({ page }) => {
  const rows = syntheticPayrollRows();
  rows.push(["SYN-X-01", "X", "30000,00", "Professional", "IT", "2080", "40", "0,00", "0,00", "0,00", "0,00"]);
  const observed = await loadValidPayroll(page, rows);
  await expect(page.locator('#generi select[data-g="X"]')).toHaveValue("");
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#kpis .s-kpi .v").nth(0)).toHaveText("10");
  await expect(page.locator("#tab-obblighi tr").nth(1).locator("td").nth(1)).toHaveText("11");
  await expect(page.locator("#errore")).toContainText("1 worker(s)");
  await expect(page.locator("#errore")).toContainText("count for the employer's size");
  await expectLocalRequests(observed);
});


test("reads the payroll tab when an XLSX contains a cover sheet and a title row", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-cover.xlsx");
  await expect(page.locator('#mappa select[data-key="annual_hours"]')).toHaveValue("annual_hours");
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#tab-categorie tr").nth(1).locator("td").nth(1)).toHaveText("5");
  await expectLocalRequests(observed);
});

test("rejects duplicate XLSX headers that normalize to the same name", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-duplicate-headers.xlsx");
  await expect(page.locator("#errore")).toContainText("duplicate or ambiguous column headers");
  await expect(page.locator("#errore")).toContainText("worker_id");
  await expect(page.locator("#errore")).toContainText("Worker ID");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});

test("rejects a workbook when two worksheets match payroll columns equally", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-two-matching-sheets.xlsx");
  await expect(page.locator("#errore")).toContainText("multiple worksheets match");
  await expect(page.locator("#errore")).toContainText("Payroll 2025");
  await expect(page.locator("#errore")).toContainText("Payroll 2024");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});

test("requires an explicit choice when two XLSX headers could mean base pay", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-ambiguous-base-pay.xlsx");
  await expect(page.locator('#mappa select[data-key="base_pay"]')).toHaveValue("");
  await expect(page.locator("#colonne-sub")).toContainText("More than one column could match Base pay");
  await expect(page.locator("#esegui")).toBeDisabled();

  await page.locator('#mappa select[data-key="base_pay"]').selectOption("salary");
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  const directiveRow = page.locator("#tab-categorie tr").nth(1);
  await expect(directiveRow.locator("td").nth(3)).toContainText("23.08");
  await expectLocalRequests(observed);
});

test("shows an error for a corrupt XLSX archive without a browser exception", async ({ page }) => {
  const observed = await openApp(page);
  await page.locator("#file-paghe").setInputFiles({
    name: "synthetic-corrupt.xlsx",
    mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    buffer: Buffer.from("not an xlsx archive", "utf8")
  });
  await expect(page.locator("#errore")).toContainText("not a zip file");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});


test("rejects an XLSX column with data but no header", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-blank-header-with-data.xlsx");
  await expect(page.locator("#errore")).toContainText("blank column header at position 12 contains data");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});


test("finds payroll headers after a long metadata preamble", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-late-header.xlsx");
  await expect(page.locator('#mappa select[data-key="annual_hours"]')).toHaveValue("annual_hours");
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#tab-categorie tr").nth(1).locator("td").nth(1)).toHaveText("5");
  await expectLocalRequests(observed);
});

test("ignores hidden archive worksheets when a visible payroll sheet is available", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-visible-and-hidden.xlsx");
  await expect(page.locator('#mappa select[data-key="annual_hours"]')).toHaveValue("annual_hours");
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expectLocalRequests(observed);
});

test("asks the user to unhide a payroll worksheet instead of silently importing a visible cover", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-hidden-only.xlsx");
  await expect(page.locator("#errore")).toContainText("matching payroll data is in a hidden worksheet");
  await expect(page.locator("#errore")).toContainText("unhide it and retry");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});

test("requires explicit choices for multiple ambiguous XLSX fields", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxPayroll(page, "synthetic-payroll-ambiguous-id-and-base-pay.xlsx");
  await expect(page.locator('#mappa select[data-key="worker_id"]')).toHaveValue("");
  await expect(page.locator('#mappa select[data-key="base_pay"]')).toHaveValue("");
  await expect(page.locator("#colonne-sub")).toContainText("More than one column could match");

  await page.locator('#mappa select[data-key="base_pay"]').selectOption("salary");
  await page.locator('#mappa select[data-key="worker_id"]').selectOption("pseudonymous id");
  await uploadPayCodeMap(page);
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  const categoryRow = page.locator("#tab-categorie tr").nth(1);
  await expect(categoryRow.locator("td").nth(3)).toContainText("23.08");
  await expectLocalRequests(observed);
});

test("reports a truncated XLSX central directory as a controlled file error", async ({ page }) => {
  const observed = await openApp(page);
  const bytes = new Uint8Array(22);
  const view = new DataView(bytes.buffer);
  view.setUint32(0, 0x06054b50, true);
  view.setUint16(8, 1, true);
  view.setUint16(10, 1, true);
  view.setUint32(12, 46, true);
  view.setUint32(16, 21, true);
  await page.locator("#file-paghe").setInputFiles({
    name: "synthetic-truncated-directory.xlsx",
    mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    buffer: Buffer.from(bytes)
  });
  await expect(page.locator("#errore")).toContainText("damaged zip archive");
  await expect(page.locator("#esegui")).toBeDisabled();
  await expectLocalRequests(observed);
});


test("reconciles all payroll rows, including unclassified gender, and exports only aggregates", async ({ page }) => {
  const rows = payrollRowsWithGrossTotal();
  rows.push(["SYN-X-01", "X", "30000,00", "Professional", "IT", "2080", "40", "0,00", "0,00", "0,00", "0,00", "30000,00"]);
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await uploadPayCodeMap(page, true);
  await page.locator("#mostra-colonne").click();
  await expect(page.locator('#mappa select[data-key="payroll_total"]')).toHaveValue("gross_total_paid");
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("11 payroll rows checked");
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("11 within tolerance");
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("0 over tolerance");

  const downloadPromise = page.waitForEvent("download");
  await page.locator("#scarica-xlsx").click();
  const download = await downloadPromise;
  const filePath = await download.path();
  expect(filePath).toBeTruthy();
  const bytes = await readFile(filePath);
  const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const sheets = await readXlsx(arrayBuffer);
  const reconciliation = sheets.find((sheet) => sheet.name === "Payroll reconciliation");
  expect(reconciliation).toBeTruthy();
  const value = (label) => reconciliation.rows.find((row) => row[0] === label)?.[1];
  expect(value("Payroll rows checked")).toBe(11);
  expect(value("Rows within tolerance")).toBe(11);
  expect(value("Rows over tolerance")).toBe(0);
  expect(value("Gross total column")).toBe("gross_total_paid");
  expect(JSON.stringify(reconciliation.rows)).not.toContain("SYN-");
  await expectLocalRequests(observed);
});

test("reports total-pay differences without blocking the assessment", async ({ page }) => {
  const rows = payrollRowsWithGrossTotal();
  const totalIndex = rows[0].indexOf("gross_total_paid");
  rows[1][totalIndex] = "48100,05";
  rows[2][totalIndex] = "48100,01";
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await uploadPayCodeMap(page, true);
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("9 within tolerance");
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("1 over tolerance");
  await expect(page.locator("#errore")).toBeHidden();
  await expectLocalRequests(observed);
});

test("counts missing and invalid annual gross totals separately", async ({ page }) => {
  const rows = payrollRowsWithGrossTotal();
  const totalIndex = rows[0].indexOf("gross_total_paid");
  rows[1][totalIndex] = "";
  rows[2][totalIndex] = "not-money";
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await uploadPayCodeMap(page, true);
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("8 within tolerance");
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("1 missing totals");
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("1 invalid amounts");
  await expectLocalRequests(observed);
});

test("allows assessment without a gross total and clearly skips reconciliation", async ({ page }) => {
  const observed = await loadValidPayroll(page);
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("No separate annual gross total is mapped");
  await expectLocalRequests(observed);
});

test("requires an explicit choice between ambiguous gross total columns", async ({ page }) => {
  const rows = payrollRowsWithGrossTotal();
  const totalIndex = rows[0].indexOf("gross_total_paid");
  rows[0].splice(totalIndex + 1, 0, "total gross pay");
  for (const row of rows.slice(1)) row.splice(totalIndex + 1, 0, row[totalIndex]);
  const observed = await openApp(page);
  await uploadPayroll(page, rows);
  await uploadPayCodeMap(page, true);
  await expect(page.locator('#mappa select[data-key="payroll_total"]')).toHaveValue("");
  await expect(page.locator("#colonne-sub")).toContainText("More than one column could match");
  await expect(page.locator("#esegui")).toBeDisabled();
  await page.locator('#mappa select[data-key="payroll_total"]').selectOption("gross_total_paid");
  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#payroll-reconciliation-result")).toContainText("10 payroll rows checked");
  await expectLocalRequests(observed);
});
