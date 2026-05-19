---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: congestion_management_costs
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L179-180
references:
  - vault-curl-schema-validation.md L179-180
tags: [drift]
---

# ENTSO-E · congestion_management_costs: `business_type` and `resolution` nullability not marked

## Context

The verifier reports `Nullable mismatch: business_type, resolution` for `entsoe\datasets\congestion_management_costs.md`.

Canonical: both fields are nullable. Vault schema table does not mark them nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/congestion_management_costs.md` schema table rows show `Nullable: Yes` for `business_type` and `resolution`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
