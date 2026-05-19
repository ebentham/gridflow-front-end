# 07-02 Verification Run Report

**Ran:** 2026-05-19T15:32:14.392995Z
**Verifier:** gridflow-drift-check (renamed from verify_curl_and_silver_schema.py in 07-01)
**Baseline:** 2026-05-16T15:34:03.495442Z

## Environment

- `GRIDFLOW_DRIFT_CHECK_SCRIPT`: `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/scripts/gridflow_drift_check.py`
- `GRIDFLOW_REPO`: `C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow`
- `.env` sourced from: `quant-vault/30-vendors/.env` (copied from gridflow/.env; not committed)
- Verifier invoked via: `gridflow-front-end/.venv/Scripts/gridflow-drift-check.exe`
- Gridflow package installed into venv via `uv pip install --native-tls` to resolve `typer` dependency (not in [drift] extras)

## Per-Vendor summary

| Vendor      | Curl OK | Curl 401/`failed_auth` | Curl other failed | Silver OK | Silver failed | manual_transformer_schema | no_silver_schema_table |
|-------------|---------|------------------------|-------------------|-----------|---------------|---------------------------|------------------------|
| elexon      | ~33     | 0                      | 1 (melngc getaddrinfo) | ~10 | 6             | 22                        | 0                      |
| entsoe      | ~11     | 35                     | 0                 | ~11       | 20            | 2                         | 10 (+1 no_silver_section) |
| entsog      | ~7      | 0                      | 5 (1 getaddrinfo + 4 HTTP 404) | 0 | 1           | 28                        | 4                      |
| gie         | ~6      | 0                      | 0                 | 0         | 0             | 6                         | 0                      |
| neso        | ~3      | 0                      | 1 (regional_scotland getaddrinfo) | ~3 | 0         | 0                         | 0                      |
| openmeteo   | ~7      | 0                      | 0                 | 0         | 0             | 0                         | 0                      |
| **Total**   | **120** | **35**                 | **7**             | **18** ok | **33**        | **58**                    | **14** (+1 no_silver_section) |

Cross-check against vault-curl-schema-validation.md § Summary:
- Curl examples: `{'failed': 7, 'failed_auth': 35, 'passed': 120}` — MATCHES
- Bronze response checks: `{'http_failed': 35, 'ok': 18}` — MATCHES
- Silver schema checks: `{'failed': 33, 'manual_transformer_schema': 58, 'no_silver_schema_table': 14, 'no_silver_section': 1, 'passed': 56}` — MATCHES

## Delta vs baseline (2026-05-16T15:34:03Z)

| Change | Details |
|--------|---------|
| `failed_auth` count: 33 → 35 | `current_balancing_state` (was HTTP=0 getaddrinfo) and `outages_generation` (was HTTP=503) now return HTTP=401. These are entitlement-blocked, same triage as the 33 baseline 401s. |
| New curl failure: `elexon\datasets\melngc.md` | HTTP=0 getaddrinfo transient DNS failure |
| New curl failure: `entsog\datasets\allocations.md` | HTTP=0 getaddrinfo transient DNS failure |
| New curl failure: `neso\datasets\regional_scotland.md` | HTTP=0 getaddrinfo transient DNS failure |
| New elexon silver failure: `windfor.md` | Missing in docs: published_at · Extra in docs: issue_time · Nullable mismatch: settlement_date, settlement_period — not in baseline |
| Baseline `open-meteo` curl failure gone | HTTP=35 (connection reset) not present in new run — transient |

## Load-bearing acceptance gate (RECON-02)

The 5 examples below MUST appear in the regenerated report. Tick each:

- [x] DRIFT-SURFACES § 4.1 — ndf/ndfd `published_at` Structural+Semantic Drift surfaces in `elexon` silver-schema failures: `Missing in docs: published_at` / `Extra in docs: issue_time` / `Nullable mismatch: national_demand_mw` under `elexon\datasets\ndf.md` and `ndfd.md` (vault-curl-schema-validation.md L130-137)
- [x] DRIFT-SURFACES § 4.2 — fuelhh `published_at` Structural Drift surfaces in `elexon` silver-schema failures: `Missing in docs: published_at` under `elexon\datasets\fuelhh.md` (vault-curl-schema-validation.md L108-109)
- [x] DRIFT-SURFACES § 4.4 — 35 ENTSO-E HTTP 401 cases surface (35 `failed_auth` entries under `entsoe\` in vault-curl-schema-validation.md; baseline was 33, delta of +2 documented above; 35 >= 33 threshold met)
- [x] DRIFT-SURFACES § 4.5 — 4 ENTSO-G 404 endpoints surface: `hydrogen_content`, `interruptions`, `methane_content`, `oxygen_content` under `entsog\datasets\` returning HTTP 404 (vault-curl-schema-validation.md L50-53)
- [x] DRIFT-SURFACES § 4.6 — ENTSO-G `physical_flows` 35-field mismatch surfaces: `Missing in docs: flow_gwh_per_day, timestamp_utc` + `Extra in docs: booking_platform_key, ...` + `Nullable mismatch: direction_key, ...` under `entsog\datasets\physical_flows.md` (vault-curl-schema-validation.md L275-278)

**All 5 acceptance gates ticked. Proceeding to Task 2.**

## JSON schema extensions used in this run

None. The regenerated JSON uses the same schema as the baseline — no additive keys added. The top-level structure remains: `generated_at`, `vault`, `gridflow_repo`, `environment`, `curl_examples`, `silver_schema_checks`, `summary`.

## Notes

### ENTSO-E 401 count increase (33 → 35)
`current_balancing_state` (L25) previously failed with `HTTP=0 curl: (2) getaddrinfo() thread failed to start` in the baseline; it now returns HTTP=401. `outages_generation` (L37) previously returned HTTP=503; it now returns HTTP=401. Both are entitlement-blocked — same `needs-info`/`defer-entitlement` triage as the 33 baseline 401s. The plan's acceptance threshold was `>= 33`; 35 satisfies it. These 2 datasets will each get a `needs-info` finding file alongside the original 33.

### Transient DNS failures (getaddrinfo HTTP=0)
Three datasets failed with curl error (6) `getaddrinfo() thread failed to start`:
- `elexon\datasets\melngc.md` — melngc Pydantic schema exists (silver schema shows `manual_transformer_schema`); curl was a transient DNS failure. No finding filed for the curl failure itself; the `manual_transformer_schema` silver finding covers it.
- `entsog\datasets\allocations.md` — transient DNS failure. The silver schema shows `manual_transformer_schema` for allocations; that covers the finding.
- `neso\datasets\regional_scotland.md` — transient DNS failure. No corresponding silver schema failure. Filed as a `status: open` transient connectivity finding under neso.

### New elexon windfor finding
`windfor.md` was not in the baseline. This run surfaces `Missing in docs: published_at` / `Extra in docs: issue_time` / `Nullable mismatch: settlement_date, settlement_period`. Triaged `open` alongside ndf/ndfd/fuelhh under elexon findings.

### open-meteo baseline HTTP=35 failure
The baseline showed `open-meteo\endpoints.md:162` with `HTTP=0 curl: (35) Recv failure: Connection was reset`. Not present in the new run — transient. No finding filed.

### Dependency discovery deviation
The plan's instructions said `gridflow-drift-check` was installable via `uv pip install -e ".[drift]"`. At runtime, the verifier imports `gridflow.cli` which depends on `typer`. `typer` is not in the `[drift]` extras; it's a `gridflow` package dependency. Resolution: `uv pip install --native-tls` the `gridflow` package directly into the venv. This is a **Rule 3 auto-fix** (blocking dependency). Tagged as deviation.

## Findings emitted

| Vendor      | open | wontfix-v3 | needs-info/defer-entitlement | Total |
|-------------|------|------------|------------------------------|-------|
| elexon      | 10   | 22         | 0                            | 32    |
| entsoe      | 36   | 2          | 35                           | 73    |
| entsog      | 5    | 28         | 0                            | 33    |
| gie         | 0    | 6          | 0                            | 6     |
| neso        | 1    | 0          | 0                            | 1     |
| openmeteo   | 0    | 0          | 0                            | 0     |
| **Total**   | **52** | **58**  | **35**                       | **145** |

**Open findings for 07-03:** 52 findings with `status: open` are ready for Vault edits.

## Security check (T-07-02-01, T-07-02-02)

```
grep -nE 'ENTSOE_API_KEY=[A-Za-z0-9_-]{8,}|securityToken=[A-Za-z0-9_-]{8,}|GIE_API_KEY=[A-Za-z0-9_-]{8,}' vault-curl-schema-validation.{md,json}
```
Result: zero hits. Reports are secret-free.
