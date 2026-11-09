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
    rows: list[list[object]] = [PAYROLL_HEADERS]
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


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_workbook(OUTPUT / "synthetic-payroll.xlsx", "Payroll", payroll_rows())
    write_workbook(OUTPUT / "synthetic-pay-codes.xlsx", "Codes", PAY_CODE_ROWS)


if __name__ == "__main__":
    main()
