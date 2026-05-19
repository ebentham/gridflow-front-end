---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: auction_revenue
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L168-169
references:
  - vault-curl-schema-validation.md L168-169
tags: [drift]
---

# ENTSO-E · auction_revenue: `business_type` and `resolution` nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, resolution` for `entsoe\datasets\auction_revenue.md`.

Canonical: both fields are nullable in the Pydantic class.

Vault schema table: rows for these fields do not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/auction_revenue.md` schema table rows for `business_type` and `resolution` show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
