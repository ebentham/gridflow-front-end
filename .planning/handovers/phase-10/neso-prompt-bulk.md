# NESO — BULK / resumable Claude Design prompt (paste-ready)

**Attach:** `authored-pages/entsoe/actual_generation.html` (primary D-22 reference) · `authored-pages/neso/carbon_intensity.html` (NESO layout example — gCO₂/kWh cells; older lean D-20 format, so take Overview/Caveats from the primary) · **all 33** `content-briefs/neso/*.md` dataset briefs (NOT `_landing.md`).
**Workflow:** paste prompt → attach all → "Produce all." → say **"continue"** each pause (~6-8 turns for 33 pages) → at `ALL DONE`, export the workspace zip → send it to me.

--- paste everything below this line into the first message of a fresh Claude Design conversation ---

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one NESO Carbon Intensity
dataset (the National Energy System Operator's GB grid carbon-intensity API) for
full-stack data-science recruiters in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html — the gold-standard STRUCTURAL
   reference. Mimic its structure, inline <style> block, class names, and layout
   exactly. Take its Overview + Caveats SECTION TREATMENT (not its content).
2. authored-pages/neso/carbon_intensity.html — a NESO layout example showing the
   vendor's gCO2/kWh / settlement-period content. It is the older lean format —
   match its NESO-specific cells, but follow reference #1 for Overview/Caveats.
3. ALL NESO dataset briefs (content-briefs/neso/*.md) — one page per brief.

═══════════════════════════════════════════════════════════════════════════════
BULK / RESUMABLE MODE  ← read this first
═══════════════════════════════════════════════════════════════════════════════
Produce ONE complete HTML page per attached brief, saved in your workspace as
authored-pages/neso/<slug>.html (<slug> = the brief's `slug:` frontmatter).

- Process briefs in ALPHABETICAL ORDER of slug, deterministically.
- Do NOT produce a _landing.html — the vendor hub is maintained separately.
- You will NOT fit all 33 pages in one response — expected. When within ~2 pages of
  your output limit, STOP at a clean page boundary (NEVER mid-page) and print exactly
  this status block, then wait:

      ───────────────
      STATUS
      done (N of 33): slugA, slugB, ...
      remaining: slugX, slugY, ...
      ───────────────

- When I reply "continue", resume with the FIRST slug in `remaining` and keep going.
- NEVER regenerate a slug already in `done`. NEVER skip a slug. NEVER reorder.
- When `remaining` is empty, finish with a single line:  ALL DONE (33 of 33).
- If a brief is malformed, skip it, keep going, and list it under `could not render:`
  in the final status — do not stop.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (NESO)
═══════════════════════════════════════════════════════════════════════════════
- NESO is the National Energy System Operator (formerly National Grid ESO). Its
  Carbon Intensity API (api.carbonintensity.org.uk) is a PUBLIC JSON REST API — NO
  auth, only an `Accept: application/json` header. The API & ingestion Auth card
  says "None (public; Accept: application/json)". No banner/badge.
- Reporting unit gCO2/kWh on a 30-minute settlement grid (UTC). The IntensityIndex
  categorical is one of: "very low" / "low" / "moderate" / "high" / "very high".
- SCHEMAS EXIST FOR ALL 33 DATASETS — this vendor is NOT schema-absent. Read each
  brief's Schema section; it names one of these schemas/neso.py classes:
    CarbonIntensity        (intensity_* and carbon_intensity)
    CarbonIntensityStats   (intensity_stats, intensity_stats_block)
    CarbonIntensityFactor  (intensity_factors)
    GenerationMix          (generation, generation_current, generation_pt24h)
    RegionalIntensity      (regional_*)
  The schema table CITES the schemas/neso.py class. CRITICAL: the silver transformers
  are GENERATED DYNAMICALLY at import by register_neso_transformers()
  (silver/neso/carbon_intensity.py) — pair the class citation with that note. Do NOT
  present the dynamic generation as schema-absence, and NEVER write "no Pydantic
  class" for a NESO dataset — every NESO dataset has a real Pydantic class.
- Queried per settlement-period / date / region-id / postcode depending on endpoint.
- "Generation Mix" and "Carbon Intensity - Regional" carry a vendor "beta" flag — if
  a brief's caveat notes it, render it; do NOT add a visual "beta" badge.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT (every page, in this order)
═══════════════════════════════════════════════════════════════════════════════
1. <head>: <meta charset="utf-8">; <title><slug> · NESO Carbon Intensity · Gridflow</title>;
   <meta name="viewport" content="width=1280">  (desktop-first — NOT device-width);
   Google Fonts preconnect + Fraunces + Inter + JetBrains Mono; <link rel="stylesheet"
   href="../../assets/theme.css" />; the same inline <style> block as actual_generation.html
   (schema-table, data-table, code-grid/code-pill, page-layout/sidebar, caveat-item +
   .discrepancy, eyebrow-discrepancy, src-cite, related-grid).

2. <body data-page="dataset" data-root="../../" data-screen-label="NESO · <slug>">

3. Breadcrumb + Hero (border-bottom: 1px solid var(--rule)):
   - .crumbs: Gridflow / Data sources / NESO Carbon Intensity / <slug>
   - 2-col grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT: eyebrow + chips ("30 min · ~0 lag" + "Illustrative snapshot");
           <h1 class="display-2"> mono <slug> on line 1, brief Tagline on line 2
           (keep <span class="italic fg-accent"> if present); <p class="lede"> Lede;
           <p class="tiny mt-16"> Verified line.
     RIGHT: 3×2 metadata grid from the brief's "Hero metadata" table (6 cells).

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4,1fr);">
   4 cells from the brief's "Stats strip" table (stat-n value, stat-l label).

5. <div class="container"><div class="page-layout">
     <nav class="sidebar">: (a) "On this page" anchors to every #section you render;
       (b) "NESO Carbon Intensity" → <a href="../neso.html">← All datasets</a>, then
       current slug active, then the brief's "Sidebar siblings" as faint
       style="color:var(--ink-faint);" href="#" links.
     <div class="main-content"> sections in order:
       #overview — SYNTHESISED (brief has no # Overview). 3 paragraphs (rules below).
                   Eyebrow "Overview" + display-3 "What this dataset is.".
       #snapshot — chart from "Sample chart" (data-chart + seed from brief), .chart with
                   the brief's toggle chips, footer "Static snapshot · live wiring planned"
                   in mono uppercase.
       #schema   — table from brief's "Schema" + a .card row PARQUET PATH / PARTITION BY /
                   DEDUP KEY. Intro cites the schemas/neso.py class the brief names AND
                   notes the transformer is dynamically generated via
                   register_neso_transformers(). Every row cites schemas/neso.py L<n> in
                   <span class="cite">.
       #sample   — .data-table, brief's verbatim rows; bolded brief row gets
                   outline: 1px solid #3b6b4b; caption = .tiny from "Sources:". Render
                   null cells (e.g. actual_gco2_kwh on forecast-only datasets) as
                   class="nul" with the brief's literal.
       #api      — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL /
                   DuckDB·SQL / Python·polars) with the brief's verbatim code. Auth card:
                   "None (public; Accept: application/json)".
       #caveats  — eyebrow "Caveats" + display-3 "Things to know before using this." +
                   intro <p class="small"> linking to vendor-wide caveats at
                   <a href="../neso.html#about">…</a>; numbered caveat-item 01..NN from
                   the brief; last gets style="border-bottom:1px solid var(--rule);
                   padding-bottom:16px;".
       #related  — .related-grid (2 cols) from "Related datasets"; cross-vendor card
                   (Elexon fuelhh / system_prices, Open-Meteo historical_demand) gets
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
or Caveats (forecast vs actual, regional granularity, the IntensityIndex band, the
30-min settlement grid); close with what one row represents.
P2 (~60-80w) HOW GRIDFLOW INGESTS IT: "It is sourced from the NESO Carbon Intensity
API at <code>{endpoint}</code>, queried per {settlement-period | date | region |
postcode}, validated against <code>{Class}</code>; the silver transformer
(<code>{Transformer}</code>) is generated dynamically at import by
<code>register_neso_transformers()</code>." Class + endpoint + transformer from the
brief's Schema preamble + API cards. One sentence on the JSON-REST shape.
P3 (~50-80w) WHY IT MATTERS + VERIFICATION: one sentence on the analytics role (the
canonical GB carbon signal for marginal-emission-factor work with Elexon fuelhh,
carbon-aware load shifting, weather-driven carbon attribution with Open-Meteo) from
the Lede + cross-vendor Related; close with the brief's Verified line.
Rules: NO new figures/stats not in the brief; 3 paragraphs, flowing prose, no bullets;
inline-code styling for slug + endpoint + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING + CHART + ANTI-GOALS
═══════════════════════════════════════════════════════════════════════════════
- Tagline → 2nd line of <h1>; Lede → <p class="lede" style="max-width:600px;">;
  Verified line → <p class="tiny mt-16">. Hero table → 3×2 (long mono values 10px).
- Schema citations: cite the schemas/neso.py class the brief names + the dynamic-
  transformer note. Every row → <span class="cite">schemas/neso.py L<n></span>.
  NEVER write "no Pydantic class" — NESO datasets are all typed.
- Sample cells by type: date/time → class="date"; string/index → class="str"; numeric →
  class="num" (right-aligned); null → class="nul" (gray italic, brief's literal — e.g.
  actual_gco2_kwh null on forecast datasets).
- Caveats: discrepancy variant (class="caveat-item discrepancy" + eyebrow-discrepancy)
  only for declared/emitted mismatches or non-empty discrepancies_found.
- CHART TYPES — ONLY: sparkline (carbon-intensity time series — diurnal shape),
  stackedArea (generation mix by fuel %), barsH (regional ranking, emission factors),
  priceLadder (rare). Use the brief's type + seed; fall back sparkline/stackedArea.
  Don't invent kinds.
- ANTI-GOALS: no live indicators / "X min ago" / uptime badges / KPI tiles; no
  "Get API key →" / SaaS CTAs / author photos / testimonials / hire-me chips; no emojis;
  no device-width viewport; no invented sample numbers, citations, or codelist sections;
  no 5th tab or extra cards.

═══════════════════════════════════════════════════════════════════════════════
PER-PAGE OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
For each page: write a one-line header `--- <slug>.html ---`, then a complete standalone
HTML document (DOCTYPE → </html>) in its own code fence labelled `html`, and save it to
authored-pages/neso/<slug>.html in your workspace. Per page, self-check before moving on:
data-root="../../"; sidebar anchors match real section ids; every schema row cites
schemas/neso.py L<n> with the dynamic-transformer note; sample rows verbatim; null cells
rendered as the brief's literal; no emojis; both inline scripts present; asset paths
../../assets/. Then continue to the next slug (or emit the STATUS block if near the limit).
```
