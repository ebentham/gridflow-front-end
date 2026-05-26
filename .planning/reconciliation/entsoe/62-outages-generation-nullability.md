---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: outages_generation
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L206-207
references:
  - vault-curl-schema-validation.md L206-207
tags: [drift]
---

# ENTSO-E · outages_generation: `resolution` and `unit_name` nullability not marked

## Context

The verifier reports `Nullable mismatch: resolution, unit_name` for `entsoe\datasets\outages_generation.md`.

Canonical: both fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/outages_generation.md` schema table rows for `resolution` and `unit_name` show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
