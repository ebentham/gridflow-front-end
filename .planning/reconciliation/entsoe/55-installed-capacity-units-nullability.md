---
status: open
created: 2026-05-19
vendor: entsoe
dataset: installed_capacity_units
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L196-197
references:
  - vault-curl-schema-validation.md L196-197
tags: [drift]
---

# ENTSO-E · installed_capacity_units: `resolution` and `unit_name` nullability not marked

## Context

The verifier reports `Nullable mismatch: resolution, unit_name` for `entsoe\datasets\installed_capacity_units.md`.

Canonical: both fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/installed_capacity_units.md` schema table rows for `resolution` and `unit_name` show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
