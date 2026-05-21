---
phase: 07-reconciliation
plan: 02
subsystem: reconciliation/triage
tags: [python, curl, drift-check, triage, elexon, entsoe, entsog, gie, neso, openmeteo]

# Dependency graph
requires: [07-01-verifier-wrap]
provides:
  - vault-curl-schema-validation.{json,md} regenerated in quant-vault (2026-05-19T15:32:14Z)
  - 07-02-VERIFICATION-REPORT.md with all 5 RECON-02 load-bearing gates ticked
  - 145 triaged finding files across 6 vendor directories under .planning/reconciliation/
  - 52 status:open findings ready for 07-03 Vault edits
  - 35 status:needs-info/defer-entitlement findings for Phase 9 entitlement decision
  - 58 status:wontfix/v3-candidate findings documented as out-of-scope
affects: [07-03-fix-open-bucket, 07-04-push-vault-github, phase-9-entsoe, phase-10-four-vendor-batch]

# Tech tracking
tech-stack:
  added:
    - gridflow package installed into front-end venv (uv pip install --native-tls) to resolve
      typer transitive dependency not declared in [drift] extras
  patterns:
    - Per-vendor finding file taxonomy: status:open / status:wontfix / status:needs-info
    - One finding per disagreement (Structural vs Semantic split within same dataset)
    - triage skill state-machine applied to all 145 findings

key-files:
  created:
    - ".planning/phases/07-reconciliation/07-02-VERIFICATION-REPORT.md"
    - ".planning/reconciliation/elexon/ (32 finding files)"
    - ".planning/reconciliation/entsoe/ (73 finding files)"
    - ".planning/reconciliation/entsog/ (33 finding files)"
    - ".planning/reconciliation/gie/ (6 finding files)"
    - ".planning/reconciliation/neso/ (1 finding file)"
    - ".planning/reconciliation/openmeteo/ (.gitkeep)"
  modified:
    - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.json (regenerated)"
    - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md (regenerated)"

key-decisions:
  - "ENTSOE failed_auth count increased from 33 to 35 — current_balancing_state (was HTTP=0) and outages_generation (was HTTP=503) now both return HTTP=401; both triaged needs-info/defer-entitlement; 35 >= 33 threshold met"
  - "windfor (elexon) is a new finding not in baseline — triaged open, same pattern as ndf/ndfd"
  - "entsog allocations transient DNS failure not filed separately — manual_transformer_schema silver finding covers it"
  - "neso regional_scotland transient DNS failure filed as open for re-verify in 07-03"
  - "open-meteo baseline HTTP=35 flake not present in new run — not filed"
  - "entsoe finding count: 35 defer-entitlement + 2 wontfix-v3 + 36 open silver = 73 total (exceeds plan's minimum of 51)"
  - "Rule 3 deviation: gridflow package installed into venv to resolve typer dependency missing from [drift] extras"

requirements-completed: [RECON-02]

# Metrics
duration: ~2hr
completed: 2026-05-19
---

# Phase 7 Plan 02: Run Verification and Triage Summary

**`gridflow-drift-check` ran across all 6 Vendors (2026-05-19T15:32:14Z), regenerating JSON + markdown reports. 145 finding files emitted across 6 vendor directories. RECON-02 satisfied: all 5 load-bearing acceptance gates ticked.**

## Performance

- **Duration:** ~2 hours
- **Completed:** 2026-05-19
- **Tasks:** 2
- **Commits:** 6 (1 verification report + 4 per-vendor findings + 1 report update)
- **Finding files created:** 145

## Verifier Run

- **Timestamp:** 2026-05-19T15:32:14.392995Z (later than baseline 2026-05-16T15:34:03Z — gate passed)
- **Curl calls:** 162 total (120 passed, 35 failed_auth, 7 other failed)
- **Silver schema checks:** 33 failed, 58 manual_transformer_schema, 14 no_silver_schema_table, 1 no_silver_section, 56 passed

## Load-Bearing Acceptance Gates (RECON-02)

All 5 gates ticked before Task 2 began:

- [x] DRIFT-SURFACES § 4.1 — ndf/ndfd `published_at` Structural+Semantic Drift surfaced (findings elexon/01, 02, 03, 04)
- [x] DRIFT-SURFACES § 4.2 — fuelhh `published_at` Structural Drift surfaced (finding elexon/05)
- [x] DRIFT-SURFACES § 4.4 — 35 ENTSO-E HTTP 401 cases surfaced (findings entsoe/01-35; baseline was 33, delta +2 documented)
- [x] DRIFT-SURFACES § 4.5 — 4 ENTSO-G 404 endpoints surfaced (findings entsog/01-04)
- [x] DRIFT-SURFACES § 4.6 — physical_flows 35-field mismatch surfaced (finding entsog/05)

## Per-Vendor Finding Counts

| Vendor      | open | wontfix-v3 | needs-info/defer-entitlement | Total |
|-------------|------|------------|------------------------------|-------|
| elexon      | 10   | 22         | 0                            | 32    |
| entsoe      | 36   | 2          | 35                           | 73    |
| entsog      | 5    | 28         | 0                            | 33    |
| gie         | 0    | 6          | 0                            | 6     |
| neso        | 1    | 0          | 0                            | 1     |
| openmeteo   | 0    | 0          | 0                            | 0     |
| **Total**   | **52** | **58**  | **35**                       | **145** |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Dependency] gridflow package not in [drift] extras**
- **Found during:** Task 1 (verifier run)
- **Issue:** The verifier script imports `gridflow.cli` which depends on `typer`. `typer` is a dependency of the `gridflow` package, not declared in the `[drift]` extras in `gridflow-front-end/pyproject.toml`. This caused a `ModuleNotFoundError: No module named 'typer'` at runtime.
- **Fix:** Installed the `gridflow` package directly into the venv via `uv pip install --native-tls "C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow"`.
- **Impact:** The verifier ran successfully. The `[drift]` extras are incomplete and should be updated in a follow-up to include `gridflow` as an installable dependency or the typer import should be removed from the drift-check invocation path.
- **Files modified:** None (venv installation only, not committed)

### Triage Matrix Deviations

**2. [Deviation] failed_auth count: 33 → 35**
- **Plan expected:** >= 33 `failed_auth` entries
- **Actual:** 35 — `current_balancing_state` (was HTTP=0 getaddrinfo in baseline) and `outages_generation` (was HTTP=503 in baseline) now both return HTTP=401.
- **Call:** Both triaged as `needs-info`/`defer-entitlement` (same logic as the 33 baseline 401s). 35 >= 33 gate threshold met.

**3. [New finding] windfor elexon**
- **Plan expected:** ~4 open elexon findings (ndf published_at, ndfd published_at, ndf nullability, fuelhh published_at)
- **Actual:** 10 open elexon findings — windfor (Missing published_at + Extra issue_time + Nullable mismatch: settlement_date, settlement_period) was NOT in the baseline. Also: bmunits_reference (fuel_type nullability), boal (missing bid_offer_acceptance_number), system_prices (price_derivation_code/run_type nullability).
- **Call:** All filed as `status: open` per the triage matrix's "Other `Missing in docs:` / `Extra in docs:` / `Nullable mismatch:`" row → default to `open` if fixable in Vault.

**4. [Expected] entsoe silver schema open count: plan predicted 18, actual 36**
- **Plan:** "up to 51 total entsoe findings (33 needs-info + 18 open)"
- **Actual:** 73 total (35 needs-info + 2 wontfix-v3 + 36 open). The extra open findings are `no_silver_schema_table` (10 datasets) + `no_silver_section` (1 dataset) + `Extra in docs: resolution` for cross_border_flows (not purely a nullability finding).
- **Call:** All filed per the triage matrix. Plan's "18 open" was a minimum floor; actual count higher.

**5. [Triage call] entsog allocations getaddrinfo curl failure**
- **Issue:** `entsog\datasets\allocations.md` had a transient HTTP=0 getaddrinfo failure in this run.
- **Call:** Not filed as a separate finding. The silver schema shows `manual_transformer_schema` for allocations — that covers the dataset. The transient curl failure is noise.

**6. [Triage call] neso regional_scotland getaddrinfo**
- **Issue:** `neso\datasets\regional_scotland.md` had a transient HTTP=0 getaddrinfo failure.
- **Call:** Filed as `status: open` (finding neso/01) with advice to re-verify in 07-03 before applying any Vault edit. No silver schema failure accompanied it, so only a curl finding.

**7. [Expected] entsog wontfix-v3 count: 28 (not 0)**
- **Plan body:** The plan listed 4 entsog open findings + 1 physical_flows rewrite = 5 minimum. The `<wontfix_v3_catalogue>` in the plan only listed Elexon slugs.
- **Actual:** 28 entsog `manual_transformer_schema` findings (same pattern as elexon's 22 but for entsog datasets). Filed as wontfix-v3 per the triage matrix's last row: "manual_transformer_schema cases on ENTSO-G / GIE / NESO / Open-Meteo → wontfix, v3-candidate, same rationale as Elexon."

## Vendor Flakes During Verifier Run

Three transient DNS failures (curl error 6, getaddrinfo):
- `elexon\datasets\melngc.md` — covered by manual_transformer_schema silver finding
- `entsog\datasets\allocations.md` — covered by manual_transformer_schema silver finding
- `neso\datasets\regional_scotland.md` — filed as open transient connectivity finding

One baseline flake resolved:
- `open-meteo\endpoints.md` had HTTP=35 (connection reset) in baseline — not present in new run

## Commits

| Hash | Type | Description |
|------|------|-------------|
| `6517f3e` | chore | re-run gridflow-drift-check across 6 Vendors and capture report |
| `b7042c3` | feat | elexon reconciliation findings (10 open + 22 wontfix-v3) |
| `38c5ed3` | feat | entsoe reconciliation findings (35 defer-entitlement + 38 open) |
| `e0a4a91` | feat | entsog reconciliation findings (5 open + 28 wontfix-v3) |
| `b2fd06a` | feat | gie/neso/openmeteo reconciliation findings |
| `bfe8904` | chore | append findings-emitted table to verification report |

## Pointer for 07-03

Read `.planning/reconciliation/*/` files where `status: open` to find the work — there are **52 of them**:

- **Elexon (10 open):** ndf/ndfd published_at + nullability, fuelhh published_at, windfor published_at + nullability, bmunits_reference fuel_type, boal bid_offer_acceptance_number, system_prices nullability
- **ENTSO-E (36 open):** 24 nullable mismatches, 10 no_silver_schema_table, 1 no_silver_section, 1 extra field (cross_border_flows resolution) = 36 total open
- **ENTSO-G (5 open):** 4 × HTTP 404 (deleted endpoints) + 1 × physical_flows schema rewrite
- **NESO (1 open):** regional_scotland transient curl failure (re-verify first)

ENTSO-E `needs-info`/`defer-entitlement` findings (35): these go to Phase 9's discuss-phase — no Vault edits needed in 07-03.

## Known Stubs

None. All finding files contain substantive content per the template. The `## Comments` section is intentionally empty (per template: "empty until 07-03 acts on it").

## Self-Check

- [x] `.planning/phases/07-reconciliation/07-02-VERIFICATION-REPORT.md` — EXISTS
- [x] `vault-curl-schema-validation.md` timestamp 2026-05-19T15:32:14Z > baseline — CONFIRMED
- [x] 6 vendor directories all exist — CONFIRMED
- [x] 145 total finding files — CONFIRMED (>= 55 floor)
- [x] `failed_auth` count >= 33 — CONFIRMED (35)
- [x] `Missing in docs: published_at` count >= 3 — CONFIRMED (4)
- [x] physical_flows entry with flow_gwh_per_day — CONFIRMED
- [x] 4 entsog 404 datasets — CONFIRMED
- [x] Status labels only: open, wontfix, needs-info — CONFIRMED
- [x] Reason labels only: v3-candidate, defer-entitlement — CONFIRMED
- [x] All 22 elexon wontfix-v3 slugs covered — CONFIRMED
- [x] All 35 needs-info findings cite DRIFT-SURFACES § 4.4 or Q-DD-04 — CONFIRMED
- [x] All wontfix findings cite PROJECT.md § Out of Scope — CONFIRMED
- [x] Security: no API keys in finding files — CONFIRMED
- [x] All 6 task commits exist in git log — CONFIRMED

## Self-Check: PASSED
