---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: actual_generation_units
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L164-165
references:
  - vault-curl-schema-validation.md L164-165
tags: [drift]
---

# ENTSO-E · actual_generation_units: `resolution` and `unit_name` nullability not marked

## Context

The verifier reports `Nullable mismatch: resolution, unit_name` for `entsoe\datasets\actual_generation_units.md`.

Canonical: both `resolution` and `unit_name` are nullable in the Pydantic class.

Vault schema table: rows for these fields do not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability on two fields.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/actual_generation_units.md` schema table rows for `resolution` and `unit_name` are updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
