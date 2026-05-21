---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: wind_solar_forecast
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L223-224
references:
  - vault-curl-schema-validation.md L223-224
tags: [drift]
---

# ENTSO-E · wind_solar_forecast: `resolution` nullability not marked in schema table

## Context

The verifier reports `Nullable mismatch: resolution` for `entsoe\datasets\wind_solar_forecast.md`.

Canonical: `resolution` is nullable. Vault schema table does not mark it nullable.

Trust chain: Canonical → Vault. Semantic drift.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/wind_solar_forecast.md` schema table row for `resolution` shows `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
