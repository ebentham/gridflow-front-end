---
status: open
created: 2026-05-19
vendor: entsoe
dataset: generation_units_master_data
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L192-193
references:
  - vault-curl-schema-validation.md L192-193
tags: [drift]
---

# ENTSO-E · generation_units_master_data: `production_type` and `unit_name` nullability not marked

## Context

The verifier reports `Nullable mismatch: production_type, unit_name` for `entsoe\datasets\generation_units_master_data.md`.

Canonical: both fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/generation_units_master_data.md` schema table rows for `production_type` and `unit_name` show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
