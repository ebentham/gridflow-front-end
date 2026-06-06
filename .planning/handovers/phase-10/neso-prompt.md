# NESO — Claude Design prompt (paste-ready)

**Attach to the Claude Design session:** `authored-pages/entsoe/actual_generation.html` (primary reference) · `authored-pages/neso/carbon_intensity.html` (vendor layout example) · the batch's `content-briefs/neso/<slug>.md` files.
**Batch order:** see the master handover (§ NESO). 33 datasets, 4 groups (Carbon Intensity National 10 · Statistics 2 · Generation Mix 3 · Regional 18).
**Vendor essentials baked in:** JSON REST · no auth (`Accept: application/json` only) · 30-min settlement · gCO₂/kWh · **schemas exist** (`schemas/neso.py`) **but transformers are dynamically generated** (`register_neso_transformers()`) · Generation-Mix + Regional carry a vendor `beta` flag · queried per settlement-period / date / region-id / postcode.

> If Task 00 D-1 = **D-20 (lean)**: delete the `#overview` section, the "OVERVIEW SYNTHESIS RULES" block, and the `#caveats` rendered-section instruction.

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
2. authored-pages/neso/carbon_intensity.html — a NESO layout example showing how
   this vendor's gCO2/kWh / settlement-period content renders. Take vendor layout
   cues from it, but it is the older lean format — defer to reference #1 for the
   Overview/Caveats treatment.
3. One or more content briefs from content-briefs/neso/*.md — your input.

For each brief, produce ONE complete standalone HTML file named <slug>.html that
will be saved to authored-pages/neso/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (NESO — read before rendering)
═══════════════════════════════════════════════════════════════════════════════
- NESO is the National Energy System Operator (formerly National Grid ESO). Its
  Carbon Intensity API (api.carbonintensity.org.uk) is a public JSON REST API —
  NO authentication, only an `Accept: application/json` header. Built with the
  Environmental Defense Fund Europe + University of Oxford.
- Reporting unit is gCO2/kWh on a 30-minute settlement grid (UTC). The
  IntensityIndex categorical is one of: "very low" / "low" / "moderate" / "high" /
  "very high".
- Schema classes EXIST in schemas/neso.py: CarbonIntensity (all intensity_*),
  CarbonIntensityStats (intensity_stats*), CarbonIntensityFactor (intensity_
  factors), GenerationMix (generation*), RegionalIntensity (regional_*). The
  Schema table cites these classes. BUT the silver transformers are DYNAMICALLY
  GENERATED at import time by register_neso_transformers() (silver/neso/
  carbon_intensity.py) — they are real registered classes, not static. Each
  brief's Schema preamble names both; render what the brief says.
- Data is queried per settlement-period / date / region-id / postcode depending on
  the endpoint family.
- The "Generation Mix - National" and "Carbon Intensity - Regional" categories
  carry a vendor "beta" flag (visible in endpoint category strings). If a brief's
  caveat notes this, render it.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT
═══════════════════════════════════════════════════════════════════════════════
Every page must contain, in this order:

1. <head>
   - <meta charset="utf-8">
   - <title><slug> · NESO Carbon Intensity · Gridflow</title>
   - <meta name="viewport" content="width=1280">  ← desktop-first; do NOT use
     "width=device-width, initial-scale=1"
   - Google Fonts preconnect + Fraunces + Inter + JetBrains Mono link
   - <link rel="stylesheet" href="../../assets/theme.css" />
   - The same <style> block as actual_generation.html (schema-table, data-table,
     code-grid/code-pill, page-layout/sidebar, caveat-item with .discrepancy
     variant, eyebrow-discrepancy, src-cite, related-grid)

2. <body data-page="dataset" data-root="../../" data-screen-label="NESO · <slug>">

3. Breadcrumb + Hero band (border-bottom: 1px solid var(--rule))
   - .crumbs: Gridflow / Data sources / NESO Carbon Intensity / <slug>
   - Two-column grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT  — eyebrow row + chips ("30 min · ~0 lag" + "Illustrative snapshot")
             <h1 class="display-2"> with mono <slug> on line 1, brief's Tagline on
             line 2 (preserve <span class="italic fg-accent"> wrapper if in brief)
             <p class="lede"> from brief's Lede
             <p class="tiny mt-16"> from brief's Verified line
     RIGHT — 3×2 metadata grid from brief's "Hero metadata" table (6 cells)

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4, 1fr);">
   4 cells from brief's "Stats strip" table — stat-n value, stat-l label.

5. <div class="container"><div class="page-layout">
     <nav class="sidebar"> with two sections:
       a) "On this page" — anchors to every #section_id you render
       b) "NESO Carbon Intensity" — <a href="../neso.html">← All datasets</a> then
          current slug active, then brief's "Sidebar siblings" list with
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
                     schemas/neso.py class the brief names AND notes the transformer
                     is dynamically generated via register_neso_transformers().
                     Every row cites schemas/neso.py L<n> in <span class="cite">.
       #sample     — .data-table with brief's verbatim rows. Bolded brief row gets
                     outline: 1px solid #3b6b4b. Caption = .tiny from "Sources:".
                     Render null cells (e.g. actual_gco2_kwh on forecast-only
                     datasets) as class="nul" with the brief's literal.
       #api        — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs
                     (Example URL / DuckDB·SQL / Python·polars) with verbatim code.
                     Auth card says "None (public; Accept: application/json)".
       #caveats    — eyebrow "Caveats" + display-3 "Things to know before using
                     this." + intro <p class="small"> linking to vendor-wide caveats.
                     Numbered caveat-item 01..NN from brief; last gets the closing
                     border-bottom style.
       #related    — .related-grid from brief's "Related datasets". Cross-vendor
                     card (Elexon fuelhh / system_prices, Open-Meteo historical_
                     demand) gets border:1px solid var(--ink) + "cross-vendor" chip.

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
    Schema preamble / Caveats (forecast-vs-actual, regional granularity, the
    IntensityIndex band, the 30-min settlement grid).
  - Close with what one row represents (e.g. "Each row is one 30-minute settlement
    period's forecast carbon intensity in gCO2/kWh.").

Paragraph 2 — HOW GRIDFLOW INGESTS IT (~60-80 words):
  - "It is sourced from the NESO Carbon Intensity API at <code>{endpoint}</code>,
    queried per {settlement-period | date | region | postcode}, ..."
  - Schema: cite the schemas/neso.py class the brief names (e.g.
    <code>CarbonIntensity</code>), and note "the silver transformer
    (<code>{Transformer}</code>) is generated dynamically at import by
    <code>register_neso_transformers()</code>" (from API Card 2 + the brief's
    Schema preamble).
  - One sentence on the JSON-REST shape (no XML, no pagination quirk).

Paragraph 3 — WHY IT MATTERS + VERIFICATION (~50-80 words):
  - One sentence on the role in analytics: the canonical GB carbon signal for
    marginal-emission-factor work (pair with Elexon fuelhh), carbon-aware load
    shifting, weather-driven carbon attribution (Open-Meteo). Draw from the Lede +
    cross-vendor Related.
  - Close with the brief's Verified line (e.g. "Verified against the NESO API and
    gridflow connector source on {date}; NESO is a public no-auth API.").

Hard rules: NO new figures not in the brief; 3 paragraphs only, flowing prose, no
bullets; inline-code styling for slug + endpoint + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING RULES (brief markdown → HTML)
═══════════════════════════════════════════════════════════════════════════════
- "**Tagline:**" → 2nd line of <h1 class="display-2"> (preserve italic fg-accent).
- "**Lede:**" → <p class="lede" style="max-width: 600px;">.
- "**Verified line:**" → <p class="tiny mt-16" style="max-width:600px;">.
- Hero metadata table → 3×2 grid (6 cells). Long mono values → font-size:10px.
- Stats strip table → 4 cells; numeric → .stat-n; label → .stat-l.
- Sidebar siblings → current slug active; others faint links to "#".
- Schema → render the Schema preamble in the section intro (cite the class +
  the dynamic-transformer note). Every column row's citation →
  <span class="cite">schemas/neso.py L<n></span>.
- Sample data → .data-table; class hints: date/time → "date"; string/index → "str";
  numeric → "num" (right-aligned); null → "nul" (gray italic, brief's literal —
  e.g. actual_gco2_kwh null on forecast datasets).
- Caveats → numbered caveat-item; discrepancy variant only for declared/emitted
  mismatches or cited discrepancies_found.
- Caveat source attribution → <span class="src-cite">…</span>.
- Related grid → 3–4 cards (mono slug + freq chip + arrow, .small desc, .tiny
  "vendor · category · freq"). Cross-vendor card → border 1px solid var(--ink) +
  "cross-vendor" accent chip + href to ../<vendor>/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
CHART TYPES (data-chart attribute values — rendered by ../../assets/charts.js)
═══════════════════════════════════════════════════════════════════════════════
ONLY: sparkline (carbon-intensity time series — has a daily/diurnal shape),
stackedArea (generation mix by fuel %), barsH (regional intensity ranking,
emission factors by fuel), priceLadder (rare). Use the brief's "Sample chart"
type + seed; fall back sparkline/stackedArea. Don't invent chart kinds.

═══════════════════════════════════════════════════════════════════════════════
AUTH & SCHEMA HANDLING (NESO specifics)
═══════════════════════════════════════════════════════════════════════════════
- NESO is PUBLIC, no key (Accept: application/json header only). Auth card says so.
  No registration banner.
- Schemas EXIST — cite the schemas/neso.py class the brief names. Always pair the
  class citation with the note that the transformer is dynamically generated
  (register_neso_transformers). Do not present the dynamic generation as a
  schema-absence — the Pydantic class is real.
- If a brief flags the beta status of Generation-Mix / Regional, render it as a
  caveat; do not add a visual "beta" badge.

═══════════════════════════════════════════════════════════════════════════════
ANTI-GOALS (do NOT do these)
═══════════════════════════════════════════════════════════════════════════════
- No "live" indicators / "X min ago" / uptime badges / KPI tiles.
- No "Get API key →" / SaaS CTAs; no author photos / testimonials / hire-me chips.
- No emojis. No <meta name="viewport" content="width=device-width, initial-scale=1">.
- No invented Sample-data numbers, citations, or codelist sections.
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
  [ ] data-page / data-root="../../" / data-screen-label="NESO · <slug>"
  [ ] Sidebar anchors match real section ids
  [ ] Every schema row cites schemas/neso.py L<n>; dynamic-transformer noted
  [ ] Sample rows verbatim; null cells rendered as the brief's literal
  [ ] No emojis, no live wording, no fake timestamps
  [ ] Both inline scripts present at end
  [ ] All asset paths ../../assets/theme.css | charts.js | site.js
```
