"""
The whole kit in one command:

    python src/run_all.py

payroll extract -> job evaluation -> Article 9 and 10 -> report and figures -> Excel model
-> board deck -> Tableau extracts. Deterministic: the same inputs give the same outputs.
"""
import time

import build_deck
import build_extract
import build_report
import build_tableau
import build_workbook
import report_html
from workers import load_workers


def main() -> None:
    start = time.perf_counter()
    build_extract.main()
    workers = load_workers()
    build_report.write(workers)
    report_html.build()
    print("report -> reports/readiness_report.md, reports/index.html, reports/figures/")
    model = build_workbook.build(workers)
    print(f"workbook -> deliverables/pay_transparency_model.xlsx ({len(model.checks)} reconciliation checks)")
    build_deck.build(workers)
    print("deck -> deliverables/board_briefing.pptx")
    build_tableau.write(workers)
    print("tableau -> tableau/*.csv")
    print(f"done in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
