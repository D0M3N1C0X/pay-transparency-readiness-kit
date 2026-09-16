"""
Every assumption the kit makes, in one place.

Anything a client would change - hours, thresholds, factor weights, band limits - lives
here and is written into the workbook's Settings sheet, so the Python pipeline and the
Excel model always start from the same numbers.
"""
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SOURCE_EMPLOYEES = DATA / "source" / "employees.csv"
JOB_EVALUATION = DATA / "job_evaluation.csv"
PAYROLL_EXTRACT = DATA / "payroll_extract.csv"
REPORTS = ROOT / "reports"
DELIVERABLES = ROOT / "deliverables"
TABLEAU = ROOT / "tableau"

# Provenance of the vendored source table (see data/README.md).
SOURCE_REPO = "https://github.com/D0M3N1C0X/hr-people-analytics"
SOURCE_COMMIT = "201495b"
SOURCE_SHA256 = "372723241e92aa3d233c9298f8a0d2e713e72ff8f0c989e24a7bf743fc7da79c"

SEED = 2026
SNAPSHOT = date(2026, 6, 30)          # population: workers active on this date
ASSESSMENT_DATE = date(2026, 9, 16)   # date of this dry run and of the legal status notes

# Legal entities, one per Member State. Pay is reported per employer.
ENTITIES = {
    "IT": "IT · Milan",
    "PL": "PL · Kraków",
    "DE": "DE · Munich",
    "ES": "ES · Barcelona",
}

# Synthetic assumption: a 40-hour contractual full-time week in all four entities.
FULL_TIME_WEEKLY_HOURS = 40
WEEKS_PER_YEAR = 52

# Article 10(1)(a): a difference of at least 5% in any category of workers.
JPA_THRESHOLD = 0.05
# Article 10(1)(c): six months from submission to remedy an unjustified difference.
REMEDY_MONTHS = 6
# Disclosure control (Article 12(3)): below this many workers of one sex in a category,
# an average can reveal an identifiable person's pay. The Directive sets no number;
# five matches the confidentiality threshold of engagement-survey-analytics.
MIN_CELL = 5

# Article 9(2)-(4): size bands, reporting frequency and first deadline.
SIZE_BANDS = [  # (minimum workers, label, frequency, first deadline)
    (250, "250 or more", "Every year", date(2027, 6, 7)),
    (150, "150 to 249", "Every three years", date(2027, 6, 7)),
    (100, "100 to 149", "Every three years", date(2031, 6, 7)),
    (0, "Fewer than 100", "Voluntary, unless national law requires it", None),
]

# Gender-neutral job evaluation (Article 4(4)): the four criteria the Directive names.
FACTORS = ["skills", "effort", "responsibility", "working_conditions"]
# Whole-number weights that sum to 100, so points are exact integers in Python and Excel
# alike: a role scores between 100 and 500.
FACTOR_WEIGHTS = {"skills": 35, "effort": 15, "responsibility": 35, "working_conditions": 15}

# Categories of workers: point bands. Lower limit inclusive.
BANDS = [
    (100, "Cat A"),
    (160, "Cat B"),
    (200, "Cat C"),
    (250, "Cat D"),
    (300, "Cat E"),
    (340, "Cat F"),
    (400, "Cat G"),
]

# ---- Pay components used to build the synthetic payroll extract ------------------------
# Annual target bonus as a share of base pay, by job level.
BONUS_TARGET = {"L1": 0.0, "L2": 0.0, "L3": 0.05, "L4": 0.08, "L5": 0.12, "L6": 0.20}
# Payout multiplier by performance rating (1-5).
BONUS_PAYOUT = {1: 0.0, 2: 0.5, 3: 1.0, 4: 1.25, 5: 1.5}
# Sales commission: share of base pay at an average territory.
COMMISSION_RATE = 0.15
# Monthly shift allowance for on-site Operations and Customer Service staff, L1-L3.
SHIFT_ALLOWANCE_MONTHLY = {"IT": 110, "PL": 70, "DE": 150, "ES": 100}
# Annual car allowance for L5-L6.
CAR_ALLOWANCE_ANNUAL = {"IT": 6000, "PL": 4200, "DE": 7200, "ES": 5400}
