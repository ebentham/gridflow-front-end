---
status: open
created: 2026-05-19
vendor: entsoe
dataset: outages_production
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L210-211
references:
  - vault-curl-schema-validation.md L210-211
tags: [drift]
---

# ENTSO-E · outages_production: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, document_mrid, document_status, production_type, resolution, timeseries_mrid, unit_name` for `entsoe\datasets\outages_production.md`.

Canonical: all 7 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/outages_production.md` schema table rows for all 7 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
