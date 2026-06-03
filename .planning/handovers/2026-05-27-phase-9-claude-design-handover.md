# Phase 9 — ENTSO-E pages via Claude Design

**Date:** 2026-05-27
**Phase:** 9 — ENTSO-E full content build (49 datasets)
**Authoring path:** Claude Design (external) draws the HTML; main Claude drops it into `authored-pages/entsoe/<slug>.html`, runs `gridflow-build`, verifies, and commits.

This doc is the handover pack you (the human) carry between this repo and a fresh Claude Design conversation. It contains:

1. **The Claude Design prompt** — paste verbatim to seed a new Claude Design session
2. **Companion files to attach** — exactly what to drop into Claude Design alongside the prompt
3. **Suggested batch order** — which briefs to ship first
4. **Acceptance criteria** — what to check on each returned HTML before sending back to main Claude

---

## Workflow

```
You (human)                                 Claude Design                 Main Claude (here)
───────────                                 ─────────────                 ──────────────────
1. Open fresh Claude Design conversation
2. Paste § "Claude Design prompt" below ─►  [seeded]
3. Attach reference + brief files        ─►  [reads context]
4. Ask: "Produce <slug>.html"            ─►  [renders HTML]   ─────►     5. Paste HTML back
                                                                          6. main Claude saves to
                                                                             authored-pages/entsoe/<slug>.html
                                                                          7. main Claude runs gridflow-build
                                                                          8. main Claude reports verification
9. Approve next batch                                                     10. Commit on feature branch
```

**Branch:** Create `feat/phase-9-entsoe-pages` before starting (main Claude will do this on first acceptance).

---

## Companion files to attach (every Claude Design session)

These give Claude Design everything it needs without main Claude having to feed it constraints turn by turn:

1. **`authored-pages/entsoe/actual_generation.html`** — gold-standard visual reference. Claude Design will mimic its structure, classes, and inline styles. **This file was upgraded on 2026-05-27 to D-22 standard:** it now contains both an `#overview` section (3 paragraphs synthesised from the brief) and a `#caveats` section (6 numbered caveats from the brief, including a `caveat-item discrepancy` example at #04). The earlier D-20 version lacked both sections — do not use any older copy.
2. **`content-briefs/entsoe/<slug>.md`** — one brief per dataset you want produced. You can attach multiple briefs in one session (3–5 thematically related briefs works well — e.g. all four `outages_*` briefs together).
3. **`site/hifi/assets/theme.css`** — only attach if Claude Design asks for the token list. The reference HTML uses all the relevant tokens already, so usually unnecessary.

Do **not** attach: any other authored page (would confuse the reference), `disbsad-v2.html` (rejected layout), the build script (irrelevant), STATE.md / CONTROL.md (meta noise).

> **About the Overview gap.** The 49 ENTSO-E briefs are D-20 vintage and do not carry a `# Overview` markdown section — so Claude Design **synthesises** the Overview at render time from material that already exists in the brief (Lede, Schema preamble, API endpoint + transformer names, Verified line). The "Overview synthesis rules" section inside the Claude Design prompt below spells out exactly which brief fields feed which Overview paragraph and the hard no-fabrication constraints. The updated reference page is the visual + tonal model.

---

## Suggested batch order

49 briefs total (48 datasets + 1 `_landing.md`). 35 carry `entitlement_required: true` (HTTP 401 on the free key); 13 are unblocked.

Recommend this order to validate the entitlement treatment early then crank through:

**Batch 1 — Prove the pattern (2 briefs)**
- `day_ahead_prices` (unblocked, classic price series) — your "second `actual_generation`"
- `installed_capacity` (entitlement-blocked, structured codelist similar to `actual_generation`) — proves the entitlement-required treatment

→ stop, paste both HTMLs back, main Claude lands them, you eyeball at `http://localhost:8765/data-sources/entsoe/day_ahead_prices.html`.

**Batch 2 — Forecasts cluster (4 briefs)**
- `load_forecast`, `load_forecast_weekly`, `load_forecast_monthly`, `load_forecast_yearly`
- `generation_forecast`, `wind_solar_forecast`, `forecast_margin` — author together so sidebar siblings cross-reference cleanly

**Batch 3 — Balancing cluster (~8 briefs)**
- `activated_balancing_prices`, `activated_balancing_qty`, `balancing_energy_bids`, `aggregated_balancing_energy_bids`
- `imbalance_prices`, `imbalance_volume`, `current_balancing_state`
- `procured_balancing_capacity`, `contracted_reserves`, `cross_zonal_balancing_capacity`

**Batch 4 — Transmission / capacity cluster (~10 briefs)**
- `cross_border_flows`, `net_positions`, `commercial_schedules`, `commercial_schedules_net_positions`
- `net_transfer_capacity`, `total_capacity_allocated`, `total_nominated_capacity`, `transfer_capacity_use`
- `offered_transfer_capacity_continuous`, `offered_transfer_capacity_explicit`, `offered_transfer_capacity_implicit`
- `dc_link_intraday_transfer_limits`

**Batch 5 — Outages (5 briefs)**
- `outages_consumption`, `outages_generation`, `outages_production`, `outages_transmission`, `outages_offshore_grid`

**Batch 6 — Long tail (~14 briefs)**
- `actual_load`, `actual_generation_units`, `generation_units_master_data`, `installed_capacity_units`
- `auction_revenue`, `congestion_income`, `congestion_management_costs`, `balancing_financial_expenses_income`
- `redispatching_cross_border`, `redispatching_internal`, `countertrading`, `water_reservoirs`

**Batch 7 — Landing page (1 brief)**
- `_landing.md` → `_landing.html` (vendor hub for `site/hifi/data-sources/entsoe.html`). Save as `authored-pages/entsoe/_landing.html`.

  > **Hub depth ≠ dataset-page depth — do NOT carry over the `../../` contract used everywhere else in this doc.** A vendor hub renders one level below the site root (`data-sources/<vendor>.html`), so it is **depth-1**. On the hub `_landing.html`:
  > - `<body … data-root="../" …>` — **not** `../../`. The hub's injected top-nav + footer are built from `data-root` (see `site/hifi/assets/site.js`); `../../` resolves them one level above the project root and 404s in production (GitHub Pages *project* site), while staying invisible on the origin-root dev server where `../` and `../../` collapse.
  > - asset links are `../assets/theme.css|charts.js|site.js` — **not** `../../assets/`.
  > - dataset card hrefs are slug-prefixed `<vendor>/<slug>.html` (e.g. `entsoe/day_ahead_prices.html`).
  >
  > Canonical reference: the Jinja template `templates/vendor-hub.html.j2` (`data-root="../"`). `gridflow-build` copies `_landing.html` **verbatim** (no path rewriting), so these must be correct in the authored source.

You don't have to follow this order — it's just the path with the cleanest cross-references.

---

## Acceptance criteria (run on every returned HTML before main Claude lands it)

Spot-check each Claude Design output against this list. If anything fails, push back in the same Claude Design conversation rather than letting main Claude paper over it.

- [ ] **Body attribute contract:** `<body data-page="dataset" data-root="../../" data-screen-label="ENTSO-E · <slug>">`
- [ ] **Asset paths:** `../../assets/theme.css`, `../../assets/charts.js`, `../../assets/site.js` (relative, not absolute)
- [ ] **Breadcrumb:** Gridflow / Data sources / ENTSO-E Transparency / `<slug>` — exactly four crumbs, last is plain text
- [ ] **Hero metadata grid:** 6 cells in 3×2 layout sourced from brief's "Hero metadata" table
- [ ] **Stats strip:** 4 cells from brief's "Stats strip" table
- [ ] **Sidebar siblings:** `← All datasets` → `../entsoe.html`; current slug active; brief's "Sidebar siblings" list as faint `style="color:var(--ink-faint);"` links
- [ ] **Chart:** `data-chart="<type>"` matches brief's "Sample chart" type; seed matches; only types in `{stackedArea, sparkline, barsH, priceLadder}` (anything else means Claude Design invented a chart kind — push back)
- [ ] **Schema table:** every column from brief is present; every row has a `<span class="cite">` citation to a gridflow source file
- [ ] **Sample data:** rows are **verbatim from the brief** — no invented numbers, no rearranged columns. Highlighted row (bolded in brief) gets `outline: 1px solid #3b6b4b; outline-offset: -1px;`.
- [ ] **Overview:** 3 paragraphs synthesised from brief content (slug + endpoint + transformer + verified line); no invented figures or market claims; inline-code styling on slug and key class names. First paragraph opens with `<code>{slug}</code>` styled inline-code.
- [ ] **API & ingestion:** 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL / DuckDB · SQL / Python · polars) with brief's verbatim code
- [ ] **Caveats:** section eyebrow + display-3 title + intro paragraph linking to vendor-wide caveats; numbered `01`..`NN` in brief order; each ends in a source attribution (in prose or `<span class="src-cite">`); last `.caveat-item` has `style="border-bottom: 1px solid var(--rule); padding-bottom: 16px;"`
- [ ] **Discrepancy treatment:** any caveat citing "declared but not emitted" / "schema says X, transformer does Y" wording gets `class="caveat-item discrepancy"` + `<div class="eyebrow-discrepancy">DISCREPANCY · …</div>` eyebrow
- [ ] **Related grid:** 3–4 cards; cross-vendor card (Elexon `fuelhh` etc.) has `border:1px solid var(--ink)` and `<span class="tiny" style="color: var(--accent);">cross-vendor</span>` badge
- [ ] **Scripts:** both inline scripts (IntersectionObserver + `setTab`) present at end of `<body>`
- [ ] **Entitlement-required pages:** verified line says "live API requires extended ENTSO-E registration" (verbatim from brief); final caveat is the entitlement note (verbatim from brief); no visual banner or badge added
- [ ] **No anti-goals:** no `<meta name="viewport" content="width=device-width">`; no emojis; no fake live indicators / SaaS chrome / hire-me CTAs / testimonials
- [ ] **No invented codelists:** if the brief omits a `# Production types`-style codelist, the page omits the `#<codelist>` section (don't fabricate one)

---

## Claude Design prompt

Copy everything below this line into the **first message** of a fresh Claude Design conversation. Then attach the reference HTML and brief(s) and ask for the page(s).

```
You are producing standalone HTML documentation pages for an editorial portfolio
site called gridflow-front-end. Each page documents one ENTSO-E Transparency
Platform dataset for full-stack data-science recruiters in energy trading.

The site is editorial, quiet, paper-and-ink — not a SaaS dashboard. Cream paper,
ink/charcoal text, forest-green accent (#3b6b4b). Three fonts via Google Fonts:
Fraunces (display), Inter (UI / body), JetBrains Mono (code / numbers).

I am attaching:
1. authored-pages/entsoe/actual_generation.html  — the gold-standard reference.
   Mimic its structure, inline <style> block, class names, and layout exactly.
2. One or more content briefs from content-briefs/entsoe/*.md — your input.

For each brief, produce ONE complete standalone HTML file named <slug>.html
that will be saved to authored-pages/entsoe/<slug>.html.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURAL CONTRACT
═══════════════════════════════════════════════════════════════════════════════
Every page must contain, in this order:

1. <head>
   - <meta charset="utf-8">
   - <title><slug> · ENTSO-E Transparency · Gridflow</title>
   - <meta name="viewport" content="width=1280">  ← desktop-first; do NOT use
     "width=device-width, initial-scale=1"
   - Google Fonts preconnect + Fraunces + Inter + JetBrains Mono link
   - <link rel="stylesheet" href="../../assets/theme.css" />
   - The same <style> block as actual_generation.html (schema-table, data-table,
     code-grid/code-pill, page-layout/sidebar, caveat-item with .discrepancy
     variant, eyebrow-discrepancy, src-cite, related-grid)

2. <body data-page="dataset" data-root="../../" data-screen-label="ENTSO-E · <slug>">

3. Breadcrumb + Hero band (border-bottom: 1px solid var(--rule))
   - .crumbs: Gridflow / Data sources / ENTSO-E Transparency / <slug>
   - Two-column grid (1.35fr 1fr, gap 56px, align-items: end):
     LEFT  — eyebrow row + chips ("PT15M · T+1h lag" + "Illustrative snapshot")
             <h1 class="display-2"> with mono <slug> on line 1, brief's Tagline
             on line 2 (preserve <span class="italic fg-accent"> wrapper if in brief)
             <p class="lede"> from brief's Lede
             <p class="tiny mt-16"> from brief's Verified line
     RIGHT — 3×2 metadata grid from brief's "Hero metadata" table

4. Stats strip: <div class="stats-strip" style="grid-template-columns: repeat(4, 1fr);">
   4 cells from brief's "Stats strip" table — stat-n value, stat-l label.

5. <div class="container"><div class="page-layout">
     <nav class="sidebar"> with two sections:
       a) "On this page" — anchors to every #section_id you render
       b) "ENTSO-E Transparency" — <a href="../entsoe.html">← All datasets</a>
          then current slug as active, then briefs's "Sidebar siblings" list
          with style="color:var(--ink-faint);" and href="#"

     <div class="main-content">  — sections in this order:
       #overview   — SYNTHESISED at render time. The brief has NO `# Overview`
                     section — you compose three paragraphs from existing brief
                     material under strict no-fabrication rules (see Overview
                     synthesis rules below). Section eyebrow "Overview" +
                     display-3 "What this dataset is.". 3 × <p> at
                     max-width: 680px; font-size: 15px; line-height: 1.65.
       #snapshot   — chart from "Sample chart" (data-chart attribute, seed from
                     brief). Wrapped in .chart with toggle chips 24h/7d/30d
                     (24h active). Footer: "Static snapshot · live wiring planned"
                     in JetBrains Mono uppercase.
       #schema     — table from brief's "Schema" section + a .card row with
                     PARQUET PATH / PARTITION BY / DEDUP KEY
       #sample     — .data-table with brief's verbatim rows. The row bolded
                     in the brief gets outline: 1px solid #3b6b4b. Caption
                     under table is .tiny from brief's "Sources:" paragraph.
       #<codelist> — OPTIONAL. Only if brief has a "# Production types" or
                     similar codelist section. Render as .code-grid with .code-pill items.
       #api        — 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs
                     (data-tab-group, three panels: URL / SQL / Python·polars).
                     Use brief's verbatim code blocks.
       #caveats    — Section eyebrow "Caveats" + display-3 "Things to know
                     before using this." + intro <p class="small"> linking
                     to vendor-wide caveats. Then numbered <div class="caveat-item">
                     entries (01..NN) from brief's "# Caveats" section. Last
                     caveat-item gets style="border-bottom: 1px solid var(--rule);
                     padding-bottom: 16px;" to close the list visually.
       #related    — .related-grid (2 columns) with cards from brief's
                     "Related datasets" section. Cross-vendor card (e.g. Elexon
                     fuelhh from an ENTSO-E page) gets border:1px solid var(--ink)
                     and <span class="tiny" style="color: var(--accent);">cross-vendor</span>

6. </div></div></div>

7. Scripts: <script src="../../assets/charts.js"></script>
            <script src="../../assets/site.js"></script>
   Then TWO inline scripts (copy verbatim from actual_generation.html):
     - IntersectionObserver for sidebar active-link
     - setTab function for the API tabs

═══════════════════════════════════════════════════════════════════════════════
OVERVIEW SYNTHESIS RULES (the brief has NO Overview — you compose it)
═══════════════════════════════════════════════════════════════════════════════
The ENTSO-E briefs are D-20 vintage and do not carry an `# Overview` section.
The reference page (actual_generation.html) shows the target shape and tone.
You compose three paragraphs from material that ALREADY exists in the brief —
NO new claims, NO invented numbers, NO speculation about market behaviour
beyond what the brief states.

Paragraph 1 — WHAT THE DATASET IS (~60-90 words):
  - Open with the slug as styled inline-code:
    <code class="mono" style="font-size:13px; background: var(--paper-deep);
    padding: 2px 6px; border: 1px solid var(--rule);">{slug}</code>
  - Then a one-clause definition (paraphrase / expand the brief's Lede).
  - Then 1-2 sentences of immediate domain context drawn from the brief's
    Schema preamble, codelist, or Caveats #01-#02. If the dataset has a
    codelist (B01..B25, A01..A99, etc.), name the codelist range.
  - Close with what one row represents (e.g. "Each row is one production
    type's contribution to a single 15-, 30-, or 60-minute interval.").

Paragraph 2 — HOW GRIDFLOW INGESTS IT (~60-80 words):
  - Open with "It is sourced from the ENTSO-E Transparency Platform at"
    + the endpoint pattern in inline-code styling (from brief's API
    Card 1 ENDPOINT).
  - Mention the raw payload type (GL_MarketDocument, Acknowledgement_,
    Publication_, etc.) as inline-code.
  - State the schema class name (from brief's Schema preamble) as inline-code.
  - State the transformer class name (from brief's API Card 2 TRANSFORMER)
    as inline-code.
  - Use this template:
    "It is sourced from the ENTSO-E Transparency Platform at <code>{endpoint}</code>,
    queried per bidding zone over a date range. The raw XML lands in bronze
    as a <code>{document_type}</code>, is validated against <code>{Schema}</code>,
    and written to the silver parquet partition via <code>{Transformer}</code>."

Paragraph 3 — WHY IT MATTERS + VERIFICATION (~50-80 words):
  - One sentence on the dataset's role in domain analytics — what model it
    feeds, what cross-vendor analogue it has, or what canonical analysis it
    enables. Draw from the brief's Lede and any cross-vendor Related entries.
  - Close with the verification status: take the brief's Verified line,
    rephrase if needed (e.g. "Schema verified against gridflow source on
    {date}; the live API requires extended ENTSO-E registration." for
    entitlement-blocked datasets).

Hard rules:
  - NO new figures, prices, market shares, or statistics not in the brief.
  - NO speculation about future behaviour or hypothetical use cases.
  - NO cross-references to datasets not in the brief's "Related datasets"
    list or Caveats.
  - For entitlement-blocked datasets (frontmatter `entitlement_required: true`):
    P3 must mention the live-API restriction; the wording in the reference
    actual_generation.html Overview is the model.
  - Inline-code styling: use the same `class="mono" style="font-size:12-13px;
    background: var(--paper-deep); padding: 2px 6px; border: 1px solid
    var(--rule);"` pattern for slug + endpoint + class names. Drop the
    background/border for bare references (e.g. "GB's <code>fuelhh</code>").
  - 3 paragraphs only. No bullet points. Flowing editorial prose.

═══════════════════════════════════════════════════════════════════════════════
MAPPING RULES (brief markdown → HTML)
═══════════════════════════════════════════════════════════════════════════════
- "**Tagline:**" → second line of <h1 class="display-2">. Preserve <span
  class="italic fg-accent">…</span> wrapper if present.
- "**Lede:**" → <p class="lede" style="max-width: 600px;">
- "**Verified line:**" → <p class="tiny mt-16" style="max-width:600px;">
- Hero metadata table → 3×2 grid (6 cells). Long mono values get font-size:10px.
- Stats strip table → 4 cells; numeric → .stat-n; longer label → .stat-l
- Sidebar siblings → use brief's bullet list. Current slug appears once at top
  of the section as the active link; others as faint links to "#".
- Schema → render frontmatter sources_consulted citations in the section intro
  paragraph. Every column row's "Gridflow citation" column maps to
  <span class="cite">schemas/entsoe.py L<N></span> at end of .col-note.
- Sample data → .data-table; column cells get class hint by type:
    date/time   → class="date"  (warm tan)
    string/EIC  → class="str"   (peach)
    numeric     → class="num"   (mint green, text-align: right)
    null/empty  → class="nul"   (gray italic, display "" verbatim)
- Caveats → numbered <div class="caveat-item"> with .caveat-num "01" "02" …
  Add class="caveat-item discrepancy" + eyebrow-discrepancy header when:
    • frontmatter discrepancies_found: is non-empty AND this caveat references it
    • OR caveat text uses "declared but not", "transformer does not", "schema
      says X but" wording
- Source attribution at end of each caveat → "<span class='src-cite'>…</span>"
- Related grid → 3–4 cards. Each card: header row with mono slug + frequency
  chip + arrow, then <p class="small"> description, then <span class="tiny">
  taxonomy line ("vendor · category · freq").
- Cross-vendor card (Elexon dataset linked from an ENTSO-E page) gets:
    border: 1px solid var(--ink)  (instead of var(--rule))
    a "cross-vendor" tiny chip in --accent color
    href that crosses to ../elexon/<slug>.html

═══════════════════════════════════════════════════════════════════════════════
CHART TYPES (data-chart attribute values)
═══════════════════════════════════════════════════════════════════════════════
ONLY use these — they're rendered by ../../assets/charts.js:
  stackedArea    — multi-series stacked area (generation by fuel, load by zone)
  sparkline      — single time series line (price series, ROC series)
  barsH          — horizontal bars (rankings, capacity by category)
  priceLadder    — vertical price/quantity ladder (auction bids, order book)

If the brief's "Sample chart" specifies a different type, fall back to
sparkline for single-series, stackedArea for multi-series. Don't invent
chart kinds.

═══════════════════════════════════════════════════════════════════════════════
ENTITLEMENT-REQUIRED HANDLING
═══════════════════════════════════════════════════════════════════════════════
When frontmatter has `entitlement_required: true`:
  • DO NOT add a visual banner or badge — keep editorial tone.
  • Use brief's verbatim Verified line (typically says "live API requires
    extended ENTSO-E registration").
  • Include brief's verbatim entitlement caveat as a numbered caveat (usually
    last).
  • Sample data is whatever the brief provides (authored from vault Bronze,
    not live).
  • The Auth card under API & ingestion can note the 401 condition if the
    brief mentions it.

═══════════════════════════════════════════════════════════════════════════════
ANTI-GOALS (do NOT do these)
═══════════════════════════════════════════════════════════════════════════════
- No "live" indicators, "X min ago", uptime badges, KPI tiles
- No "Get API key →" buttons or other SaaS CTAs
- No author photos, testimonials, hire-me chips
- No emojis (the existing reference has none — keep it that way)
- No <meta name="viewport" content="width=device-width, initial-scale=1">
- No alternative "disbsad-v2" layout (sticky anchor bar across top, centered
  1440px container) — use the sidebar layout from the reference
- No invented numbers in Sample data — only what's in the brief
- No invented citations — only the gridflow source paths the brief provides
- No 5th tab or extra cards beyond what the brief specifies

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════
For each brief:
  1. Produce a complete, standalone HTML document (DOCTYPE → </html>)
  2. Wrap it in a code fence labelled `html` so I can copy it cleanly
  3. Filename: <slug>.html where <slug> matches the `slug:` field in frontmatter
  4. Above each HTML block, write a one-line header: `--- <slug>.html ---`
  5. After all HTML blocks, list any briefs you couldn't render and the
     reason (e.g. missing chart type, conflicting frontmatter)

═══════════════════════════════════════════════════════════════════════════════
FINAL CHECK before returning
═══════════════════════════════════════════════════════════════════════════════
For each HTML block, verify:
  [ ] data-page / data-root / data-screen-label correct
  [ ] All sidebar anchors match actual section ids
  [ ] Every schema row has a citation in <span class="cite">
  [ ] Sample data rows are verbatim (no fabrication)
  [ ] No emojis, no live wording, no fake timestamps
  [ ] Both IntersectionObserver and setTab inline scripts present at end
  [ ] All asset paths are ../../assets/theme.css | charts.js | site.js
```

---

## After Claude Design returns HTML

Paste the HTML block(s) into a new message to main Claude with:

> "Here is the produced HTML for `<slug>` (and any others). Land it."

Main Claude will:

1. Save each HTML to `authored-pages/entsoe/<slug>.html` (overwriting if it exists)
2. Run `gridflow-build` to render under `site/hifi/data-sources/entsoe/`
3. Spot-check against the Acceptance criteria above
4. Report status, then ask before committing

If anything fails the acceptance check, main Claude will tell you what to push back on in the Claude Design conversation rather than auto-fixing — keeps the source of truth in the brief + reference.

---

## Phase 9 close-out (not yet — at the end)

When all 49 HTMLs are landed:

1. Expand `site/hifi/data/entsoe.json` from 1 → 49 entries (49 datasets, 1 entry per dataset, grouped logically — main Claude will draft from the briefs)
2. Verify `gridflow-build --check` passes (idempotence — no changes on second run)
3. Smoke-test in browser at `http://localhost:8765/data-sources/entsoe.html` and 4–5 dataset pages
4. Mark Phase 9 complete in STATE.md / CONTROL.md / ROADMAP.md
5. PR `feat/phase-9-entsoe-pages` → `main`

---

*Last updated: 2026-05-27 — Created at start of Phase 9 execution. Mirrors the pattern that produced the 33 Elexon authored pages in Phase 8C.*
