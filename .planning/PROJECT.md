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

**Elexon dataset depth (33 datasets — matches gridflow connector + vault reality):**
- [ ] Fix 22 existing Elexon dataset pages to fuelhh-level fidelity (6 complete pages to regenerate from template, 16 broken stubs to complete)
- [ ] Build 3 manifest-only datasets that have no page today: `remit`, `bmunits_reference`, `soso`
- [ ] Build 8 vault-only datasets that have no page or manifest entry today: `atl`, `imbalngc`, `inddem`, `indgen`, `lolpdrm`, `market_depth`, `melngc`, `tsdfd`
- [ ] Reconcile the dataset count: 33 everywhere (`data/elexon.json`, catalog UI, footer, index stat strip)

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

**Vault integration (vault → site direction):**
- [ ] Wire the build script to read per-dataset content from the Obsidian Vault (`C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\<vendor>\datasets\*.md`) so the vault becomes the canonical content layer rendered into site HTML at build time
- [ ] Audit + refine vault content where stale or thin (Codex has done initial mapping; verify against gridflow schemas before rendering each page). Reference: `anthropic-skills:gridflow-dataset-spec` skill for vault page conventions.
- [ ] Decide how the cross-repo content gets to CI: vendor-copy at build-time, configurable path, or symlinked checkout

### Out of Scope

<!-- Explicit boundaries with reasoning. -->

- **Additional model case studies (SRMC, full power stack, renewable forecast)** — Deferred to a later milestone; demand-forecast already covers the "we have models" point for v1
- **Real Elexon API wiring / live data ingestion** — Illustrative snapshots only in v1; a "live wiring" milestone is plausible but not committed
- **ENTSO-E dataset coverage beyond 1 dataset** — One dataset is the cross-vendor template proof; full coverage is a later milestone per vendor
- **New visual identity / design system rebuild** — Current cream/forest/Fraunces serves the purpose; revisit only if evidence demands it
- **Adopting a Node/Go SSG (11ty, Astro, Hugo)** — Rejected after research: introduces a non-Python toolchain to a Python-first portfolio for negligible benefit at ~50-page scale. v1 uses a small Python + Jinja2 build script (the "middle path") instead
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
- **Dataset reality:** 33 active Elexon endpoints in `gridflow/src/gridflow/connectors/elexon/endpoints.py` and 33 vault dataset specs. On the site: 22 pages exist on disk (6 complete: `fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`; 16 broken stubs missing `#overview`/`#schema`/`#sample`/`#api` sections), 11 datasets have no site page yet (`atl`, `bmunits_reference`, `imbalngc`, `inddem`, `indgen`, `lolpdrm`, `market_depth`, `melngc`, `remit`, `soso`, `tsdfd`). v1 closes the gap.
- Massive duplication: ~30-line `<style>` block repeated in all 22 Elexon dataset HTML files; two scroll-spy script variants scattered across pages; per-page global `setTab()` redeclared 22 times.
- 26 modified files in-flight on this branch (uncommitted) doing a partial typography refactor and the start of the 'live → snapshot' honesty pivot — needs to be finished and committed.

**Audience reality:**
- Recruiters typically skim a portfolio site for 30–90 seconds before deciding whether to click through to the GitHub repos. The site has to land its credibility signal fast and reward deeper reading without requiring it.
- The author's own daily use is as a working reference — depth and navigation matter even when polish doesn't.

**Source-of-truth hierarchy (revised after vault audit 2026-05-17):**
1. **gridflow code** — `gridflow/src/gridflow/schemas/*.py` (Pydantic schemas), `silver/**/*.py` (silver transforms), `connectors/**/*.py` (endpoint definitions). The canonical truth for what each dataset is, returns, and how it lands. 33 active Elexon endpoints.
2. **Live API responses** — verified via `scripts/verify_curl_and_silver_schema.py` in the vault repo (last verified 2026-05-08, 33 endpoints all returned HTTP 200). Validates the gridflow schemas against reality.
3. **Obsidian Vault** (`C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\<vendor>\datasets\*.md`) — authored documentation layer, derived from #1 and #2 per the vault's own amendment plan. Has 33 Elexon datasets matching gridflow connector reality.
4. **On-site rendered pages** (`site/hifi/data-sources/<vendor>/<dataset>.html`) — published view, generated from vault content via the Python + Jinja2 build script at build/CI time. Deploy artifact stays pure-static HTML (Pages serves it directly).

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
| **v1 Elexon dataset scope = 33 (gridflow + vault reality), not 22 or 25** | User picked "Match reality (33)" after vault audit revealed gridflow connector has 33 endpoints and vault has 33 specs; 22-pages / 25-manifest / 28-claimed were all stale | — Pending |
| **Vault → site direction**: build script reads vault `.md` files, generates site HTML | User picked "Vault → site"; vault is the authored content layer (Codex has done initial mapping), site is the published view rendered from it | — Pending |
| **Templating mechanism: Python + Jinja2 build script (Option B), CI build** | User picked "Option B + CI build" — generated HTML is gitignored, deploy.yml runs `gridflow-build` before `upload-pages-artifact`; PRs stay small | — Pending |
| **ENTSO-E cross-vendor proof: Generation by PSR type** | User picked the template-stretching choice (different schema vocabulary, quarter-hour settlement in some markets) over the familiar shape of day-ahead prices | — Pending |
| Stub other vendor hubs (ENTSO-G, GIE, Open-Meteo, NESO) + ENTSO-E hub in v1 | User picked both as additional v1 items | — Pending |
| Defer more model case studies, real-data wiring, full ENTSO-E coverage, new visual identity | User did not pick "More model studies"; "actual data" snapshots ruled out; aesthetic kept | — Pending |
| Source-of-truth hierarchy (revised): gridflow code > live API > vault > on-site | Vault's own amendment-plan declares it derivative; gridflow code is canonical | — Pending |

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
