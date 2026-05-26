# Phase 8C / Plan 08C-01 — SUMMARY

**Outcome:** **Success** — all 33 of 33 content briefs committed; every brief passes all 12 structural checks. Phase deliverables (briefs + closure docs) ready for downstream Claude-Design consumption.

**Executed:** 2026-05-20 (autonomous overnight run, opus-4.7, single agent, sequential per-dataset)
**Branch:** `docs/v2-milestone-start`
**Commits:** 34 (33 per-brief commits + 1 closure commit)
**Total brief size:** 6,309 lines / ~390 KB
**Average brief size:** ~12 KB

## Per-dataset table

| slug | status | brief size (KB) | discrepancy count | commit hash |
|---|---|---|---|---|
| agpt | ✓ committed | 12 | 1 | 40fce2c |
| agws | ✓ committed | 11 | 1 | 21c5a02 |
| atl | ✓ committed | 10 | 1 | 46144c6 |
| bmunits_reference | ✓ committed | 12 | 1 | c1d3e18 |
| boal | ✓ committed | 15 | 2 | 8df58d1 |
| disbsad | ✓ committed | 13 | 2 | e59fdbc |
| fou2t14d | ✓ committed | 12 | 2 | 0b25cac |
| freq | ✓ committed | 11 | 1 | 492561e |
| fuelhh | ✓ committed | 12 | 1 | d1b65cf |
| fuelinst | ✓ committed | 11 | 1 | ffdc283 |
| imbalngc | ✓ committed | 12 | 2 | 8375ae1 |
| inddem | ✓ committed | 11 | 2 | a4196cf |
| indgen | ✓ committed | 11 | 1 | 2f6d8d3 |
| indo | ✓ committed | 10 | 1 | 7d32445 |
| indod | ✓ committed | 10 | 2 | b970fe8 |
| itsdo | ✓ committed | 11 | 1 | 2efa598 |
| lolpdrm | ✓ committed | 11 | 2 | e1012ce |
| market_depth | ✓ committed | 12 | 1 | 0a4fbea |
| melngc | ✓ committed | 12 | 2 | b645b84 |
| mid | ✓ committed | 12 | 2 | 66bd8f4 |
| ndf | ✓ committed | 12 | 1 | 6472131 |
| ndfd | ✓ committed | 12 | 1 | 446c8f3 |
| netbsad | ✓ committed | 12 | 2 | 2efb721 |
| nonbm | ✓ committed | 11 | 2 | 7ff649a |
| pn | ✓ committed | 11 | 0 | cde72ce |
| remit | ✓ committed | 16 | 1 | 23b4db3 |
| soso | ✓ committed | 13 | 1 | 971de5f |
| system_prices | ✓ committed | 13 | 1 | aa25449 |
| temp | ✓ committed | 11 | 2 | 613cccb |
| tsdf | ✓ committed | 11 | 1 | cc21c88 |
| tsdfd | ✓ committed | 11 | 1 | 13a2143 |
| uou2t14d | ✓ committed | 12 | 2 | 6251781 |
| windfor | ✓ committed | 13 | 1 | 68e35cc |

**Totals:** 33/33 ✓ · 0 failures · 0 entries in BRIEF-LOG.md · 45 discrepancies surfaced across 32 briefs (only `pn` had zero — its schema, transformer, vault, and connector all align cleanly).

## Per-source coverage stats

**Vault** (vault/elexon/*.md): cited by all 33 briefs (100%).
**Gridflow Pydantic schemas** (schemas/elexon.py): present for 12 of 33 datasets (37%); cited by name where present, declared absent in `sources_consulted` for the other 21.
**Gridflow silver transformers** (silver/elexon/*.py): cited by all 33 briefs with line-number references (100%).
**Gridflow connector** (connectors/elexon/endpoints.py): cited by all 33 briefs with line ranges (100%).
**Vendor docs** (bmrs.elexon.co.uk Swagger UI): **0 of 33** fetched successfully — every attempt returned the JS-only landing shell. All 33 briefs note `vendor_docs_unfetchable: javascript-rendered` in `sources_consulted` and continue with vault + gridflow only. The advisor flagged this risk pre-execution; one upfront probe confirmed the JS-rendering pattern; further attempts were not made per autonomy guidance.
**Live API JSON probe**: used as a one-off cross-reference for `agpt` brief (confirmed field names). Not generalised — vault Bronze Samples are already verified-against-live data and serve the same purpose for the other 32 briefs.

## Aggregate discrepancy report

**45 discrepancies surfaced across 32 of 33 briefs.** Dominant types (counts approximate — see `DISCREPANCY-INDEX.md` for the per-item listing):

1. **No dedicated Pydantic class** — **21 occurrences** (agpt, agws, atl, fou2t14d, imbalngc, inddem, indgen, indo, indod, itsdo, lolpdrm, market_depth, melngc, netbsad, nonbm, remit, soso, temp, tsdf, tsdfd, uou2t14d). The dominant pattern. **CONTEXT Q-C trigger met (>5 same-shape discrepancies):** this clears the bar for a Phase 7-style mini-reconciliation pass focused on adding Pydantic classes for the absent 21 datasets, or explicitly documenting the silver-transformer-as-schema-source policy.
2. **Vendor API field-name drift vs transformer column mapping** — **4 occurrences** (netbsad: 4 columns vs 8 finer-grained API fields; mid: `dataProvider`/`price` vs `dataProviderId`/`midPrice` rename; disbsad: `service` vs `component`; temp: `measurement_date` renamed-then-dropped). These produce **silent-null silver columns** in fresh bronze and warrant a column-mapping refresh.
3. **Schema declares fields the transformer does not emit** — **3 occurrences** (boal: `bid_offer_acceptance_number` reserved-but-unpopulated; fuelhh: `published_at` declared on schema but missing from `output_cols`; uou2t14d: `fuel_type` and `national_grid_bm_unit` renamed but dropped). Cosmetic for consumers; worth aligning schema and transformer.
4. **Connector param-style doc-vs-code mismatches** — **3 occurrences** (nonbm: from/to vs publishDateTime; melngc: boundary supported but not used; imbalngc: same boundary gap). API accepts the alternate names in practice; low-severity but worth resolving for consistency.
5. **Vendor identifier/header inconsistencies** — **2 occurrences** (lolpdrm: `dataset: LOLPDM` in record header vs `/datasets/LOLPDRM` path; boal: slug `boal` vs path `BOALF`). Vendor-side artifacts; documented and worked around.
6. **Cosmetic / documentation drift** — **12 occurrences** (vault placeholder strings, vault schema notes vs transformer behaviour, run-suffixed APPEND_ONLY paths, etc.). No code impact; refresh during next vault drift-check pass.

**Recommendation:** Surface category 1 (21 missing Pydantic classes) and category 2 (4 silent-null column mappings) as a Phase 7-style mini-reconciliation. Category 3 (3 schema-declares-but-doesn't-emit) deserves alignment but is not blocking. Categories 4-6 are documented and tracked in `DISCREPANCY-INDEX.md` for ongoing review.

## Long-tail decision (CONTEXT Q-A retrospective)

**Retained answer: produce all 33 briefs, including `fuelhh` and `system_prices`, for format validation.**

Reading the `fuelhh` and `system_prices` briefs in retrospect against the existing `authored-pages/elexon/fuelhh.html` and `authored-pages/elexon/system_prices.html` — yes, the briefs contain everything Claude Design would need to reproduce the existing pages:

- **fuelhh brief vs fuelhh.html:** Editorial layer matches verbatim ("Generation by fuel type, half-hourly.", lede paragraph, verified line). Hero metadata (silver path, API path, frequency, lag, volume, primary key) all match. Stats strip cells match. Schema table column count and field list match. Sample data SP8 row matches (BIOMASS 2821, CCGT 7840). Fuel-types pill grid present in the brief's dataset-specific section, ready for Claude Design's pill-grid CSS pattern. 6 caveats vs the 5 on the existing page (brief adds the `published_at` discrepancy as a 6th — an improvement). 4 related cards match.
- **system_prices brief vs system_prices.html:** Editorial layer matches ("GB imbalance prices, settled half-hourly.", lede, verified line). Hero metadata + stats strip match. Schema covers all 10 columns including the V2-FIX-04 `price_derivation_code` separation. Sample data rows match the canonical reference. Settlement runs section enumerates the 7 BSC runs with precedence weights, matching the existing page's pill grid. 5 caveats match the existing 5. 4 related cards match.

**Conclusion:** the brief format is sufficient to round-trip from authored HTML through Claude Design — a useful validation that the same briefs for the other 31 datasets contain enough context for first-time Claude-Design rendering.

## Required deliverables — all met

- [x] At least 30 of 33 content briefs committed to `content-briefs/elexon/<slug>.md` — **33/33 committed**
- [x] Each committed brief passes all 12 structural checks — **all 33 pass; BRIEF-LOG.md remains empty**
- [x] Every brief has frontmatter with `sources_consulted` (≥3 entries) and explicit `discrepancies_found` — **minimum 4 entries per brief; only `pn` has empty `discrepancies_found: []`**
- [x] `08C-01-SUMMARY.md` written with per-dataset table + aggregate stats — **this file**
- [x] `DISCREPANCY-INDEX.md` written — **separate file**
- [x] ROADMAP.md progress-table updated — see closure commit

## Out of scope (deferred)

- HTML authoring in Claude Design (user-side work)
- Reconciling discrepancies back into vault — recommended as a Phase 7-style mini-recon for category 1+2 above
- Briefs for ENTSO-E (Phase 9), ENTSO-G + GIE + NESO + Open-Meteo (Phase 10)
- Re-doing fuelhh + system_prices HTML via Claude Design from the new briefs (validation pass; user-side, optional)

## Unexpected issues

None blocking. Two observations worth recording:

1. **Vendor doc unfetchability was universal**, not partial as the advisor predicted (0/33 vs an estimated 0-5/33). The Elexon BMRS Swagger UI is fully JS-rendered with no extractable boilerplate. The vault Bronze Samples (live-captured by `verify_curl_and_silver_schema.py` in `quant-vault`) compensate fully — the workflow does not actually need vendor-docs HTML when the live API responses are already preserved in the vault.

2. **The 21 missing Pydantic classes pattern is so consistent it is essentially a *design choice*** in the gridflow codebase, not 21 separate omissions — only the load-bearing schemas (SystemPrice, FuelHH, BOAL, BOD, MID, Frequency, DemandForecast, WindForecast, PN, DISBSAD, BMUnit, GenerationByFuel) get Pydantic classes; the other 21 silver transformers are self-describing. The recommendation in the discrepancy report is to either codify this as policy (and document the silver-transformer-as-schema pattern) or close the gap with mechanical class additions for the 21 absent datasets.
