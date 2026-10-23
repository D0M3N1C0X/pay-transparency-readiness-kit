"""The browser tool: its inputs come from the pipeline, its JavaScript is checked against cases computed here, and
the page keeps its promise that nothing leaves the computer."""
import json
import re

import build_web
from config import ROOT

WEB = ROOT / "web"


def test_inputs_come_from_the_pipeline():
    assert json.loads((WEB / "inputs.json").read_text(encoding="utf-8")) == json.loads(json.dumps(build_web.cfg()))


def test_javascript_cases_are_current(tmp_path, monkeypatch):
    """The cases tests/js/check_engine.mjs runs must be the ones the pipeline gives today."""
    committed = build_web.VECTORS.read_text(encoding="utf-8")
    monkeypatch.setattr(build_web, "VECTORS", tmp_path / "v.json")
    build_web.write_vectors()
    assert (tmp_path / "v.json").read_text(encoding="utf-8") == committed


def test_cases_cover_the_edges():
    v = json.loads((ROOT / "tests" / "fixtures" / "js_vectors.json").read_text(encoding="utf-8"))
    statuses = {r["status"] for c in v["cases"] for r in c["screen"]}
    bands = {o["size_band"] for c in v["cases"] for o in c["obligations"]}
    assert statuses == {"flag", "ok", "one_sex"}
    assert len(bands) == 4
    assert any(r["small_cell"] for c in v["cases"] for r in c["screen"])


def test_every_text_in_both_languages():
    page = (WEB / "index.html").read_text(encoding="utf-8")
    app = (WEB / "app.js").read_text(encoding="utf-8")
    keys = set(re.findall(r'data-i18n="(\w+)"', page)) | set(re.findall(r'data-i18n-attr="[\w-]+:(\w+)"', page))
    assert [k for k in sorted(keys) if len(re.findall(rf"\b{k}:", app)) < 2] == []


def test_the_page_loads_nothing_from_outside():
    """'Nothing is sent anywhere': no script, style or font from another site, and no visit counter."""
    page = (WEB / "index.html").read_text(encoding="utf-8")
    assert not re.search(r'(src|href)="https?://(?!github\.com/D0M3N1C0X/)', page)
    for js in WEB.rglob("*.js"):
        text = js.read_text(encoding="utf-8")
        assert "goatcounter" not in text.lower()
        assert not re.search(r"fetch\(\s*[\"'`]https?:", text), js.name
