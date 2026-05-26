---
phase: 07-reconciliation
plan: "03"
subsystem: reconciliation
tags: [vault-edit, re-vendor, drift-check, finding-closure, elexon, entsoe, entsog, neso]
dependency_graph:
  requires: [07-02-run-verification-and-triage]
  provides: [vault-drift-clean, finding-ledger-closed]
  affects: [vault/elexon, vault/entsoe, vault/entsog, .planning/reconciliation]
tech_stack:
  added: []
  patterns:
    - D-01: Vault is derivative of Canonical (Pydantic schemas). Never edit gridflow/.
    - Re-vendor via `cp + diff -q` byte-equivalence gate
    - Finding closure via Python regex over frontmatter YAML
key_files:
  created:
    - .planning/phases/07-reconciliation/07-03-RERUN-REPORT.md
    - vault/entsoe/actual_generation_units.md
    - vault/entsoe/aggregated_balancing_energy_bids.md
    - vault/entsoe/auction_revenue.md
    - vault/entsoe/balancing_energy_bids.md
    - vault/entsoe/balancing_financial_expenses_income.md
    - vault/entsoe/congestion_income.md
    - vault/entsoe/congestion_management_costs.md
    - vault/entsoe/cross_border_flows.md
    - vault/entsoe/cross_zonal_balancing_capacity.md
    - vault/entsoe/current_balancing_state.md
    - vault/entsoe/dc_link_intraday_transfer_limits.md
    - vault/entsoe/generation_forecast.md
    - vault/entsoe/generation_units_master_data.md
    - vault/entsoe/installed_capacity.md
    - vault/entsoe/installed_capacity_units.md
    - vault/entsoe/net_transfer_capacity.md
    - vault/entsoe/outages_consumption.md
    - vault/entsoe/outages_generation.md
    - vault/entsoe/outages_offshore_grid.md
    - vault/entsoe/outages_production.md
    - vault/entsoe/outages_transmission.md
    - vault/entsoe/procured_balancing_capacity.md
    - vault/entsoe/water_reservoirs.md
    - vault/entsoe/wind_solar_forecast.md
    - vault/entsog/ (new directory: 5 files)
  modified:
    - vault/elexon/ndf.md
    - vault/elexon/ndfd.md
    - vault/elexon/fuelhh.md
    - vault/elexon/windfor.md
    - vault/elexon/bmunits_reference.md
    - vault/elexon/boal.md
    - vault/elexon/system_prices.md
    - vault/entsoe/actual_generation.md
    - .planning/reconciliation/elexon/ (10 findings closed)
    - .planning/reconciliation/entsoe/ (35 findings: 24 closed + 11 wontfix)
    - .planning/reconciliation/entsog/ (5 findings closed)
    - .planning/reconciliation/neso/ (1 finding closed)
decisions:
  - "D-01 re-triage: 11 ENTSO-E findings with no canonical class -> wontfix/v3-candidate"
  - "Resolution field fix inverted vs plan: str='' is NOT nullable (annotation_allows_none returns False)"
  - "NESO transient DNS failure confirmed resolved in re-run (no Vault edit needed)"
metrics:
  duration: "~120 minutes (continuation agent)"
  completed: "2026-05-19"
  tasks_completed: 4
  files_changed: 37
---

# Phase 07 Plan 03: Fix Open Bucket and Re-vendor Summary

**One-liner:** Eliminated all 33 verifier schema failures by fixing Vault nullability mismatches (Elexon, ENTSO-E, ENTSO-G) and rewriting the physical_flows schema table; re-vendored 37 files byte-identically; closed 36 findings, wontfix'd 11 D-01 no-canonical-class findings.

---

## What Was Built

### Task 1 — Vault edits (in quant-vault, 5 commits)

**Elexon (7 files, 10 findings):**
- `ndf.md`, `ndfd.md`: Renamed `issue_time` → `published_at` (source `publishTime`); changed `national_demand_mw` Nullable: Yes → No (canonical: `float`, not nullable)
- `fuelhh.md`: Added `published_at` row to schema table (was missing from docs, in canonical)
- `windfor.md`: Changed `settlement_date`, `settlement_period` Nullable: No → Yes (canonical: `date | None`, `int | None`); renamed `issue_time` → `published_at`
- `bmunits_reference.md`: Changed `fuel_type` Nullable: No → Yes (canonical: `str | None = None`)
- `boal.md`: Added `bid_offer_acceptance_number` row (was missing; canonical: `int | None`)
- `system_prices.md`: Removed `\|` escape from `str | None` type cells (caused column-shift in parser); kept Nullable: Yes; added notes clarifying optional

**ENTSO-E (25 files, 25 findings):**
- `str = ""` fields (resolution, business_type, bid_mrid, direction, area_name, market_agreement_type, unit_name, production_type, asset_mrid, asset_name, outage_type, document_mrid, document_status, timeseries_mrid, data_provider, original/standard_market_product): Changed Yes/Yes(default "") → No. `annotation_allows_none(str) = False`.
- `datetime[UTC] \| None` type cells (ingested_at): Removed `\|` escape to fix column-shift parser bug; kept Nullable: Yes (canonical: `datetime | None = None`)
- `cross_border_flows.md`: Removed extra `resolution` row (canonical `EntsoeCrossborderFlow` has no `resolution` field)

**ENTSO-G (5 files, 5 findings):**
- `hydrogen_content.md`, `interruptions.md`, `methane_content.md`, `oxygen_content.md`: Added `removed: 2026-05-19` + `removed_reason` to frontmatter (vendor took endpoints down, HTTP 404)
- `physical_flows.md`: Rewrote 35-field malformed bronze-dump schema table to correct 9-field silver table matching `EntsogPhysicalFlow`; updated Silver sample; added Bronze response keys section

### Task 2 — Re-vendor (3 commits in gridflow-front-end)

- Copied 37 files from quant-vault to gridflow-front-end/vault/
- Created vault/entsog/ directory (new vendor mirror)
- All 37 files byte-verified: `diff -q == 0` against upstream quant-vault
- D-01 re-triage: 11 ENTSO-E no-canonical-class findings → wontfix/v3-candidate
- 36 findings closed (Elexon 01-10, ENTSO-E nullability 24 findings, ENTSO-G 01-05, NESO 01)

### Task 3 — Drift check re-run

**Results (07-02 baseline → 07-03 re-run):**
- Schema failed: **33 → 0** (complete elimination)
- Schema passed: **56 → 89** (+33)
- Curl failed (non-auth): **7 → 5** (NESO + melngc DNS flakes resolved naturally)
- 35 ENTSO-E 401 auth failures: unchanged (expected, pre-existing)

**NESO finding:** regional_scotland was `HTTP=0 getaddrinfo()` in baseline, not in failed list in re-run → transient DNS confirmed. Closed without Vault edit.

### Task 4 — CI gates (awaiting human verification)

All gates passed locally:
- `gridflow-build --check`: OK — 34 pages + 7 hubs/stubs, idempotent
- `htmlhint`: Scanned 45 files, no errors found
- `lychee --offline --include-fragments`: 968 OK, 0 Errors, 93 Excluded

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Nullability direction was INVERTED in finding acceptance prose**

- **Found during:** Task 1 execution (analysis of what `annotation_allows_none` returns)
- **Issue:** The plan and finding files said "mark Nullable: Yes" for fields like `resolution: str = ""`. But `annotation_allows_none(str)` returns `False` (no `None` in type args). The Vault was showing `Yes (default "")` which the parser reads as `doc_nullable=True`, while canonical has `code_nullable=False` → mismatch. The correct fix is the OPPOSITE: change to Nullable: No.
- **Fix:** Anchored all edits to D-01 (Canonical is source of truth). Changed all `str = ""` fields to Nullable: No. Changed all `str | None = None` fields to Nullable: Yes. This eliminated 33 verifier failures.
- **Files modified:** 25 ENTSO-E files + 7 Elexon files
- **Commits:** `ad65dd4` (ENTSO-E), `c41d162` (Elexon) in quant-vault

**2. [Rule 2 - Missing] `\|` escape in table type cells causes column-shift parser bug**

- **Found during:** Task 1 — examining why `ingested_at: datetime | None` showed as non-nullable
- **Issue:** `str \| None` in a markdown table cell causes the parser to split on `\|` at the table level, shifting cells. `cells[2]` (Nullable column) receives `None` instead of `Yes`. Parser reads `"None".startswith("y") = False` → doc_nullable=False, but canonical is `True` → mismatch.
- **Fix:** Changed type cell from `datetime[UTC] \| None` → `datetime` (keeping Nullable: Yes). Same for `str \| None` → `str` in system_prices. The type column is descriptive documentation, not code; removing the `\|` doesn't lose information when Nullable column is set correctly.
- **Files modified:** system_prices.md (Elexon), 25 ENTSO-E files (ingested_at cells)
- **Commits:** Part of `c41d162`, `ad65dd4` in quant-vault

### D-01 Re-triages (11 findings)

The plan expected these to be closeable by Vault edit. They cannot be:
- No canonical Pydantic class exists for: `commercial_schedules_net_positions`, `countertrading`, `net_positions`, `offered_transfer_capacity_continuous/explicit/implicit`, `redispatching_cross_border/internal`, `total_capacity_allocated`, `total_nominated_capacity`, `transfer_capacity_use`
- Authoring a schema table without a canonical class violates D-01 (Vault is derivative)
- Re-triaged to `wontfix/v3-candidate`: canonical classes must be added to gridflow first

---

## Drift Check Delta Table

| Metric | 07-02 | 07-03 | Delta |
|--------|-------|-------|-------|
| Schema passed | 56 | 89 | +33 |
| Schema failed | 33 | 0 | -33 |
| Schema manual_transformer | 58 | 58 | 0 |
| Schema no_silver_schema_table | 14 | 14 | 0 |
| Schema no_silver_section | 1 | 1 | 0 |
| Curl passed | 120 | 122 | +2 |
| Curl failed (non-auth) | 7 | 5 | -2 |
| Curl failed_auth | 35 | 35 | 0 |

---

## Finding Ledger Final State

| Vendor | Closed | Wontfix/v3 | Still open |
|--------|--------|------------|-----------|
| Elexon (07-03 scope) | 10 | 0 | 0 |
| ENTSO-E (07-03 scope) | 24 | 11 | 0 |
| ENTSO-G | 5 | 0 | 0 |
| NESO | 1 | 0 | 0 |
| **Total** | **40** | **11** | **0** |

Note: Elexon findings 11-32 (manual-transformer-schema) and ENTSO-E findings 01-36 (401 auth) and ENTSO-G findings 06-33 (manual-transformer-schema) were closed/wontfix'd in plan 07-02.

---

## Known Stubs

None — this plan only edits Vault markdown documentation files and finding records. No site HTML was generated or modified directly.

---

## Self-Check: PASSED

- vault/entsog/ directory: FOUND
- 5 ENTSO-G files in vault/entsog/: FOUND
- 25 ENTSO-E files in vault/entsoe/: FOUND
- 07-03-RERUN-REPORT.md: FOUND
- Commit 60004c2 (re-vendor): FOUND
- Commit a62acad (findings closure): FOUND
- Commit 63dbda5 (NESO + report): FOUND
- Schema failed in re-run: 0 (verified in report)
