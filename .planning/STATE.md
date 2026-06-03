# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 8 (dataset-page formatting bug fix) planned 2026-05-19. RESEARCH.md confirmed both hypothesised causes at `dataset.html.j2:18` (`align-items: end` dominant + `grid-template-columns: 1fr auto` × unwrapped SILVER PATH mono amplifier); candidates table reviewed and recommendation revised from (c) to **(a) only** after inner-grid sizing arithmetic surfaced a text-overflow regression in (b)/(c). Single plan `08-01-PLAN.md` (4 tasks, 2 commits expected): Task 1 single-token template edit `end` → `start`, Task 2 re-render 34 pages, Task 3 user-verified checkpoint (3 desktop + 2 mobile per D-02 — `autonomous: false`), Task 4 v1 CI gates. theme.css intentionally untouched. Next: `/gsd-execute-phase 8`.

## Current Position

**Phase:** 9 — ENTSO-E full coverage (49 datasets) — **COMPLETE 2026-06-03**
**Plan:** Briefs (step 1) 1/1 complete 2026-05-20 (7 commits `aab2128..9b5e296`); page authoring (step 2) complete 2026-06-03 — 49 pages Claude-Designed in 5 batches, landed to `authored-pages/entsoe/`, `site/hifi/data/entsoe.json` authored to 49 entries (9 groups). See `phases/09-entsoe-content-briefs/09-01-SUMMARY.md`.
**Status:** Phase 9 complete — all 5 success criteria met: 49 vault files; `entsoe.json` = 49 entries; `gridflow-build` writes 49 authored pages; `/data-sources/entsoe.html` is a 49-dataset catalog; `gridflow-build --check` exits 0 (idempotent across 86 pages + 8 hubs). Pages carry synthesised `#overview` + `#caveats` (D-22 applied to ENTSO-E — richer than SC#3's D-20 baseline). ENTSOE-01..ENTSOE-05 satisfied.
**Last activity:** 2026-06-03 — final Claude Design batch (5 outages + 12 long-tail) landed 49/49. Two vault build-blockers fixed across earlier batches (`activated_balancing_qty` heading; `commercial_schedules_net_positions` Overview/API). One latent production bug found and deferred to a separate site-wide fix: authored vendor-hub `data-root="../../"` should be `../` (breaks JS-injected nav/footer on the GitHub Pages project subpath; affects the elexon hub too). Branch `feat/phase-9-entsoe-pages`; PR opened to main.

```
[███████████████████████████░░░░] ~75% — Phases 7–9 complete; ENTSO-E 49/49 shipped (ENTSOE-01..ENTSOE-05). Only Phase 10 remains in v2 (four-vendor batch: ENTSO-G 33 · GIE 8 · NESO 34 · Open-Meteo 6 = 81 datasets + site-wide count to 163).
```

## Accumulated Context

### Decisions Locked (validated in v1, carried into v2)

| # | Decision | Locked in |
|---|----------|-----------|
| 1 | Templating mechanism: Python + Jinja2 + `gridflow-build` CLI (Option B), CI build, generated HTML gitignored | PROJECT.md (v1) |
| 2 | Source-of-truth direction: vault → site (build reads vault `.md`, renders to site HTML) | PROJECT.md (v1) |
| 3 | Vault vendored in-repo at `vault/<vendor>/` (vendoring pattern preserved by ADR-0002; upstream Vault now also on private GitHub) | PROJECT.md (v1) + ADR-0002 (v2) |
| 4 | Editorial aesthetic kept: cream-forest + Fraunces | PROJECT.md (v1) |
| 5 | Kill "live" framing site-wide; templates born honest | PROJECT.md (v1) |
| 6 | Recruiter-first audience: full-stack DS in energy trading | PROJECT.md (v1) |
| 7 | Core value: domain depth | PROJECT.md (v1) |
| 8 | Pydantic class drift policy: render-with-flag (closing the gap is a v3 candidate; Phase 7 triages 22 Elexon `manual_transformer_schema` cases as `wontfix`/`v3-candidate`) | PROJECT.md (v1) |

### Decisions Locked (v2)

| # | Decision | Locked in |
|---|----------|-----------|
| 1 | Phase shape: Reconciliation + bug fix + ENTSO-E + 4-vendor batch (4 phases — 7/8/9/10) | ADR-0001 + PROJECT.md Key Decisions (v2) |
| 2 | Vault is **derivative** — Reconciliation fixes Vault, never overrides Canonical | grill 2026-05-19 + 07-CONTEXT.md D-01 |
| 3 | Reconciliation = the drift-detection research package, brought forward from post-v2 | grill 2026-05-19 + 07-CONTEXT.md D-02 |
| 4 | Drift gates per-Vendor; Phase 8 (bug fix) independent of Phase 7 (Reconciliation) | grill 2026-05-19 + 07-CONTEXT.md D-03 |
| 5 | All-Vendor Reconciliation done upfront in Phase 7, not interleaved per-Vendor | grill 2026-05-19 + 07-CONTEXT.md D-04 |
| 6 | Phase 7 split into 4 sub-plans per logical step (`07a` wrap · `07b` triage · `07c` fix · `07d` push) | discuss-phase 2026-05-19 + 07-CONTEXT.md D-05 |
| 7 | ENTSO-E entitlement (33 HTTP 401 cases) deferred from Phase 7 to Phase 9 discuss as `needs-info`/`defer-entitlement` | discuss-phase 2026-05-19 + 07-CONTEXT.md D-06 |
| 8 | Pocock skill set (`to-issues` + `triage`) for Phase 7 exploratory work; GSD for pre-planned phases | grill 2026-05-19 + 07-CONTEXT.md D-07 |
| 9 | Reconciliation findings live as local markdown under `.planning/reconciliation/<vendor>/`, not GitHub Issues | grill 2026-05-19 + 07-CONTEXT.md D-08 |
| 10 | Vault committed to **private** GitHub repo `EBentham/quant-vault`, no GitHub App auth | ADR-0002 + discuss-phase 2026-05-19 + 07-CONTEXT.md D-09 |
| 11 | Strict scope discipline — no Pydantic drift fix, related blurbs, or fuel-pill restoration in v2 | PROJECT.md Key Decisions (v2) |
| 12 | [drift] extras = PyYAML only; pydantic comes transitively via gridflow sys.path insert (adding pydantic as wheel dep would conflict) | 07-01 execution 2026-05-19 |
| 13 | `_discover_curl()` runs at module level on import (fail-loud on misconfigured env, T-07-01-04 accepted); shutil.which('curl') > shutil.which('curl.exe') > RuntimeError | 07-01 execution 2026-05-19 |
| 14 | `gridflow-drift-check --help` not implemented; full verifier runs immediately — 07-02 must invoke without --help | 07-01 execution 2026-05-19 |
| 15 | ENTSO-E failed_auth count increased 33→35 — `current_balancing_state` (was HTTP=0) and `outages_generation` (was HTTP=503) now both return HTTP=401; both triaged needs-info/defer-entitlement; 35 >= 33 threshold met | 07-02 execution 2026-05-19 |
| 16 | windfor (elexon) is a new finding not in baseline — triaged open, same pattern as ndf/ndfd | 07-02 execution 2026-05-19 |
| 17 | neso regional_scotland transient DNS failure filed as open for re-verify in 07-03 | 07-02 execution 2026-05-19 |
| 18 | entsoe finding count: 35 defer-entitlement + 2 wontfix-v3 + 36 open silver = 73 total (exceeds plan's minimum of 51); 36 open = 24 nullable mismatches + 10 no_silver_schema_table + 1 no_silver_section + 1 extra field | 07-02 execution 2026-05-19 |
| 19 | gridflow package installed into front-end venv (Rule 3 deviation) to resolve typer transitive dependency not declared in [drift] extras | 07-02 execution 2026-05-19 |
| 20 | **Brief format tightened post-POC** — Lede compressed to 1 sentence ~15-25 words; `# Overview` section removed entirely (was redundant with hero lede + stripped from rendered HTML); each `# Caveats` body compressed to 1 sentence. Applies to Phase 9 (49 ENTSO-E briefs) and Phase 10 (80 four-vendor briefs). 33 Elexon briefs back-tightened for consistency. See updated `08C-BRIEF-RECIPE.md` and `content-briefs/elexon/fuelhh.md` (gold standard). | 5-dataset POC review 2026-05-20 |
| 21 | **ENTSO-E entitlement resolved (not blocking content)** — 35 ENTSO-E datasets return HTTP 401 on the unregistered gridflow default key (Phase 7 D-06 deferred this decision to Phase 9). Resolution: produce full briefs for all 49 datasets from vault + gridflow source (both accessible without an API key); flag the 35 with `entitlement_required: true` in frontmatter and an "extended ENTSO-E registration" disclaimer in the Verified line. Live-API verification deferred until a user with the registration tier runs verification; gridflow connector code is the canonical source for schema/transformer truth either way. | Phase 9 brief production 2026-05-20 |
| 22 | **D-22 (2026-05-20 evening): Elexon-only Overview restoration + realistic chart shapes** — The 3-paragraph `# Overview` section, removed by D-20, is restored to all 33 Elexon briefs and injected into the 33 `authored-pages/elexon/<slug>.html` pages in concise form (~110 words, modeled on `authored-pages/elexon/fuelhh.html`). Concurrently, `site/hifi/assets/charts.js` is extended with a `SHAPES` registry of 9 deterministic domain-shape generators (`diurnal-load`, `diurnal-price`, `frequency`, `volatile-spikes`, `diurnal-wind`, `diurnal-solar`, `diurnal-temp`, `flat-baseload`, `bipolar-flow`); each brief's `# Sample chart` and the HTML's `data-opts` JSON now select a domain shape (sparkline, priceLadder) or explicit series (agpt/agws stackedArea) or inline items (barsH). Sacred refs (`fuelhh.html`, `system_prices.html`) preserved unchanged. Other vendors (Phase 9 ENTSO-E, Phase 10 ENTSO-G/GIE/NESO/Open-Meteo) remain on the D-20 no-Overview format until separately retrofitted — user's Claude Design budget is low this week. | Phase 8C closing pass 2026-05-20 evening · 4 commits `e1d3bb3..<pending>` |

### Decisions Overridden (v2)

| # | Original decision | Overridden by | Reason |
|---|-------------------|---------------|--------|
| 1 | "Assume vault content complete; no upfront audit phase — let `gridflow-build --check` surface gaps" (v2 original scoping 2026-05-18) | ADR-0001 (2026-05-19) | `gridflow-build --check` is an *idempotence* check, not a content-accuracy check; drift research surfaced real shipped Drift on the live Site (`ndf`/`ndfd`/`fuelhh`, 33 ENTSO-E 401s, ENTSO-G `physical_flows` 35-field mismatch). Accuracy constraint in PROJECT.md § Constraints made the original decision untenable |

### Open Todos / Carry-overs from v1

- Drift-detection research package at `.planning/research/post-v1/drift-detection/` is now Phase 7 input (no longer post-v2)
- v3 candidates catalogued in `PROJECT.md § Out of Scope`, `MILESTONE-COMPLETE.md § Deferred to v2`, and `07-CONTEXT.md § Deferred`

### Phase 7 resolved items

All Phase 7 open items resolved during execution:
- Sub-plan filenames: `07-01..07-04` (per project convention)
- JSON schema: verifier reports committed to quant-vault at `vault-curl-schema-validation.{json,md}` (Q-DD-17 default lean)
- Finding file format: YAML frontmatter with `status:` + `reason:` + `vendor:` + `dataset:` + `drift_category:` + `verifier_finding_id:` + `references:` + `tags:` (established in 07-02)
- `[drift]` extras: in `gridflow-front-end/pyproject.toml` (Q-DD-16 lean confirmed — quant-vault has no pyproject.toml)
- Sequencing: 07-01 → 07-02 → 07-03 → 07-04 (sequential Wave 1 then Wave 2)
- LICENSE: MIT (inertia from gridflow-front-end; planner decision in 07-04)

## Session Continuity

**Last action:** Phase 8D execution complete 2026-05-20. 5 vendor-hub briefs committed (entsoe 49/6, entsog 33/5, gie 8/2, neso 33/4, openmeteo 6/2); build.py override extended for vendor hubs; SUMMARY + ROADMAP updated. 8 `docs(08D):` + `fix(08D):` commits on branch `docs/v2-milestone-start`. BRIEF-LOG.md has one logged false positive (NESO Check 7 regex needs `[a-z0-9_]+` to handle numeric slug suffixes). **2026-05-20 follow-on:** 5-dataset POC (entsoe/actual_generation + 4 cross-vendor) rendered through Claude Design; user reviewed and stripped `# Overview` + `# Caveats` sections as redundant/verbose. Brief format tightened to match (D-20). `build.py` extended with `copy_authored_dataset_pages_for_coming_soon()` so authored dataset HTML for COMING_SOON vendors lands at `data-sources/<vendor>/<slug>.html`. All 33 Elexon briefs back-tightened to the new format (Lede ≤25 words; no `# Overview`; terse Caveats).

**2026-05-20 evening (D-22 retrofit):** Elexon-only Overview restoration + realistic chart shapes shipped in 4 commits on `docs/v2-milestone-start`. (1) `feat(charts): domain-realistic shape generators` extends `site/hifi/assets/charts.js` with a 9-shape `SHAPES` registry; sparkline / priceLadder / stackedArea accept `opts.shape` / `opts.series` / `opts.values` while preserving legacy seed-based behavior byte-identical for the fuelhh default. (2) `docs(briefs): D-22 — add concise Overview + realistic chart shape to 33 Elexon briefs` adds the 3-paragraph Overview (~110w) and per-dataset Shape/Params/Series/Items to every Elexon brief; sacred fuelhh.md and system_prices.md updated in line (Overview content fresh; default chart paths preserved). (3) `feat(authored/elexon): inject Overview section + realistic chart shapes — 33 pages` runs a one-off Python retrofit script that injects `<section id="overview">` between stats-strip and snapshot chart, updates each chart's `data-opts` JSON, and adds `#overview` as the first/active sidebar nav anchor on the 31 Claude Design output pages (fuelhh.html + system_prices.html no-op). (4) Recipe + STATE updated. Visual spot-check via curl confirms Overview renders + shape-based charts wire correctly + sacred refs unchanged.

**2026-06-03 (Phase 9 complete):** Final Claude Design batch landed 49/49 ENTSO-E pages. `entsoe.json` authored to 49 entries across 9 groups (Generation 8 · Prices 1 · Demand & Forecasts 6 · Balancing 8 · Reserves 3 · Cross-Border Flows 5 · Transfer Capacity 7 · Outages 5 · Congestion/Redispatch/Auction 6). `gridflow-build` → 86 pages, `--check` idempotent. The D-22 overview-synthesis decision was applied to ENTSO-E during the batches (every page got a 3-paragraph `#overview` + `#caveats`), so the Phase 9 pages exceed SC#3's original D-20 no-Overview baseline. Phase 9 closed out in 5 commits on `feat/phase-9-entsoe-pages`; PR opened to main. Full record: `phases/09-entsoe-content-briefs/09-01-SUMMARY.md`.

**Next action:** Plan Phase 10 — four-vendor batch (ENTSO-G 33 · GIE 8 · NESO 34 · Open-Meteo 6 = 81 datasets; same tightened brief → Claude Design pattern) + move the 4 vendors from `COMING_SOON_VENDORS` to `REAL_VENDORS` in `build.py` + update site-wide count strings to 163. Run `/gsd-plan-phase 10`.
**Resume from:** Phase 10 kickoff. The Phase 10 vendor-hub briefs already exist (`content-briefs/<vendor>/_landing.md`, Phase 8D); per-dataset briefs for the 4 vendors are the next production step (same tightened format; whether to apply D-22 overview synthesis as ENTSO-E did is a Phase 10 decision). **Carry-over:** authored vendor-hub `data-root="../../"`→`"../"` bug (see `09-01-SUMMARY.md` § "Carried forward") — a flagged spawned task; fix site-wide before/with Phase 10.

**Elexon-D-22 position (post-retrofit):**
- `site/hifi/assets/charts.js` — extended with `SHAPES` registry; legacy seed paths preserved byte-identical.
- `content-briefs/elexon/*.md` (33 files) — all have `# Overview` (~110w) + `# Sample chart` with Shape/Params/Series/Items.
- `authored-pages/elexon/*.html` (33 files) — 31 have new `<section id="overview">` + updated `data-opts` + `#overview` sidebar nav; 2 sacred refs (fuelhh, system_prices) unchanged.
- `.planning/phases/08C-elexon-content-briefs/d22-retrofit.py` — one-off retrofit script kept as a record of the per-page edits (re-runnable if briefs are re-authored).
- `.planning/phases/08C-elexon-content-briefs/08C-BRIEF-RECIPE.md` — D-22 callout + restored `# Overview` spec + Shape/Params/Series/Items contract.

**Branch state as of Phase 8D completion (~88 commits ahead of main, NOT pushed):**
- `content-briefs/elexon/` — 33 files (Phase 8C, committed)
- `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/_landing.md` — 5 files (Phase 8D, committed)
- `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/<one_slug>.md` — 5 sample per-dataset briefs (pre-Phase-8D, committed)
- `authored-pages/elexon/` — 33 files (Phase 8B, committed)
- `src/gridflow_front_end/build.py` — both per-dataset (8B) and per-hub (8D) override paths wired
- Untracked: `.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, `.planning/research/*.md` (pre-existing, gitignored-intent)
- Modified (pre-existing user work, not from this session's agents): `CLAUDE.md`

---

*State updated 2026-05-19 — Phase 8 plan-phase complete. 1 plan / 4 tasks / 2 commits / 1 user-checkpoint. 5/31 v2 REQ-IDs delivered (Phase 7 RECON-01..RECON-05). Next: /gsd-execute-phase 8.*
