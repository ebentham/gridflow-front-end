---
status: open
created: 2026-05-19
vendor: entsoe
dataset: balancing_energy_bids
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L170-171
references:
  - vault-curl-schema-validation.md L170-171
tags: [drift]
---

# ENTSO-E · balancing_energy_bids: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: bid_mrid, business_type, data_provider, direction, ingested_at, original_market_product, resolution, standard_market_product` for `entsoe\datasets\balancing_energy_bids.md`.

Same mismatch pattern as `aggregated_balancing_energy_bids` (finding 39) — both datasets share the same Pydantic class shape for these fields.

Trust chain: Canonical → Vault. Semantic drift: 8 nullable fields not marked.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/balancing_energy_bids.md` schema table rows for all 8 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
