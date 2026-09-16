"""
Recalculates a copy of the workbook with LibreOffice, so its formulas carry values.

LibreOffice does not recalculate .xlsx files on load by default, and openpyxl stores formulas
without results. A one-line Basic macro in a throwaway profile calls calculateAll() and saves.

    python src/recalc_libreoffice.py deliverables/pay_transparency_model.xlsx build/
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub RecalculateAndSave()
      ThisComponent.calculateAll()
      ThisComponent.store()
      ThisComponent.close(True)
    End Sub
</script:module>"""


def recalc(source: Path, out_dir: Path, timeout: int = 600) -> Path:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise SystemExit("LibreOffice (soffice) is not on PATH")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / source.name
    shutil.copyfile(source, target)
    before = target.stat().st_mtime_ns
    with tempfile.TemporaryDirectory(prefix="lo-profile-") as profile:
        url = Path(profile).as_uri()
        subprocess.run([soffice, "--headless", "--terminate_after_init", f"-env:UserInstallation={url}"],
                       check=True, capture_output=True, timeout=120)
        macro_dir = Path(profile) / "user" / "basic" / "Standard"
        (macro_dir / "Module1.xba").write_text(MACRO)
        subprocess.run([soffice, "--headless", "--norestore", f"-env:UserInstallation={url}",
                        "vnd.sun.star.script:Standard.Module1.RecalculateAndSave?language=Basic&location=application",
                        str(target.resolve())], check=True, capture_output=True, timeout=timeout)
    if target.stat().st_mtime_ns == before:
        raise SystemExit("LibreOffice exited without saving: nothing was recalculated")
    return target


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: recalc_libreoffice.py WORKBOOK OUT_DIR")
    print(f"recalculated -> {recalc(Path(sys.argv[1]), Path(sys.argv[2]))}")
