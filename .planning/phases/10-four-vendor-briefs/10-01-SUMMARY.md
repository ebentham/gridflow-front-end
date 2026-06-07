---
plan_id: 10-01
phase: 10
title: Four-vendor batch coverage + site-wide consistency — v2 close-out
status: complete
completed: 2026-06-07
requirements: [ENTSOG-01, ENTSOG-02, ENTSOG-03, ENTSOG-04, GIE-01, GIE-02, GIE-03, GIE-04, NESO-01, NESO-02, NESO-03, NESO-04, METEO-01, METEO-02, METEO-03, METEO-04, SITE-01, SITE-02]
---

# Phase 10 / Plan 10-01 — Summary (v2 milestone close-out)

## Outcome

**Complete.** All four remaining vendors (ENTSO-G, GIE, NESO, Open-Meteo) are documented at full fidelity. The site now carries **162 datasets across 6 vendors**, every vendor is a real hub (zero coming-soon stubs), site-wide count strings are consistent, and all three CI gates are green. This closes the **v2 full-vendor-coverage milestone** (Phases 7 → 8B/C/D → 9 → 10).

## Per-vendor delivery

| Vendor | Datasets | Groups | Authored pages | Format | Schema handling | Commit |
|---|---|---|---|---|---|---|
| ENTSO-G | 33 | 5 (Operational·Point 19 · Zone 1 · CMP 3 · Tariff 2 · Reference·Topology 8) | 33 | D-22 | 1 typed (`EntsogPhysicalFlow`); 32 dynamic via `GenericEntsogJsonTransformer` (`silver/entsog/generic.py`) | `d3620a4` |
| GIE | 8 | 2 (Storage AGSI+ 7 · LNG ALSI 1) | 8 | D-22 | `GasStorage` (storage, storage_reports) + `LNGTerminal` (lng); 5 reference/news dynamic via `AgsiJsonTransformer` | `f82311e` |
| NESO | 33 | 4 (Carbon·National 10 · Statistics 2 · Generation Mix 3 · Carbon·Regional 18) | 33 | D-22 | all typed (`schemas/neso.py`) but transformers generated via `register_neso_transformers()` — never schema-absent | `000179b` |
| Open-Meteo | 6 | 2 (Forecast 3 · Historical 3) | 6 | D-22 | `DemandWeather`/`WindWeather`/`SolarWeather` in **`schemas/weather.py`** (not `openmeteo.py`); dual-host `forecast.py`/`historical.py` | `41b19b7` |

**Total: 80 authored pages** (entsog 33 + gie 8 + neso 33 + openmeteo 6). With Elexon (33) + ENTSO-E (49), the site renders **162 dataset pages + 6 vendor hubs**.

Each vendor hub gained a vendor-wide `#about` section (3–4 SoT-cited caveats) so the D-22 dataset pages' `#caveats` intro links (`../<vendor>.html#about`) resolve under `lychee --include-fragments`. Hubs were orchestrator-maintained; Claude Design produced **dataset pages only** (re-rendering a hub risks a depth-2 `data-root` regression that breaks GitHub Pages — observed once in the entsog proof batch and rejected).

## Wiring (T05–T08)

- **Manifests (T05):** `site/hifi/data/{entsog,gie,neso,openmeteo}.json` authored from each `_landing.md` `# Groups` table; every manifest's `id` set validated to exactly equal the vendored `vault/<vendor>/*.md` slugs (the load-bearing invariant — `build_vendor` skips vault files absent from the manifest and exits on manifest slugs with no vault file).
- **Migration (T06):** the four vendors moved `COMING_SOON_VENDORS` → `REAL_VENDORS` with full `vendor_meta`. The GIE `gie_agsi`/`gie_alsi` split collapsed into one `REAL_VENDORS["gie"]` (D-3); the three now-redundant gie-split special-cases (`build_coming_soon_stubs`, `copy_authored_dataset_pages_for_coming_soon`, `_vendor_stub_metadata`) were removed. `COMING_SOON_VENDORS` is now empty (machinery retained, dormant). `gie_agsi.html`/`gie_alsi.html` are no longer emitted.
- **Counts (T08):** site-wide strings reconciled to **162** — `index.html` stat strip + pillar prose (and "seven vendors" → "six"), `data-sources.html` eyebrow + per-section totals (Electricity 115, Gas 41, Weather 6) + per-vendor cards + at-a-glance table, `site.js` footer. The GIE catalog card now links to the unified `gie.html`.
- **Hub `data-root` (T07):** verify-only no-op — all six authored hubs already read `data-root="../"`.

## Decisions locked (Task 00)

- **D-1 — D-22 for all four vendors:** synthesised 3-paragraph `#overview` + rendered `#caveats`, matching Phase 9. The 4 D-20 POC pages were re-rendered for consistency → **80 pages, not 76**.
- **D-2 — site-wide count = 162:** empirical (`vault/neso` = 33 dataset `.md`, no README). The legacy "163" / "NESO 34" was a doc-era miscount; corrected in REQUIREMENTS (NESO-01/02/03, SITE-01), ROADMAP, and the three shipped count surfaces.
- **D-3 — GIE unified:** one hub (AGSI + ALSI as two groups), both split stubs removed.
- **D-4 — shared reference:** `authored-pages/entsoe/actual_generation.html` as the D-22 structural reference for all four vendors, each vendor's POC page as the vendor-specific layout example.

## CI evidence (cold rebuild, 2026-06-07)

```
rm -rf site/hifi/data-sources && gridflow-build
  → wrote 162 dataset pages + 6 vendor hub(s) + 0 coming-soon hub(s) + 0 coming-soon dataset stub(s)
gridflow-build --check
  → OK: idempotent across 162 pages + 6 hubs + 0 dataset stubs.
htmlhint --config .htmlhintrc 'site/hifi/**/*.html'
  → Scanned 172 files, no errors found.
lychee --no-progress --offline --include-fragments 'site/hifi/**/*.html'
  → 4349 Total · 0 Errors.
```

`grep -n COMING_SOON_VENDORS src/gridflow_front_end/build.py` shows the four vendor keys only under `REAL_VENDORS`; `ruff check` passes.

## Commit range

`feat/phase-10-four-vendor`: `b6a08fa` (plan + handover pack) · `d3620a4` (entsog) · `f82311e` (gie) · `000179b` (neso) · `41b19b7` (openmeteo) · `03240b7` (`fix(site)` counts → 162) · `e8f6b74` (`feat(build)` manifests + REAL_VENDORS migration) · `docs:` (this reconcile).

## Carried forward

- **`site/hifi/data/vendors.json`** — a git-tracked orphan (referenced by no code/JS) carrying stale per-vendor counts and fake `lastFetch` "live" timestamps that contradict the "kill all live framing" anti-goal. Flagged as a separate cleanup task; intentionally out of this PR's scope.

Nothing else outstanding — Phase 10 closes v2. Next: PR to `main`, then `/gsd-complete-milestone`.
