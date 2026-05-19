---
status: open
created: 2026-05-19
vendor: entsoe
dataset: dc_link_intraday_transfer_limits
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L188-189
references:
  - vault-curl-schema-validation.md L188-189
tags: [drift]
---

# ENTSO-E · dc_link_intraday_transfer_limits: `business_type` and `resolution` nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, resolution` for `entsoe\datasets\dc_link_intraday_transfer_limits.md`.

Canonical: both fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/dc_link_intraday_transfer_limits.md` schema table rows show `Nullable: Yes` for `business_type` and `resolution`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
