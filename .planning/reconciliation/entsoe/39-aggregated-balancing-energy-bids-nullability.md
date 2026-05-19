---
status: open
created: 2026-05-19
vendor: entsoe
dataset: aggregated_balancing_energy_bids
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L166-167
references:
  - vault-curl-schema-validation.md L166-167
tags: [drift]
---

# ENTSO-E · aggregated_balancing_energy_bids: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: bid_mrid, business_type, data_provider, direction, ingested_at, original_market_product, resolution, standard_market_product` for `entsoe\datasets\aggregated_balancing_energy_bids.md`.

Canonical: all 8 of these fields are nullable in the Pydantic class.

Vault schema table: none of these rows marks the field nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability on 8 fields.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/aggregated_balancing_energy_bids.md` schema table rows for all 8 fields are updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
