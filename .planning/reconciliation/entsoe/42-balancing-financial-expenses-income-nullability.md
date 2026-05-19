---
status: open
created: 2026-05-19
vendor: entsoe
dataset: balancing_financial_expenses_income
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L172-173
references:
  - vault-curl-schema-validation.md L172-173
tags: [drift]
---

# ENTSO-E · balancing_financial_expenses_income: Multiple fields nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, data_provider, ingested_at, resolution` for `entsoe\datasets\balancing_financial_expenses_income.md`.

Canonical: all 4 fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/balancing_financial_expenses_income.md` schema table rows for `business_type`, `data_provider`, `ingested_at`, `resolution` show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
