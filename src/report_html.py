"""
Render reports/readiness_report.md as one self-contained HTML page (reports/index.html).

Adapted from hr-people-analytics (src/build_report_html.py, same author, MIT) so the two
reports read as one series. Changes: bullet lists, status pills for this kit's labels, and
chart plates that follow dark mode, because these SVGs carry their own dark palette.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SOURCE = REPORTS / "readiness_report.md"

TITLE = "Pay Transparency Readiness"

STYLE = """
<style>
/* Portfolio identity 1.0 (brand/tokens.css in d0m3n1c0x.github.io): light in the Apple manner, dark in the
   Revolut manner. System fonts only, so the page loads nothing from other sites. */
:root{
  --paper:#ffffff; --paper-2:#f5f5f7; --surface:#ffffff; --ink:#1d1d1f; --ink-soft:#424245; --muted:#6e6e73;
  --line:#e8e8ed; --line-strong:#d2d2d7; --accent:#0066cc; --accent-2:#5e5ce6; --accent-wash:#eef5fd;
  --flag:#d70015; --flag-wash:#fdeceb; --ok:#17783a; --ok-wash:#e6f4ea; --warn:#b25000; --warn-wash:#fff4e5;
  --plate:#ffffff; --plate-edge:#e8e8ed; --shadow:0 1px 2px rgba(0,0,0,.04),0 12px 32px rgba(0,0,0,.06); --glow:none;
  --font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --display:-apple-system,BlinkMacSystemFont,"SF Pro Display","Inter","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#000000; --paper-2:#0b0c0f; --surface:#15171c; --ink:#f5f5f7; --ink-soft:#c7c9d1; --muted:#8b8f9a;
    --line:#23262e; --line-strong:#343844; --accent:#4f8cff; --accent-2:#8b5cf6; --accent-wash:#101b33;
    --flag:#ff6961; --flag-wash:#331314; --ok:#32d74b; --ok-wash:#0f2a17; --warn:#ffb340; --warn-wash:#2e220c;
    --plate:#15171c; --plate-edge:#23262e; --shadow:none;
    --glow:radial-gradient(60% 120% at 90% 0%,rgba(79,140,255,.22),transparent 70%),radial-gradient(40% 100% at 100% 40%,rgba(139,92,246,.18),transparent 70%);
  }
}
:root[data-theme="dark"]{
  --paper:#000000; --paper-2:#0b0c0f; --surface:#15171c; --ink:#f5f5f7; --ink-soft:#c7c9d1; --muted:#8b8f9a;
  --line:#23262e; --line-strong:#343844; --accent:#4f8cff; --accent-2:#8b5cf6; --accent-wash:#101b33;
  --flag:#ff6961; --flag-wash:#331314; --ok:#32d74b; --ok-wash:#0f2a17; --warn:#ffb340; --warn-wash:#2e220c;
  --plate:#15171c; --plate-edge:#23262e; --shadow:none;
  --glow:radial-gradient(60% 120% at 90% 0%,rgba(79,140,255,.22),transparent 70%),radial-gradient(40% 100% at 100% 40%,rgba(139,92,246,.18),transparent 70%);
}

*{box-sizing:border-box}
body{margin:0; background:var(--paper); color:var(--ink); font-family:var(--font);
  font-size:17px; line-height:1.6; -webkit-font-smoothing:antialiased; letter-spacing:-.003em}
.page{padding:0 clamp(1rem,4vw,2rem) 5rem}
.doc{display:grid; gap:1.4rem; justify-items:center}
.doc > *{width:100%; max-width:44rem; margin:0}
.doc > figure, .doc > .table-wrap{max-width:60rem}

h1,h2,h3{font-family:var(--display); text-wrap:balance; margin:0; color:var(--ink)}
h1{font-size:clamp(2.3rem,6vw,3.6rem); font-weight:700; letter-spacing:-.03em; line-height:1.05}
h2{font-size:clamp(1.55rem,3.4vw,2.1rem); font-weight:700; letter-spacing:-.02em; line-height:1.15;
   display:flex; align-items:baseline; gap:.8rem; padding-top:2.75rem; margin-top:1.25rem; border-top:1px solid var(--line)}
h2 .num{font:600 .8rem/1 var(--font); color:var(--accent); background:var(--accent-wash);
  padding:.35em .6em; border-radius:999px; font-variant-numeric:tabular-nums; transform:translateY(-.2em)}
h3{font-size:1.2rem; font-weight:600; letter-spacing:-.01em; padding-top:1rem}
p{margin:0; color:var(--ink-soft)}
strong{color:var(--ink); font-weight:600}
a{color:var(--accent); text-decoration:underline; text-decoration-thickness:1px; text-underline-offset:3px}
a:hover{text-decoration-thickness:2px}
a:focus-visible{outline:3px solid var(--accent); outline-offset:3px; border-radius:6px}

.masthead{position:relative; padding:clamp(2.5rem,7vw,5rem) 0 2rem; margin:0 0 .5rem}
.masthead::before{content:""; position:absolute; inset:0 calc(50% - 50vw); background:var(--glow); z-index:-1; pointer-events:none}
.eyebrow{font:600 .8rem/1.2 var(--font); letter-spacing:.06em; text-transform:uppercase; color:var(--accent); margin-bottom:1rem}
dl.meta{display:grid; grid-template-columns:auto 1fr; gap:.5rem 1.4rem; margin:2rem 0 0; font-size:.95rem;
  padding:1.2rem 1.4rem; background:var(--paper-2); border-radius:18px}
dl.meta dt{font:600 .72rem/1.6 var(--font); letter-spacing:.06em; text-transform:uppercase; color:var(--muted); padding-top:.2em}
dl.meta dd{margin:0; color:var(--ink-soft)}

.notice{background:var(--accent-wash); border-radius:18px; padding:1.1rem 1.35rem; font-size:.97rem; color:var(--ink-soft)}
p.note{font-size:.9rem; color:var(--muted)}

figure{display:flex; flex-direction:column; gap:.7rem}
figure .plate{background:var(--plate); border:1px solid var(--plate-edge); border-radius:20px; box-shadow:var(--shadow);
  padding:.4rem; overflow-x:auto}
figure svg{display:block; width:100%; height:auto; min-width:32rem}
figcaption{font-size:.85rem; color:var(--muted); padding:0 .4rem}

.table-wrap{overflow-x:auto; border:1px solid var(--line); border-radius:18px; background:var(--surface)}
table{border-collapse:collapse; width:100%; font-size:.93rem; font-variant-numeric:tabular-nums}
th,td{padding:.7rem 1rem; text-align:left; border-bottom:1px solid var(--line)}
thead th{font:600 .72rem/1.3 var(--font); letter-spacing:.05em; text-transform:uppercase; color:var(--muted);
  background:var(--paper-2); border-bottom:1px solid var(--line-strong); white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.r,th.r{text-align:right}
td.r{font-variant-numeric:tabular-nums}

.pill{display:inline-block; padding:.2em .7em; border-radius:999px; font-size:.75rem; font-weight:600; white-space:nowrap}
.pill.flag{background:var(--flag-wash); color:var(--flag)}
.pill.ok{background:var(--ok-wash); color:var(--ok)}
.pill.warn{background:var(--warn-wash); color:var(--warn)}
ul{margin:0; padding-left:1.2rem; display:grid; gap:.55rem; color:var(--ink-soft)}
ul li::marker{color:var(--accent)}

code{font-family:var(--mono); font-size:.86em; background:var(--paper-2); color:var(--ink); padding:.12em .4em; border-radius:6px}
ol{margin:0; padding-left:1.3rem; display:grid; gap:.75rem; color:var(--ink-soft)}
ol li::marker{color:var(--accent); font-weight:600}
hr{border:none; height:1px; background:var(--line); margin:1rem 0}

footer.colophon{max-width:44rem; margin:3.5rem auto 0; padding-top:1.25rem; border-top:1px solid var(--line);
  font-size:.85rem; color:var(--muted)}
@media (max-width:640px){
  body{font-size:16px}
  dl.meta{grid-template-columns:1fr; gap:.15rem}
  dl.meta dd{margin-bottom:.5rem}
}
</style>
"""

COLOPHON = ('<footer class="colophon">Generated from <code>reports/readiness_report.md</code> by '
            '<code>python3 src/run_all.py</code>. Synthetic data, fixed seed: no real person\'s pay. '
            'Not legal advice. Source: <a href="https://github.com/D0M3N1C0X/pay-transparency-readiness-kit">'
            'pay-transparency-readiness-kit</a>.</footer>')

PILLS = {"Justify or remedy": "flag", "Gap": "flag", "Not transposed": "flag",
         "Below 5%": "ok", "Ready": "ok", "Transposed": "ok",
         "Partial": "warn", "Partly transposed": "warn", "Draft": "warn"}


# --------------------------------------------------------------------------
# Inline markdown
# --------------------------------------------------------------------------

REPO = "https://github.com/D0M3N1C0X/pay-transparency-readiness-kit"


def href(target: str) -> str:
    """Links written for the repository, rewritten for the published page: the site serves the
    deliverables next to index.html; everything else is read on GitHub."""
    if not target.startswith("../"):
        return target
    path = target[3:]
    if path.startswith("deliverables/"):
        return path.split("/", 1)[1]
    return f"{REPO}/blob/main/{path}"


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{href(m.group(2))}">{m.group(1)}</a>', out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", out)
    out = out.replace(" - ", " &ndash; ")
    return out


def cell(text: str, align: str) -> str:
    klass = ' class="r"' if align == "r" else ""
    if text in PILLS:
        return f'<td{klass}><span class="pill {PILLS[text]}">{inline(text)}</span></td>'
    return f"<td{klass}>{inline(text)}</td>"


def parse_table(rows: list[str]) -> str:
    def split(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    headers = split(rows[0])
    # `---:` means right-aligned; `:---` and `:---:` do not.
    aligns = ["r" if c.strip().endswith(":") and not c.strip().startswith(":") else "l"
              for c in split(rows[1])]
    body = []
    for row in rows[2:]:
        cells = split(row)
        body.append("<tr>" + "".join(cell(c, aligns[i] if i < len(aligns) else "l")
                                     for i, c in enumerate(cells)) + "</tr>")
    head = "".join(
        '<th{}>{}</th>'.format(' class="r"' if aligns[i] == "r" else "", inline(h))
        for i, h in enumerate(headers))
    label = re.sub(r"<[^>]+>", "", inline(headers[0])) if headers else ""
    return ('<div class="table-wrap" tabindex="0" role="region" aria-label="Table: ' + label.replace('"', "") + '">'
            + '<table><thead><tr>' + head + "</tr></thead><tbody>"
            + "".join(body) + "</tbody></table></div>")


def figure(alt: str, src: str) -> str:
    svg_path = REPORTS / src
    if not svg_path.exists():
        return f'<p class="note">[missing figure: {html.escape(src)}]</p>'
    svg = svg_path.read_text(encoding="utf-8")
    svg = re.sub(r'\s(width|height)="\d+"', "", svg, count=2)
    return (f'<figure><div class="plate">{svg}</div>'
            f"<figcaption>{html.escape(alt)}</figcaption></figure>")


def paragraph(lines: list[str]) -> str:
    text = "\n".join(lines).strip()
    if not text:
        return ""
    # A run of "**Label:** value" entries becomes the masthead metadata list,
    # even where the source wraps a value across several lines.
    if re.match(r"^\*\*[^*]+:\*\*", text) and text.count("**") >= 4:
        parts = re.split(r"\*\*([^*]+):\*\*", text)
        items = [f"<dt>{inline(label)}</dt><dd>{inline(' '.join(value.split()))}</dd>"
                 for label, value in zip(parts[1::2], parts[2::2], strict=True)]
        return '<dl class="meta">' + "".join(items) + "</dl>"
    if text.startswith("*") and text.endswith("*") and not text.startswith("**"):
        return f'<p class="note">{inline(text.strip("*"))}</p>'
    return f"<p>{inline(text)}</p>"


def convert(md: str) -> str:
    out: list[str] = []
    buf: list[str] = []
    table: list[str] = []
    quote: list[str] = []
    olist: list[str] = []
    ulist: list[str] = []

    def flush() -> None:
        nonlocal buf, table, quote, olist, ulist
        if buf:
            out.append(paragraph(buf))
            buf = []
        if table:
            out.append(parse_table(table))
            table = []
        if quote:
            out.append(f'<div class="notice">{inline(" ".join(quote))}</div>')
            quote = []
        if olist:
            out.append("<ol>" + "".join(f"<li>{inline(i)}</li>" for i in olist) + "</ol>")
            olist = []
        if ulist:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in ulist) + "</ul>")
            ulist = []

    for raw in md.splitlines():
        line = raw.rstrip()

        if line.startswith("|"):
            flush() if (buf or quote or olist) else None
            table.append(line)
            continue
        if line.startswith("> "):
            flush() if (buf or table or olist) else None
            quote.append(line[2:])
            continue
        if re.match(r"^\d+\.\s", line):
            flush() if (buf or table or quote or ulist) else None
            olist.append(re.sub(r"^\d+\.\s", "", line))
            continue
        if line.startswith("- "):
            flush() if (buf or table or quote or olist) else None
            ulist.append(line[2:])
            continue
        if ulist and line.startswith("  ") and line.strip():
            ulist[-1] += " " + line.strip()
            continue

        if not line.strip() or line.strip() == "---":
            flush()
            continue
        if not line.startswith(("#", "![")):
            buf.append(line)
            continue

        flush()

        if line.startswith("!["):
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if m:
                out.append(figure(m.group(1), m.group(2)))
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            heading = line[3:]
            m = re.match(r"^(\d+)\.\s+(.*)$", heading)
            if m:
                out.append(f'<h2><span class="num">{int(m.group(1)):02d}</span>'
                           f"<span>{inline(m.group(2))}</span></h2>")
            else:
                out.append(f"<h2><span>{inline(heading)}</span></h2>")
            continue
        if line.startswith("# "):
            out.append('<header class="masthead"><p class="eyebrow">Directive (EU) 2023/970 '
                       "&middot; dry run at 30 June 2026</p>"
                       f"<h1>{inline(line[2:])}</h1>")
            out.append("__CLOSE_MASTHEAD__")
            continue

    flush()

    body = "\n".join(b for b in out if b)
    # the metadata list belongs inside the masthead, everything after it does not
    body = body.replace("__CLOSE_MASTHEAD__\n<dl", "<dl").replace("</dl>", "</dl></header>", 1)
    body = body.replace("__CLOSE_MASTHEAD__", "</header>")
    return body


def build() -> Path:
    body = convert(SOURCE.read_text(encoding="utf-8"))
    target = REPORTS / "index.html"
    target.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                      '<meta name="viewport" content="width=device-width,initial-scale=1">'
                      f"<title>{TITLE}</title>{STYLE}</head><body>"
                      f'<div class="page"><article class="doc">{body}</article>{COLOPHON}</div>'
                      "</body></html>\n", encoding="utf-8")
    return target


if __name__ == "__main__":
    print(f"report page -> {build().relative_to(ROOT)}")
