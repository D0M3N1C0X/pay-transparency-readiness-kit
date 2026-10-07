"""
Office files are zip archives stamped with the time they were written, so the same workbook
built twice differs byte for byte. Rewriting every entry with a fixed timestamp, and pinning
the created/modified dates inside docProps/core.xml, makes the content reproducible.

Compressed bytes can still differ between zlib builds, so CI compares the decompressed
entries (``same_content``) rather than the files themselves.

    python src/deterministic.py --check deliverables/pay_transparency_model.xlsx
"""
import sys

from excel_twin.determinism import check_against_git, differences, normalise, same_content  # noqa: F401

if __name__ == "__main__":
    if sys.argv[1:2] != ["--check"] or len(sys.argv) < 3:
        raise SystemExit("usage: deterministic.py --check FILE [FILE ...]")
    raise SystemExit(check_against_git(sys.argv[2:]))
