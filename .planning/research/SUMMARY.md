# Project Research Summary

**Project:** gridflow-front-end
**Domain:** Editorial portfolio + UK/EU energy-data documentation static site
**Researched:** 2026-05-17
**Confidence:** HIGH

## Executive Summary

The v1 cleanup milestone is **not a feature build; it is a credibility-recovery pass on an existing static site** whose canonical reference pages (`fuelhh.html`, `demand-forecast.html`) already define the fidelity bar. All four research streams converge on the same execution shape: commit the 26-file in-flight refactor first (Phase 0), extract duplicated CSS/JS to shared assets (Phase 2 unblocks everything downstream), introduce a small Python + Jinja2 build script over the existing `data/elexon.json` manifest as the "middle path" between hand-editing 22 files forever and adopting a full SSG (Phase 3), then prove the cross-vendor template with ENTSO-E (Phase 4), and run a single atomic honesty sweep that touches all six liveness surfaces at once (Phase 5). Two findings are load-bearing for the planner: **CSS extraction can ship before the templating decision is made and benefits every path**, which lowers the stakes of the Option A vs Option B decision; and **the dataset-count discrepancy (22 pages on disk · 25 manifest IDs · 28 claimed in UI) is structurally upstream of the depth pass** — it must be resolved (likely by absorbing the 3 missing datasets into the manifest count) before regenerated pages can render counts honestly. The single highest risk is a partial honesty pivot: touching only some of the six "live"-framing surfaces is worse than touching none, because the contradiction between honest prose and lying chrome reads as carelessness rather than as work-in-progress.

## Key Findings

### Recommended Stack

The recommendation is **Option B — a ~150–200 line Python build script + Jinja2 templates** running over the existing `site/hifi/data/elexon.json` manifest, as a sibling to the existing `gridflow-serve` CLI. Build inputs live in a new `build/` directory at repo root; generated HTML lands in the same `site/hifi/data-sources/<vendor>/` paths it occupies today. GitHub Pages still deploys `site/hifi/` unchanged. Jinja2 goes in a `[build]` extra in `pyproject.toml`; the deployed artefact stays pure static; the `gridflow-serve` dev server stays stdlib-only. This is *not* an SSG adoption — 11ty/Astro/Hugo were evaluated and rejected because they introduce a Node ecosystem to a Python-first portfolio and offer no benefit at ~50-page scale. Full alternatives matrix and version pins in `.planning/research/STACK.md`.

**Core technologies:**
- **Python 3.11+** — already the author's runtime; sibling projects are Python; reads as deliberate craft for a Python/data portfolio
- **Jinja2 3.1.6** — industry-standard Python templating; single build-time dependency; solves the 22-file duplication without a node toolchain
- **HTML5 / CSS3 / vanilla JS (ES2017+)** — unchanged; GitHub Pages serves the build output directly
- **uv + pytest + ruff + mypy** — per user global preferences; cheap smoke tests on generated HTML
- **htmlhint / lychee** — CI-side pre-deploy link/HTML validation, catches the exact bug class motivating the milestone

### Expected Features

The dataset-page anatomy is **a fixed 7-section template** (hero + metadata card · stats strip · sticky sidebar · overview · snapshot chart · schema + sample · API tabs · numbered caveats · related-cards), extracted directly from the user-confirmed `fuelhh.html` reference. The model case study anatomy mirrors academic paper structure (Question → Inputs → Estimator → Validation → Caveats → What's next) from `demand-forecast.html`. Full anatomy, anti-feature classification, and benchmark-site cross-references in `.planning/research/FEATURES.md`.

**Must have (table stakes for v1):**
- Mobile-functional viewport on all pages (the 23-page `width=1280` bug is recruiter-bounce-class)
- All 22 Elexon dataset pages at fuelhh fidelity — 7-section anatomy, numbered caveats with specific failure modes (not generic disclaimers)
- Honesty sweep complete across all six surfaces (see "Cross-cutting findings" below)
- Reconciled dataset count (one number, one source, propagated everywhere)
- One ENTSO-E vendor hub + 1 ENTSO-E dataset at fuelhh fidelity (cross-vendor template proof)
- Distinctly-styled "coming soon" landing pages for ENTSO-G, GIE, Open-Meteo, NESO (NOT the same chrome as real vendor hubs — see Pitfall 9)
- A11y minimums: `<main>` landmark, `aria-current="page"`, `aria-hidden` on decorative icons, sidebar hover fix
- One license decision, `LICENSE` file at repo root, aligned inline strings
- Obsidian Vault sync to `gridflow/quant-vault/30-vendors/` (ship last in milestone; on-site → vault direction)

**Should have (differentiators):**
- Tab group on API section (URL / DuckDB SQL / Python parquet) — three angles on the same data
- Inline `code` references to the Pydantic schema class name (`gridflow/schemas/elexon.py · ElexonFuelHH`) bridging site claims to sibling-repo code
- Per-page `verified-against-vendor-docs: YYYY-MM-DD` micro-line + link to specific vendor doc page
- "Why X not Y?" callouts (the `demand-forecast.html` pattern, e.g. "Why indo not itsdo?") — surfaces the rejected alternative
- Inline ADR cross-references (`per ADR-014`) anchoring decisions to a numbered system
- Stage labels (`Shipping · Planned · F6 · Planned · F7`) instead of dates or "coming soon"

**Defer (v2+, explicitly out of scope per PROJECT.md):**
- Wire `data/*.json` manifests to render vendor-hub cards via `site.js fetch()` at runtime (build-time generation is the right answer until ~100+ datasets)
- More model case studies beyond demand-forecast (SRMC, full stack, wind, solar, fundamentals SMP)
- Real Elexon API wiring / nightly snapshot regeneration via GitHub Actions
- Full ENTSO-E dataset coverage beyond the 1-dataset proof
- Search UI, dark-mode toggle, blog index
- Astro/11ty migration (revisit only if a fourth content type appears or if Option B's Python script becomes a bandwidth sink)

### Architecture Approach

Three architectural options were evaluated; **Option B (tiny build script) is recommended**, with Option A (stay-static, just extract CSS/JS) as a viable fallback if author bandwidth tightens. Option C (full SSG) is rejected for this milestone. The "middle path" (Option B) is structurally identical to a tiny 11ty implementation, so migrating later is a 30-minute structural mapping rather than a rewrite. Critically, **CSS extraction (Phase 2) ships before any templating decision and benefits all three paths** — this hedge makes the A vs B decision low-stakes and roadmap-deferrable. Full per-concern build-vs-runtime table, 8-phase dependency graph, and three-site reference anatomy (Stripe API / Cloudflare Dev Docs / Elexon BMRS) in `.planning/research/ARCHITECTURE.md`.

**Major components:**
1. **Manifest** (`site/hifi/data/elexon.json`, `vendors.json`) — single source of truth for structural facts (id, category, freq, lag, rows). Counts derive from `len(manifest)`; siblings and related-grids derive from category groupings.
2. **Per-dataset content partials** (`build/content/<vendor>/<slug>.md` with YAML frontmatter) — the ~80% of variation between two dataset pages: prose, schema rows, sample rows, caveats.
3. **Canonical templates** (`build/templates/dataset.html.j2`, `vendor-hub.html.j2`) — one HTML layout each, declared once. Editing layout means editing the template, not 22 files.
4. **Build script** (`src/gridflow_front_end/build.py`, exposed as `gridflow-build` console script) — reads manifest + partials + templates, emits HTML into `site/hifi/data-sources/`. Idempotent. Stdlib-or-Jinja2-only.
5. **Hand-authored pages** (home, architecture, data-sources hub, model case studies) — one-off editorial structure; templating is overkill. Build can inject manifest-derived counts via a marker-region pattern if needed.
6. **Existing runtime** (`site.js` chrome injection, `charts.js` seeded SVG, `theme.css`) — unchanged contracts; absorbs the duplicated scroll-spy IIFE and the duplicated dataset-page styles in Phase 2.

### Critical Pitfalls

Top pitfalls, mapped to phases. Full 11-pitfall catalogue (with warning signs, prevention, recovery cost) in `.planning/research/PITFALLS.md § Pitfall-to-Phase Mapping`.

1. **Pitfall 0 — Uncommitted in-flight refactor (BLOCKING).** 26 modified files since the initial commit. Every cleanup commit will entangle with the in-flight typography/honesty/pillar-status edits unless they ship in 4 logical commits first. Also: add `.gitattributes` with `*.html text eol=lf` to stop the CRLF warning noise. **Phase 0 — precedes everything else.**
2. **Pitfall 1 — Partial honesty pivot.** "Live" framing is encoded in six surfaces (hero `chip live`, hero `LAST FETCH` stat-card, footer "last sync" in `site.js`, time-window tab pills on snapshot charts, Related-card live chips, footer build-version string). Touching only some is worse than touching none. Treat as one atomic pass with a fixed grep checklist; zero hits required. **Phase 5 — scope before depth, execute after depth.**
3. **Pitfall 6 — Hand-edit-22 vs SSG false dichotomy.** The trap is treating "hand-edit each of 22" and "adopt Astro/11ty/Hugo" as the only options. Middle path (Option B) satisfies the no-build-step constraint by committing generated HTML. **Decision must precede Phase 3 (Elexon dataset depth).**
4. **Pitfall 2 — Phantom coverage (sidebar over-promises).** Every dataset sidebar advertises six anchors (`#overview / #schema / #sample / #api / #caveats / #related`); only `#caveats` and `#related` exist on the 16 broken stubs. A recruiter clicking "Schema" and finding nothing concludes "this is theatre." Enforce: per-page assertion that every sidebar anchor resolves to an existing `<section id>`. **Phase 3 + 4.**
5. **Pitfall 3 — Vendor-doc drift.** The site invites the spot-check (Elexon's `/datasets/FUELHH` URL is right there). Each dataset page needs a `verified: YYYY-MM-DD` micro-line + a link to the vendor doc page. Drift is already real (BOAL → BOALF rename documented in-page). **Phase 3.**
6. **Pitfall 10 — Mobile fix is viewport-only.** The `width=1280` → `width=device-width` find-and-replace is necessary but not sufficient; the underlying dataset-page CSS was never written for mobile (sidebar `220px + 1fr`, hero `1fr auto`, 5-column stats strip, hard-coded `min-width: 340px`). The actual mobile work is a CSS pass after extraction (Phase 2). **Phase 1 (viewport tag) + Phase 5 (mobile CSS).**

## Cross-Cutting Findings

These appear in two or more research files and are the load-bearing decisions for the planner.

### 1. The "middle path" architectural choice

All four researchers converged on Option B (Python + Jinja2 build script over the existing JSON manifest) as the right shape for this repo's constraints: Python-first author, ~25 pages per vendor, solo maintenance, deploy must stay pure-static GitHub Pages, portfolio-piece framing where "I built a 100-line Python templater over my own data" is a *stronger* recruiter signal than "I installed Astro." ARCHITECTURE.md explicitly notes the roadmap can override and pick Option A (stay-static) if bandwidth tightens; both work.

### 2. Phase 0 is non-negotiable

The 26-file in-flight refactor must be committed in 4 logical chunks (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks) **before any structural cleanup work begins**. Otherwise every subsequent commit entangles with three concurrent refactors, bisect dies, and the partial honesty edits to `fuelhh.html` become un-reviewable. Add `.gitattributes` in the first cleanup commit.

### 3. The 22 / 25 / 28 dataset-count discrepancy is upstream-blocking

22 dataset pages exist on disk · 25 IDs in `data/elexon.json` · 28 claimed in the catalogue UI. The depth pass cannot render counts honestly until this is resolved. ARCHITECTURE.md leans toward absorbing the 3 missing datasets (`remit`, `bmunits_reference`, `soso`) into the manifest count of 25 because the manifest is structurally authoritative; FEATURES.md is agnostic. Either way, the decision precedes Phase 3.

### 4. The honesty pivot has six surfaces, not one

(1) Hero `chip live` badges · (2) Hero `LAST FETCH · N min ago` stat-card · (3) Footer "last sync" string in `site.js` · (4) Time-window `24h / 7d / 30d` tab pills on snapshot charts (they don't switch anything) · (5) Related-card live chips · (6) Footer `v0.4.2 · build 2026.04.30` string. Touching only one surface is worse than touching none because the contradiction reads as carelessness. Atomic pass with a grep checklist; zero hits required for completion.

### 5. CSS extraction ships before the SSG decision and benefits all paths

Moving the duplicated ~30-line `<style>` block (× 22 files = ~660 lines) into `theme.css`, consolidating the scroll-spy IIFE and `setTab()` declarations into `site.js`, is valuable on its own — even in the Option A (stay-static) world. This is the single highest-leverage low-risk change in the milestone and **lowers the stakes of the Option A vs B decision** because it can ship in Phase 2 regardless of which path is chosen.

### 6. Cross-vendor template requires Elexon consistency as prerequisite

Generalising the dataset template to ENTSO-E (the cross-vendor proof) requires the Elexon pages to be at consistent fidelity first — if only 6 of 22 are full, the template's variance is too high to confidently extrapolate. Phase 4 (ENTSO-E + vendor stubs) depends on Phase 3 (Elexon depth) being substantially complete.

## Decisions the Planning Phase Must Make Upfront

These are deferred from research and must be settled before Phase 3 of the roadmap begins. Researchers' leans noted; none are mandates.

| # | Decision | Researcher lean | Stakes |
|---|----------|------------------|--------|
| 1 | **Option A (stay hand-authored, extract CSS/JS only) vs Option B (Python + Jinja2 build script)** | All four lean B; ARCHITECTURE.md says roadmap can override to A if bandwidth tighter | Sets the templating mechanism for the milestone and the next; A pays a perpetual maintenance tax, B has a one-time setup cost |
| 2 | **Commit generated HTML vs build-in-CI** | ARCHITECTURE.md notes both work; flags the trade — committing generated HTML balloons PR review surface on cross-cutting changes, but keeps deploy a single-step upload | Affects deploy.yml, PR review workflow, and contributor experience |
| 3 | **Absorb the 3 manifest-only datasets (`remit`, `bmunits_reference`, `soso`) into v1 vs shrink the manifest to 22** | ARCHITECTURE.md leans absorb (manifest is authoritative); FEATURES.md agnostic | Determines whether v1 ships 22 or 25 Elexon dataset pages; affects the count-reconciliation work in Phase 3 |
| 4 | **Which ENTSO-E dataset becomes the cross-vendor proof** | Genuinely open — no researcher picked | Determines the one ENTSO-E content authoring effort in Phase 4; choice should favour structural-template-stretch (a different param style, a different settlement granularity) over familiar-shape |

## Implications for Roadmap

The phase structure below is the convergent ordering from PITFALLS.md (§ Pitfall-to-Phase Mapping) and ARCHITECTURE.md (§ Build Order Implications). Phases are numbered to match those documents.

### Phase 0: Commit the in-flight refactor
**Rationale:** Blocks everything. 26 modified files must ship in 4 logical commits before any new cleanup work. Otherwise every subsequent commit entangles with three concurrent refactors.
**Delivers:** Clean working tree; `.gitattributes` committed; deployed Pages catches up to working-tree state.
**Avoids:** Pitfall 0 (compounding cleanup on top of uncommitted refactor).
**Research flag:** Low — mechanical work, no design decisions.

### Phase 1: Trivial bug fixes (parallelisable, no architecture dependency)
**Rationale:** These have no architectural blockers and can ship before any extraction. They're high-leverage one-line changes.
**Delivers:** Mobile viewport tag fixed on 23 pages (find-and-replace); `LICENSE` file + aligned inline strings (MIT vs Apache-2.0 contradiction resolved); `rel="noopener"` on the 2 missing external links; dead `href="#"` placeholders replaced with non-link "Planned · F<n>" chips (provisional — real fix in Phase 4).
**Addresses:** Bug & a11y fallout, License contradiction.
**Avoids:** Pitfall 10 step 1 (viewport-only).
**Research flag:** None.

### Phase 2: CSS/JS extraction (must precede page regeneration)
**Rationale:** Page regeneration in Phase 3 requires the template to be free of inline duplicated styles and per-page script declarations. Also the highest-leverage low-risk change in the milestone — valuable independent of any templating decision.
**Delivers:** Dataset-page `<style>` block (× 22, ~660 lines) moved to `theme.css`; scroll-spy IIFE moved to `site.js`; per-page `setTab()` declarations replaced with the existing `[data-tabs]` convention; sidebar hover bug fixed via a CSS class.
**Avoids:** Anti-Pattern 4 (two scroll-spy variants); reduces surface area templates must model.
**Research flag:** None — well-understood mechanical refactor.

### Phase 3: Templating + content depth (the architectural pivot)
**Rationale:** This is Option B work proper. Author the dataset template + content partials; regenerate the 6 complete pages first to byte-equivalent state for validation; then author content for the 16 broken stubs by filling Overview / Schema / Sample sections. Resolve the 22/25/28 count discrepancy in this phase (manifest is the operational source).
**Delivers:** `build/templates/dataset.html.j2` + `vendor-hub.html.j2`; `build/content/elexon/<slug>.md` × 25 (assuming absorb-3-datasets decision); `gridflow-build` console script; 25 regenerated dataset pages; reconciled count propagated everywhere.
**Uses:** Python + Jinja2 + uv (per STACK.md).
**Addresses:** "All 22 Elexon dataset pages at fuelhh fidelity"; reconciled dataset count.
**Avoids:** Pitfalls 2 (phantom coverage), 3 (vendor-doc drift), 4 (manifest-as-fiction), 6 (false dichotomy), 7 (made-up precision).
**Research flag:** **MEDIUM** — needs per-dataset content authoring per vendor docs; requires the planning-phase decisions 1–3 settled upfront; may need a re-verification spot-check pass against Elexon BMRS for several datasets.

### Phase 4: Cross-vendor proof (ENTSO-E + vendor stubs)
**Rationale:** The build script already generalises. ENTSO-E proves the template works across vendors; the 5 vendor stubs (ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO) replace dead `href="#"` placeholders with intentional-not-broken landing pages.
**Delivers:** `data/entsoe.json` + 1 ENTSO-E dataset partial + generated ENTSO-E vendor hub and dataset page; 5 visually-distinct "coming soon" vendor stub pages (no sidebar, no chart container, single-screen layout).
**Addresses:** "Build ENTSO-E hub + 1 ENTSO-E dataset at fuelhh fidelity"; "Replace dead href=# placeholders."
**Avoids:** Pitfall 9 (coming-soon stubs reading as half-done vendor pages).
**Research flag:** **HIGH** — ENTSO-E REST API is less familiar territory than Elexon; the chosen dataset's schema/params must be verified against ENTSO-E Transparency Platform docs; needs `/gsd-research-phase` for the specific dataset chosen.

### Phase 5: Honesty sweep + a11y (atomic pass)
**Rationale:** Now that pages are template-generated, the sweep is a small number of template edits rather than 22+ per-page find-and-replace. Run after depth so newly-completed pages are cleaned in the same pass; scope the grep checklist before depth so depth doesn't reintroduce landmines.
**Delivers:** All six "live"-framing surfaces relabelled in one atomic pass; mobile CSS additions in `theme.css` for `@media (max-width: 720px)` and `@media (max-width: 480px)` blocks; `<main>` landmark + `aria-label` + `aria-current="page"` + `aria-hidden="true"` added in the template.
**Addresses:** "Kill 'live' framing site-wide"; mobile viewport bug fully resolved; a11y minimums.
**Avoids:** Pitfall 1 (partial honesty pivot), Pitfall 10 step 2 (mobile CSS).
**Research flag:** None — checklist-driven mechanical pass.

### Phase 6: Cross-repo Vault sync
**Rationale:** Depends on stable on-site content (PROJECT.md hierarchy: on-site → vault). The frontmatter shape from Phase 3 was designed to align with the `gridflow-dataset-spec` skill, so this is a structural mapping not a content rewrite. Pick sync direction policy first (vault as read-only mirror of on-site is the recommendation, matches PROJECT.md hierarchy).
**Delivers:** Vault pages at `gridflow/quant-vault/30-vendors/elexon/datasets/<slug>.md` carrying provenance banner + `Last synced from on-site: YYYY-MM-DD @ commit-hash` footer; sync direction policy documented in `PROJECT.md § Key Decisions`.
**Addresses:** "Sync the Obsidian Vault dataset pages."
**Avoids:** Pitfall 5 (sync direction ambiguous).
**Research flag:** **LOW** — depends on the `anthropic-skills:gridflow-dataset-spec` skill being usable as-is; spans two repos.

### Phase 7: CI validation (cheap insurance)
**Rationale:** After all the structural work, lock in the wins with cheap automated checks.
**Delivers:** `htmlhint site/hifi/**/*.html` on push; `lychee site/hifi` link-checker; build-script idempotence check (run build twice, diff — no changes second time).
**Addresses:** Catches future regressions of the exact bug class motivating v1.
**Avoids:** Future occurrences of broken stubs / dead anchors / sidebar phantom coverage.
**Research flag:** None.

### Phase Ordering Rationale

- **Phase 0 is the gate.** Every subsequent phase depends on the in-flight refactor being shipped first.
- **Phase 1 parallelises with Phase 2.** Trivial bug fixes and CSS/JS extraction have no inter-dependency.
- **Phase 2 precedes Phase 3** because the template inputs in Phase 3 must reference shared CSS classes, not inline styles.
- **Phase 3 precedes Phase 4** because cross-vendor extrapolation requires Elexon template consistency first.
- **Phase 5 runs after Phase 3 + 4** so newly-completed pages are cleaned in the same atomic pass (but the grep checklist is *scoped* before Phase 3 so depth doesn't reintroduce landmines).
- **Phase 6 ships last** because it depends on on-site content being stable across all pages.
- **Phase 7 is non-blocking** and can be added at any point after Phase 3.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3:** Per-dataset content authoring requires vendor-doc verification for the 16 broken stubs. A `/gsd-research-phase` run on a per-dataset basis (or batched by category) is appropriate before authoring each partial — at minimum to confirm endpoint paths, primary keys, and column names against current Elexon BMRS docs.
- **Phase 4:** ENTSO-E dataset choice and schema verification is genuinely open territory. The chosen dataset needs schema + endpoint verification against the ENTSO-E Transparency Platform; the REST API replaces the SOAP-era patterns most blogs describe. `/gsd-research-phase` recommended.
- **Phase 6:** Cross-repo coordination (this repo + `gridflow` repo's `quant-vault/30-vendors/`) needs a sync-direction policy decision committed to `PROJECT.md` before any vault edits.

Phases with standard patterns (skip research-phase):
- **Phase 0:** Mechanical git work.
- **Phase 1:** Trivial fixes; viewport tag find-and-replace, license file creation, attribute additions.
- **Phase 2:** Well-understood CSS/JS extraction; the duplicated blocks are already identified in CONCERNS.md.
- **Phase 5:** Checklist-driven atomic sweep against a fixed grep list of forbidden strings.
- **Phase 7:** Established CI patterns (htmlhint, lychee).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified against PyPI / official docs (Jinja2 3.1.6 = 2025-03-05 release); recommendation grounded in this repo's constraints, not generic advice. Full source list in STACK.md § Sources. |
| Features | HIGH | Dataset-page and model case study anatomies are extracted directly from user-confirmed reference templates (`fuelhh.html`, `demand-forecast.html`); anti-features anchored in explicit PROJECT.md anti-goals. Benchmark sites (Stripe / Tailwind / Linear / FT Alphaville) referenced from training-data knowledge, not re-fetched — MEDIUM on novelty of specific differentiator features, HIGH on the structural patterns. |
| Architecture | HIGH | Patterns and reference-site anatomies (Stripe API / Cloudflare Dev Docs / Elexon BMRS) verified against live docs. Build-vs-runtime per-concern table and LOC estimates self-reported as MEDIUM-HIGH in ARCHITECTURE.md — the LOC numbers are estimates from current files; the *pattern* recommendations are HIGH. |
| Pitfalls | HIGH | Every pitfall maps to a specific phase and extends `CONCERNS.md` entries rather than duplicating them. Anchored in this codebase's actual state + explicit PROJECT.md anti-goals + recruiter-audience constraint, not generic web-dev advice. |

**Overall confidence:** HIGH.

### Gaps to Address

These could not be resolved during research and need attention during planning or execution.

- **Which specific ENTSO-E dataset becomes the cross-vendor proof in Phase 4.** No researcher picked one. Recommended criterion: pick a dataset whose schema/params *stretch* the template (different settlement granularity, different param style) over one that fits familiarly. Resolve in the planning phase.
- **Cross-repo schema verification has not been performed.** The site claims `gridflow/schemas/elexon.py · ElexonFuelHH` and similar paths in `gridflow-models`. None were re-verified against HEAD of those repos during research. A milestone-close cross-check pass is recommended (per Pitfall 8 recovery strategy).
- **The 3 manifest-only datasets (`remit`, `bmunits_reference`, `soso`) — absorb or shrink — was not resolved.** ARCHITECTURE.md leans absorb; this is a planning-phase decision (#3 in the decisions table above).
- **Commit-generated-HTML vs build-in-CI was not resolved.** Both work; the trade is PR-review-surface vs deploy-step simplicity (decision #2 above).
- **Numbers on dataset pages need provenance pass.** Per Pitfall 7, every quantitative claim (rows/month, history depth, fuel-type count) needs a source — measured-from-pipeline vs estimated vs structural. The provenance audit is part of Phase 3 content authoring but is not itself research-resolved.

## Sources

### Primary (HIGH confidence — verified against official sources)
- `.planning/research/STACK.md` — Python + Jinja2 + gridflow-build CLI recommendation, full alternatives matrix, version pins (Jinja2 3.1.6, 11ty 3.1.5, Astro 6.x, Hugo v0.161.1)
- `.planning/research/FEATURES.md` — 7-section dataset-page anatomy, model case study anatomy, anti-features, MVP definition, feature dependency graph, P1/P2/P3 prioritization matrix
- `.planning/research/ARCHITECTURE.md` — Three-option architectural choice (A/B/C), build-vs-runtime per-concern table, 8-phase dependency graph, three reference-site anatomies (Stripe API / Cloudflare / Elexon BMRS)
- `.planning/research/PITFALLS.md` — 11 forward-looking pitfalls with phase mapping, "Looks Done But Isn't" checklist, vendor-doc drift detection pattern, recovery cost table
- `.planning/PROJECT.md` — Core Value, Active requirements, Out of Scope, Key Decisions, source-of-truth hierarchy
- `.planning/codebase/CONCERNS.md` (referenced throughout) — current-state bug catalogue that pitfalls extend rather than duplicate
- Live HTML files: `site/hifi/data-sources/elexon/fuelhh.html`, `site/hifi/models/demand-forecast.html`, `site/hifi/index.html`, `site/hifi/architecture.html`
- Live JSON: `site/hifi/data/elexon.json` (the manifest that the build script consumes)

### Secondary (HIGH–MEDIUM confidence — verified docs, applied to this repo's context)
- Stripe API Reference, Cloudflare Developer Docs, Elexon BMRS Insights Solution — three-column reference-page anatomy; sidebar-tree + center-content + sibling-grouping pattern
- Jinja2 PyPI release page (2025-03-05), official Jinja2 docs, Eleventy "Pages from Data" docs, Astro getting-started, Hugo GitHub releases — stack version verification
- CSS-Tricks "Simplest Ways to Handle HTML Includes", Smashing Magazine Nunjucks tutorial, herluf-ba single-file SSG — "tiny build script" pattern precedents

### Tertiary (MEDIUM confidence — training-data knowledge, not re-fetched)
- Stripe Press, FT Alphaville, Tailwind docs, Linear docs — editorial-quiet aesthetic patterns informing the differentiator features
- Personal portfolios from quants/data scientists — model case study structure (Question → Inputs → Estimator → Validation → Caveats → What's next)

---
*Research completed: 2026-05-17*
*Ready for roadmap: yes*
