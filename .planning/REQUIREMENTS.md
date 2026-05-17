# Requirements

Scope: **v1 cleanup milestone** — credibility-recovery pass on the gridflow-front-end portfolio site. Aligns the site to gridflow connector + vault reality (33 active Elexon datasets), introduces a Python+Jinja2 build script over vault content, kills fake-liveness framing, and ships an ENTSO-E cross-vendor proof.

REQ-IDs are stable references used by `ROADMAP.md` traceability.

## v1 Requirements

### Repo hygiene (HYG)
- [ ] **HYG-01** — The 26-file in-flight refactor is split into 4 logical commits and pushed (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks)
- [ ] **HYG-02** — `.gitattributes` committed at repo root with `*.html text eol=lf` plus the same rule for `*.css`, `*.js`, `*.json`, `*.py` (stops CRLF churn between Windows-edits and Linux-CI deploys)

### Main pages (PAGE)
- [ ] **PAGE-01** — Home page (`site/hifi/index.html`) reads as editorial/quiet, uses honest framing throughout (no fake live indicators, no fake "shipping" badges), correctly states 33 Elexon datasets in its stat strip
- [ ] **PAGE-02** — Architecture page (`site/hifi/architecture.html`) passes a polish pass on its writing + diagrams; structure stays from the recent redesign
- [ ] **PAGE-03** — Data-sources hub (`site/hifi/data-sources.html`) has zero dead `<a href="#">` placeholder links; every vendor card resolves to a real vendor page or a coming-soon stub page
- [ ] **PAGE-04** — All three main pages render mobile-functional at ≤480px (no horizontal scroll, no overflow, mobile menu reachable)

### Build mechanism (BUILD)
- [ ] **BUILD-01** — `gridflow-build` console script (Python 3.11+ + Jinja2 3.1.x) exists, exposed in `pyproject.toml`
- [ ] **BUILD-02** — Jinja2 lives only in a `[build]` extras group in `pyproject.toml`; `gridflow-serve` runtime stays Python-stdlib-only
- [ ] **BUILD-03** — `dataset.html.j2` template captures the 7-section dataset-page anatomy (hero · metadata grid · stats strip · sticky sidebar · overview · snapshot chart · schema table · sample table · API tabs · numbered caveats · related cards)
- [ ] **BUILD-04** — `vendor-hub.html.j2` template captures the vendor-hub structure (hero · vendor metadata · category card grids · stats strip)
- [ ] **BUILD-05** — `vendor-coming-soon.html.j2` template captures the visually-distinct coming-soon layout (no sidebar, no chart container, single-screen, "Planned · F<n>" stage chip)
- [ ] **BUILD-06** — Build is idempotent: running `gridflow-build` twice produces no diff in the output directory
- [ ] **BUILD-07** — Generated HTML is gitignored under `site/hifi/data-sources/*/` (or equivalent); `.github/workflows/deploy.yml` runs `gridflow-build` before `actions/upload-pages-artifact@v3`
- [ ] **BUILD-08** — Build regenerates the 6 currently-complete pages (fuelhh, fuelinst, agpt, agws, nonbm, windfor) to byte-equivalent state vs the current files — validates the template captures existing fidelity before any new content lands

### Vault integration (VAULT)
- [ ] **VAULT-01** — Build script reads per-dataset content from the Obsidian Vault (`<vault>/30-vendors/<vendor>/datasets/*.md`) using the existing frontmatter + body convention
- [ ] **VAULT-02** — Vault path is configurable (env var `GRIDFLOW_VAULT_PATH` or build-time CLI flag) so CI can checkout both repos and the local dev loop can point at the developer's vault checkout
- [ ] **VAULT-03** — Per-dataset content audit pass: missing/stale sections in a dataset's vault `.md` are surfaced by the build (`gridflow-build --check`) before render; the build fails if a dataset declared in-scope for v1 lacks required sections
- [ ] **VAULT-04** — The vault → site mapping is documented in `README.md` (which vault sections feed which template sections), so a future contributor can edit either side without breaking the contract

### Elexon dataset depth (ELX) — 33 datasets at fuelhh fidelity
- [ ] **ELX-01** — All 6 existing complete dataset pages (`fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`) regenerate from the new template + vault content with byte-equivalent (or better-with-rationale) output
- [ ] **ELX-02** — All 16 broken dataset stubs (`boal`, `disbsad`, `fou2t14d`, `freq`, `indo`, `indod`, `itsdo`, `mid`, `ndf`, `ndfd`, `netbsad`, `pn`, `system_prices`, `temp`, `tsdf`, `uou2t14d`) ship at fuelhh fidelity, populated from vault content
- [ ] **ELX-03** — The 3 manifest-only datasets (`remit`, `bmunits_reference`, `soso`) ship as full dataset pages, populated from vault content
- [ ] **ELX-04** — The 8 vault-only datasets (`atl`, `imbalngc`, `inddem`, `indgen`, `lolpdrm`, `market_depth`, `melngc`, `tsdfd`) are added to `data/elexon.json` AND ship as full dataset pages
- [ ] **ELX-05** — `data/elexon.json` lists 33 datasets, grouped into the existing 4 categories (generation / prices-balancing / demand-forecasts / system-reference); footer/index/catalog-UI all show 33 (no other count appears anywhere)
- [ ] **ELX-06** — Every dataset page's sidebar anchors (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) resolve to existing `<section id>` elements in the rendered HTML (no phantom-coverage anchors)
- [ ] **ELX-07** — Every dataset page shows a `verified-against-vendor-docs: YYYY-MM-DD` micro-line linking to the specific Elexon BMRS doc page for that dataset (drives the recruiter spot-check confidence)
- [ ] **ELX-08** — Every dataset page shows the matching Pydantic schema class name (`gridflow/schemas/elexon.py · ElexonFuelHH` etc.) as an inline `<code>` reference, bridging the site to the gridflow source

### Cross-vendor proof (VEND)
- [ ] **VEND-01** — ENTSO-E vendor hub page exists at `site/hifi/data-sources/entsoe.html`, rendered via `vendor-hub.html.j2`
- [ ] **VEND-02** — ENTSO-E "Generation by PSR type" dataset page exists at `site/hifi/data-sources/entsoe/<slug>.html` at fuelhh fidelity, with vault-sourced content, demonstrating the template handles quarter-hour settlement + PSR-type taxonomy
- [ ] **VEND-03** — `site/hifi/data/entsoe.json` manifest exists with at least the one shipped dataset entry
- [ ] **VEND-04** — 5 coming-soon vendor stub pages exist for ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO Carbon Intensity — each rendered from `vendor-coming-soon.html.j2`, visually distinct from real vendor hubs (no sidebar, no chart, single-screen layout, "Planned · F<n>" stage chip)
- [ ] **VEND-05** — Every `<a href="#">` placeholder vendor row on `data-sources.html` is replaced with a real link to a vendor hub page or a coming-soon stub page

### Honesty sweep (HON)
- [ ] **HON-01** — All 6 "live"-framing surfaces removed in one atomic pass with a `grep` checklist producing zero hits in `site/hifi/`: (a) hero `<span class="chip live">` badges, (b) hero `LAST FETCH · N min ago` stat-card text, (c) footer `last sync` string in `site.js`, (d) time-window tab pills on snapshot charts (which don't actually switch anything), (e) related-card live chips, (f) hardcoded build-version footer string
- [ ] **HON-02** — Charts and numbers carry an explicit "Illustrative snapshot" chip (per chart, not page-level banner) — the framing makes it confidently honest, not apologetic
- [ ] **HON-03** — Footer build-version string removed; replaced with a static "Documentation site · cream paper · last updated YYYY-MM-DD" line tied to last actual edit (acceptable to be hand-updated each milestone)
- [ ] **HON-04** — License contradiction resolved: one license chosen (MIT vs Apache-2.0), `LICENSE` file at repo root, all inline strings in HTML/JS reference the chosen license consistently

### Accessibility minimums (A11Y)
- [ ] **A11Y-01** — Every page wraps its primary content in a `<main>` landmark
- [ ] **A11Y-02** — `aria-current="page"` on the active top-nav link; `aria-current="location"` (or `="true"`) on the active sidebar link
- [ ] **A11Y-03** — Decorative icons (arrows `→`, dots `•`, hamburger SVG, chip dots) carry `aria-hidden="true"`
- [ ] **A11Y-04** — Both `<nav>` elements on dataset pages have distinguishing `aria-label`s (e.g. `aria-label="Site"` for the injected top-nav, `aria-label="On this page"` for the sidebar)
- [ ] **A11Y-05** — Sidebar inactive items' hover affordance works (the inline `color:var(--ink-faint)` replaced with a CSS class so `:hover` can override)
- [ ] **A11Y-06** — Both external `target="_blank"` links currently missing `rel="noopener"` get it added (`architecture.html` line ~1156, `data-sources/elexon.html` line ~41)

### Mobile / responsive (MOB)
- [ ] **MOB-01** — Viewport meta tag fixed on all 23 currently-broken pages: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] **MOB-02** — Dataset-page CSS adds proper responsive rules in `theme.css` for `@media (max-width: 720px)` and `@media (max-width: 480px)` blocks — sidebar collapses, hero stacks vertically, stats strip reflows, no fixed `min-width` values that cause horizontal scroll
- [ ] **MOB-03** — Mobile menu toggle (`site.js`) reaches every page (the `width=1280` viewport bug previously prevented it from triggering)

### Structural refactor (REF)
- [ ] **REF-01** — The ~30-line `<style>` block duplicated in all 22 Elexon dataset HTML files is moved to `site/hifi/assets/theme.css`; no dataset page has an inline `<style>` block (except for truly page-specific rules like `.fuel-grid` on fuelhh)
- [ ] **REF-02** — The two scroll-spy IIFE variants (minified + un-minified) consolidated into a single helper in `site.js`, gated by `data-page="dataset"` or by presence of `.sidebar`
- [ ] **REF-03** — The per-page global `setTab(group, tab, btn)` declarations and inline `onclick="setTab(...)"` handlers replaced with the existing `[data-tabs]` convention already used on `index.html`

### CI / validation (CI)
- [ ] **CI-01** — `htmlhint` (or equivalent) runs on `site/hifi/**/*.html` (or build output) in `.github/workflows/deploy.yml` before `upload-pages-artifact` — catches structural HTML breakage of the broken-stub class
- [ ] **CI-02** — `lychee` (or equivalent link checker) runs on the built site before deploy — catches dead-link regressions
- [ ] **CI-03** — Build-script idempotence smoke test: CI runs `gridflow-build` twice and fails if `git diff` of the output directory is non-empty

## v2 Requirements (Deferred)

These were explicitly considered and deferred to a later milestone:

- More model case studies: SRMC, full power-stack, wind forecast, solar forecast, fundamentals SMP
- Real Elexon API wiring — nightly snapshot regeneration via GitHub Actions, page renders the regenerated snapshot ("Shipping" status for one dataset)
- ENTSO-E dataset coverage beyond "Generation by PSR type" (full vendor depth)
- ENTSO-G / GIE / Open-Meteo / NESO at dataset depth (each becomes its own per-vendor milestone)
- Search UI / dark mode / blog index
- Auto-generation of dataset-page schema rows from gridflow Pydantic schemas (cross-repo schema-as-source-of-truth wiring — would eliminate schema drift structurally)
- Self-hosting Google Fonts (cold-load TTI optimisation; current preconnect+font-display swap is acceptable)

## Out of Scope

These are explicit boundaries — included with reasoning to prevent re-adding:

- **Adopting a Node/Go SSG (11ty / Astro / Hugo)** — Rejected after research; introduces a non-Python toolchain to a Python-first portfolio for negligible benefit at ~50-page scale. v1 uses a small Python + Jinja2 build script (the "middle path") instead
- **Live performance metrics, uptime badges, dashboard-y elements** — Anti-goal per PROJECT.md; would imply the site is a SaaS product, not a portfolio documentation site
- **Real-time data fetches from the browser** — Deploy artifact stays pure-static; any "live" semantics goes through a build-time regeneration mechanism in a future milestone
- **New visual identity / design system rebuild** — Current cream/forest/Fraunces aesthetic stays; revisit only if evidence demands it
- **Hand-authored dataset pages bypassing the build script** — Once Option B lands, every dataset page MUST be generated from vault + manifest. No exceptions; otherwise the single-source-of-truth claim breaks
- **Author photos, testimonials, hire-me CTAs, blog index** — Editorial-quiet aesthetic; not a personal brand site

## Traceability

Every REQ-ID maps to exactly one phase in `ROADMAP.md`. 50/50 coverage; no orphans.

| REQ-ID | Phase | Status |
|--------|-------|--------|
| HYG-01 | Phase 0 — Commit in-flight refactor | Pending |
| HYG-02 | Phase 0 — Commit in-flight refactor | Pending |
| MOB-01 | Phase 1 — Trivial bug fixes | Pending |
| HON-04 | Phase 1 — Trivial bug fixes | Pending |
| A11Y-06 | Phase 1 — Trivial bug fixes | Pending |
| REF-01 | Phase 2 — Shared CSS/JS extraction | Pending |
| REF-02 | Phase 2 — Shared CSS/JS extraction | Pending |
| REF-03 | Phase 2 — Shared CSS/JS extraction | Pending |
| A11Y-05 | Phase 2 — Shared CSS/JS extraction | Pending |
| BUILD-01 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-02 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-03 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-04 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-05 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-06 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-07 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| BUILD-08 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| VAULT-01 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| VAULT-02 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| VAULT-03 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| VAULT-04 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-01 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-02 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-03 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-04 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-05 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-06 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-07 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| ELX-08 | Phase 3 — Build mechanism + Elexon dataset depth | Pending |
| VEND-01 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| VEND-02 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| VEND-03 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| VEND-04 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| VEND-05 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| PAGE-03 | Phase 4 — Cross-vendor proof + dead-link real fix | Pending |
| HON-01 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| HON-02 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| HON-03 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| MOB-02 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| MOB-03 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| A11Y-01 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| A11Y-02 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| A11Y-03 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| A11Y-04 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| PAGE-01 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| PAGE-02 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| PAGE-04 | Phase 5 — Honesty + a11y + mobile + main-page polish | Pending |
| CI-01 | Phase 6 — CI validation | Pending |
| CI-02 | Phase 6 — CI validation | Pending |
| CI-03 | Phase 6 — CI validation | Pending |

**Coverage check:** 50 REQ-IDs mapped to 7 phases. Each REQ-ID appears exactly once. Each phase has at least 2 REQ-IDs. No orphans.

**Category distribution across phases:**

| Category | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Total |
|----------|---------|---------|---------|---------|---------|---------|---------|-------|
| HYG | 2 | – | – | – | – | – | – | 2 |
| PAGE | – | – | – | – | 1 | 3 | – | 4 |
| BUILD | – | – | – | 8 | – | – | – | 8 |
| VAULT | – | – | – | 4 | – | – | – | 4 |
| ELX | – | – | – | 8 | – | – | – | 8 |
| VEND | – | – | – | – | 5 | – | – | 5 |
| HON | – | 1 | – | – | – | 3 | – | 4 |
| A11Y | – | 1 | 1 | – | – | 4 | – | 6 |
| MOB | – | 1 | – | – | – | 2 | – | 3 |
| REF | – | – | 3 | – | – | – | – | 3 |
| CI | – | – | – | – | – | – | 3 | 3 |
| **Total** | **2** | **3** | **4** | **20** | **6** | **12** | **3** | **50** |
