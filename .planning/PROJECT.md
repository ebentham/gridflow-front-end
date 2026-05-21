# Gridflow front-end

## What This Is

A static portfolio website that documents the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline and the gridflow-models modelling projects, framed for energy-trading recruiters. The site is hand-written HTML + CSS + vanilla JS deployed via GitHub Pages from `site/hifi/`. Twin audience: full-stack data-science recruiters in energy trading (primary), and the author themselves as a working catalog of UK/EU power & gas data sources and trading models (secondary). Explicitly **not** a product, not a dashboard — no fake live indicators, no SaaS-style KPIs.

## Core Value

**When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data."**

Domain depth wins every tradeoff: depth of dataset documentation > visual polish > breadth of vendor coverage > novel features.

## Current Milestone: v2 full-vendor-coverage

**Goal:** Move every vendor on the site from "coming soon" to a complete dataset catalog. A recruiter clicks any vendor, sees a full dataset list; clicks any dataset, gets `fuelhh`-fidelity documentation (schema · sample · API · caveats · related). Ship 129 new dataset pages across ENTSO-E (48 new), ENTSO-G (33), GIE (8), NESO (34), and Open-Meteo (6) — total catalogue across 6 vendors reaches 163 datasets. **Front-loaded with a Reconciliation phase (per ADR-0001, 2026-05-19) that reconciles every Vendor's Vault layer against the Canonical before any content phase ships.**

**Target features:**
- Reconcile the Vault layer: wrap the existing verifier as `gridflow-drift-check`, run Verification across all 6 Vendors, triage every Drift finding, fix the `open` bucket, and commit the upstream Vault to a private GitHub repo (`EBentham/quant-vault`) per ADR-0002
- Diagnose and fix the dataset-page top-of-page formatting bug (confirmed on `fuelhh.html`) before scaling (parallel-eligible with the Reconciliation phase per ADR-0001 D-03)
- Render the remaining 48 ENTSO-E datasets at `fuelhh` fidelity; upgrade ENTSO-E hub from 1-dataset proof to a 49-dataset catalog (the ENTSO-E entitlement decision lands in this phase's discuss-phase per Phase 7 D-06)
- Render ENTSO-G (33), GIE (8), NESO (34), Open-Meteo (6) at `fuelhh` fidelity; upgrade their hubs from coming-soon stubs to real catalogs
- Keep `gridflow-build` idempotent, CI-gated, and vault-driven across the expanded surface

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
- ✓ `gridflow-build` CLI (Python 3.11+ + Jinja2 3.1.x) over Obsidian Vault content, idempotent, CI-gated — shipped v1 Phase 3 (PR #6)
- ✓ `dataset.html.j2` + `vendor-hub.html.j2` + `vendor-coming-soon.html.j2` Jinja2 templates capturing the full page anatomy — shipped v1 Phase 3 (PR #6)
- ✓ 33 Elexon dataset pages at `fuelhh` fidelity, generated from vault content — shipped v1 Phase 3
- ✓ ENTSO-E cross-vendor proof: hub + `actual_generation` dataset at `fuelhh` fidelity — shipped v1 Phase 4 (PR #7)
- ✓ 5 coming-soon vendor stubs (ENTSO-G · GIE AGSI · GIE ALSI · Open-Meteo · NESO) — shipped v1 Phase 4 (acts as scaffolding for v2 upgrades)
- ✓ Honesty sweep (zero `live` framing surfaces), mobile CSS (≤480px / ≤720px), a11y minimums (`<main>`, `aria-current`, `aria-label`, `aria-hidden`) — shipped v1 Phase 5 (PR #8)
- ✓ CI gates: `htmlhint` + `lychee` + `gridflow-build --check` idempotence — shipped v1 Phase 6 (PR #9 + #10 + #11)
- ✓ Vendored vault snapshot in-repo at `vault/elexon/` (33 files) + `vault/entsoe/` (1 file) — shipped v1 (CI cannot clone the upstream non-public `quant-vault`)
- ✓ MIT license at repo root with consistent inline strings; `.gitattributes` line-ending normalisation — shipped v1 Phase 0–1
- ✓ Shared CSS/JS extracted: no dataset-page inline `<style>`, one scroll-spy `IntersectionObserver`, `[data-tabs]` convention site-wide — shipped v1 Phase 2 (PR #5)

### Active

<!-- v2 full-vendor-coverage milestone. Rescoped 2026-05-19 per ADR-0001: new Phase 7 (Reconciliation) inserted ahead of content phases; existing Phases 7/8/9 renumbered to 8/9/10. -->

**Reconciliation (Phase 7, gating for content phases 9 and 10):**
- [ ] Wrap `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` as the `gridflow-drift-check` console script; fix the two Windows-specific portability blockers
- [ ] Run Verification across all 6 Vendors; produce JSON + markdown reports; emit a finding file under `.planning/reconciliation/<vendor>/<NN>-<slug>.md` for every Drift instance
- [ ] Triage every finding into `open` (fixable in v2) / `wontfix` `reason: v3-candidate` (needs gridflow code changes) / `needs-info` `reason: defer-entitlement` (e.g. ENTSO-E entitlement)
- [ ] Fix the `open` bucket: edit the upstream Vault, re-vendor into `gridflow-front-end/vault/<vendor>/`; re-run `gridflow-drift-check` to confirm no new Drift
- [ ] Commit the upstream Vault to a new private GitHub repo `EBentham/quant-vault` per ADR-0002; no GitHub App auth

**Dataset-page formatting bug (Phase 8, gating for content phases 9 and 10; parallel-eligible with Phase 7):**
- [ ] Diagnose the top-of-page formatting bug confirmed on `fuelhh.html`; root-cause in template/CSS/vault content
- [ ] Apply the fix and verify it propagates cleanly to all 34 existing dataset pages via `gridflow-build`
- [ ] No regression on the v1 honesty / a11y / mobile guarantees

**ENTSO-E full coverage (48 new datasets + hub upgrade):**
- [ ] Vendor 48 new `.md` files into `vault/entsoe/` from upstream `quant-vault/30-vendors/entsoe/datasets/`
- [ ] Author / extend `site/hifi/data/entsoe.json` manifest with 49 dataset entries (1 existing + 48 new), grouped into ENTSO-E categories
- [ ] Build all 49 ENTSO-E dataset pages at `fuelhh` fidelity via `gridflow-build`
- [ ] Upgrade `data-sources/entsoe.html` hub from 1-dataset proof to 49-dataset catalog (built from the expanded manifest)
- [ ] Every page: 6-anchor sidebar resolves to real `<section id>`s; verified-against-vendor-docs micro-line; schema reference (or drift-surface flag)

**Remaining four vendors at depth (81 new datasets + 4 hub upgrades):**
- [ ] Vendor `.md` files into `vault/entsog/` (33), `vault/gie/` (8), `vault/neso/` (34), `vault/openmeteo/` (6) from upstream `quant-vault`
- [ ] Author manifests `data/entsog.json`, `data/gie.json` (covers both AGSI + ALSI), `data/neso.json`, `data/openmeteo.json`
- [ ] Build all 81 dataset pages at `fuelhh` fidelity via `gridflow-build`
- [ ] Replace the 5 coming-soon stubs (entsog · gie_agsi · gie_alsi · openmeteo · neso) with real vendor hubs rendered from `vendor-hub.html.j2`
- [ ] `data-sources.html` catalog rows updated: every vendor now links to a real hub, every dataset count reflects the new totals (162 → 163 site-wide)

**Cross-cutting:**
- [ ] `gridflow-build --check` stays green on the expanded set; idempotence CI gate holds across 163 pages
- [ ] `htmlhint` + `lychee` gates stay green on the expanded set; no new dead anchors or structural HTML breakage
- [ ] Site-wide dataset count strings (footer, index stat strip) updated to reflect the new total

### Out of Scope

<!-- Explicit boundaries with reasoning. -->

- **Additional model case studies (SRMC, full power stack, renewable forecast)** — Deferred; demand-forecast already covers the "we have models" point. Not in v2 scope
- **Real Elexon / ENTSO-E / other vendor API wiring + live data ingestion** — Illustrative snapshots only; a "live wiring" milestone is plausible but not committed. Drift-detection research lives at `.planning/research/post-v1/drift-detection/`
- **Pydantic schema drift fix on the 22 Elexon datasets rendered with `drift-surface flagged`** — Considered for v2, explicitly deferred: closing the gap means declaring `ElexonAGPT`, `ElexonAGWS`, `ElexonFOU2T14D`, etc. in `gridflow.schemas.elexon` (cross-repo work) and re-running build. v3 candidate
- **Per-dataset related-card blurbs (hand-curated "Pair with X to do Y" copy)** — Considered for v2, deferred. Restoring via a `related_blurbs:` vault frontmatter field is a v3 candidate
- **`fuelhh` fuel-pill grid (16-pill colour swatch)** — Dataset-specific markup retired by the shared template. Restoring via a `fuel_types: [...]` vault frontmatter field is a v3 candidate
- **New visual identity / design system rebuild** — Current cream/forest/Fraunces serves the purpose; revisit only if evidence demands it
- **Adopting a Node/Go SSG (11ty, Astro, Hugo)** — Rejected after research: introduces a non-Python toolchain to a Python-first portfolio for negligible benefit. v1 uses Python + Jinja2; v2 stays on the same pipeline
- **Live performance metrics, uptime badges, dashboard-y elements** — Explicitly anti-goal; would imply the site is a product
- **Real-time data fetches from the browser** — Deferred; everything ships static
- **Bronze/silver gold-layer pipeline visualisations or a SQL playground** — Deferred; documentation site, not an interactive demo

## Context

**Sibling projects this site documents:**
- `gridflow` (github.com/EBentham/gridflow) — Python ETL pipeline that standardises UK/EU power & gas market data (Elexon BMRS, ENTSO-E Transparency Platform, ENTSO-G, GIE, Open-Meteo, NESO Carbon Intensity) into a medallion-architecture (bronze/silver/gold) DuckDB warehouse with Pydantic schemas and Polars transforms
- `gridflow-models` (github.com/EBentham/gridflow-models) — modelling layer built on gridflow: short-run marginal cost (SRMC) model, full power-stack model, demand forecasting, renewable forecasting

**Tech context (post-v1):**
- Static site with a build step. `gridflow-build` (Python 3.11+ + Jinja2 3.1.x) reads vendored vault `.md` files under `vault/<vendor>/` and renders to `site/hifi/data-sources/<vendor>/<dataset>.html` via the `dataset.html.j2`, `vendor-hub.html.j2`, and `vendor-coming-soon.html.j2` templates. Generated HTML is gitignored. CI runs `gridflow-build` before `upload-pages-artifact`.
- Python 3.11+ dev server (`gridflow-serve`, stdlib only); deploy is GitHub Pages off the built `site/hifi/` tree.
- Shared chrome injected at runtime by `site/hifi/assets/site.js` from a body `data-page` / `data-root` / `data-screen-label` attribute contract. Single scroll-spy `IntersectionObserver`, `[data-tabs]` convention site-wide. No inline `<style>` blocks on dataset pages.
- **Dataset reality (v1 shipped):** 33 Elexon dataset pages at `fuelhh` fidelity + ENTSO-E hub + 1 ENTSO-E dataset (`actual_generation`) + 5 coming-soon vendor stubs. Total live pages: 34 dataset pages.
- **Vault reality (live vault):** 163 dataset specs across 6 vendors — Elexon 33, ENTSO-E 49, ENTSO-G 33, GIE 8, NESO 34, Open-Meteo 6. This repo's `vault/` snapshot currently holds Elexon 33 + ENTSO-E 1 (the rest vendor in during v2).
- **Known bug entering v2 (gating):** Dataset pages have incorrect formatting at the top of the page, confirmed on `fuelhh.html`. Must be diagnosed and fixed before scaling 129 new pages off the same template.
- CI green: `htmlhint` (custom `.htmlhintrc` with `attr-value-double-quotes` and `spec-char-escape` disabled), `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence all gate deploy.

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
| Editorial / quiet aesthetic; keep current cream-forest + Fraunces identity | User selected from Stripe Press / FT Alphaville framing; current look serves the purpose | ✓ Validated (v1) |
| Recruiter-first audience: full-stack data scientist in energy trading (code + ML + domain) | User explicitly prioritised recruiter over self-reference | ✓ Validated (v1) |
| Core value = domain depth over polish, gateway, or personal reference | User chose depth from explicit options | ✓ Validated (v1) |
| Kill all 'live' framing — site is a documentation site, charts/numbers are illustrative | User chose "Kill all 'live'" + "Illustrative / shape only" | ✓ Validated (v1, HON-01) |
| **v1 Elexon dataset scope = 33** (gridflow + vault reality, not 22 / 25) | gridflow connector has 33 endpoints; vault has 33 specs; 22-pages / 25-manifest / 28-claimed were all stale | ✓ Validated (v1, ELX-05) |
| **Vault → site direction**: build script reads vault `.md`, generates site HTML | Vault is the authored content layer (Codex did initial mapping); site is the published view rendered from it | ✓ Validated (v1, VAULT-01) |
| **Templating mechanism: Python + Jinja2 build script (Option B), CI build** | Generated HTML gitignored; deploy.yml runs `gridflow-build` before `upload-pages-artifact`; PRs stay small | ✓ Validated (v1, BUILD-01..08) |
| **ENTSO-E cross-vendor proof: Generation by PSR type** | Template-stretching choice (different schema vocabulary, quarter-hour settlement) over familiar day-ahead-prices shape | ✓ Validated (v1, VEND-02) |
| Stub other vendor hubs (ENTSO-G, GIE, Open-Meteo, NESO) + ENTSO-E hub in v1 | Coming-soon stubs render from `vendor-coming-soon.html.j2`; v2 upgrades them to real hubs | ✓ Validated (v1, VEND-04) |
| Source-of-truth hierarchy (revised): gridflow code > live API > vault > on-site | Vault's own amendment-plan declares it derivative; gridflow code is canonical | ✓ Validated (v1) |
| **v1 Decision: Vault vendored in-repo at `vault/<vendor>/`, not cross-repo checkout** | Upstream `quant-vault` is not a GitHub repo, so CI cannot clone it. `--vault-path` / `$GRIDFLOW_VAULT_PATH` enables local dev against the live vault; CI uses the vendored snapshot | ✓ Locked (v1) — v2 extends snapshot to all 6 vendors |
| **v1 Decision: Pydantic class drift policy = render-with-flag** | 22 of 33 Elexon datasets render "no dedicated Pydantic class declared yet — drift-surface flagged" rather than block the build. Honest gap-surfacing over fake-coverage | ✓ Locked (v1) — closing the gap is a v3 candidate |
| **v1 Decision: Templates born honest** | `dataset.html.j2` never emits `chip live`, `LAST FETCH`, `N min ago`, or time-window pill chips. HON-01 grep checklist returns zero hits on generated pages by construction | ✓ Locked (v1) — v2 inherits the honest template |
| **v2 Decision (rescoped 2026-05-19): Phase shape = Reconciliation + bug fix + ENTSO-E + batch the rest (4 phases)** | Phase 7: Reconciliation (gating for content phases). Phase 8: bug fix (parallel-eligible with Phase 7). Phase 9: ENTSO-E full coverage (48 new — biggest, proves template handles vendor stretch at scale). Phase 10: batch ENTSO-G + GIE + NESO + Open-Meteo (81 mechanical pages, template is proven by then). Per ADR-0001 and Phase 7 D-05 | — Pending (v2) |
| **v2 Decision: ~~Assume vault content complete; no upfront audit phase~~ (OVERRIDDEN 2026-05-19 by ADR-0001)** | `gridflow-build --check` is an *idempotence* check, not a content-accuracy check; drift research surfaced real shipped Drift on the live Site (`ndf`/`ndfd`/`fuelhh` `published_at` omission · 33 ENTSO-E 401s · ENTSO-G `physical_flows` 35-field mismatch). The accuracy constraint in § Constraints made the original decision untenable. See ADR-0001 | ✗ Overridden by Phase 7 (Reconciliation) |
| **v2 Decision (2026-05-19): Vault is committed to a new private GitHub repo `EBentham/quant-vault`, no GitHub App auth** | Phase 7's Reconciliation work needs the Vault to be version-controlled. Private over public (privacy on a recruiter-facing portfolio); no GitHub App because cross-repo automated drift CI is not yet load-bearing for v2. Vendoring pattern (`gridflow-front-end/vault/<vendor>/` as snapshot) is preserved. See ADR-0002 | — Pending (v2, Phase 7d) |
| **v2 Decision (2026-05-19): Reconciliation findings live as local markdown under `.planning/reconciliation/<vendor>/`, not GitHub Issues** | Avoids splitting workflow context across two systems. Matches the existing single-context discipline. Canonical labels per `docs/agents/triage-labels.md` (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/issue-tracker.md` | — Pending (v2, Phase 7b/c) |
| **v2 Decision (2026-05-19): Pocock skill set (`to-issues`, `triage`) for Phase 7's exploratory work; GSD for pre-planned phases** | Phase 7 has inherent open-endedness — Verification surfaces unknown findings; Pocock's capture-triage-act shape fits better than GSD's task-list shape. Phases 8/9/10 stay on standard GSD flow | — Pending (v2, Phase 7b/c) |
| **v2 Decision (2026-05-19): ENTSO-E entitlement (33 HTTP 401 cases) deferred from Phase 7 to Phase 9 discuss** | Phase 7 only triages as `needs-info`/`defer-entitlement`; the actual resolution (extend access vs `skip-with-warn`) binds on content shape which Phase 9 owns. Avoids blocking Phase 7 on unbounded vendor lead-time | — Pending (Phase 9 discuss) |
| **v2 Decision: Strict scope discipline — no drift fix, related blurbs, or fuel-pill restoration** | All three are real gaps but v2 stays narrow on "full vendor coverage" + Reconciliation. v3 candidates: Pydantic drift closure (declaring `ElexonAGPT` / `ElexonAGWS` / etc.), `related_blurbs:` vault field, `fuel_types: [...]` vault field. Phase 7 explicitly triages the 22 Elexon `manual_transformer_schema` cases as `wontfix`/`v3-candidate` | — Pending (v2) |

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
*Last updated: 2026-05-19 — v2 milestone rescoped per `docs/adr/0001-reconciliation-phase-added-to-v2.md` and `docs/adr/0002-vault-hosted-private-github-repo.md`. New Phase 7 (Reconciliation) inserted at start of v2; existing Phases 7/8/9 renumbered to 8/9/10. Initial v2 milestone start was 2026-05-18 after v1 completion (50/50 REQ-IDs delivered, deployed at https://ebentham.github.io/gridflow-front-end/).*
