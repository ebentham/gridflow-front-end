---
status: open
created: 2026-05-19
vendor: entsoe
dataset: procured_balancing_capacity
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L214-215
references:
  - vault-curl-schema-validation.md L214-215
tags: [drift]
---

# ENTSO-E · procured_balancing_capacity: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, data_provider, ingested_at, market_agreement_type, resolution` for `entsoe\datasets\procured_balancing_capacity.md`.

Canonical: all 5 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/procured_balancing_capacity.md` schema table rows for all 5 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
