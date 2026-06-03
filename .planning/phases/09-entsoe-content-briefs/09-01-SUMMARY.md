# Phase 9 — ENTSO-E full coverage — SUMMARY

**Status:** ✅ Complete 2026-06-03
**Branch:** `feat/phase-9-entsoe-pages`
**Requirements satisfied:** ENTSOE-01, ENTSOE-02, ENTSOE-03, ENTSOE-04, ENTSOE-05

---

## Outcome

All **49 ENTSO-E datasets** are documented at `fuelhh` fidelity. The
`/data-sources/entsoe.html` hub went from a 1-dataset cross-vendor proof to a
**49-dataset catalog**. This was the largest single vendor in v2 and the first
non-Elexon vendor authored at scale — it proved the authored-page pipeline holds
against ENTSO-E's different schema vocabulary (codelists, PSR-type taxonomy,
bidding-zone / zone-pair domains, quarter-hour settlement, H6/H7 transformer
families).

## Two-step delivery

1. **Briefs (step 1) — complete 2026-05-20.** 49 self-contained content briefs at
   `content-briefs/entsoe/<slug>.md`, produced by a background agent against the
   tightened D-20 format (7 commits `aab2128..9b5e296`). 35 flagged
   `entitlement_required: true` (resolves the Phase 7 D-06 entitlement question via
   STATE D-21 — produce-full-brief-from-source, flag-in-frontmatter).
2. **Page authoring (step 2) — complete 2026-06-03 (this phase's close).** The 49
   briefs + the D-22 reference page were carried through **Claude Design** in 5
   batches; output verified, landed into `authored-pages/entsoe/<slug>.html`, and the
   `site/hifi/data/entsoe.json` manifest authored to 49 entries.

## Claude Design batches (step 2)

| Batch | Datasets | Notes |
|---|---|---|
| 1 | day_ahead_prices, installed_capacity (+ `_landing` hub, + `actual_generation` D-20→D-22 upgrade) | Established the D-22 page anatomy; fixed `_landing.html` asset/href depth (hub is one level shallower than dataset pages) |
| 2 | generation/load forecasts (5) | — |
| 3 | balancing cluster (10) | `activated_balancing_qty` silver-only discrepancy surfaced; `barsH` data-driven `items` arrays first used |
| 4 | transmission / transfer-capacity (12) | `commercial_schedules_net_positions` deprecation pointer (ADR-019); `net_positions` zone-not-zone-pair discrepancy |
| 5 | outages (5) + long tail (12) | Final tranche → 49/49. First batch needing **zero** vault edits |

## Success criteria — all met

1. ✅ `ls vault/entsoe/*.md` = 49; entitlement decision documented (skip-with-warn caveat, STATE D-21).
2. ✅ `site/hifi/data/entsoe.json` = exactly 49 dataset entries, grouped into 9 categories; valid JSON, no duplicate ids.
3. ✅ `gridflow-build` writes 49 authored HTML files under `site/hifi/data-sources/entsoe/`; sidebar anchors resolve; entitlement wording present on the 35 blocked datasets; codelist/PSR vocabulary renders cleanly.
4. ✅ `/data-sources/entsoe.html` renders a 49-dataset catalog (49 cards, 6 editorial groups).
5. ✅ All three CI gates verified locally (not just deferred to CI): `gridflow-build --check` exits 0 (idempotent across 86 pages + 8 hubs); `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` = 174 files, 0 errors; `lychee --no-progress --offline --include-fragments './site/hifi/**/*.html'` = 0 errors (after the `#about` hub fix — see below).

## Deviation from original SC#3 (positive)

ROADMAP SC#3 was written under D-20, which stated `#overview` and `#caveats` are
*intentionally absent*. During the Claude Design batches the user chose
**overview synthesis at render time** (the D-22 decision applied to ENTSO-E): every
page now carries a synthesised 3-paragraph `#overview` and a `#caveats` section.
The shipped pages are therefore **richer** than SC#3 required — `#overview` and
`#caveats` are present, not absent. This aligns ENTSO-E with the D-22 Elexon format.

## Notable handling

- **Entitlement (35 datasets):** no visual banner; verified line says "live API requires
  extended ENTSO-E registration"; final caveat is the 401 entitlement note. `actual_load`
  is the sole free-tier dataset and correctly carries no entitlement note.
- **Discrepancies:** surfaced only where a brief's `discrepancies_found` is populated —
  e.g. `congestion_management_costs` (`domain_style="zone"`, cites `endpoints.py L184`),
  `net_positions`, `commercial_schedules*`, `actual_generation` (`area_name` declared-not-emitted).
  Verified each rendered discrepancy against its brief; no fabricated discrepancies.
- **Hub `#about` anchor (lychee CI gate):** running the real CI link-checker locally
  surfaced 49 errors — every ENTSO-E dataset page links to `../entsoe.html#about`
  ("ENTSO-E-wide caveats", mirroring the Elexon pattern), but Claude Design's hub titled
  that section "What to watch for." and omitted `id="about"`. Fix: added `id="about"` to
  the existing caveats section in `authored-pages/entsoe/_landing.html` (respects CD's
  content; no new section). lychee then 0 errors (2578→2627 OK). This is the gate the
  pages had never hit (uncommitted = unlinted until close-out).
- **Vault build-blocker fixes (derivative-vault rule):** `activated_balancing_qty.md`
  (silver-only — `## Expected API tuple` → `## API endpoint` + silver-only callout) and
  `commercial_schedules_net_positions.md` (deprecated — added `## Overview` + `## API endpoint`).
  Both fixes landed in the vault `.md` to satisfy the build's content validator, never by
  inverting the SoT hierarchy.

## Carried forward (not blocking)

- **Latent production bug — `data-root` on authored vendor hubs.** Every authored
  `_landing.html` (entsoe **and** elexon) sets `data-root="../../"`, but a vendor hub is one
  level below the site root, so on the GitHub Pages *project* subpath
  (`EBentham.github.io/gridflow-front-end/`, no CNAME) the JS-injected nav/footer links
  resolve to the org root and break. Invisible locally (localhost serves at origin root,
  where the extra `../` clamps). The canonical template `vendor-hub.html.j2` correctly uses
  `data-root="../"`. Site-wide, so deferred to a separate fix (spawned task) rather than
  diverging ENTSO-E from Elexon in this phase.
- **Manifest taxonomy (9 groups) vs hub editorial taxonomy (6 groups).** Internal-only:
  the cross-vendor `data-sources.html` shows a vendor card (not group names), and authored
  pages bypass the template's `manifest_siblings`. No user-visible inconsistency. Pre-existing
  pattern since Batch 1.

## Next

Phase 10 — four-vendor batch (ENTSO-G 33 · GIE 8 · NESO 34 · Open-Meteo 6 = 81 datasets)
+ site-wide count strings to 163 + move the four vendors from `COMING_SOON_VENDORS` to
`REAL_VENDORS`.
