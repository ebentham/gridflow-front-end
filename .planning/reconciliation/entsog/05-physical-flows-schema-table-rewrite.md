---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsog
dataset: physical_flows
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L275-278
references:
  - DRIFT-SURFACES.md § 4.6
  - vault-curl-schema-validation.md L275-278
tags: [drift]
---

# ENTSO-G · physical_flows: 35-field schema mismatch — schema table rewrite required

## Context

The verifier reports the worst single-file Drift in the ecosystem for `entsog\datasets\physical_flows.md`:

- `Missing in docs: flow_gwh_per_day, timestamp_utc` — 2 Canonical silver-layer fields absent from the Vault table
- `Extra in docs: booking_platform_key, booking_platform_label, booking_platform_url, capacity_booking_status, capacity_type, data_set, flow_status, general_remarks, id, id_point_type, indicator, interruption_calculation_remark, interruption_type, is_archived, is_cam_relevant, is_cmp_relevant, is_na, is_unlimited, item_remarks, last_update_date_time, original_period_from, period_from, period_to, period_type, point_type, restoration_information, tso_eic_code, tso_item_identifier, value` — 29 raw API response keys documented in the Vault table that do NOT exist in the Canonical Pydantic silver-layer class
- `Nullable mismatch: direction_key, operator_key, operator_label, point_key, point_label, unit` — 6 fields whose nullability is wrong

Root cause: the Vault schema table was populated from raw API response keys rather than from the Canonical Pydantic silver-layer class. The silver layer consolidates the 29+ raw keys into 2 derived columns (`flow_gwh_per_day`, `timestamp_utc`). The Vault has been used as a raw-response dump rather than tracking the silver schema.

Trust chain: Canonical → Vault. Structural drift (29 extra fields + 2 missing fields + 6 nullability mismatches = 37 total disagreements in one file).

Per DRIFT-SURFACES.md § 4.6.

## Acceptance

Closed when `quant-vault/30-vendors/entsog/datasets/physical_flows.md` schema table is **rewritten** to match the Canonical Pydantic class:
- Remove all 29 raw-key rows (`booking_platform_key`, etc.)
- Add `flow_gwh_per_day` and `timestamp_utc` rows with correct types and descriptions
- Update nullability flags for `direction_key`, `operator_key`, `operator_label`, `point_key`, `point_label`, `unit`
- Optionally preserve the raw-keys discussion in a prose `## Bronze response keys` section for Site narrative value

After Vault edit, re-vendor and rebuild. The schema table length will shrink significantly.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
