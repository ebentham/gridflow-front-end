# ENTSO-G — BULK / resumable Claude Design prompt (paste-ready)

**Use this instead of `entsog-prompt.md` when you want to attach ALL briefs at once.**

**Attach:** `authored-pages/entsoe/actual_generation.html` (primary reference) · `authored-pages/entsog/aggregated_physical_flows.html` (validated D-22 ENTSO-G example) · **all 33** `content-briefs/entsog/*.md` dataset briefs (NOT `_landing.md`).
**Workflow:** paste prompt → attach all → "Produce all." → say **"continue"** each time it pauses → when it says `ALL DONE`, export the workspace zip → send it to me.

--- paste everything below this line into the first message of a fresh Claude Design conversation ---

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one ENTSO-G Transparency
Platform dataset (European gas transmission) for full-stack data-science recruiters
in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html — the gold-standard STRUCTURAL
   reference. Mimic its structure, inline <style> block, class names, and layout
   exactly. Take its Overview + Caveats SECTION TREATMENT (not its content).
2. authored-pages/entsog/aggregated_physical_flows.html — a validated ENTSO-G page
   in the exact target format (JSON, no-Pydantic schema). Match it.
3. ALL ENTSO-G dataset briefs (content-briefs/entsog/*.md) — one page per brief.

═══════════════════════════════════════════════════════════════════════════════
BULK / RESUMABLE MODE  ← read this first
═══════════════════════════════════════════════════════════════════════════════
Produce ONE complete HTML page per attached brief, saved in your workspace as
authored-pages/entsog/<slug>.html (<slug> = the brief's `slug:` frontmatter).

- Process briefs in ALPHABETICAL ORDER of slug, deterministically.
- Do NOT produce a _landing.html — the vendor hub is maintained separately.
- You will NOT fit all pages in one response — that is expected and fine. When you
  are within ~2 pages of your output limit, STOP at a clean page boundary (NEVER
  mid-page). Then print exactly this status block and wait:

      ───────────────
      STATUS
      done (N of TOTAL): slugA, slugB, ...
      remaining: slugX, slugY, ...
      ───────────────

- When I reply "continue", resume with the FIRST slug in `remaining` and keep going.
- NEVER regenerate a slug already in `done`. NEVER skip a slug. NEVER reorder.
- When `remaining` is empty, finish with a single line:  ALL DONE (TOTAL of TOTAL).
- If a brief is malformed or missing a required field, skip it, keep going, and
  list it under a `could not render:` line in the final status — do not stop.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (ENTSO-G)
═══════════════════════════════════════════════════════════════════════════════
- Public JSON API at transparency.entsog.eu/api/v1 — NO auth, no key. Raw payload
  is JSON (NOT XML), bronze lands as raw_<uuid>.json.
- SCHEMA COVERAGE IS PER-DATASET — read each brief's Schema section:
  • physical_flows is the ONE dataset with a Pydantic class (EntsogPhysicalFlow,
    via PhysicalFlowsTransformer) — cite it where the brief names it.
  • ALL OTHER datasets are schema-absent — NO Pydantic class; columns derived
    dynamically by GenericEntsogJsonTransformer (silver/entsog/generic.py). Their
    schema table cites silver/entsog/*.py line numbers, and the Overview P2 uses
    the "no Pydantic class — columns derived dynamically" wording. NEVER invent a
    schema class for a dataset whose brief says it has none.
- Queried per operator-point-direction at GB interconnection points (Bacton IUK,
  Bacton BBL, Moffat). Quirk: timeZone=UCT (literally "UCT", not "UTC") — sending
  UTC returns HTTP 400. Empty windows return HTTP 404 + {"message":"No result
  found"} (the empty-set convention, not an error). Preserve both verbatim from
  each brief's caveats.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT (every page, in this order)
═══════════════════════════════════════════════════════════════════════════════
1. <head>: <meta charset="utf-8">; <title><slug> · ENTSO-G Transparency · Gridflow</title>;
   <meta name="viewport" content="width=1280">  (desktop-first — NOT device-width);
   Google Fonts preconnect + Fraunces + Inter + JetBrains Mono; <link rel="stylesheet"
   href="../../assets/theme.css" />; the same inline <style> block as actual_generation.html
   (schema-table, data-table, code-grid/code-pill, page-layout/sidebar, caveat-item +
   .discrepancy, eyebrow-discrepancy, src-cite, related-grid).

2. <body data-page="dataset" data-root="../../" data-screen-label="ENTSO-G · <slug>">

3. Breadcrumb + Hero (border-bottom: 1px solid var(--rule)):
   - .crumbs: Gridflow / Data sources / ENTSO-G Transparency / <slug>
   - 2-col grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT: eyebrow + chips ("daily · same-day" + "Illustrative snapshot");
           <h1 class="display-2"> mono <slug> on line 1, brief Tagline on line 2
           (keep <span class="italic fg-accent"> if present); <p class="lede"> Lede;
           <p class="tiny mt-16"> Verified line.
     RIGHT: 3×2 metadata grid from the brief's "Hero metadata" table (6 cells).

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4,1fr);">
   4 cells from the brief's "Stats strip" table (stat-n value, stat-l label).

5. <div class="container"><div class="page-layout">
     <nav class="sidebar">: (a) "On this page" anchors to every #section you render;
       (b) "ENTSO-G Transparency" → <a href="../entsog.html">← All datasets</a>, then
       current slug active, then the brief's "Sidebar siblings" as faint
       style="color:var(--ink-faint);" href="#" links.
     <div class="main-content"> sections in order:
       #overview — SYNTHESISED (brief has no # Overview). 3 paragraphs (rules below).
                   Eyebrow "Overview" + display-3 "What this dataset is.".
       #snapshot — chart from "Sample chart" (data-chart + seed from brief), .chart with
                   the brief's toggle chips, footer "Static snapshot · live wiring planned"
                   in mono uppercase.
       #schema   — table from brief's "Schema" + a .card row PARQUET PATH / PARTITION BY /
                   DEDUP KEY. Schema-absent datasets: intro states "No Pydantic class —
                   columns derived dynamically by GenericEntsogJsonTransformer"; every row
                   cites a silver/entsog/*.py path in <span class="cite">. physical_flows:
                   cite EntsogPhysicalFlow.
       #sample   — .data-table, brief's verbatim rows; bolded brief row gets
                   outline: 1px solid #3b6b4b; caption = .tiny from "Sources:".
       #api      — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL /
                   DuckDB·SQL / Python·polars) with the brief's verbatim code. Auth card:
                   "None (public)".
       #caveats  — eyebrow "Caveats" + display-3 "Things to know before using this." +
                   intro <p class="small"> linking to vendor-wide caveats at
                   <a href="../entsog.html#about">…</a>; numbered caveat-item 01..NN from
                   the brief; last gets style="border-bottom:1px solid var(--rule);
                   padding-bottom:16px;".
       #related  — .related-grid (2 cols) from "Related datasets"; cross-vendor card
                   (GIE storage, Elexon fuelhh) gets border:1px solid var(--ink) +
                   a "cross-vendor" accent chip, href ../<vendor>/<slug>.html.

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
or Caveats; close with what one row represents.
P2 (~60-80w) HOW GRIDFLOW INGESTS IT: "It is sourced from the ENTSO-G Transparency
Platform at <code>{endpoint}</code>, queried per operator-point-direction over a
gas-day range (timeZone=UCT). The raw JSON lands in bronze and is written to silver
via <code>{Transformer}</code>" + (schema-absent → ", with no Pydantic class — columns
are derived dynamically") | (physical_flows → ", validated against
<code>EntsogPhysicalFlow</code>"). Endpoint + transformer from the brief's API cards.
P3 (~50-80w) WHY IT MATTERS + VERIFICATION: one sentence on the analytics role
(gas-supply tightness, GB interconnection flows, nomination-vs-actual, gas-to-power)
from the Lede + cross-vendor Related; close with the brief's Verified line.
Rules: NO new figures/stats not in the brief; 3 paragraphs, flowing prose, no bullets;
inline-code styling for slug + endpoint + class/transformer names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING + CHART + ANTI-GOALS
═══════════════════════════════════════════════════════════════════════════════
- Tagline → 2nd line of <h1>; Lede → <p class="lede" style="max-width:600px;">;
  Verified line → <p class="tiny mt-16">. Hero table → 3×2 (long mono values 10px).
- Schema citations: silver/entsog path for schema-absent rows, EntsogPhysicalFlow only
  for physical_flows. NEVER invent a class.
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
authored-pages/<slug>.html in your workspace. Per page, self-check before moving on:
data-root="../../"; sidebar anchors match real section ids; every schema row cites a
gridflow source (silver path for schema-absent, no invented class); sample rows verbatim;
UCT/404 caveats preserved; no emojis; both inline scripts present; asset paths ../../assets/.
Then continue to the next slug (or emit the STATUS block if near the output limit).
```
