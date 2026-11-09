import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { readXlsx } from "../../web/design/xlsx.js";
import { parseCsv } from "../../web/design/table.js";

const BASE_URL = "http://127.0.0.1:4173";

function syntheticPayrollCsv() {
  const rows = [[
    "worker_id", "gender", "base_pay", "category", "country", "annual_hours",
    "weekly_hours", "fixed_allowance", "bonus", "one_off", "commission"
  ]];
  for (let index = 1; index <= 5; index += 1) {
    rows.push([
      "SYN-F-" + String(index).padStart(2, "0"), "F", "40000,00", "Professional",
      "IT", "2080", "40", "2000,00", "5000,00", "1000,00", "100,00"
    ]);
  }
  for (let index = 1; index <= 5; index += 1) {
    rows.push([
      "SYN-M-" + String(index).padStart(2, "0"), "M", "21000,00", "Professional",
      "IT", "1040", "40", "1000,00", "0,00", "0,00", "200,00"
    ]);
  }
  return rows.map((row) => row.join(";")).join("\n") + "\n";
}

function syntheticPayCodesCsv() {
  return [
    "pay_code;column_header;description;classification",
    "001;fixed_allowance;Contractual fixed allowance;fixed_continuing",
    "002;bonus;Annual bonus;variable",
    "003;one_off;One-time amount;one_off",
    ""
  ].join("\n");
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

async function uploadCsvInputs(page) {
  await page.locator("#file-paghe").setInputFiles({
    name: "synthetic-payroll.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(syntheticPayrollCsv(), "utf8")
  });
  await expect(page.locator('#mappa select[data-key="annual_hours"]')).toHaveValue("annual_hours");

  await page.locator("#file-codici").setInputFiles({
    name: "synthetic-pay-codes.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(syntheticPayCodesCsv(), "utf8")
  });
  await expect(page.locator("#codici-sub")).toContainText("Loaded 3 pay-code entries");
}

async function uploadXlsxInputs(page) {
  const fixtures = "test-results/e2e-fixtures/";
  await page.locator("#file-paghe").setInputFiles(fixtures + "synthetic-payroll.xlsx");
  await expect(page.locator('#mappa select[data-key="annual_hours"]')).toHaveValue("annual_hours");
  await page.locator("#file-codici").setInputFiles(fixtures + "synthetic-pay-codes.xlsx");
  await expect(page.locator("#codici-sub")).toContainText("Loaded 3 pay-code entries");
}

async function runAssessment(page) {
  await expect(page.locator("#base-dati")).toHaveValue("actual");
  await expect(page.locator("#periodo")).toBeDisabled();
  await expect(page.locator("#periodo")).toHaveValue("pAnnuale");
  const previousCalendarYear = await page.evaluate(() => new Date().getFullYear() - 1);
  await expect(page.locator("#anno-paghe")).toHaveValue(String(previousCalendarYear));

  await expect(page.locator('#componenti input[value="fixed_allowance"]')).toBeChecked();
  await expect(page.locator('#componenti input[value="fixed_allowance"]')).toBeDisabled();
  await expect(page.locator('#componenti input[value="bonus"]')).toBeChecked();
  await expect(page.locator('#componenti input[value="bonus"]')).toBeDisabled();
  await expect(page.locator('#componenti input[value="one_off"]')).toBeChecked();
  await expect(page.locator('#componenti input[value="one_off"]')).toBeDisabled();

  await expect(page.locator('#fisse input[value="fixed_allowance"]')).toBeChecked();
  await expect(page.locator('#fisse input[value="fixed_allowance"]')).toBeDisabled();
  await expect(page.locator('#fisse input[value="bonus"]')).not.toBeChecked();
  await expect(page.locator('#fisse input[value="one_off"]')).not.toBeChecked();

  await expect(page.locator('#componenti input[value="commission"]')).not.toBeChecked();
  await page.locator('#componenti input[value="commission"]').check();
  await expect(page.locator("#esegui")).toBeDisabled();
  await expect(page.locator("#codici-sub")).toContainText("commission");
  await expect(page.locator("#codici-sub")).toContainText("classification");
  await page.locator('#componenti input[value="commission"]').uncheck();

  await expect(page.locator("#esegui")).toBeEnabled();
  await page.locator("#esegui").click();
  await expect(page.locator("#risultati")).toBeVisible();

  const directiveRow = page.locator("#tab-categorie tr").nth(1);
  const directiveCells = await directiveRow.locator("td").allTextContents();
  expect(directiveCells[1]).toBe("5");
  expect(directiveCells[2]).toBe("5");
  expect(directiveCells[3]).toContain("23.08");
  expect(directiveCells[4]).toContain("21.15");
  expect(directiveCells[7].replace(/\u2212/g, "-")).toContain("-9.1%");

  const italyRow = page.locator("#tab-italia-cat tr").nth(1);
  const italyCells = await italyRow.locator("td").allTextContents();
  expect(italyCells[1]).toBe("5");
  expect(italyCells[2]).toBe("5");
  expect(italyCells[3]).toContain("4.5%");

  const metadata = await page.locator("#stampa-meta").textContent();
  expect(metadata).toContain(String(previousCalendarYear));
  expect(metadata).not.toContain("synthetic-payroll");

  return previousCalendarYear;
}

async function expectLocalProcessing(observed, page) {
  expect(observed.requests.every((entry) => entry.origin === BASE_URL && entry.method === "GET")).toBe(true);
  expect(observed.errors).toEqual([]);
  const persisted = await page.evaluate(() => JSON.stringify(
    Object.entries(localStorage).map(([key, value]) => [key, value])
  ));
  for (const marker of ["SYN-F-", "SYN-M-", "synthetic-payroll", "48000", "21000"]) {
    expect(persisted).not.toContain(marker);
  }
}

test("CSV actual-pay workflow classifies pay codes, blocks unmapped components and exports the map", async ({ page }) => {
  const observed = await openApp(page);
  await uploadCsvInputs(page);
  await runAssessment(page);

  const downloadPromise = page.waitForEvent("download");
  await page.locator("#scarica-xlsx").click();
  const download = await downloadPromise;
  const filePath = await download.path();
  expect(filePath).toBeTruthy();
  const bytes = await readFile(filePath);
  const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const sheets = await readXlsx(arrayBuffer);
  const codeSheet = sheets.find((sheet) => sheet.name === "Pay-code map");
  expect(codeSheet).toBeTruthy();

  expect(codeSheet.rows[0]).toEqual([
    "Pay code",
    "Payroll column header",
    "Description",
    "Classification",
    "Included in components",
    "Included in fixed and continuing pay (Italy)"
  ]);
  const fixed = codeSheet.rows.find((row) => row[0] === "001");
  const bonus = codeSheet.rows.find((row) => row[0] === "002");
  const oneOff = codeSheet.rows.find((row) => row[0] === "003");
  expect(fixed).toEqual([
    "001", "fixed_allowance", "Contractual fixed allowance",
    "Fixed and continuing", "Yes", "Yes"
  ]);
  expect(bonus[5]).toBe("No");
  expect(oneOff[5]).toBe("No");

  await expectLocalProcessing(observed, page);
  await page.locator("#pulisci").click();
  await expect(page.locator("#risultati")).toBeHidden();
  await expect(page.locator("#file-paghe")).toHaveValue("");
  await expect(page.locator("#file-codici")).toHaveValue("");
});


test("downloads a local pay-code draft with exact numeric payroll headers", async ({ page }) => {
  const observed = await openApp(page);
  await page.locator("#file-paghe").setInputFiles({
    name: "synthetic-payroll.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(syntheticPayrollCsv(), "utf8")
  });
  await expect(page.locator("#scarica-bozza-codici")).toBeVisible();
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#scarica-bozza-codici").click();
  const download = await downloadPromise;
  const filePath = await download.path();
  expect(filePath).toBeTruthy();
  const draftText = await readFile(filePath, "utf8");
  const draft = parseCsv(draftText);
  expect(draft.headers).toEqual(["pay_code", "column_header", "description", "classification"]);
  expect(draft.rows.map((row) => row.column_header)).toEqual(["fixed_allowance", "bonus", "one_off", "commission"]);
  expect(draft.rows.every((row) => !row.pay_code && !row.description && !row.classification)).toBe(true);
  expect(draftText).not.toContain("SYN-F-");
  expect(draftText).not.toContain("40000");
  await expectLocalProcessing(observed, page);
});

test("compressed XLSX payroll and code-map files run through the same local assessment", async ({ page }) => {
  const observed = await openApp(page);
  await uploadXlsxInputs(page);
  await runAssessment(page);
  await expectLocalProcessing(observed, page);
});
