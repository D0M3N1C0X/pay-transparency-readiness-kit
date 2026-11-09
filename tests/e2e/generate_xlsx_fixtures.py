from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "test-results" / "e2e-fixtures"

PAYROLL_HEADERS = [
    "worker_id",
    "gender",
    "base_pay",
    "category",
    "country",
    "annual_hours",
    "weekly_hours",
    "fixed_allowance",
    "bonus",
    "one_off",
    "commission",
]
PAY_CODE_ROWS = [
    ["pay_code", "column_header", "description", "classification"],
    ["001", "fixed_allowance", "Contractual fixed allowance", "fixed_continuing"],
    ["002", "bonus", "Annual bonus", "variable"],
    ["003", "one_off", "One-time amount", "one_off"],
]


def payroll_rows() -> list[list[object]]:
    rows: list[list[object]] = [PAYROLL_HEADERS.copy()]
    groups = [
        ("F", "SYN-F", 40000, 2080, 2000, 5000, 1000, 100),
        ("M", "SYN-M", 21000, 1040, 1000, 0, 0, 200),
    ]
    for gender, prefix, base, annual_hours, fixed, bonus, one_off, commission in groups:
        for index in range(1, 6):
            rows.append(
                [
                    f"{prefix}-{index:02d}",
                    gender,
                    base,
                    "Professional",
                    "IT",
                    annual_hours,
                    40,
                    fixed,
                    bonus,
                    one_off,
                    commission,
                ]
            )
    return rows


def write_workbook(path: Path, sheet_name: str, rows: list[list[object]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(row)
    workbook.save(path)


def write_multisheet_workbook(path: Path, sheets: list[tuple[str, list[list[object]]]]) -> None:
    workbook = Workbook()
    for index, (name, rows) in enumerate(sheets):
        sheet = workbook.active if index == 0 else workbook.create_sheet()
        sheet.title = name
        for row in rows:
            sheet.append(row)
    workbook.save(path)


def payroll_with_duplicate_headers() -> list[list[object]]:
    rows = payroll_rows()
    for index, row in enumerate(rows):
        row.append("Worker ID" if index == 0 else row[0])
    return rows


def payroll_with_ambiguous_base_pay() -> list[list[object]]:
    rows = payroll_rows()
    base_index = rows[0].index("base_pay")
    rows[0].insert(base_index + 1, "salary")
    for row in rows[1:]:
        actual_base_pay = row[base_index]
        row[base_index] = 999999
        row.insert(base_index + 1, actual_base_pay)
    return rows


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    payroll = payroll_rows()
    write_workbook(OUTPUT / "synthetic-payroll.xlsx", "Payroll", payroll)
    write_workbook(OUTPUT / "synthetic-pay-codes.xlsx", "Codes", PAY_CODE_ROWS)
    write_workbook(
        OUTPUT / "synthetic-payroll-duplicate-headers.xlsx",
        "Payroll",
        payroll_with_duplicate_headers(),
    )
    write_workbook(
        OUTPUT / "synthetic-payroll-ambiguous-base-pay.xlsx",
        "Payroll",
        payroll_with_ambiguous_base_pay(),
    )
    write_multisheet_workbook(
        OUTPUT / "synthetic-payroll-cover.xlsx",
        [
            ("Read me", [["Synthetic payroll export"], ["Use the Payroll tab for the assessment"]]),
            ("Payroll", [["Export generated for browser tests"], *payroll]),
        ],
    )
    write_multisheet_workbook(
        OUTPUT / "synthetic-payroll-two-matching-sheets.xlsx",
        [("Payroll 2025", payroll), ("Payroll 2024", payroll)],
    )


if __name__ == "__main__":
    main()
