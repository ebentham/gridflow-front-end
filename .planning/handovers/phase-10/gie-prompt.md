# GIE — Claude Design prompt (paste-ready)

**Attach to the Claude Design session:** `authored-pages/entsoe/actual_generation.html` (primary reference) · `authored-pages/gie/storage.html` (vendor layout example) · the batch's `content-briefs/gie/<slug>.md` files.
**Batch order:** see the master handover (§ GIE). 8 datasets, 2 groups (Storage/AGSI 7 · LNG/ALSI 1).
**Vendor essentials baked in:** JSON · **`x-key` header API key** (the only authenticated vendor — free registration) · gas-day 06:00 UTC · **dual-host BASE URL** (`agsi.gie.eu` / `alsi.gie.eu`) · **mixed schema coverage** (`GasStorage` + `LNGTerminal` typed; 5 reference/news datasets dynamic) · queried per country.

> If Task 00 D-1 = **D-20 (lean)**: delete the `#overview` section, the "OVERVIEW SYNTHESIS RULES" block, and the `#caveats` rendered-section instruction.

--- paste everything below this line into the first message of a fresh Claude Design conversation ---

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one GIE dataset (European gas
storage / LNG inventory — Gas Infrastructure Europe's AGSI+ and ALSI platforms)
for full-stack data-science recruiters in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html — the gold-standard STRUCTURAL
   reference. Mimic its structure, inline <style> block, class names, and layout
   exactly. Take its Overview + Caveats SECTION TREATMENT (not its content).
2. authored-pages/gie/storage.html — a GIE layout example showing how this vendor's
   dual-host / gas-day content renders. Take vendor layout cues from it, but it is
   the older lean format — defer to reference #1 for the Overview/Caveats treatment.
3. One or more content briefs from content-briefs/gie/*.md — your input.

For each brief, produce ONE complete standalone HTML file named <slug>.html that
will be saved to authored-pages/gie/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (GIE — read before rendering)
═══════════════════════════════════════════════════════════════════════════════
- GIE (Gas Infrastructure Europe) runs two transparency platforms: AGSI+ (gas
  storage inventory, host agsi.gie.eu) and ALSI (LNG terminal inventory, host
  alsi.gie.eu). One gridflow vendor "gie" covers both as two groups.
- The payload is JSON. GIE is the ONLY vendor in this batch that requires
  authentication: an API key passed as an `x-key` request header (free
  registration at agsi.gie.eu/account). This is NOT a 401-blocking entitlement —
  the data in the briefs is authored from vault; the Auth card simply states the
  x-key requirement. No registration banner or badge.
- Schema coverage is MIXED: storage + storage_reports → GasStorage; lng →
  LNGTerminal (both in schemas/gie.py). The 5 reference/news datasets
  (about_listing, about_summary, news, news_item, unavailability) have NO Pydantic
  class — columns are dynamic via AgsiJsonTransformer (silver/gie/agsi.py). Read
  each brief's Schema preamble: cite the class it names, or the silver path if it
  says "no dedicated schema".
- Data is queried per country: AGSI 9 (AT BE DE ES FR GB IT NL PL), ALSI 8
  (BE ES FR GB IT NL PL PT).
- Gas-day convention: each gas day starts 06:00 UTC (the gasDayStart field), NOT
  midnight. Preserve this from the brief.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT
═══════════════════════════════════════════════════════════════════════════════
Every page must contain, in this order:

1. <head>
   - <meta charset="utf-8">
   - <title><slug> · GIE Storage · Gridflow</title>
   - <meta name="viewport" content="width=1280">  ← desktop-first; do NOT use
     "width=device-width, initial-scale=1"
   - Google Fonts preconnect + Fraunces + Inter + JetBrains Mono link
   - <link rel="stylesheet" href="../../assets/theme.css" />
   - The same <style> block as actual_generation.html (schema-table, data-table,
     code-grid/code-pill, page-layout/sidebar, caveat-item with .discrepancy
     variant, eyebrow-discrepancy, src-cite, related-grid)

2. <body data-page="dataset" data-root="../../" data-screen-label="GIE · <slug>">

3. Breadcrumb + Hero band (border-bottom: 1px solid var(--rule))
   - .crumbs: Gridflow / Data sources / GIE Storage / <slug>
   - Two-column grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT  — eyebrow row + chips ("daily · gas-day" + "Illustrative snapshot")
             <h1 class="display-2"> with mono <slug> on line 1, brief's Tagline on
             line 2 (preserve <span class="italic fg-accent"> wrapper if in brief)
             <p class="lede"> from brief's Lede
             <p class="tiny mt-16"> from brief's Verified line
     RIGHT — 3×2 metadata grid from brief's "Hero metadata" table. NOTE: the BASE
             URL / API PATH cell may carry two hosts (agsi.gie.eu / alsi.gie.eu) —
             render with <br/> and font-size:10px.

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4, 1fr);">
   4 cells from brief's "Stats strip" table — stat-n value, stat-l label.

5. <div class="container"><div class="page-layout">
     <nav class="sidebar"> with two sections:
       a) "On this page" — anchors to every #section_id you render
       b) "GIE Storage" — <a href="../gie.html">← All datasets</a> then current
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
                     PARQUET PATH / PARTITION BY / DEDUP KEY. If the brief names a
                     Pydantic class (GasStorage / LNGTerminal), the intro cites it;
                     if it says "no dedicated schema", the intro states columns are
                     dynamic via AgsiJsonTransformer and every row cites a
                     silver/gie/*.py path.
       #sample     — .data-table with brief's verbatim rows. Bolded brief row gets
                     outline: 1px solid #3b6b4b. Caption = .tiny from "Sources:".
       #api        — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs
                     (Example URL / DuckDB·SQL / Python·polars) with verbatim code.
                     The Auth card states the x-key header requirement.
       #caveats    — eyebrow "Caveats" + display-3 "Things to know before using
                     this." + intro <p class="small"> linking to vendor-wide caveats.
                     Numbered caveat-item 01..NN from brief; last gets the closing
                     border-bottom style.
       #related    — .related-grid from brief's "Related datasets". Cross-vendor
                     card (ENTSO-G aggregated_physical_flows, Elexon fuelhh) gets
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
    Schema preamble or Caveats (e.g. % full vs 5-year benchmark; gas-day grain).
  - Close with what one row represents (e.g. "Each row is one country's gas-in-
    storage and net withdrawal for a single gas day.").

Paragraph 2 — HOW GRIDFLOW INGESTS IT (~60-80 words):
  - "It is sourced from GIE's {AGSI+|ALSI} platform at <code>{host}/api</code>,
    queried per country with an <code>x-key</code> header, ..."
  - Schema: if the brief names GasStorage / LNGTerminal, cite it; otherwise
    "with no dedicated Pydantic class — columns are derived dynamically by
    <code>AgsiJsonTransformer</code>". Name the transformer from API Card 2.
  - Mention the gas-day grain (06:00 UTC) once.

Paragraph 3 — WHY IT MATTERS + VERIFICATION (~50-80 words):
  - One sentence on the role in analytics: storage % full is the structural
    gas-tightness signal for the Oct–Mar withdrawal season; pair with ENTSO-G
    nominations + Elexon CCGT. Draw from the Lede and cross-vendor Related.
  - Close with the brief's Verified line (e.g. "Schema verified against gridflow
    connector source on {date}; GIE requires a free x-key registration for live
    access.").

Hard rules: NO new figures not in the brief; 3 paragraphs only, flowing prose, no
bullets; inline-code styling for slug + host + transformer/class names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING RULES (brief markdown → HTML)
═══════════════════════════════════════════════════════════════════════════════
- "**Tagline:**" → 2nd line of <h1 class="display-2"> (preserve italic fg-accent).
- "**Lede:**" → <p class="lede" style="max-width: 600px;">.
- "**Verified line:**" → <p class="tiny mt-16" style="max-width:600px;">.
- Hero metadata table → 3×2 grid. Dual-host cell → <br/> + font-size:10px.
- Stats strip table → 4 cells; numeric → .stat-n; label → .stat-l.
- Sidebar siblings → current slug active; others faint links to "#".
- Schema → render the Schema preamble in the section intro. Every column row's
  citation → <span class="cite">{class or silver path}</span>. Cite GasStorage /
  LNGTerminal where the brief names them; cite silver/gie/agsi.py for the dynamic
  reference/news datasets. DO NOT invent a class the brief doesn't name.
- Sample data → .data-table; class hints: date/time → "date"; string → "str";
  numeric → "num" (right-aligned); null/empty → "nul" (gray italic, literal text).
- Caveats → numbered caveat-item; discrepancy variant only for declared/emitted
  mismatches or non-empty discrepancies_found cited by that caveat.
- Caveat source attribution → <span class="src-cite">…</span>.
- Related grid → 3–4 cards (mono slug + freq chip + arrow, .small desc, .tiny
  "vendor · category · freq"). Cross-vendor card → border 1px solid var(--ink) +
  "cross-vendor" accent chip + href to ../<vendor>/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
CHART TYPES (data-chart attribute values — rendered by ../../assets/charts.js)
═══════════════════════════════════════════════════════════════════════════════
ONLY: sparkline (storage % full over a season, net withdrawal), stackedArea
(storage by country), barsH (capacity / inventory by country), priceLadder (rare).
Use the brief's "Sample chart" type + seed; fall back sparkline/stackedArea.
Don't invent chart kinds.

═══════════════════════════════════════════════════════════════════════════════
AUTH & SCHEMA HANDLING (GIE specifics)
═══════════════════════════════════════════════════════════════════════════════
- GIE requires an `x-key` header API key (free registration). The API & ingestion
  Auth card states this. There is NO 401 banner / badge — keep editorial tone.
- Mixed schema coverage: cite GasStorage (storage, storage_reports) and LNGTerminal
  (lng) where named; for the 5 reference/news datasets use the dynamic-derivation
  wording and cite silver/gie/agsi.py. Never invent a class.
- The two COMING_SOON build stubs (gie_agsi + gie_alsi) merge into one gie hub —
  if a brief's caveat mentions this, render it; otherwise ignore (it's a build
  concern, not a page concern).

═══════════════════════════════════════════════════════════════════════════════
ANTI-GOALS (do NOT do these)
═══════════════════════════════════════════════════════════════════════════════
- No "live" indicators / "X min ago" / uptime badges / KPI tiles.
- No "Get API key →" / SaaS CTAs; no author photos / testimonials / hire-me chips.
- No emojis. No <meta name="viewport" content="width=device-width, initial-scale=1">.
- No invented Sample-data numbers, citations, schema classes, or codelist sections.
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
  [ ] data-page / data-root="../../" / data-screen-label="GIE · <slug>"
  [ ] Sidebar anchors match real section ids
  [ ] Every schema row cites a class or silver path (no invented class)
  [ ] Sample rows verbatim; gas-day + x-key facts preserved
  [ ] No emojis, no live wording, no fake timestamps
  [ ] Both inline scripts present at end
  [ ] All asset paths ../../assets/theme.css | charts.js | site.js
```
