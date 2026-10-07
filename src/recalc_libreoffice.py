"""
Recalculates a copy of the workbook with LibreOffice, so its formulas carry values.

LibreOffice does not recalculate .xlsx files on load by default, and openpyxl stores formulas
without results. A one-line Basic macro in a throwaway profile calls calculateAll() and saves.

    python src/recalc_libreoffice.py deliverables/pay_transparency_model.xlsx build/
"""
import sys
from pathlib import Path

from excel_twin.recalc import recalc

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: recalc_libreoffice.py WORKBOOK OUT_DIR")
    print(f"recalculated -> {recalc(Path(sys.argv[1]), Path(sys.argv[2]))}")
