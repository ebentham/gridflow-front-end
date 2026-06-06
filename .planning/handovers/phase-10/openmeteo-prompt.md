# Open-Meteo — Claude Design prompt (paste-ready)

**Attach to the Claude Design session:** `authored-pages/entsoe/actual_generation.html` (primary reference) · `authored-pages/openmeteo/forecast_solar.html` (vendor layout example) · the batch's `content-briefs/openmeteo/<slug>.md` files.
**Batch order:** see the master handover (§ Open-Meteo). 6 datasets, 2 groups (Forecast 3 · Historical 3).
**Vendor essentials baked in:** JSON columnar · no auth (free non-commercial) · **dual base-URL** (`archive-api.open-meteo.com` historical vs `api.open-meteo.com` forecast — not a versioning split) · **schemas live in `weather.py` NOT `openmeteo.py`** (`DemandWeather`, `WindWeather`, `SolarWeather`) · three-form naming asymmetry (`open-meteo` vault / `openmeteo` slug / `open_meteo` registry) · ERA5 ~5-day lag · queried per site.

> If Task 00 D-1 = **D-20 (lean)**: delete the `#overview` section, the "OVERVIEW SYNTHESIS RULES" block, and the `#caveats` rendered-section instruction.

--- paste everything below this line into the first message of a fresh Claude Design conversation ---

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one Open-Meteo dataset (an
open weather API — ECMWF/GFS forecasts + ERA5 reanalysis) for full-stack
data-science recruiters in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html — the gold-standard STRUCTURAL
   reference. Mimic its structure, inline <style> block, class names, and layout
   exactly. Take its Overview + Caveats SECTION TREATMENT (not its content).
2. authored-pages/openmeteo/forecast_solar.html — an Open-Meteo layout example
   showing how this vendor's dual-host / hourly-weather content renders. Take
   vendor layout cues from it, but it is the older lean format — defer to reference
   #1 for the Overview/Caveats treatment.
3. One or more content briefs from content-briefs/openmeteo/*.md — your input.

For each brief, produce ONE complete standalone HTML file named <slug>.html that
will be saved to authored-pages/openmeteo/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (Open-Meteo — read before rendering)
═══════════════════════════════════════════════════════════════════════════════
- Open-Meteo is an open-source weather API (Zürich). Aggregates ECMWF/GFS/ICON
  NWP models for forecasts and ERA5 reanalysis for archive. The payload is JSON
  columnar (arrays of hourly values). Free for non-commercial use — NO key.
- DUAL BASE-URL (not a version split): forecast datasets hit
  api.open-meteo.com/v1; historical datasets hit archive-api.open-meteo.com/v1.
  The connector routes per dataset.startswith("historical"). The BASE URL hero
  cell carries both with (forecast)/(archive) qualifiers — render with <br/> and
  font-size:10px.
- Schema classes live in schemas/weather.py (NOT schemas/openmeteo.py — the module
  is named for the domain, for future multi-source weather): DemandWeather,
  WindWeather, SolarWeather (+ _BaseWeather abstract). The Schema table cites
  schemas/weather.py. Silver transformers: forecast.py (ForecastDemandWeather,
  ForecastWindWeather, ForecastSolarWeather) + historical.py (HistoricalDemand/
  Wind/SolarWeather). Render what the brief names.
- Naming asymmetry (three forms, all intentional): vault dir "open-meteo" (hyphen);
  slug + module "openmeteo"; registry key + bronze/silver path "open_meteo". The
  slug in your output is the no-hyphen form (matches the brief's slug:). The live
  API host keeps the hyphen (api.open-meteo.com).
- Data is queried per site: 7 demand locations (London, Birmingham, Manchester,
  Leeds, Glasgow, Cardiff, Belfast), 12 wind sites, 6 solar sites. ERA5 archive
  reaches back to 1940; ~5-day publication lag. ERA5 returns null for 80/120/180m
  wind heights (forecast has them). GTI uses UK geometry tilt=35, azimuth=180.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT
═══════════════════════════════════════════════════════════════════════════════
Every page must contain, in this order:

1. <head>
   - <meta charset="utf-8">
   - <title><slug> · Open-Meteo · Gridflow</title>
   - <meta name="viewport" content="width=1280">  ← desktop-first; do NOT use
     "width=device-width, initial-scale=1"
   - Google Fonts preconnect + Fraunces + Inter + JetBrains Mono link
   - <link rel="stylesheet" href="../../assets/theme.css" />
   - The same <style> block as actual_generation.html (schema-table, data-table,
     code-grid/code-pill, page-layout/sidebar, caveat-item with .discrepancy
     variant, eyebrow-discrepancy, src-cite, related-grid)

2. <body data-page="dataset" data-root="../../" data-screen-label="Open-Meteo · <slug>">

3. Breadcrumb + Hero band (border-bottom: 1px solid var(--rule))
   - .crumbs: Gridflow / Data sources / Open-Meteo / <slug>
   - Two-column grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT  — eyebrow row + chips ("hourly · ~5-day lag" or "hourly · real-time" +
             "Illustrative snapshot")
             <h1 class="display-2"> with mono <slug> on line 1, brief's Tagline on
             line 2 (preserve <span class="italic fg-accent"> wrapper if in brief)
             <p class="lede"> from brief's Lede
             <p class="tiny mt-16"> from brief's Verified line
     RIGHT — 3×2 metadata grid from brief's "Hero metadata" table. The BASE URL /
             API PATH cell carries the dual host — render with <br/> + font-size:10px.

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4, 1fr);">
   4 cells from brief's "Stats strip" table — stat-n value, stat-l label.

5. <div class="container"><div class="page-layout">
     <nav class="sidebar"> with two sections:
       a) "On this page" — anchors to every #section_id you render
       b) "Open-Meteo" — <a href="../openmeteo.html">← All datasets</a> then current
          slug active, then brief's "Sidebar siblings" list with
          style="color:var(--ink-faint);" and href="#"

     <div class="main-content"> — sections in this order:
       #overview   — SYNTHESISED (brief has no # Overview). 3 paragraphs per the
                     synthesis rules below. Eyebrow "Overview" + display-3 "What
                     this dataset is.".
       #snapshot   — chart from "Sample chart" (data-chart, seed from brief).
                     .chart with the brief's toggle chips. Footer "Static snapshot ·
                     live wiring planned" in mono uppercase.
       #schema     — table from brief's "Schema" section + a .card row with
                     PARQUET PATH / PARTITION BY / DEDUP KEY. The intro cites the
                     schemas/weather.py class the brief names (NOT openmeteo.py).
                     Every row cites schemas/weather.py L<n> in <span class="cite">.
       #sample     — .data-table with brief's verbatim rows. Bolded brief row gets
                     outline: 1px solid #3b6b4b. Caption = .tiny from "Sources:".
                     Null cells (e.g. ERA5 80/120/180m wind) → class="nul".
       #api        — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs
                     (Example URL / DuckDB·SQL / Python·polars) with verbatim code.
                     Auth card says "None (public; free non-commercial)".
       #caveats    — eyebrow "Caveats" + display-3 "Things to know before using
                     this." + intro <p class="small"> linking to vendor-wide caveats.
                     Numbered caveat-item 01..NN from brief; last gets the closing
                     border-bottom style.
       #related    — .related-grid from brief's "Related datasets". Cross-vendor
                     card (Elexon fuelhh / windfor, NESO carbon_intensity) gets
                     border:1px solid var(--ink) + "cross-vendor" accent chip.

6. </div></div></div>

7. Scripts: <script src="../../assets/charts.js"></script>
            <script src="../../assets/site.js"></script>
   Then TWO inline scripts verbatim from actual_generation.html
   (IntersectionObserver sidebar active-link + setTab for API tabs).

═══════════════════════════════════════════════════════════════════════════════
OVERVIEW SYNTHESIS RULES (the brief has NO Overview — you compose it)
═══════════════════════════════════════════════════════════════════════════════
Three paragraphs from material that ALREADY exists in the brief — NO new claims,
numbers, or speculation.

Paragraph 1 — WHAT THE DATASET IS (~60-90 words):
  - Open with the slug as styled inline-code (mono, background var(--paper-deep),
    padding 2px 6px, border 1px solid var(--rule)).
  - One-clause definition (paraphrase the Lede); 1-2 sentences of context from the
    Schema preamble / Caveats (forecast vs ERA5 archive, the variable family —
    temperature/wind/solar, the per-site geography).
  - Close with what one row represents (e.g. "Each row is one hour's weather
    variables at one GB site.").

Paragraph 2 — HOW GRIDFLOW INGESTS IT (~60-80 words):
  - "It is sourced from Open-Meteo's {forecast | ERA5 archive} endpoint at
    <code>{host}/v1/{path}</code>, queried per site, ..." Use the correct host:
    api.open-meteo.com for forecast_*, archive-api.open-meteo.com for historical_*.
  - Schema: cite the schemas/weather.py class the brief names
    (<code>DemandWeather</code> / <code>WindWeather</code> / <code>SolarWeather</code>)
    and the transformer (forecast.py / historical.py class from API Card 2). Note
    the module is weather.py, not openmeteo.py, if the brief surfaces it.
  - One sentence on the JSON columnar shape (hourly arrays).

Paragraph 3 — WHY IT MATTERS + VERIFICATION (~50-80 words):
  - One sentence on the role in analytics: the weather driver for demand/
    generation models — ERA5 for multi-year backtest calibration, forecast for
    wind/solar nowcast skill vs Elexon outturn. Draw from the Lede + cross-vendor
    Related (Elexon windfor/fuelhh, NESO carbon_intensity).
  - Close with the brief's Verified line (e.g. "Verified against the Open-Meteo API
    and gridflow connector source on {date}; free public access, no key.").

Hard rules: NO new figures not in the brief; 3 paragraphs only, flowing prose, no
bullets; inline-code styling for slug + host + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING RULES (brief markdown → HTML)
═══════════════════════════════════════════════════════════════════════════════
- "**Tagline:**" → 2nd line of <h1 class="display-2"> (preserve italic fg-accent).
- "**Lede:**" → <p class="lede" style="max-width: 600px;">.
- "**Verified line:**" → <p class="tiny mt-16" style="max-width:600px;">.
- Hero metadata table → 3×2 grid. Dual-host BASE URL cell → <br/> + font-size:10px.
- Stats strip table → 4 cells; numeric → .stat-n; label → .stat-l.
- Sidebar siblings → current slug active; others faint links to "#".
- Schema → render the Schema preamble in the section intro (cite the
  schemas/weather.py class + the forecast.py/historical.py transformer). Every
  column row's citation → <span class="cite">schemas/weather.py L<n></span>.
- Sample data → .data-table; class hints: date/time → "date"; string → "str";
  numeric → "num" (right-aligned); null → "nul" (gray italic, brief's literal —
  e.g. ERA5 wind_speed_120m null).
- Caveats → numbered caveat-item; discrepancy variant only for declared/emitted
  mismatches or cited discrepancies_found.
- Caveat source attribution → <span class="src-cite">…</span>.
- Related grid → 3–4 cards (mono slug + freq chip + arrow, .small desc, .tiny
  "vendor · category · freq"). Cross-vendor card → border 1px solid var(--ink) +
  "cross-vendor" accent chip + href to ../<vendor>/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
CHART TYPES (data-chart attribute values — rendered by ../../assets/charts.js)
═══════════════════════════════════════════════════════════════════════════════
ONLY: sparkline (temperature / irradiance / wind-speed time series — strong daily
diurnal shape), stackedArea (multi-variable or multi-site), barsH (capacity-factor
or variable ranking), priceLadder (rare). Use the brief's "Sample chart" type +
seed; fall back sparkline/stackedArea. Don't invent chart kinds.

═══════════════════════════════════════════════════════════════════════════════
AUTH & SCHEMA HANDLING (Open-Meteo specifics)
═══════════════════════════════════════════════════════════════════════════════
- Open-Meteo is PUBLIC, no key (free non-commercial). Auth card says so. No banner.
- Schemas live in schemas/weather.py — cite that module, NEVER schemas/openmeteo.py.
- Use the correct host per dataset family (forecast vs archive). If a brief flags
  the dual-host or the naming asymmetry as a caveat, render it; do not editorialise
  beyond the brief.
- ERA5 null heights (80/120/180m wind) and GTI geometry (tilt=35, azimuth=180) are
  real — preserve from the brief; render null sample cells as class="nul".

═══════════════════════════════════════════════════════════════════════════════
ANTI-GOALS (do NOT do these)
═══════════════════════════════════════════════════════════════════════════════
- No "live" indicators / "X min ago" / uptime badges / KPI tiles.
- No "Get API key →" / SaaS CTAs; no author photos / testimonials / hire-me chips.
- No emojis. No <meta name="viewport" content="width=device-width, initial-scale=1">.
- No invented Sample-data numbers, citations, or codelist sections.
- No citing schemas/openmeteo.py (it does not exist — the module is weather.py).
- No 5th tab or extra cards beyond the brief.

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
Per brief: a complete standalone HTML doc (DOCTYPE → </html>) in an `html` code
fence, filename <slug>.html matching the brief's slug, one-line header
`--- <slug>.html ---` above each block; after all blocks, list any you couldn't
render and why.

═══════════════════════════════════════════════════════════════════════════════
FINAL CHECK before returning (per HTML block)
═══════════════════════════════════════════════════════════════════════════════
  [ ] data-page / data-root="../../" / data-screen-label="Open-Meteo · <slug>"
  [ ] Sidebar anchors match real section ids
  [ ] Every schema row cites schemas/weather.py L<n> (never openmeteo.py)
  [ ] Correct host per family (forecast vs archive) in API + Overview
  [ ] Sample rows verbatim; null cells rendered as the brief's literal
  [ ] No emojis, no live wording, no fake timestamps
  [ ] Both inline scripts present at end
  [ ] All asset paths ../../assets/theme.css | charts.js | site.js
```
