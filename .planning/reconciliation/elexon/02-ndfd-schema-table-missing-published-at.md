---
status: open
created: 2026-05-19
vendor: elexon
dataset: ndfd
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L134-137
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L134-137
tags: [drift]
---

# Elexon · ndfd: Schema table uses `issue_time` instead of `published_at`

## Context

The verifier reports `Missing in docs: published_at` and `Extra in docs: issue_time` for `elexon\datasets\ndfd.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): `ElexonDemandForecast.published_at: datetime | None` (same class covers ndf and ndfd — demand forecast). The live API response field is `published_at`.

Vault (`quant-vault/30-vendors/elexon/datasets/ndfd.md`): the schema table names the field `issue_time`, matching the same error as `ndf.md`.

Trust chain: Live API → Canonical → Vault → Site. Vault must track Canonical; the wrong field name is in the Vault table. Structural drift (field name mismatch).

Same root cause as finding 01 (ndf). Both ndf and ndfd share the `ElexonDemandForecast` Pydantic class.

Per DRIFT-SURFACES.md § 4.1.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/ndfd.md` schema table row is changed from `issue_time` to `published_at`. After Vault edit, re-vendor into `gridflow-front-end/vault/elexon/` and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
