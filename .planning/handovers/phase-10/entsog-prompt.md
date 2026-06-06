# ENTSO-G — Claude Design prompt (paste-ready)

**Attach to the Claude Design session:** `authored-pages/entsoe/actual_generation.html` (primary reference) · `authored-pages/entsog/aggregated_physical_flows.html` (vendor layout example) · the batch's `content-briefs/entsog/<slug>.md` files.
**Batch order:** see the master handover (`2026-06-05-phase-10-claude-design-handover.md` § ENTSO-G).
**Vendor essentials baked into this prompt:** JSON payload (not XML) · `timeZone=UCT` quirk · HTTP-404-empty convention · **mostly no Pydantic schema** (1 of 33 typed; the rest dynamic via `GenericEntsogJsonTransformer`) · queried per operator-point-direction.

> If Task 00 D-1 was decided **D-20 (lean)**: delete the `#overview` section from the STRUCTURAL CONTRACT, the entire "OVERVIEW SYNTHESIS RULES" block, and the `#caveats` rendered-section instruction — leave caveats as research-record only.

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
2. authored-pages/entsog/aggregated_physical_flows.html — an ENTSO-G layout example
   showing how this vendor's JSON / no-Pydantic-schema content renders. Take vendor
   layout cues from it, but it is the older lean format — defer to reference #1 for
   the Overview/Caveats treatment.
3. One or more content briefs from content-briefs/entsog/*.md — your input.

For each brief, produce ONE complete standalone HTML file named <slug>.html that
will be saved to authored-pages/entsog/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
VENDOR FACTS (ENTSO-G — read before rendering)
═══════════════════════════════════════════════════════════════════════════════
- ENTSO-G is the European gas transmission transparency platform. Public JSON API
  at transparency.entsog.eu/api/v1 — NO authentication, no key.
- The raw payload is JSON (NOT XML — this is the gas sibling of ENTSO-E but uses a
  different transport). Bronze lands as raw_<uuid>.json.
- Only ONE of the 33 datasets has a Pydantic schema class (physical_flows →
  EntsogPhysicalFlow). The other 32 have NO Pydantic class — their columns are
  derived dynamically at silver time by GenericEntsogJsonTransformer
  (silver/entsog/generic.py). The brief's Schema table cites silver source-file
  line numbers, NOT a schema class. DO NOT invent a Pydantic class name for a
  dataset whose brief says "No Pydantic class".
- Data is queried per operator-point-direction (the pointDirection param) at GB
  interconnection points: Bacton IUK, Bacton BBL, Moffat (GB↔IE/NL pipelines).
- Vendor quirk: the connector sends timeZone=UCT (literally "UCT", not "UTC") —
  sending "UTC" returns HTTP 400. Surface this verbatim from the brief's caveats;
  do not "correct" it.
- Empty windows return HTTP 404 + {"message":"No result found"} — the documented
  empty-set convention, not an error.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT
═══════════════════════════════════════════════════════════════════════════════
Every page must contain, in this order:

1. <head>
   - <meta charset="utf-8">
   - <title><slug> · ENTSO-G Transparency · Gridflow</title>
   - <meta name="viewport" content="width=1280">  ← desktop-first; do NOT use
     "width=device-width, initial-scale=1"
   - Google Fonts preconnect + Fraunces + Inter + JetBrains Mono link
   - <link rel="stylesheet" href="../../assets/theme.css" />
   - The same <style> block as actual_generation.html (schema-table, data-table,
     code-grid/code-pill, page-layout/sidebar, caveat-item with .discrepancy
     variant, eyebrow-discrepancy, src-cite, related-grid)

2. <body data-page="dataset" data-root="../../" data-screen-label="ENTSO-G · <slug>">

3. Breadcrumb + Hero band (border-bottom: 1px solid var(--rule))
   - .crumbs: Gridflow / Data sources / ENTSO-G Transparency / <slug>
   - Two-column grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT  — eyebrow row + chips ("daily · same-day" + "Illustrative snapshot")
             <h1 class="display-2"> with mono <slug> on line 1, brief's Tagline
             on line 2 (preserve <span class="italic fg-accent"> wrapper if in brief)
             <p class="lede"> from brief's Lede
             <p class="tiny mt-16"> from brief's Verified line
     RIGHT — 3×2 metadata grid from brief's "Hero metadata" table (6 cells:
             SILVER PATH, API PATH, FREQUENCY, PUBLICATION LAG, VOLUME, PRIMARY KEY)

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4, 1fr);">
   4 cells from brief's "Stats strip" table — stat-n value, stat-l label.

5. <div class="container"><div class="page-layout">
     <nav class="sidebar"> with two sections:
       a) "On this page" — anchors to every #section_id you render
       b) "ENTSO-G Transparency" — <a href="../entsog.html">← All datasets</a>
          then current slug as active, then brief's "Sidebar siblings" list with
          style="color:var(--ink-faint);" and href="#"

     <div class="main-content"> — sections in this order:
       #overview   — SYNTHESISED (the brief has no # Overview). 3 paragraphs per
                     the synthesis rules below. Eyebrow "Overview" + display-3
                     "What this dataset is.".
       #snapshot   — chart from "Sample chart" (data-chart attribute, seed from
                     brief). Wrapped in .chart with toggle chips from the brief.
                     Footer: "Static snapshot · live wiring planned" in mono uppercase.
       #schema     — table from brief's "Schema" section + a .card row with
                     PARQUET PATH / PARTITION BY / DEDUP KEY. For schema-absent
                     datasets, the intro line states "No Pydantic class — columns
                     derived dynamically by GenericEntsogJsonTransformer" and every
                     row's citation is a silver/entsog/*.py path in <span class="cite">.
       #sample     — .data-table with brief's verbatim rows. The bolded brief row
                     gets outline: 1px solid #3b6b4b. Caption = .tiny from the
                     brief's "Sources:" paragraph.
       #api        — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs
                     (Example URL / DuckDB·SQL / Python·polars) with verbatim code.
       #caveats    — eyebrow "Caveats" + display-3 "Things to know before using
                     this." + intro <p class="small"> linking to vendor-wide caveats.
                     Then numbered <div class="caveat-item"> 01..NN from the brief.
                     Last caveat-item gets style="border-bottom: 1px solid
                     var(--rule); padding-bottom: 16px;".
       #related    — .related-grid (2 columns) from brief's "Related datasets".
                     Cross-vendor card (e.g. Elexon fuelhh, GIE storage) gets
                     border:1px solid var(--ink) + a "cross-vendor" accent chip.

6. </div></div></div>

7. Scripts: <script src="../../assets/charts.js"></script>
            <script src="../../assets/site.js"></script>
   Then TWO inline scripts (copy verbatim from actual_generation.html):
     - IntersectionObserver for sidebar active-link
     - setTab function for the API tabs

═══════════════════════════════════════════════════════════════════════════════
OVERVIEW SYNTHESIS RULES (the brief has NO Overview — you compose it)
═══════════════════════════════════════════════════════════════════════════════
Compose three paragraphs from material that ALREADY exists in the brief — NO new
claims, NO invented numbers, NO speculation beyond what the brief states.

Paragraph 1 — WHAT THE DATASET IS (~60-90 words):
  - Open with the slug as styled inline-code:
    <code class="mono" style="font-size:13px; background: var(--paper-deep);
    padding: 2px 6px; border: 1px solid var(--rule);">{slug}</code>
  - One-clause definition (paraphrase the brief's Lede).
  - 1-2 sentences of domain context from the brief's Schema preamble or Caveats.
  - Close with what one row represents (e.g. "Each row is one operator-point-
    direction's nominated quantity for a single gas day.").

Paragraph 2 — HOW GRIDFLOW INGESTS IT (~60-80 words):
  - Open with "It is sourced from the ENTSO-G Transparency Platform at" + the
    endpoint pattern in inline-code (from the brief's API Card 1 ENDPOINT, e.g.
    <code>/api/v1/operationalData?indicator=Nomination</code>), queried per
    operator-point-direction over a gas-day range with timeZone=UCT.
  - State that the raw JSON lands in bronze and is transformed to silver. For the
    schema: if the brief names a Pydantic class (only physical_flows →
    EntsogPhysicalFlow), cite it; OTHERWISE write "with no Pydantic class — column
    shape is derived dynamically by <code>GenericEntsogJsonTransformer</code>"
    (from the brief's Schema preamble / API Card 2 TRANSFORMER).
  - Template:
    "It is sourced from the ENTSO-G Transparency Platform at <code>{endpoint}</code>,
    queried per operator-point-direction over a gas-day range (timeZone=UCT). The
    raw JSON lands in bronze and is written to the silver parquet partition via
    <code>{Transformer}</code>{, with no Pydantic class — columns are derived
    dynamically | , validated against <code>EntsogPhysicalFlow</code>}."

Paragraph 3 — WHY IT MATTERS + VERIFICATION (~50-80 words):
  - One sentence on the dataset's role in domain analytics (gas-supply tightness,
    GB interconnection flows, nomination-vs-actual deltas, gas-to-power chain) —
    draw from the brief's Lede and cross-vendor Related entries (GIE storage,
    Elexon fuelhh).
  - Close with the verification status from the brief's Verified line (e.g.
    "Schema and API verified against gridflow connector source and vault
    curl-tests on {date}; ENTSO-G is a public no-auth API.").

Hard rules: NO new figures/prices/statistics not in the brief; NO speculation;
3 paragraphs only, flowing editorial prose, no bullets; inline-code styling for
slug + endpoint + transformer/class names.

═══════════════════════════════════════════════════════════════════════════════
MAPPING RULES (brief markdown → HTML)
═══════════════════════════════════════════════════════════════════════════════
- "**Tagline:**" → second line of <h1 class="display-2">. Preserve <span
  class="italic fg-accent">…</span> if present.
- "**Lede:**" → <p class="lede" style="max-width: 600px;">
- "**Verified line:**" → <p class="tiny mt-16" style="max-width:600px;">
- Hero metadata table → 3×2 grid (6 cells). Long mono values get font-size:10px.
- Stats strip table → 4 cells; numeric → .stat-n; longer label → .stat-l.
- Sidebar siblings → current slug active at top; others faint links to "#".
- Schema → render the brief's Schema preamble in the section intro. Every column
  row's "Gridflow citation" maps to <span class="cite">{silver/entsog/...py L<n>}
  </span> at the end of the row. DO NOT fabricate a schema class for schema-absent
  datasets — cite the silver source path exactly as the brief does.
- Sample data → .data-table; column cells get a class hint by type:
    date/time → class="date"; string/key → class="str"; numeric →
    class="num" (right-aligned); null/empty → class="nul" (gray italic, render the
    brief's literal e.g. "(empty)").
- Caveats → numbered <div class="caveat-item"> with .caveat-num "01" "02" …
  Add class="caveat-item discrepancy" + eyebrow-discrepancy header only when the
  caveat references a declared/emitted mismatch or the frontmatter
  discrepancies_found is non-empty and this caveat cites it.
- Source attribution at the end of each caveat → "<span class='src-cite'>…</span>"
  (the brief puts it in italic parens — preserve the source path).
- Related grid → 3–4 cards: mono slug + frequency chip + arrow, <p class="small">
  description, <span class="tiny"> "vendor · category · freq" line.
- Cross-vendor card (GIE storage, Elexon fuelhh, ENTSO-E actual_generation from an
  ENTSO-G page) gets border:1px solid var(--ink), a "cross-vendor" accent chip,
  and an href crossing to ../<vendor>/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
CHART TYPES (data-chart attribute values — rendered by ../../assets/charts.js)
═══════════════════════════════════════════════════════════════════════════════
ONLY use these:
  sparkline   — single time series (daily flows, nominations at one point)
  stackedArea — multi-series stacked (flows by direction / point)
  barsH       — horizontal bars (capacity by interconnection point, rankings)
  priceLadder — vertical ladder (rarely used for gas; auction premiums if any)
Use the type the brief's "Sample chart" specifies; match its seed. Fall back to
sparkline (single-series) / stackedArea (multi-series). Don't invent chart kinds.

═══════════════════════════════════════════════════════════════════════════════
AUTH & SCHEMA HANDLING (ENTSO-G specifics)
═══════════════════════════════════════════════════════════════════════════════
- ENTSO-G is PUBLIC, no key. The API & ingestion Auth card says "None (public)".
  There is NO entitlement/registration banner (unlike ENTSO-E) — keep editorial tone.
- For schema-absent datasets (all but physical_flows): the #schema intro states the
  dynamic-derivation fact, the schema table cites silver/entsog/generic.py (and
  silver/entsog/datetime.py for timestamp columns) line numbers, and the Overview P2
  uses the "no Pydantic class" wording. Never cite a class that the brief doesn't name.
- Preserve the UCT quirk and the 404-empty convention verbatim from the brief's
  caveats — they are real and load-bearing, not typos to fix.

═══════════════════════════════════════════════════════════════════════════════
ANTI-GOALS (do NOT do these)
═══════════════════════════════════════════════════════════════════════════════
- No "live" indicators, "X min ago", uptime badges, KPI tiles.
- No "Get API key →" / SaaS CTAs. No author photos, testimonials, hire-me chips.
- No emojis (the reference has none — keep it that way).
- No <meta name="viewport" content="width=device-width, initial-scale=1">.
- No invented numbers in Sample data; no invented citations; no invented Pydantic
  class for a schema-absent dataset; no invented codelist sections.
- No 5th tab or extra cards beyond what the brief specifies.

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
For each brief:
  1. A complete standalone HTML document (DOCTYPE → </html>).
  2. Wrapped in a code fence labelled `html`.
  3. Filename: <slug>.html matching the brief's `slug:` frontmatter.
  4. Above each HTML block, a one-line header: `--- <slug>.html ---`.
  5. After all blocks, list any briefs you couldn't render and why.

═══════════════════════════════════════════════════════════════════════════════
FINAL CHECK before returning (per HTML block)
═══════════════════════════════════════════════════════════════════════════════
  [ ] data-page / data-root="../../" / data-screen-label="ENTSO-G · <slug>"
  [ ] All sidebar anchors match real section ids
  [ ] Every schema row cites a gridflow source in <span class="cite"> (silver path
      for schema-absent datasets — no invented class)
  [ ] Sample data rows verbatim (no fabrication)
  [ ] UCT / 404-empty caveats preserved verbatim
  [ ] No emojis, no live wording, no fake timestamps
  [ ] Both IntersectionObserver and setTab inline scripts present at end
  [ ] All asset paths ../../assets/theme.css | charts.js | site.js
```
