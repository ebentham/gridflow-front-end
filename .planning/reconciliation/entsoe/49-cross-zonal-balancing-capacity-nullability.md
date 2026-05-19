---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: cross_zonal_balancing_capacity
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L184-185
references:
  - vault-curl-schema-validation.md L184-185
tags: [drift]
---

# ENTSO-E · cross_zonal_balancing_capacity: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, data_provider, ingested_at, market_agreement_type, resolution` for `entsoe\datasets\cross_zonal_balancing_capacity.md`.

Canonical: all 5 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/cross_zonal_balancing_capacity.md` schema table rows for all 5 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
