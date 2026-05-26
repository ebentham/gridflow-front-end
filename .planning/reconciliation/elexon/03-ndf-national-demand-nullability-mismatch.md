---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: elexon
dataset: ndf
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L130-133
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L132-133
tags: [drift]
---

# Elexon · ndf: `national_demand_mw` nullability not marked in schema table

## Context

The verifier reports `Nullable mismatch: national_demand_mw` for `elexon\datasets\ndf.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): `ElexonDemandForecast.national_demand_mw` is declared nullable (`Optional[...]` or `Field(default=None)`). The live API response can return null for this field.

Vault (`quant-vault/30-vendors/elexon/datasets/ndf.md`): the schema table row for `national_demand_mw` does not indicate it is nullable (e.g., `Nullable: Yes` column is absent or set to `No`).

Trust chain: Live API → Canonical → Vault → Site. The Vault table omits the nullable flag — a Semantic drift (incorrect field semantics, not a missing/extra field).

Different fix from finding 01 (published_at vs issue_time) — this requires updating the nullable annotation on the row, not renaming the field.

Per DRIFT-SURFACES.md § 4.1 (Semantic part).

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/ndf.md` schema table row for `national_demand_mw` is updated to show `Nullable: Yes` (or equivalent per the template's column convention). After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
