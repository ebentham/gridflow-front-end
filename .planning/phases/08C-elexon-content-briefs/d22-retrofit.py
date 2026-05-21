"""D-22 retrofit: inject Overview section + update chart data-opts + sidebar nav.

Run once. Reads each Elexon brief, extracts # Overview content + # Sample chart
Shape/Params/Items, edits the corresponding authored-pages/elexon/<slug>.html.

Preserves fuelhh.html and system_prices.html (sacred refs) — their #overview
sections already exist and are canonical. Only touches their chart data-opts
if it would meaningfully improve realism; otherwise no-ops on them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end")
BRIEFS_DIR = ROOT / "content-briefs" / "elexon"
PAGES_DIR = ROOT / "authored-pages" / "elexon"

SACRED = {"fuelhh", "system_prices"}

# Per-dataset chart data-opts.
# Format: {"slug": "<json-string-for-data-opts>"} — written verbatim into data-opts='...'.
# barsH entries embed a synthetic plausible `items` array.
CHART_OPTS: dict[str, str] = {
    # ── sparkline (shape-based) ──────────────────────────────────────────
    "atl": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":42000,"trough":26000,"noise":0.04,"seed":13}}',
    "inddem": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":42000,"trough":26000,"noise":0.04,"seed":27}}',
    "indo": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":42000,"trough":26000,"noise":0.04,"seed":11}}',
    "itsdo": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":38000,"trough":22000,"noise":0.04,"seed":19}}',
    "ndf": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":42500,"trough":26500,"noise":0.03,"seed":31}}',
    "ndfd": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":42000,"trough":27000,"noise":0.03,"seed":32}}',
    "tsdf": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":38000,"trough":22000,"noise":0.03,"seed":29}}',
    "tsdfd": '{"width":900,"height":280,"shape":"diurnal-load","params":{"peak":38500,"trough":22500,"noise":0.03,"seed":30}}',
    "melngc": '{"width":900,"height":280,"shape":"flat-baseload","params":{"mean":8500,"noise":0.12,"seed":39}}',
    "imbalngc": '{"width":900,"height":280,"shape":"volatile-spikes","params":{"base":80,"spike_prob":0.06,"spike_height":600,"noise":0.15,"seed":41}}',
    "lolpdrm": '{"width":900,"height":280,"shape":"flat-baseload","params":{"mean":6800,"noise":0.18,"seed":23}}',
    "nonbm": '{"width":900,"height":280,"shape":"volatile-spikes","params":{"base":40,"spike_prob":0.04,"spike_height":350,"noise":0.1,"seed":26}}',
    "freq": '{"width":900,"height":280,"shape":"frequency","params":{"mean":50,"amplitude":0.15,"noise":0.03,"seed":50}}',
    "mid": '{"width":900,"height":280,"shape":"diurnal-price","params":{"base":80,"morning_peak":95,"evening_peak":125,"trough":50,"noise":0.05,"seed":12}}',
    "windfor": '{"width":900,"height":280,"shape":"diurnal-wind","params":{"mean":9500,"volatility":2200,"persistence":0.85,"seed":24}}',
    "indgen": '{"width":900,"height":280,"shape":"flat-baseload","params":{"mean":34000,"noise":0.08,"seed":28}}',
    "temp": '{"width":900,"height":280,"shape":"diurnal-temp","params":{"peak":18,"trough":6,"noise":0.5,"seed":15}}',

    # ── stackedArea (series-based for agpt/agws; default for fuelhh/inst/fou2t14d/uou2t14d) ──
    "agpt": json.dumps({
        "width": 900, "height": 280,
        "series": [
            {"name": "Wind Onshore", "color": "#3b6b4b", "shape": "diurnal-wind", "params": {"mean": 3500, "volatility": 1200, "persistence": 0.75, "seed": 42}},
            {"name": "Wind Offshore", "color": "#5a8aa6", "shape": "diurnal-wind", "params": {"mean": 5200, "volatility": 1500, "persistence": 0.78, "seed": 43}},
            {"name": "Solar", "color": "#d4a73a", "shape": "diurnal-solar", "params": {"peak": 3800, "peak_hour": 12.5, "half_width": 5}},
            {"name": "Biomass", "color": "#c9a96e", "shape": "flat-baseload", "params": {"mean": 2200, "noise": 0.04}},
            {"name": "Pumped Storage", "color": "#86627d", "shape": "bipolar-flow", "params": {"amplitude": 900, "period": 12, "noise": 0.2}},
        ],
    }, separators=(",", ":")),
    "agws": json.dumps({
        "width": 900, "height": 280,
        "series": [
            {"name": "Wind Onshore", "color": "#3b6b4b", "shape": "diurnal-wind", "params": {"mean": 3500, "volatility": 1200, "persistence": 0.75, "seed": 21}},
            {"name": "Wind Offshore", "color": "#5a8aa6", "shape": "diurnal-wind", "params": {"mean": 5200, "volatility": 1500, "persistence": 0.78, "seed": 22}},
            {"name": "Solar", "color": "#d4a73a", "shape": "diurnal-solar", "params": {"peak": 3800, "peak_hour": 12.5, "half_width": 5}},
        ],
    }, separators=(",", ":")),
    # Sacred + default-fuel-mix stackedArea: keep existing opts intact
    "fuelhh": None,  # sacred, no change
    "fuelinst": None,  # default fuel mix is fine, no change
    "fou2t14d": None,  # default fuel mix is fine
    "uou2t14d": None,  # default fuel mix is fine

    # ── priceLadder (sacred) ──────────────────────────────────────────
    "system_prices": None,  # sacred

    # ── barsH (items arrays) ──────────────────────────────────────────
    "boal": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "T_DRAXX-1", "value": 540, "color": "#c9a96e", "display": "540 MW"},
            {"label": "T_GRAIN-7", "value": 420, "color": "#c45a3a", "display": "420 MW"},
            {"label": "T_PEMB-21", "value": 380, "color": "#c45a3a", "display": "380 MW"},
            {"label": "T_SHBN-1", "value": 305, "color": "#3b6b4b", "display": "305 MW"},
            {"label": "T_FFES-1", "value": 290, "color": "#86627d", "display": "290 MW"},
            {"label": "T_DINO-1", "value": 245, "color": "#86627d", "display": "245 MW"},
            {"label": "T_KEAD-2", "value": 220, "color": "#c45a3a", "display": "220 MW"},
            {"label": "T_HRTL-1", "value": 195, "color": "#c45a3a", "display": "195 MW"},
            {"label": "T_RCBKO-1", "value": 165, "color": "#3b6b4b", "display": "165 MW"},
            {"label": "T_WLNYO-3", "value": 140, "color": "#3b6b4b", "display": "140 MW"},
        ],
    }, separators=(",", ":")),
    "disbsad": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "STOR", "value": 1820000, "color": "#3b6b4b", "display": "£1.82M"},
            {"label": "Constraint", "value": 1240000, "color": "#c45a3a", "display": "£1.24M"},
            {"label": "Response", "value": 880000, "color": "#86627d", "display": "£0.88M"},
            {"label": "Reserve (BM)", "value": 620000, "color": "#c9a96e", "display": "£0.62M"},
            {"label": "Black start", "value": 410000, "color": "#5a8aa6", "display": "£0.41M"},
            {"label": "Footroom", "value": 310000, "color": "#5a5e5f", "display": "£0.31M"},
        ],
    }, separators=(",", ":")),
    "netbsad": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "30 Apr", "value": 18.4, "color": "#3b6b4b", "display": "£18.4"},
            {"label": "29 Apr", "value": 14.1, "color": "#3b6b4b", "display": "£14.1"},
            {"label": "28 Apr", "value": 12.7, "color": "#3b6b4b", "display": "£12.7"},
            {"label": "27 Apr", "value": 21.3, "color": "#c45a3a", "display": "£21.3"},
            {"label": "26 Apr", "value": 9.8, "color": "#3b6b4b", "display": "£9.8"},
            {"label": "25 Apr", "value": 16.5, "color": "#3b6b4b", "display": "£16.5"},
            {"label": "24 Apr", "value": 22.9, "color": "#c45a3a", "display": "£22.9"},
            {"label": "23 Apr", "value": 11.4, "color": "#3b6b4b", "display": "£11.4"},
            {"label": "22 Apr", "value": 28.6, "color": "#c45a3a", "display": "£28.6"},
            {"label": "21 Apr", "value": 13.2, "color": "#3b6b4b", "display": "£13.2"},
        ],
    }, separators=(",", ":")),
    "pn": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "T_DRAXX-1", "value": 295, "color": "#c9a96e", "display": "295 MW"},
            {"label": "T_GRAIN-7", "value": 240, "color": "#c45a3a", "display": "240 MW"},
            {"label": "T_PEMB-21", "value": 215, "color": "#c45a3a", "display": "215 MW"},
            {"label": "T_HEYM-1", "value": 195, "color": "#86627d", "display": "195 MW"},
            {"label": "T_FFES-1", "value": 175, "color": "#86627d", "display": "175 MW"},
            {"label": "T_KEAD-2", "value": 160, "color": "#c45a3a", "display": "160 MW"},
            {"label": "T_HRTL-1", "value": 145, "color": "#c45a3a", "display": "145 MW"},
            {"label": "T_SHBN-1", "value": 135, "color": "#3b6b4b", "display": "135 MW"},
            {"label": "T_RCBKO-1", "value": 125, "color": "#3b6b4b", "display": "125 MW"},
            {"label": "T_WLNYO-3", "value": 115, "color": "#3b6b4b", "display": "115 MW"},
            {"label": "T_DINO-1", "value": 105, "color": "#86627d", "display": "105 MW"},
            {"label": "T_GANN-21", "value": 95, "color": "#3b6b4b", "display": "95 MW"},
            {"label": "T_TKNEW-1", "value": 80, "color": "#3b6b4b", "display": "80 MW"},
            {"label": "T_HUMR-1", "value": 70, "color": "#3b6b4b", "display": "70 MW"},
            {"label": "T_BLLA-3", "value": 60, "color": "#3b6b4b", "display": "60 MW"},
        ],
    }, separators=(",", ":")),
    "market_depth": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "30 Apr", "value": 18400, "color": "#3b6b4b", "display": "18.4 GWh"},
            {"label": "29 Apr", "value": 16200, "color": "#3b6b4b", "display": "16.2 GWh"},
            {"label": "28 Apr", "value": 15800, "color": "#3b6b4b", "display": "15.8 GWh"},
            {"label": "27 Apr", "value": 21500, "color": "#c45a3a", "display": "21.5 GWh"},
            {"label": "26 Apr", "value": 14600, "color": "#3b6b4b", "display": "14.6 GWh"},
            {"label": "25 Apr", "value": 17900, "color": "#3b6b4b", "display": "17.9 GWh"},
            {"label": "24 Apr", "value": 23100, "color": "#c45a3a", "display": "23.1 GWh"},
            {"label": "23 Apr", "value": 16800, "color": "#3b6b4b", "display": "16.8 GWh"},
            {"label": "22 Apr", "value": 26400, "color": "#c45a3a", "display": "26.4 GWh"},
            {"label": "21 Apr", "value": 15300, "color": "#3b6b4b", "display": "15.3 GWh"},
        ],
    }, separators=(",", ":")),
    "bmunits_reference": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "CCGT", "value": 92, "color": "#c45a3a", "display": "92 units"},
            {"label": "Wind", "value": 168, "color": "#3b6b4b", "display": "168 units"},
            {"label": "Solar", "value": 24, "color": "#d4a73a", "display": "24 units"},
            {"label": "Nuclear", "value": 16, "color": "#86627d", "display": "16 units"},
            {"label": "Biomass", "value": 12, "color": "#c9a96e", "display": "12 units"},
            {"label": "OCGT", "value": 41, "color": "#c45a3a", "display": "41 units"},
            {"label": "Pumped storage", "value": 9, "color": "#86627d", "display": "9 units"},
            {"label": "Hydro", "value": 28, "color": "#5a8aa6", "display": "28 units"},
            {"label": "Storage (BESS)", "value": 86, "color": "#5a5e5f", "display": "86 units"},
            {"label": "Interconnector", "value": 8, "color": "#5a8aa6", "display": "8 units"},
        ],
    }, separators=(",", ":")),
    "soso": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "IFA (France)", "value": 92000, "color": "#c45a3a", "display": "92 GWh"},
            {"label": "ElecLink (France)", "value": 64000, "color": "#c45a3a", "display": "64 GWh"},
            {"label": "BritNed (NL)", "value": 58000, "color": "#5a8aa6", "display": "58 GWh"},
            {"label": "NSL (Norway)", "value": 51000, "color": "#86627d", "display": "51 GWh"},
            {"label": "Viking Link (DK)", "value": 47000, "color": "#86627d", "display": "47 GWh"},
            {"label": "Moyle (NI)", "value": 18000, "color": "#3b6b4b", "display": "18 GWh"},
            {"label": "EWIC (IRE)", "value": 22000, "color": "#3b6b4b", "display": "22 GWh"},
            {"label": "Greenlink (IRE)", "value": 14000, "color": "#3b6b4b", "display": "14 GWh"},
        ],
    }, separators=(",", ":")),
    "remit": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "Nuclear", "value": 1820, "color": "#86627d", "display": "1820 MW"},
            {"label": "CCGT", "value": 1240, "color": "#c45a3a", "display": "1240 MW"},
            {"label": "Coal", "value": 0, "color": "#5a5e5f", "display": "0 MW"},
            {"label": "Wind", "value": 410, "color": "#3b6b4b", "display": "410 MW"},
            {"label": "Interconnector", "value": 720, "color": "#5a8aa6", "display": "720 MW"},
            {"label": "OCGT", "value": 180, "color": "#c45a3a", "display": "180 MW"},
            {"label": "Biomass", "value": 290, "color": "#c9a96e", "display": "290 MW"},
            {"label": "Hydro / pumped", "value": 130, "color": "#5a8aa6", "display": "130 MW"},
        ],
    }, separators=(",", ":")),
    "indod": json.dumps({
        "width": 900, "height": 280,
        "items": [
            {"label": "30 Apr", "value": 41200, "color": "#3b6b4b", "display": "41.2 GW"},
            {"label": "29 Apr", "value": 40800, "color": "#3b6b4b", "display": "40.8 GW"},
            {"label": "28 Apr", "value": 39600, "color": "#3b6b4b", "display": "39.6 GW"},
            {"label": "27 Apr", "value": 38200, "color": "#3b6b4b", "display": "38.2 GW"},
            {"label": "26 Apr", "value": 35400, "color": "#3b6b4b", "display": "35.4 GW"},
            {"label": "25 Apr", "value": 36100, "color": "#3b6b4b", "display": "36.1 GW"},
            {"label": "24 Apr", "value": 40300, "color": "#3b6b4b", "display": "40.3 GW"},
            {"label": "23 Apr", "value": 41100, "color": "#3b6b4b", "display": "41.1 GW"},
            {"label": "22 Apr", "value": 40600, "color": "#3b6b4b", "display": "40.6 GW"},
            {"label": "21 Apr", "value": 39900, "color": "#3b6b4b", "display": "39.9 GW"},
        ],
    }, separators=(",", ":")),
}


def parse_brief_overview(brief_path: Path) -> tuple[str, str, str]:
    """Extract 3 Overview paragraphs from a brief. Returns (p1, p2, p3) raw markdown."""
    text = brief_path.read_text(encoding="utf-8")
    m = re.search(r"^# Overview\s*\n\n(.*?)\n\n# ", text, re.DOTALL | re.MULTILINE)
    if not m:
        raise ValueError(f"No # Overview section in {brief_path}")
    body = m.group(1)
    # split into paragraphs by "^N. " markers (1. 2. 3.)
    parts = re.split(r"\n\n(?=\d+\.)", body)
    if len(parts) != 3:
        raise ValueError(f"Expected 3 Overview paragraphs in {brief_path}, got {len(parts)}")
    # strip the leading "N. " from each
    out = []
    for p in parts:
        p = re.sub(r"^\d+\.\s+", "", p.strip())
        out.append(p)
    return tuple(out)


def render_overview_html(slug: str, p1: str, p2: str, p3: str) -> str:
    """Render the # Overview section as HTML, matching the sacred fuelhh.html pattern.

    Markdown-to-HTML: <code>...</code> stays as-is (already inline HTML in briefs);
    we just wrap into <p> tags.
    """
    return f'''      <!-- ── Overview ── -->
      <section id="overview" style="padding-top:8px;margin-bottom:48px" data-screen-label="Overview">
        <div class="eyebrow mb-8">Overview</div>
        <h2 class="display-3 mb-24">What this dataset is.</h2>
        <p style="max-width:680px;font-size:15px;line-height:1.65;margin-bottom:16px">{p1}</p>
        <p style="max-width:680px;font-size:15px;line-height:1.65;margin-bottom:16px">{p2}</p>
        <p style="max-width:680px;font-size:15px;line-height:1.65">{p3}</p>
      </section>

'''


def process_page(slug: str) -> str:
    """Edit authored-pages/elexon/<slug>.html with Overview + chart-opts + nav updates.

    Returns a 1-line summary of what was done.
    """
    page_path = PAGES_DIR / f"{slug}.html"
    brief_path = BRIEFS_DIR / f"{slug}.md"
    if not page_path.exists() or not brief_path.exists():
        return f"SKIP {slug}: missing file"

    html = page_path.read_text(encoding="utf-8")
    orig = html
    changes: list[str] = []

    # ── 1. Chart data-opts update ──
    new_opts = CHART_OPTS.get(slug)
    if new_opts is not None:
        # Find the chart line and replace data-opts. Anchor on data-chart="..." to be safe.
        # Pattern: <div data-chart="X" data-opts='...'>
        pat = re.compile(r"(<div data-chart=\"[^\"]+\" data-opts=)'[^']*'", re.DOTALL)
        n_repl = 0
        new_html, n_repl = pat.subn(lambda m: m.group(1) + "'" + new_opts + "'", html, count=1)
        if n_repl == 1:
            html = new_html
            changes.append("chart-opts")
        else:
            changes.append(f"chart-opts:NOT-FOUND")

    # ── 2. For sacred refs: stop here (don't touch overview section or sidebar) ──
    if slug in SACRED:
        if html != orig:
            page_path.write_text(html, encoding="utf-8")
        return f"OK {slug} (sacred): {', '.join(changes) or 'no-op'}"

    # ── 3. Sidebar nav update: add #overview as the new active link ──
    # Find: <a href="#snapshot" class="active">Snapshot chart</a>
    # Replace with: <a href="#overview" class="active">Overview</a><a href="#snapshot">Snapshot chart</a>
    nav_pat = re.compile(r'<a href="#snapshot" class="active">Snapshot chart</a>')
    if nav_pat.search(html):
        html = nav_pat.sub(
            '<a href="#overview" class="active">Overview</a><a href="#snapshot">Snapshot chart</a>',
            html, count=1,
        )
        changes.append("sidebar-nav")
    else:
        changes.append("sidebar-nav:NOT-FOUND")

    # ── 4. Inject the Overview <section> just before <section id="snapshot"> ──
    # Anchor on the snapshot section start (with its specific class+attrs):
    overview_pat = re.compile(r'(\s*)<section id="snapshot"', re.MULTILINE)
    m = overview_pat.search(html)
    if m:
        p1, p2, p3 = parse_brief_overview(brief_path)
        overview_html = render_overview_html(slug, p1, p2, p3)
        # Insert overview_html before the matched whitespace + "<section id=\"snapshot\""
        # The original is "\n      <section id=\"snapshot\"" — keep that indentation; prepend overview as a sibling.
        insertion_point = m.start()
        # Use the same leading whitespace by detecting what comes before
        # The simplest robust approach: insert before the start of the snapshot section
        html = html[:insertion_point] + "\n" + overview_html + html[m.start(1) + len(m.group(1)):]
        changes.append("overview-section")
    else:
        changes.append("overview-section:NOT-FOUND")

    if html != orig:
        page_path.write_text(html, encoding="utf-8")
    return f"OK {slug}: {', '.join(changes)}"


def main() -> None:
    slugs = sorted(p.stem for p in BRIEFS_DIR.glob("*.md"))
    for slug in slugs:
        result = process_page(slug)
        print(result)


if __name__ == "__main__":
    main()
