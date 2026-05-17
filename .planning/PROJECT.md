# Gridflow front-end

## What This Is

A static portfolio website that documents the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline and the gridflow-models modelling projects, framed for energy-trading recruiters. The site is hand-written HTML + CSS + vanilla JS deployed via GitHub Pages from `site/hifi/`. Twin audience: full-stack data-science recruiters in energy trading (primary), and the author themselves as a working catalog of UK/EU power & gas data sources and trading models (secondary). Explicitly **not** a product, not a dashboard — no fake live indicators, no SaaS-style KPIs.

## Core Value

**When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data."**

Domain depth wins every tradeoff: depth of dataset documentation > visual polish > breadth of vendor coverage > novel features.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ Static-site deploy pipeline — GitHub Actions → Pages, artefact = `site/hifi/` (`.github/workflows/deploy.yml`) — existing
- ✓ Hand-authored HTML with runtime-injected shared chrome (nav + footer) driven by body `data-page` / `data-root` attributes (`site/hifi/assets/site.js`) — existing
- ✓ Editorial visual identity: cream + forest-green palette, Fraunces serif headings, Inter body, JetBrains Mono for code (`site/hifi/assets/theme.css`) — user-confirmed good
- ✓ Local dev server (`gridflow-serve` CLI, Python 3.11+ stdlib only, `src/gridflow_front_end/serve.py`) — existing
- ✓ `fuelhh.html` as the canonical dataset-page reference template (Overview / Schema / Sample / Caveats / Related sections) — user-confirmed reference
- ✓ Deterministic seeded inline-SVG chart renderers (`site/hifi/assets/charts.js`) — existing
- ✓ Demand-forecast page as the canonical model-case-study template (`site/hifi/models/demand-forecast.html`) — existing

### Active

<!-- v1 cleanup milestone. -->

**Main-page polish:**
- [ ] Home page (`site/hifi/index.html`) — editorial polish pass, honest framing, fix mobile-viewport
- [ ] Architecture page (`site/hifi/architecture.html`) — polish pass on writing and diagrams; structure stays
- [ ] Data-sources landing (`site/hifi/data-sources.html`) — polish, kill dead `href="#"` links, fix mobile-viewport

**Elexon dataset depth:**
- [ ] Bring all 22 existing Elexon dataset pages to fuelhh-level fidelity (Overview, Schema, Sample, Caveats, Related)
- [ ] Reconcile the dataset-count discrepancy (22 pages on disk · 25 manifest IDs in `data/elexon.json` · 28 claimed in catalog UI) into one source-of-truth

**Cross-vendor proof:**
- [ ] Replace dead `<a href="#">` vendor placeholders with clean "coming soon" landing pages for ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO (no dataset pages yet)
- [ ] Build ENTSO-E hub + 1 ENTSO-E dataset at fuelhh fidelity (proves the cross-vendor template works)

**Honesty sweep:**
- [ ] Kill 'live' framing site-wide: replace `live` / `X min ago` / `last sync` chips and timestamps with honest 'static, illustrative snapshot' framing
- [ ] Make snapshot semantics explicit: charts and numbers are illustrative (shape only), not real Elexon values

**Bug & a11y fallout:**
- [ ] Fix mobile viewport on the 23 broken pages (`<meta name="viewport" content="width=1280">` → `width=device-width, initial-scale=1`)
- [ ] Pick one license, add `LICENSE` file at repo root, align all inline strings (currently MIT vs Apache-2.0 contradiction)
- [ ] Add `<main>` semantic landmark, `aria-current` on active nav, `aria-hidden` on decorative icons
- [ ] Fix sidebar hover affordance (inline `color:var(--ink-faint)` overrides `:hover`)
- [ ] Add `rel="noopener"` to the two `target="_blank"` external links missing it
- [ ] Finish & commit the in-flight refactor (typography `fg-accent` sweep, removal of false pillar-status badges, fuelhh honesty edits)

**Structural / CSS debt:**
- [ ] Extract the duplicated per-dataset `<style>` block (~30 lines × 22 files) into `theme.css`
- [ ] Consolidate the two scroll-spy script variants and the per-page `setTab` declarations into shared assets

**Cross-repo sync:**
- [ ] Sync the Obsidian Vault dataset pages (in the `gridflow` repo at `quant-vault/30-vendors/elexon/datasets/`) so they match the new on-site content. Reference: `anthropic-skills:gridflow-dataset-spec` skill.

### Out of Scope

<!-- Explicit boundaries with reasoning. -->

- **Additional model case studies (SRMC, full power stack, renewable forecast)** — Deferred to a later milestone; demand-forecast already covers the "we have models" point for v1
- **Real Elexon API wiring / live data ingestion** — Illustrative snapshots only in v1; a "live wiring" milestone is plausible but not committed
- **ENTSO-E dataset coverage beyond 1 dataset** — One dataset is the cross-vendor template proof; full coverage is a later milestone per vendor
- **New visual identity / design system rebuild** — Current cream/forest/Fraunces serves the purpose; revisit only if evidence demands it
- **Static-site-generator / template engine adoption** — An implementation choice deferred to the planning phase; the requirement is "all 22 dataset pages reach fuelhh fidelity without becoming unmaintainable", the means is open
- **Live performance metrics, uptime badges, dashboard-y elements** — Explicitly anti-goal; would imply the site is a product
- **Other vendors at dataset depth (ENTSO-G, GIE, Open-Meteo, NESO datasets)** — Deferred; v1 caps at Elexon + 1 ENTSO-E dataset
- **Real-time data fetches from the browser** — Deferred; everything ships static

## Context

**Sibling projects this site documents:**
- `gridflow` (github.com/EBentham/gridflow) — Python ETL pipeline that standardises UK/EU power & gas market data (Elexon BMRS, ENTSO-E Transparency Platform, ENTSO-G, GIE, Open-Meteo, NESO Carbon Intensity) into a medallion-architecture (bronze/silver/gold) DuckDB warehouse with Pydantic schemas and Polars transforms
- `gridflow-models` (github.com/EBentham/gridflow-models) — modelling layer built on gridflow: short-run marginal cost (SRMC) model, full power-stack model, demand forecasting, renewable forecasting

**Tech context (from `.planning/codebase/`):**
- Static site, **no framework, no build step**. HTML files are the source. Shared chrome injected at runtime by `site/hifi/assets/site.js` from a body `data-page` / `data-root` / `data-screen-label` attribute contract.
- Python 3.11+ dev server (`gridflow-serve`, stdlib only); deploy is GitHub Pages directly off `site/hifi/`.
- 22 Elexon dataset pages exist on disk; 6 are structurally complete (`fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`), 16 are broken stubs missing the `#overview`, `#schema`, `#sample`, `#api` sections.
- Massive duplication: ~30-line `<style>` block repeated in all 22 Elexon dataset HTML files; two scroll-spy script variants scattered across pages; per-page global `setTab()` redeclared 22 times.
- 26 modified files in-flight on this branch (uncommitted) doing a partial typography refactor and the start of the 'live → snapshot' honesty pivot — needs to be finished and committed.

**Audience reality:**
- Recruiters typically skim a portfolio site for 30–90 seconds before deciding whether to click through to the GitHub repos. The site has to land its credibility signal fast and reward deeper reading without requiring it.
- The author's own daily use is as a working reference — depth and navigation matter even when polish doesn't.

**Source-of-truth hierarchy:**
1. Vendor docs (Elexon BMRS docs, ENTSO-E Transparency Platform docs, etc.) — absolute truth
2. On-site documentation (`site/hifi/data-sources/<vendor>/<dataset>.html`) — authored truth; must align with vendor docs and must not drift
3. Obsidian Vault dataset pages (in the `gridflow` repo, `quant-vault/30-vendors/`) — working state, potentially stale; synced from on-site content

## Constraints

- **Tech stack**: Static site, no SSG today — must remain deployable as a plain GitHub Pages artefact from `site/hifi/`. If a build step is added, it must produce a deployable static directory and not break the existing deploy.
- **Runtime**: Python 3.11+ stdlib only for the dev server. No third-party Python deps in the deployed path.
- **Browser compatibility**: Modern evergreen browsers only. ES2017+, no transpilation, no polyfills, no module system in the deployed JS.
- **Mobile**: Must work on phones — currently broken on 23/27 pages (`width=1280` viewport bug). Mobile-functional is recruiter table-stakes.
- **Accuracy**: Schema, primary keys, frequencies, lags, caveats must match vendor docs. The site loses all credibility if a recruiter spot-checks against the real Elexon API and finds drift.
- **Honesty**: No fake live timestamps, no fake "shipping" badges, no performance metrics. Anti-goal: looking like a SaaS product or dashboard.
- **Cross-repo coordination**: Vault sync requires coordinating changes across the `gridflow` repo (vault at `quant-vault/30-vendors/`). Direction is on-site → vault.
- **Author bandwidth**: Solo project, hand-authored, no automation other than GitHub Pages deploy. Scope must fit a single-author cleanup pace.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Editorial / quiet aesthetic; keep current cream-forest + Fraunces identity | User selected from Stripe Press / FT Alphaville framing; current look serves the purpose | — Pending |
| Recruiter-first audience: full-stack data scientist in energy trading (code + ML + domain) | User explicitly prioritised recruiter over self-reference | — Pending |
| Core value = domain depth over polish, gateway, or personal reference | User chose depth from explicit options | — Pending |
| Kill all 'live' framing — site is a documentation site, charts/numbers are illustrative | User chose "Kill all 'live'" + "Illustrative / shape only" | — Pending |
| Fix all 22 Elexon stubs to fuelhh fidelity *in this milestone* (vs deferring) | User chose "Fix fully in v1" over lighter "Hide from nav" / "Mark WIP" options | — Pending |
| Stub other vendor hubs + 1 ENTSO-E dataset in v1 (proves cross-vendor template) | User picked both as additional v1 items | — Pending |
| Sync Obsidian Vault in v1 (spans the `gridflow` repo) | User picked it as an additional v1 item | — Pending |
| Defer more model case studies, real-data wiring, full ENTSO-E coverage, new visual identity | User did not pick "More model studies"; "actual data" snapshots ruled out; aesthetic kept | — Pending |
| Source-of-truth hierarchy: vendor docs > on-site > Obsidian Vault | User stated this in kickoff | — Pending |
| SSG / template-engine adoption left to planning phase (not predetermined) | Requirement is fuelhh fidelity across 22 + 1 pages without becoming unmaintainable; means is open | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition` or equivalent):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-17 after initialization*
