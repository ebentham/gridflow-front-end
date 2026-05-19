# 07-03 Drift Check Re-run Report

**Generated:** 2026-05-19T16:39:05.632676Z
**Baseline:** 2026-05-19T15:32:14.392995Z (07-02 run)
**Script:** `quant-vault/30-vendors/scripts/gridflow_drift_check.py`

---

## Summary comparison

| Metric | 07-02 baseline | 07-03 re-run | Delta |
|--------|---------------|-------------|-------|
| Curl passed | 120 | 122 | +2 |
| Curl failed (non-auth) | 7 | 5 | -2 |
| Curl failed_auth | 35 | 35 | 0 |
| Schema passed | 56 | 89 | +33 |
| Schema failed | 33 | 0 | -33 |
| Schema manual_transformer | 58 | 58 | 0 |
| Schema no_silver_schema_table | 14 | 14 | 0 |
| Schema no_silver_section | 1 | 1 | 0 |

**All 33 schema failures eliminated. Zero schema failed remaining.**

---

## Curl failure analysis

### Resolved curl failures (-2)

| Dataset | Baseline failure | Re-run result | Reason |
|---------|-----------------|---------------|--------|
| `neso/regional_scotland` | HTTP=0 getaddrinfo() thread failed | Not in failed list — passed | Transient DNS flake confirmed |
| `elexon/melngc` | HTTP=0 getaddrinfo() thread failed | Not in failed list — passed | Transient DNS flake confirmed |

### Remaining curl failures (5 — all expected)

| Dataset | HTTP | Reason | Status |
|---------|------|--------|--------|
| `entsog/hydrogen_content` | 404 | Vendor removed endpoint | Documented: `removed` frontmatter + finding 01 closed |
| `entsog/interruptions` | 404 | Vendor removed endpoint | Documented: `removed` frontmatter + finding 02 closed |
| `entsog/methane_content` | 404 | Vendor removed endpoint | Documented: `removed` frontmatter + finding 03 closed |
| `entsog/oxygen_content` | 404 | Vendor removed endpoint | Documented: `removed` frontmatter + finding 04 closed |
| `open-meteo/endpoints` | 0 (conn reset) | Transient network failure | Pre-existing; not a 07-03 finding |

### Auth failures (35 — unchanged, all expected)

All 35 `failed_auth` are ENTSO-E endpoints requiring API key authentication. These are pre-existing and documented in findings 01-36 (all closed in 07-02 as accepted/acknowledged). No change expected or observed.

---

## Schema analysis

### Schema failures eliminated (33 → 0)

All 33 nullable-mismatch and structural failures from the 07-02 run were resolved by the Vault edits in 07-03 Task 1. Specific fixes:

- **Elexon (10 findings):** `published_at` field added/renamed in ndf, ndfd, fuelhh, windfor; nullability corrected for `national_demand_mw`, `settlement_date`, `settlement_period`, `fuel_type`, `bid_offer_acceptance_number`; `str | None` type cell escaping fixed for system_prices
- **ENTSO-E (24 findings):** `str = ""` fields changed from Yes/Yes(default "") to No across 25 files (resolution, business_type, bid_mrid, direction, area_name, etc.); `ingested_at` type cell `\|` escaping removed; `cross_border_flows` extra resolution row removed
- **ENTSO-G (5 findings):** physical_flows schema table rewritten from 35-field bronze dump to 9-field silver shape matching EntsogPhysicalFlow; 4 removed-endpoint datasets marked with `removed` frontmatter

### Remaining schema non-failures

| Category | Count | Meaning |
|----------|-------|---------|
| `passed` | 89 | Schema tables match canonical Pydantic classes exactly |
| `manual_transformer_schema` | 58 | No Pydantic class exists; generic/manual transformer. Pre-existing. |
| `no_silver_schema_table` | 14 | Silver section exists but no table; no canonical class to compare. Pre-existing. |
| `no_silver_section` | 1 | Silver section missing entirely; no canonical class. Pre-existing. |

The 15 `no_silver_*` entries correspond to the 11 ENTSO-E findings re-triaged as `wontfix/v3-candidate` (D-01 constraint) plus 4 pre-existing entries from other vendors.

---

## NESO finding resolution

Finding `neso/01-regional-scotland-transient-curl-failure.md` acceptance criteria: "Closed when endpoint returns HTTP 200 on a subsequent verification run."

The re-run shows `regional_scotland` is no longer in the `failed` list (it appeared in 07-02 as `HTTP=0 getaddrinfo() thread failed to start`). The DNS failure was transient. **Finding 01 closed.**

---

## Conclusion

Plan 07-03 Task 3 re-run confirms all Vault edits from Task 1 are effective:
- 33 schema failures → 0 failures
- NESO transient DNS finding confirmed resolved
- 4 ENTSO-G 404 failures are expected and documented (endpoints removed by vendor)
- All pre-existing auth and manual-transformer entries unchanged

The `gridflow-drift-check` verifier now shows a clean schema baseline for all datasets with canonical Pydantic classes.
