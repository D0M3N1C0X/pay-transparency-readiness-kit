"""
Three SVG charts for the report, written by hand so the kit needs no plotting library.

Colours are the validated reference palette (slot 1 blue, slot 2 orange; blue and red as the
diverging poles), with dark-mode steps inside each file. Every mark carries a <title>, so a
browser shows its value on hover.
"""
from html import escape

STYLE = """<style>
  svg { --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --grid:#e1e0d9;
        --axis:#c3c2b7; --s1:#2a78d6; --s2:#eb6834; --pos:#e34948; --neg:#2a78d6; --mid:#f0efec; }
  @media (prefers-color-scheme: dark) {
    svg { --surface:#1a1a19; --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781; --grid:#2c2c2a;
          --axis:#383835; --s1:#3987e5; --s2:#d95926; --pos:#e66767; --neg:#3987e5; --mid:#383835; }
  }
  text { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; fill: var(--ink2); font-size: 12px; }
  .title { fill: var(--ink); font-size: 15px; font-weight: 600; }
  .sub { fill: var(--ink2); font-size: 12px; }
  .muted { fill: var(--muted); font-size: 11px; }
  .val { fill: var(--ink); font-variant-numeric: tabular-nums; }
  .num { font-variant-numeric: tabular-nums; }
</style>"""


def _svg(width, height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" '
            f'height="{height}" role="img" aria-label="{escape(label)}">{STYLE}'
            f'<rect width="{width}" height="{height}" rx="8" fill="var(--surface)"/>{body}</svg>\n')


def pct(x, digits=1):
    return f"{x * 100:.{digits}f}%"


def _bar(x, y, w, h, colour, tip):
    """Horizontal bar: square at the baseline, 4px rounded data-end."""
    r = min(4, w / 2, h / 2)
    if w <= 0:
        return ""
    path = (f"M{x},{y} H{x + w - r} Q{x + w},{y} {x + w},{y + r} V{y + h - r} "
            f"Q{x + w},{y + h} {x + w - r},{y + h} H{x} Z")
    return f'<path d="{path}" fill="var({colour})"><title>{escape(tip)}</title></path>'


def gap_by_employer(rows):
    """rows: [(label, mean gap, median gap)] -> grouped horizontal bars."""
    W, left, right, top = 720, 150, 70, 92
    band, bar = 56, 18
    H = top + band * len(rows) + 46
    vmax = max(0.25, max(max(m, d) for _, m, d in rows))
    step = 0.05
    ticks = [i * step for i in range(int(vmax / step) + 1)]
    scale = (W - left - right) / ticks[-1] if ticks[-1] else 1
    headline = ("Women earn less per hour in every employer" if all(m > 0 for _, m, _ in rows)
                else "Gender pay gap by employer")
    body = [
        f'<text x="24" y="34" class="title">{headline}</text>',
        '<text x="24" y="54" class="sub">Gender pay gap on gross hourly pay, base plus all components. Share of men\'s pay.</text>',
        f'<rect x="{left}" y="68" width="10" height="10" rx="2" fill="var(--s1)"/>'
        f'<text x="{left + 16}" y="77">Mean (Article 9(1)(a))</text>',
        f'<rect x="{left + 190}" y="68" width="10" height="10" rx="2" fill="var(--s2)"/>'
        f'<text x="{left + 206}" y="77">Median (Article 9(1)(c))</text>',
    ]
    base = top + band * len(rows)
    for t in ticks:
        x = left + t * scale
        body.append(f'<line x1="{x:.1f}" y1="{top - 6}" x2="{x:.1f}" y2="{base}" stroke="var(--grid)"/>')
        body.append(f'<text x="{x:.1f}" y="{base + 18}" text-anchor="middle" class="muted num">{t * 100:.0f}%</text>')
    body.append(f'<line x1="{left}" y1="{top - 6}" x2="{left}" y2="{base}" stroke="var(--axis)"/>')
    for i, (label, mean, median) in enumerate(rows):
        y = top + i * band + (band - 2 * bar - 2) / 2
        body.append(f'<text x="{left - 12}" y="{y + bar + 5}" text-anchor="end" class="val">{escape(label)}</text>')
        for j, (v, colour, name) in enumerate([(mean, "--s1", "mean"), (median, "--s2", "median")]):
            yy = y + j * (bar + 2)
            body.append(_bar(left, yy, v * scale, bar, colour, f"{label}, {name} hourly gap: {pct(v)}"))
            body.append(f'<text x="{left + v * scale + 6:.1f}" y="{yy + 13}" class="val">{pct(v)}</text>')
    return _svg(W, H, "".join(body), "Gender pay gap by employer, mean and median hourly pay")


def quartile_dumbbell(rows):
    """rows: [(label, share of women in lowest band, share in highest band)]."""
    W, left, right, top = 720, 150, 60, 96
    band = 44
    H = top + band * len(rows) + 50
    lo, hi = 0.2, 0.7
    scale = (W - left - right) / (hi - lo)
    X = lambda v: left + (v - lo) * scale
    headline = ("Women fill the lowest pay band and thin out at the top"
                if all(low > 0.5 > high for _, low, high in rows) else "Women in the lowest and highest pay bands")
    body = [
        f'<text x="24" y="34" class="title">{headline}</text>',
        '<text x="24" y="54" class="sub">Share of women in the lowest and highest quartile pay bands (Article 9(1)(f)).</text>',
        f'<circle cx="{left + 5}" cy="73" r="5" fill="var(--s2)"/><text x="{left + 16}" y="77">Lowest band</text>',
        f'<circle cx="{left + 125}" cy="73" r="5" fill="var(--s1)"/><text x="{left + 136}" y="77">Highest band</text>',
    ]
    base = top + band * len(rows)
    for t in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
        body.append(f'<line x1="{X(t):.1f}" y1="{top - 8}" x2="{X(t):.1f}" y2="{base}" stroke="var(--grid)"/>')
        body.append(f'<text x="{X(t):.1f}" y="{base + 18}" text-anchor="middle" class="muted num">{t * 100:.0f}%</text>')
    x50 = X(0.5)
    body.append(f'<text x="{x50:.1f}" y="{base + 34}" text-anchor="middle" class="muted">parity</text>')
    for i, (label, low, high) in enumerate(rows):
        y = top + i * band + band / 2
        body.append(f'<text x="{left - 12}" y="{y + 4}" text-anchor="end" class="val">{escape(label)}</text>')
        body.append(f'<line x1="{X(high):.1f}" y1="{y}" x2="{X(low):.1f}" y2="{y}" stroke="var(--axis)" stroke-width="2"/>')
        for v, colour, name, anchor, dx in [(high, "--s1", "highest", "end", -10), (low, "--s2", "lowest", "start", 10)]:
            body.append(f'<circle cx="{X(v):.1f}" cy="{y}" r="6" fill="var({colour})" stroke="var(--surface)" '
                        f'stroke-width="2"><title>{escape(label)}: women are {pct(v, 0)} of the {name} band</title></circle>')
            body.append(f'<text x="{X(v) + dx:.1f}" y="{y + 4}" text-anchor="{anchor}" class="val">{pct(v, 0)}</text>')
    return _svg(W, H, "".join(body), "Share of women in the lowest and highest quartile pay bands, by employer")


WORDS = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven",
         "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]


def category_grid(entities, categories, cells, threshold):
    """cells[(entity, category)] = (hourly gap, annual gap, flagged, small cell) or None."""
    flagged_n = sum(1 for c in cells.values() if c and c[2])
    count = WORDS[flagged_n] if flagged_n < len(WORDS) else str(flagged_n)
    W, left, top = 720, 150, 128
    cw = (W - left - 24) / len(categories)
    ch = 44
    H = top + ch * len(entities) + 66
    body = [
        f'<text x="24" y="34" class="title">{count} of {len(cells)} categories need a justification or a remedy</text>',
        f'<text x="24" y="54" class="sub">Mean hourly pay gap by category of workers. Coloured cells: {threshold * 100:.0f}% or more '
        'on hourly or annual pay.</text>',
        f'<rect x="{left}" y="68" width="12" height="12" rx="2" fill="var(--pos)"/>'
        f'<text x="{left + 18}" y="78">Women paid less, at or above {threshold * 100:.0f}%</text>',
        f'<rect x="{left + 250}" y="68" width="12" height="12" rx="2" fill="var(--neg)"/>'
        f'<text x="{left + 268}" y="78">Men paid less, at or above {threshold * 100:.0f}%</text>',
        f'<text x="{left}" y="100" class="muted">† flagged on annual pay only    * fewer than 5 of one sex in the category</text>',
    ]
    for j, cat in enumerate(categories):
        body.append(f'<text x="{left + j * cw + cw / 2:.1f}" y="{top - 8}" text-anchor="middle" class="val">'
                    f'{escape(cat.replace("Cat ", ""))}</text>')
    for i, ent in enumerate(entities):
        y = top + i * ch
        body.append(f'<text x="{left - 12}" y="{y + ch / 2 + 4}" text-anchor="end" class="val">{escape(ent)}</text>')
        for j, cat in enumerate(categories):
            x = left + j * cw
            cell = cells.get((ent, cat))
            if cell is None:
                continue
            hourly, annual, flagged, small = cell
            fill = "--mid"
            if flagged:
                fill = "--pos" if hourly > 0 else "--neg"
            tip = (f"{ent}, category {cat}: hourly gap {pct(hourly)}, annual gap {pct(annual)}"
                   f"{' - justify or remedy' if flagged else ''}{' - fewer than 5 of one sex' if small else ''}")
            body.append(f'<rect x="{x + 1:.1f}" y="{y + 1}" width="{cw - 2:.1f}" height="{ch - 2}" rx="4" '
                        f'fill="var({fill})"><title>{escape(tip)}</title></rect>')
            # Dark ink on the coloured fills clears 4.5:1 in both modes; white would not.
            ink = "#0b0b0b" if flagged else "var(--ink)"
            weight = "600" if flagged else "400"
            annual_only = flagged and abs(hourly) < threshold
            marks = ("†" if annual_only else "") + ("*" if small else "")
            body.append(f'<text x="{x + cw / 2:.1f}" y="{y + ch / 2 + 5}" text-anchor="middle" class="num" '
                        f'style="fill:{ink};font-weight:{weight}">{pct(hourly)}{marks}</text>')
    body.append(f'<text x="24" y="{top + ch * len(entities) + 24}" class="muted">Categories A (fewest points) to G '
                '(most), from the job evaluation. A negative gap means men are paid less.</text>')
    body.append(f'<text x="24" y="{top + ch * len(entities) + 42}" class="muted">† Flagged on annual pay only: '
                f'the hourly gap is below {threshold * 100:.0f}%, so hours worked are the likely driver.</text>')
    return _svg(W, H, "".join(body), "Hourly pay gap by employer and category of workers, with flagged categories")
