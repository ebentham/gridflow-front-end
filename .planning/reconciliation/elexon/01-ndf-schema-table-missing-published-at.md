---
status: open
created: 2026-05-19
vendor: elexon
dataset: ndf
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L130-133
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L130-133
tags: [drift]
---

# Elexon · ndf: Schema table uses `issue_time` instead of `published_at`

## Context

The verifier reports `Missing in docs: published_at` and `Extra in docs: issue_time` for `elexon\datasets\ndf.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): `ElexonDemandForecast.published_at: datetime | None`. The live API response field is `published_at`.

Vault (`quant-vault/30-vendors/elexon/datasets/ndf.md`, approximately line 99/111): the schema table row names the field `issue_time`, which is neither the Canonical field name nor the live API response field name.

Trust chain: Live API → Canonical → Vault → Site. Vault must track Canonical; the Vault table has the wrong field name. This is a Structural drift (field name mismatch between Canonical Pydantic field and Vault table row).

Site impact: `site/hifi/data-sources/elexon/ndf.html` renders `Point-in-time field: issue_time` — deployed and wrong.

Per DRIFT-SURFACES.md § 4.1.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/ndf.md` schema table row is changed from `issue_time` to `published_at`. The `Extra in docs: issue_time` finding is resolved by the same edit. After Vault edit, re-vendor into `gridflow-front-end/vault/elexon/` and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
