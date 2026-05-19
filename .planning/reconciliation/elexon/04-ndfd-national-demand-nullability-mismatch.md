---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: elexon
dataset: ndfd
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L134-137
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L135-137
tags: [drift]
---

# Elexon · ndfd: `national_demand_mw` nullability not marked in schema table

## Context

The verifier reports `Nullable mismatch: national_demand_mw` for `elexon\datasets\ndfd.md`.

Canonical: `ElexonDemandForecast.national_demand_mw` is nullable (same class covers ndf and ndfd).

Vault (`quant-vault/30-vendors/elexon/datasets/ndfd.md`): schema table row for `national_demand_mw` does not mark it nullable.

Same semantic drift as finding 03 (ndf), mirrored in ndfd. Semantic drift: incorrect field nullability.

Per DRIFT-SURFACES.md § 4.1 (Semantic part).

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/ndfd.md` schema table row for `national_demand_mw` is updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
