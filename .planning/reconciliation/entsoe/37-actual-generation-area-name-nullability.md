---
status: open
created: 2026-05-19
vendor: entsoe
dataset: actual_generation
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L162-163
references:
  - vault-curl-schema-validation.md L162-163
tags: [drift]
---

# ENTSO-E · actual_generation: `area_name` nullability not marked in schema table

## Context

The verifier reports `Nullable mismatch: area_name` for `entsoe\datasets\actual_generation.md`.

Canonical: `area_name` is nullable in the ENTSO-E actual generation Pydantic class.

Vault schema table: `area_name` row does not mark the field nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability annotation.

Note: this dataset also has a 401 HTTP finding (finding 01). The silver schema comparison is done independently of the curl result — the Vault schema table can still be verified against the Canonical Pydantic class even when the live API is inaccessible.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/actual_generation.md` schema table row for `area_name` is updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
