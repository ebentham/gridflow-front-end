# Open-Meteo — BULK / resumable Claude Design prompt (paste-ready)

**Attach:** `authored-pages/entsoe/actual_generation.html` (primary D-22 reference) · `authored-pages/openmeteo/forecast_solar.html` (Open-Meteo layout example — dual-host cell; older lean D-20, so take Overview/Caveats from the primary) · **all 6** `content-briefs/openmeteo/*.md` dataset briefs (NOT `_landing.md`).
**Workflow:** paste prompt → attach all → "Produce all." (6 pages ≈ 1-2 turns) → at `ALL DONE`, export the workspace zip → send it to me.

--- paste everything below this line into the first message of a fresh Claude Design conversation ---

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one Open-Meteo dataset (an open
weather API — ECMWF/GFS forecasts + ERA5 reanalysis) for full-stack data-science
recruiters in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html — the gold-standard STRUCTURAL
   reference. Mimic its structure, inline <style> block, class names, and layout
   exactly. Take its Overview + Caveats SECTION TREATMENT (not its content).
2. authored-pages/openmeteo/forecast_solar.html — an Open-Meteo layout example
   showing the dual-host BASE URL cell and hourly-weather content. It is the older
   lean format — match its vendor-specific cells, but follow reference #1 for the
   Overview/Caveats sections.
3. ALL Open-Meteo dataset briefs (content-briefs/openmeteo/*.md) — one page per brief.

═══════════════════════════════════════════════════════════════════════════════
BULK / RESUMABLE MODE  ← read this first
═══════════════════════════════════════════════════════════════════════════════
Produce ONE complete HTML page per attached brief, saved in your workspace as
authored-pages/openmeteo/<slug>.html (<slug> = the brief's `slug:` frontmatter).

- Process briefs in ALPHABETICAL ORDER of slug, deterministically.
- Do NOT produce a _landing.html — the vendor hub is maintained separately.
- If you reach your output limit before all 6 are done, STOP at a clean page
  boundary (NEVER mid-page) and print exactly this status block, then wait:

      ───────────────
      STATUS
      done (N of 6): slugA, slugB, ...
      remaining: slugX, slugY, ...
      ───────────────

- When I reply "continue", resume with the FIRST slug in `remaining` and keep going.
- NEVER regenerate a slug already in `done`. NEVER skip a slug. NEVER reorder.
- When `remaining` is empty, finish with a single line:  ALL DONE (6 of 6).

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (Open-Meteo)
═══════════════════════════════════════════════════════════════════════════════
- Open-Meteo is an open-source weather API. Payload is JSON columnar (arrays of
  hourly values). Free for non-commercial use — NO key. The Auth card says
  "None (public; free non-commercial)". No banner.
- DUAL BASE-URL (not a version split): forecast datasets use api.open-meteo.com/v1;
  historical datasets use archive-api.open-meteo.com/v1 (ERA5 reanalysis). The
  connector routes per dataset.startswith("historical"). The BASE URL hero cell
  carries both with (forecast)/(archive) qualifiers — render with <br/> + 10px.
- SCHEMA: classes live in schemas/weather.py (NOT schemas/openmeteo.py — the module
  is named for the domain). Read each brief's Schema section; it names one of:
    DemandWeather  (forecast_demand, historical_demand)
    WindWeather    (forecast_wind, historical_wind)
    SolarWeather   (forecast_solar, historical_solar)
  The schema table CITES schemas/weather.py. NEVER cite schemas/openmeteo.py (it does
  not exist). Transformers: forecast.py (Forecast{Demand,Wind,Solar}Weather) /
  historical.py (Historical{Demand,Wind,Solar}Weather).
- Queried per site (7 demand locations, 12 wind, 6 solar). ERA5 archive reaches back
  to 1940 with ~5-day publication lag; ERA5 returns null for 80/120/180m wind heights
  (forecast has them); GTI uses UK geometry tilt=35, azimuth=180. Preserve these from
  the brief.
- Naming: vault dir "open-meteo" (hyphen), slug/module "openmeteo" (no separator),
  registry/path "open_meteo" (snake). The slug in your output is the no-hyphen form;
  the live API host keeps the hyphen (api.open-meteo.com).

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT (every page, in this order)
═══════════════════════════════════════════════════════════════════════════════
1. <head>: <meta charset="utf-8">; <title><slug> · Open-Meteo · Gridflow</title>;
   <meta name="viewport" content="width=1280">  (desktop-first — NOT device-width);
   Google Fonts preconnect + Fraunces + Inter + JetBrains Mono; <link rel="stylesheet"
   href="../../assets/theme.css" />; the same inline <style> block as actual_generation.html
   (schema-table, data-table, code-grid/code-pill, page-layout/sidebar, caveat-item +
   .discrepancy, eyebrow-discrepancy, src-cite, related-grid).

2. <body data-page="dataset" data-root="../../" data-screen-label="Open-Meteo · <slug>">

3. Breadcrumb + Hero (border-bottom: 1px solid var(--rule)):
   - .crumbs: Gridflow / Data sources / Open-Meteo / <slug>
   - 2-col grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT: eyebrow + chips ("hourly · ~5-day lag" or "hourly · real-time" +
           "Illustrative snapshot"); <h1 class="display-2"> mono <slug> line 1, brief
           Tagline line 2 (keep <span class="italic fg-accent"> if present);
           <p class="lede"> Lede; <p class="tiny mt-16"> Verified line.
     RIGHT: 3×2 metadata grid from the brief's "Hero metadata" table (6 cells). The
            dual-host BASE URL / API PATH cell renders with <br/> and font-size:10px.

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4,1fr);">
   4 cells from the brief's "Stats strip" table (stat-n value, stat-l label).

5. <div class="container"><div class="page-layout">
     <nav class="sidebar">: (a) "On this page" anchors to every #section you render;
       (b) "Open-Meteo" → <a href="../openmeteo.html">← All datasets</a>, then current
       slug active, then the brief's "Sidebar siblings" as faint
       style="color:var(--ink-faint);" href="#" links.
     <div class="main-content"> sections in order:
       #overview — SYNTHESISED (brief has no # Overview). 3 paragraphs (rules below).
                   Eyebrow "Overview" + display-3 "What this dataset is.".
       #snapshot — chart from "Sample chart" (data-chart + seed from brief), .chart with
                   the brief's toggle chips, footer "Static snapshot · live wiring planned"
                   in mono uppercase.
       #schema   — table from brief's "Schema" + a .card row PARQUET PATH / PARTITION BY /
                   DEDUP KEY. Intro cites the schemas/weather.py class the brief names
                   (DemandWeather / WindWeather / SolarWeather) + the forecast.py or
                   historical.py transformer. Every row cites schemas/weather.py L<n> in
                   <span class="cite">. NEVER cite schemas/openmeteo.py.
       #sample   — .data-table, brief's verbatim rows; bolded brief row gets
                   outline: 1px solid #3b6b4b; caption = .tiny from "Sources:". Render
                   null cells (e.g. ERA5 wind_speed_120m) as class="nul" with the literal.
       #api      — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL /
                   DuckDB·SQL / Python·polars) with the brief's verbatim code. Use the
                   correct host (api.open-meteo.com for forecast_*, archive-api.open-
                   meteo.com for historical_*). Auth card: "None (public)".
       #caveats  — eyebrow "Caveats" + display-3 "Things to know before using this." +
                   intro <p class="small"> linking to vendor-wide caveats at
                   <a href="../openmeteo.html#about">…</a>; numbered caveat-item 01..NN
                   from the brief; last gets style="border-bottom:1px solid var(--rule);
                   padding-bottom:16px;".
       #related  — .related-grid (2 cols) from "Related datasets"; cross-vendor card
                   (Elexon fuelhh / windfor, NESO carbon_intensity) gets
                   border:1px solid var(--ink) + a "cross-vendor" accent chip,
                   href ../<vendor>/<slug>.html.

6. </div></div></div>

7. <script src="../../assets/charts.js"></script><script src="../../assets/site.js"></script>
   then TWO inline scripts verbatim from actual_generation.html (IntersectionObserver
   sidebar active-link + setTab for API tabs).

═══════════════════════════════════════════════════════════════════════════════
OVERVIEW SYNTHESIS (brief has no Overview — compose 3 paragraphs, no fabrication)
═══════════════════════════════════════════════════════════════════════════════
P1 (~60-90w) WHAT IT IS: open with slug as inline-code (mono, background
var(--paper-deep), padding 2px 6px, border 1px solid var(--rule)); one-clause
definition (paraphrase the Lede); 1-2 sentences of context from the Schema preamble
or Caveats (forecast vs ERA5 archive, the variable family — temperature/wind/solar,
per-site geography); close with what one row represents (one hour at one GB site).
P2 (~60-80w) HOW GRIDFLOW INGESTS IT: "It is sourced from Open-Meteo's {forecast |
ERA5 archive} endpoint at <code>{host}/v1/{path}</code>, queried per site, validated
against <code>{DemandWeather|WindWeather|SolarWeather}</code> (schemas/weather.py),
and written to silver via <code>{Transformer}</code>." Use the correct host per
family. One sentence on the JSON columnar (hourly arrays) shape.
P3 (~50-80w) WHY IT MATTERS + VERIFICATION: one sentence on the analytics role (the
weather driver for demand/generation models — ERA5 for multi-year backtest calibration,
forecast for wind/solar nowcast skill vs Elexon outturn) from the Lede + cross-vendor
Related; close with the brief's Verified line.
Rules: NO new figures/stats not in the brief; 3 paragraphs, flowing prose, no bullets;
inline-code styling for slug + host + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING + CHART + ANTI-GOALS
═══════════════════════════════════════════════════════════════════════════════
- Tagline → 2nd line of <h1>; Lede → <p class="lede" style="max-width:600px;">;
  Verified line → <p class="tiny mt-16">. Hero table → 3×2 (dual-host cell <br/> + 10px).
- Schema citations: schemas/weather.py + the class the brief names. NEVER cite
  schemas/openmeteo.py (does not exist). NEVER invent a class.
- Sample cells by type: date/time → class="date"; string → class="str"; numeric →
  class="num" (right-aligned); null → class="nul" (gray italic, brief's literal).
- Caveats: discrepancy variant only for declared/emitted mismatches or non-empty
  discrepancies_found.
- CHART TYPES — use ONLY: sparkline, stackedArea, barsH, priceLadder. Weather series
  are best as sparkline (temperature / irradiance / wind speed over time) or
  stackedArea (multi-variable / multi-height). DO NOT use donut, heatmap, line, area,
  pie, or any other value — charts.js renders ONLY those four. Use the brief's type +
  seed; fall back sparkline.
- ANTI-GOALS: no live indicators / "X min ago" / uptime badges / KPI tiles; no
  "Get API key →" / SaaS CTAs / author photos / testimonials / hire-me chips; no emojis;
  no device-width viewport; no invented sample numbers, citations, schema classes, or
  codelist sections; no 5th tab or extra cards.

═══════════════════════════════════════════════════════════════════════════════
PER-PAGE OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
For each page: write a one-line header `--- <slug>.html ---`, then a complete standalone
HTML document (DOCTYPE → </html>) in its own code fence labelled `html`, and save it to
authored-pages/openmeteo/<slug>.html in your workspace. Per page, self-check before moving
on: data-root="../../"; sidebar anchors match real section ids; schema cites
schemas/weather.py (never openmeteo.py); correct host per family; data-chart is one of the
four allowed types; sample rows verbatim; null cells as the brief's literal; no emojis;
both inline scripts; asset paths ../../assets/. Then continue (or emit STATUS if near limit).
```
