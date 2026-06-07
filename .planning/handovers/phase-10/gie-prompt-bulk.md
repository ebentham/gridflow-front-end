# GIE — BULK / resumable Claude Design prompt (paste-ready)

**Attach:** `authored-pages/entsoe/actual_generation.html` (primary D-22 reference) · `authored-pages/gie/storage.html` (GIE layout example — shows the dual-host BASE URL cell; it is the older lean D-20 format, so take Overview/Caveats from the primary) · **all 8** `content-briefs/gie/*.md` dataset briefs (NOT `_landing.md`).
**Workflow:** paste prompt → attach all → "Produce all." → say **"continue"** if it pauses (8 pages ≈ 1-2 turns) → when it says `ALL DONE`, export the workspace zip → send it to me.

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
2. authored-pages/gie/storage.html — a GIE layout example showing the vendor's
   dual-host BASE URL cell and gas-day content. It is the older lean format — match
   its GIE-specific cells, but follow reference #1 for the Overview/Caveats sections.
3. ALL GIE dataset briefs (content-briefs/gie/*.md) — one page per brief.

═══════════════════════════════════════════════════════════════════════════════
BULK / RESUMABLE MODE  ← read this first
═══════════════════════════════════════════════════════════════════════════════
Produce ONE complete HTML page per attached brief, saved in your workspace as
authored-pages/gie/<slug>.html (<slug> = the brief's `slug:` frontmatter).

- Process briefs in ALPHABETICAL ORDER of slug, deterministically.
- Do NOT produce a _landing.html — the vendor hub is maintained separately.
- If you reach your output limit before all 8 are done, STOP at a clean page
  boundary (NEVER mid-page) and print exactly this status block, then wait:

      ───────────────
      STATUS
      done (N of 8): slugA, slugB, ...
      remaining: slugX, slugY, ...
      ───────────────

- When I reply "continue", resume with the FIRST slug in `remaining` and keep going.
- NEVER regenerate a slug already in `done`. NEVER skip a slug. NEVER reorder.
- When `remaining` is empty, finish with a single line:  ALL DONE (8 of 8).
- If a brief is malformed, skip it, keep going, and list it under `could not render:`
  in the final status — do not stop.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (GIE)
═══════════════════════════════════════════════════════════════════════════════
- GIE runs two platforms: AGSI+ (gas storage, host agsi.gie.eu) and ALSI (LNG
  terminals, host alsi.gie.eu). One gridflow vendor "gie" covers both. Payload is
  JSON.
- AUTH: GIE is the ONE authenticated vendor — an API key passed as an `x-key`
  request header (free registration). The API & ingestion Auth card states the
  x-key requirement. This is NOT a 401-blocking entitlement; do NOT add a banner
  or badge. Keep editorial tone.
- SCHEMA COVERAGE IS PER-DATASET — read each brief's Schema section:
  • storage and storage_reports → GasStorage (schemas/gie.py). Cite it.
  • lng → LNGTerminal (schemas/gie.py). Cite it.
  • about_listing, about_summary, news, news_item, unavailability → NO Pydantic
    class; columns derived dynamically by AgsiJsonTransformer (silver/gie/agsi.py).
    Schema table cites silver/gie/*.py line numbers; Overview P2 uses the
    "no dedicated Pydantic class — columns derived dynamically" wording. NEVER
    invent a schema class for a dataset whose brief says it has none.
- Queried per country (AGSI 9: AT BE DE ES FR GB IT NL PL; ALSI 8: BE ES FR GB IT
  NL PL PT). Gas-day convention: each gas day starts 06:00 UTC (the gasDayStart
  field), not midnight — preserve this from the brief.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT (every page, in this order)
═══════════════════════════════════════════════════════════════════════════════
1. <head>: <meta charset="utf-8">; <title><slug> · GIE Storage · Gridflow</title>;
   <meta name="viewport" content="width=1280">  (desktop-first — NOT device-width);
   Google Fonts preconnect + Fraunces + Inter + JetBrains Mono; <link rel="stylesheet"
   href="../../assets/theme.css" />; the same inline <style> block as actual_generation.html
   (schema-table, data-table, code-grid/code-pill, page-layout/sidebar, caveat-item +
   .discrepancy, eyebrow-discrepancy, src-cite, related-grid).

2. <body data-page="dataset" data-root="../../" data-screen-label="GIE · <slug>">

3. Breadcrumb + Hero (border-bottom: 1px solid var(--rule)):
   - .crumbs: Gridflow / Data sources / GIE Storage / <slug>
   - 2-col grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT: eyebrow + chips ("daily · gas-day" + "Illustrative snapshot");
           <h1 class="display-2"> mono <slug> on line 1, brief Tagline on line 2
           (keep <span class="italic fg-accent"> if present); <p class="lede"> Lede;
           <p class="tiny mt-16"> Verified line.
     RIGHT: 3×2 metadata grid from the brief's "Hero metadata" table (6 cells). The
            BASE URL / API PATH cell may carry two hosts (agsi.gie.eu / alsi.gie.eu) —
            render with <br/> and font-size:10px.

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4,1fr);">
   4 cells from the brief's "Stats strip" table (stat-n value, stat-l label).

5. <div class="container"><div class="page-layout">
     <nav class="sidebar">: (a) "On this page" anchors to every #section you render;
       (b) "GIE Storage" → <a href="../gie.html">← All datasets</a>, then current slug
       active, then the brief's "Sidebar siblings" as faint
       style="color:var(--ink-faint);" href="#" links.
     <div class="main-content"> sections in order:
       #overview — SYNTHESISED (brief has no # Overview). 3 paragraphs (rules below).
                   Eyebrow "Overview" + display-3 "What this dataset is.".
       #snapshot — chart from "Sample chart" (data-chart + seed from brief), .chart with
                   the brief's toggle chips, footer "Static snapshot · live wiring planned"
                   in mono uppercase.
       #schema   — table from brief's "Schema" + a .card row PARQUET PATH / PARTITION BY /
                   DEDUP KEY. Typed datasets cite GasStorage / LNGTerminal. Schema-absent
                   reference/news datasets: intro states "No dedicated Pydantic class —
                   columns derived dynamically by AgsiJsonTransformer"; every row cites a
                   silver/gie/*.py path in <span class="cite">.
       #sample   — .data-table, brief's verbatim rows; bolded brief row gets
                   outline: 1px solid #3b6b4b; caption = .tiny from "Sources:".
       #api      — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL /
                   DuckDB·SQL / Python·polars) with the brief's verbatim code. Auth card
                   states the x-key header requirement.
       #caveats  — eyebrow "Caveats" + display-3 "Things to know before using this." +
                   intro <p class="small"> linking to vendor-wide caveats at
                   <a href="../gie.html#about">…</a>; numbered caveat-item 01..NN from
                   the brief; last gets style="border-bottom:1px solid var(--rule);
                   padding-bottom:16px;".
       #related  — .related-grid (2 cols) from "Related datasets"; cross-vendor card
                   (ENTSO-G aggregated_physical_flows, Elexon fuelhh) gets
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
or Caveats (% full vs 5-year benchmark, gas-day grain, AGSI vs ALSI); close with what
one row represents.
P2 (~60-80w) HOW GRIDFLOW INGESTS IT: "It is sourced from GIE's {AGSI+ | ALSI}
platform at <code>{host}/api</code>, queried per country with an <code>x-key</code>
header, ..." + schema clause: typed → ", validated against <code>GasStorage</code>
(or <code>LNGTerminal</code>)"; schema-absent → ", with no dedicated Pydantic class —
columns are derived dynamically by <code>AgsiJsonTransformer</code>". Name the
transformer from the brief's API Card 2. Mention the gas-day grain (06:00 UTC) once.
P3 (~50-80w) WHY IT MATTERS + VERIFICATION: one sentence on the analytics role
(storage % full as the structural gas-tightness signal for the Oct–Mar withdrawal
season; pair with ENTSO-G nominations + Elexon CCGT) from the Lede + cross-vendor
Related; close with the brief's Verified line.
Rules: NO new figures/stats not in the brief; 3 paragraphs, flowing prose, no bullets;
inline-code styling for slug + host + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING + CHART + ANTI-GOALS
═══════════════════════════════════════════════════════════════════════════════
- Tagline → 2nd line of <h1>; Lede → <p class="lede" style="max-width:600px;">;
  Verified line → <p class="tiny mt-16">. Hero table → 3×2 (dual-host cell <br/> + 10px).
- Schema citations: GasStorage / LNGTerminal for the typed datasets; silver/gie path for
  the schema-absent reference/news datasets. NEVER invent a class.
- Sample cells by type: date/time → class="date"; string/key → class="str"; numeric →
  class="num" (right-aligned); null/empty → class="nul" (gray italic, brief's literal).
- Caveats: discrepancy variant (class="caveat-item discrepancy" + eyebrow-discrepancy)
  only for declared/emitted mismatches or non-empty discrepancies_found.
- CHART TYPES — ONLY: sparkline, stackedArea, barsH, priceLadder. Use the brief's type +
  seed; fall back sparkline (single-series) / stackedArea (multi). Don't invent kinds.
- ANTI-GOALS: no live indicators / "X min ago" / uptime badges / KPI tiles; no
  "Get API key →" / SaaS CTAs / author photos / testimonials / hire-me chips; no emojis;
  no device-width viewport; no invented sample numbers, citations, schema classes, or
  codelist sections; no 5th tab or extra cards.

═══════════════════════════════════════════════════════════════════════════════
PER-PAGE OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
For each page: write a one-line header `--- <slug>.html ---`, then a complete standalone
HTML document (DOCTYPE → </html>) in its own code fence labelled `html`, and save it to
authored-pages/gie/<slug>.html in your workspace. Per page, self-check before moving on:
data-root="../../"; sidebar anchors match real section ids; every schema row cites a
gridflow source (GasStorage/LNGTerminal for typed, silver/gie path for schema-absent, no
invented class); sample rows verbatim; x-key + gas-day facts preserved; no emojis; both
inline scripts present; asset paths ../../assets/. Then continue to the next slug (or emit
the STATUS block if near the output limit).
```
