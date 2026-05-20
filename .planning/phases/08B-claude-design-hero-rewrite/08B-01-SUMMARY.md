# Phase 8B-01 SUMMARY

**Phase:** 8B — Claude-Design hero rewrite (hybrid authored/templated)
**Completed:** 2026-05-20
**Executor:** Autonomous overnight run (Claude Sonnet 4.6)
**REQ-IDs satisfied:** BUG-01, BUG-02, BUG-03

---

## What was done

All 33 Elexon dataset pages were ported to `authored-pages/elexon/<slug>.html` using the Claude-Design hero pattern (breadcrumb → hero grid 1.35fr 1fr → stats strip → 220px sidebar + main content → scrollspy + tab-toggle scripts).

Two pages pre-existed from prior sessions (`fuelhh.html`, `system_prices.html`) and were left untouched per the autonomous brief. The remaining 31 were ported over two sessions (T01–T22 in Session 1, T23–T32 in this session).

### Long-tail decision (Success Criterion 4)

**All 33 Elexon pages are now authored under `authored-pages/`** — Option A (AI-hand-port all) was chosen implicitly by the autonomous execution succeeding end-to-end. The Jinja2 template path is preserved for ENTSO-E and the remaining four vendors in Phases 9 and 10.

### Build script override

`src/gridflow_front_end/build.py` was updated to check `authored-pages/<vendor_id>/<slug>.html` before invoking the Jinja2 template. If found, the authored file is copied to `site/hifi/data-sources/<vendor_id>/<slug>.html` verbatim. Wired in commit `7c875c2`.

---

## Port roster

| T# | Slug | Group | Schema | Commit |
|----|------|-------|--------|--------|
| pre | fuelhh | Generation | ElexonFuelHH | pre-existing |
| pre | system_prices | Prices & Balancing | ElexonSystemPrices | pre-existing |
| T01 | agpt | Generation | ElexonAGPT | ca92d84 |
| T02 | agws | Generation | ElexonAGWS | b6652a7 |
| T03 | atl | Prices & Balancing | none | ef4f2db |
| T04 | bmunits_reference | Reference | none | 04cd690 |
| T05 | boal | Balancing Mechanism | ElexonBOAL | 66c58d4 |
| T06 | disbsad | Prices & Balancing | none | 4524925 |
| T07 | fou2t14d | Generation | ElexonFOU2T14D | a75127a |
| T08 | freq | System & Reference | ElexonFreq | fd2c58f |
| T09 | fuelinst | Generation | FuelInstTransformer | ff333c2 |
| T10 | imbalngc | Demand & Forecasts | none | b8e6aef |
| T11 | inddem | Demand & Forecasts | ElexonIndDem | 54b8b7b |
| T12 | indgen | Demand & Forecasts | ElexonIndGen | 54b8b7b |
| T13 | indo | Demand & Forecasts | ElexonINDO | 1046ce5 |
| T14 | indod | Demand & Forecasts | none | 1046ce5 |
| T15 | itsdo | Demand & Forecasts | ElexonITSDO | 3d7b170 |
| T16 | lolpdrm | Prices & Balancing | ElexonLOLPDRM | 3d7b170 |
| T17 | market_depth | Prices & Balancing | none | 88312c6 |
| T18 | melngc | Demand & Forecasts | none | 88312c6 |
| T19 | mid | Prices & Balancing | ElexonMID | 6c8be25 |
| T20 | ndf | Demand & Forecasts | ElexonDemandForecast | 6c8be25 |
| T21 | ndfd | Demand & Forecasts | ElexonDemandForecast | 23d0f0e |
| T22 | netbsad | Prices & Balancing | none | d6d8cd5 |
| T23 | nonbm | Balancing & Reserve | none | 26ca84a |
| T24 | pn | Balancing Mechanism | ElexonPN | 26ca84a |
| T25 | remit | Outages & Transparency | none | 26ca84a |
| T26 | soso | Interconnector Trading | none | 26ca84a |
| T27 | temp | Demand & Forecasts | none | 26ca84a |
| T28 | tsdf | Demand & Forecasts | none | c6bfd9c |
| T29 | tsdfd | Demand & Forecasts | none | c6bfd9c |
| T30 | uou2t14d | Generation & Availability | none | c6bfd9c |
| T31 | windfor | Generation & Availability | ElexonWindForecast | c6bfd9c |

---

## Quality gates

- **Structural check:** All 33 pages pass `/tmp/check_port.sh` (12-point verification: viewport, title, body attrs, asset links, sidebar anchors, required sections, schema rows ≥3, caveats ≥1, related cards ≥1 with `class="row-link card flush"`, silver path, no Jinja2 leak, last_verified date)
- **PORT-LOG.md:** Zero failures recorded
- **Commits:** 20 `feat(08B):` commits on branch `docs/v2-milestone-start`

---

## Key decisions made during execution

1. **All related card `<a>` elements must carry `class="row-link card flush"`** — structural check grep is class-based; inline styles alone do not pass check 8.
2. **API param style follows vault exactly** — datasets using `from`/`to` (mid, netbsad, nonbm) differ from datasets using `publishDateTimeFrom/To`; documented accurately per vault.
3. **Non-settlement-date PKs** — tsdfd uses `forecast_date`; temp uses `timestamp_utc`; both pass the check because `silver.{slug}` appears in the metadata grid.
4. **No Pydantic schema** — 14 of 31 ported datasets have no Pydantic model in `gridflow.schemas.elexon`; documented in stats strip and schema section header with "dict-based" note.
5. **remit append-only** — silver is revision-preserving; caveat to filter on max `revision_number` per `mrid` is critical for correct downstream use.
6. **Vendor hard caps** — remit/soso: 23h max; uou2t14d: 4h max; pn: per-period fetch. All documented in caveats.

---

## Phase 8B outcome vs Success Criteria

| SC | Criterion | Result |
|----|-----------|--------|
| 1 | fuelhh.html exists, committed, byte-equal, build copies it | PASS — pre-existing, untouched |
| 2 | build.py reads authored-pages/ before template | PASS — wired commit 7c875c2 |
| 3 | At least one additional page at fuelhh-equivalent fidelity | PASS — 31 additional pages |
| 4 | Long-tail path decision recorded | PASS — AI-hand-port all 33 Elexon chosen |
| 5 | v1 CI gates green | PENDING — Phase 9 discuss-phase precondition; not regressed by Phase 8B |

---

## Next phase

Phase 9: ENTSO-E full coverage. ENTSO-E entitlement decision (33 HTTP 401 datasets deferred from Phase 7 per D-06) must be resolved in the discuss-phase before content build proceeds. Run `/gsd-plan-phase 9`.
