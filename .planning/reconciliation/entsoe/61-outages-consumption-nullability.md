---
status: open
created: 2026-05-19
vendor: entsoe
dataset: outages_consumption
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L204-205
references:
  - vault-curl-schema-validation.md L204-205
tags: [drift]
---

# ENTSO-E · outages_consumption: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, document_mrid, document_status, resolution, timeseries_mrid` for `entsoe\datasets\outages_consumption.md`.

Canonical: all 5 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/outages_consumption.md` schema table rows for all 5 fields show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
