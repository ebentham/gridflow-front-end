# Phase 10 — Four-vendor batch content briefs

**Status:** In progress 2026-05-20 evening — 4 parallel background agents producing briefs across ENTSO-G, GIE, NESO, Open-Meteo.

## Scope

80 content briefs across four vendors, one brief per dataset, at `content-briefs/<vendor>/<slug>.md`. These feed Claude Design, which renders them into `authored-pages/<vendor>/<slug>.html` against the visual reference of `authored-pages/elexon/{fuelhh,system_prices}.html`.

| Vendor | Datasets | Brief location |
|---|---|---|
| ENTSO-G | 33 | `content-briefs/entsog/<slug>.md` |
| GIE (unified AGSI + ALSI) | 8 | `content-briefs/gie/<slug>.md` |
| NESO | 33 | `content-briefs/neso/<slug>.md` |
| Open-Meteo | 6 | `content-briefs/openmeteo/<slug>.md` |
| **Total** | **80** | — |

Each vendor also has 1 pre-existing **POC brief in OLD format** (verbose lede, `# Overview` present) that must be **overwritten** with the tightened D-20 version:
- `content-briefs/entsog/aggregated_physical_flows.md`
- `content-briefs/gie/storage.md`
- `content-briefs/neso/carbon_intensity.md`
- `content-briefs/openmeteo/forecast_solar.md`

## Decisions inherited

- **D-20 (brief format tightened)** — Lede ≤25 words; no `# Overview` section; terse 1-sentence Caveats. See `.planning/phases/08C-elexon-content-briefs/08C-BRIEF-RECIPE.md` (updated 2026-05-20) and `content-briefs/elexon/fuelhh.md` (gold standard).
- **D-21 (entitlement flag, not block)** — Phase 9 pattern: produce a full brief regardless of entitlement, flag in frontmatter if needed. **Not expected to apply here** — all four vendors have public APIs (GIE needs a free API key; ENTSO-G / NESO / Open-Meteo are unauthenticated).

## Vendoring

All 80 vault files vendored from upstream `quant-vault` in commit `f3e50a5` (28 entsog + 8 gie + 33 neso + 6 openmeteo).

## Per-vendor logs

Each parallel agent writes structural-check failures to `BRIEF-LOG-<vendor>.md` in this directory. Separate logs avoid concurrent-write races.

## Parallel execution

Four agents run in parallel — one per vendor. They operate on disjoint paths (different vault dirs, different `content-briefs/<vendor>/`) so there's no file contention. Each commits its own batch of briefs.
