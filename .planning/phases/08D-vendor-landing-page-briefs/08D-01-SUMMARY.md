# Phase 8D Summary: Vendor landing-page content briefs (5 hubs)

**Status:** Complete
**Completed:** 2026-05-20
**Branch:** `docs/v2-milestone-start`

## What was delivered

5 vendor-hub content briefs, one per non-Elexon vendor, ready for Claude Design to render into `authored-pages/<vendor>/_landing.html`:

| Brief | Path | Datasets | Groups | Checks | Discrepancies |
|---|---|---|---|---|---|
| `entsoe` | `content-briefs/entsoe/_landing.md` | 49 | 6 | 10/10 ✓ | 3 |
| `entsog` | `content-briefs/entsog/_landing.md` | 33 | 5 | 10/10 ✓ | 3 |
| `gie` | `content-briefs/gie/_landing.md` | 8 | 2 | 10/10 ✓ | 3 |
| `neso` | `content-briefs/neso/_landing.md` | 33 | 4 | 10/10 ✓* | 3 |
| `openmeteo` | `content-briefs/openmeteo/_landing.md` | 6 | 2 | 10/10 ✓ | 4 |

*NESO Check 7: two known false positives logged in BRIEF-LOG.md (README.md in glob + RECIPE regex excludes numeric slugs). All 33 dataset rows verified manually.

Plus one build-script patch:
- `src/gridflow_front_end/build.py` — `build_vendor()` now checks `authored-pages/<vendor>/_landing.html` before rendering from template. Committed as `8dfcab6`.

## Commits (Wave 2–3)

- `8dfcab6` — `feat(08D): add authored hub override in build_vendor` — build-script patch (Wave 1)
- `8f83f72` — `docs(08D): landing-page brief for openmeteo · 6 vault datasets, 2 groups, triangulated`
- `b2cbf2d` — `docs(08D): landing-page brief for gie · 8 vault datasets (7 AGSI + 1 ALSI), 2 groups, triangulated`
- `6457171` — `docs(08D): landing-page brief for neso · 33 vault datasets, 4 groups, triangulated`
- `bbcc55a` — `docs(08D): landing-page brief for entsog · 33 vault datasets, 5 groups, triangulated`
- `7d56ca4` — `docs(08D): landing-page brief for entsoe · 49 vault datasets, 6 groups, triangulated`

## Key findings and discrepancies surfaced

**Structural coverage:**
- Total vault datasets briefed: 49 + 33 + 8 + 33 + 6 = 129 datasets across 5 vendors
- Total groups defined: 6 + 5 + 2 + 4 + 2 = 19 dataset groups
- All vendor_meta values fully populated; 4 vendors ready for Phase 10 COMING_SOON → REAL_VENDORS promotion

**Cross-vendor discrepancies (15 total):**

1. **ENTSOE**: Lede trailing phrase "cross-vendor proof for the documentation template" is a Phase 7 artefact — Claude Design should remove it; 47 DOC_TYPES vs 49 datasets (shared API doc_type codes — normal); vendor docs access unclear
2. **ENTSOG**: Only 1 of 33 datasets has a Pydantic schema (`EntsogPhysicalFlow`) — 32 are schema-absent; `ENTSOG_TIMEZONE = "UCT"` (not UTC) is a vendor quirk requiring special handling; vendor Swagger UI unfetchable
3. **GIE**: build.py has two COMING_SOON stubs (`gie_agsi` + `gie_alsi`) — Phase 8D unifies as single `gie` hub; ALSI earliest date unverified in vault; ALSI live docs returned 404
4. **NESO**: vault `ls *.md` = 34 (includes README.md) vs 33 real datasets; earliest data date not documented by vendor; rate limit undocumented (10 req/s is gridflow default)
5. **Open-Meteo**: dual base-URL architecture (archive vs forecast hosts); three naming forms coexist (open-meteo/openmeteo/open_meteo); schema file is `weather.py` not `openmeteo.py`; vendor docs is JavaScript playground (unfetchable)

**Schema coverage across vendors:**
- ENTSOE: 32 Pydantic classes — full coverage
- ENTSOG: 1 class (physical_flows only) — 32/33 schema-absent
- GIE: 2 classes (GasStorage + LNGTerminal) — partial (reference/news datasets untyped)
- NESO: 7 classes — good coverage via dynamically-generated transformer classes
- Open-Meteo: 4 classes in `schemas/weather.py` (not `schemas/openmeteo.py`) — full coverage

**Build override patch:**
The `authored-pages/<vendor>/_landing.html` override check was added to `build_vendor()` before calling `render_vendor_hub()`. Pattern mirrors the existing dataset-page override (Phase 8B). ~5 LoC change.

## BRIEF-LOG.md

One false positive logged:
- `neso` Check 7: `ls *.md | wc -l` = 34 (README included); RECIPE regex `[a-z_]+` excludes numeric slug suffixes (fw24h, fw48h, etc.). True dataset count is 33; all 33 rows manually verified. Recommendation: RECIPE Check 7 regex should use `[a-z0-9_]+`.

## What this unblocks

- **Phase 9 (ENTSO-E)**: `content-briefs/entsoe/_landing.html` brief ready; user can Claude-Design the hub. 49 dataset content briefs are the Phase 9 deliverable.
- **Phase 10 (four-vendor batch)**: all 4 remaining vendor landing-page briefs ready. Phase 10 per-dataset briefs for entsog (33) + gie (8) + neso (33) + openmeteo (6) = 80 new dataset briefs.
- **build.py Phase 10 promotion**: vendor_meta values are fully defined in all 5 briefs; Phase 10 can promote entsog/gie/neso/openmeteo from COMING_SOON_VENDORS to REAL_VENDORS without additional research.
