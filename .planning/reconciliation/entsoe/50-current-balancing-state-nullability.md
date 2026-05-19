---
status: open
created: 2026-05-19
vendor: entsoe
dataset: current_balancing_state
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L186-187
references:
  - vault-curl-schema-validation.md L186-187
tags: [drift]
---

# ENTSO-E · current_balancing_state: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, data_provider, ingested_at, resolution` for `entsoe\datasets\current_balancing_state.md`.

Canonical: all 4 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/current_balancing_state.md` schema table rows for all 4 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
