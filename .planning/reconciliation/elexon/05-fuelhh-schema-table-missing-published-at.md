---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: elexon
dataset: fuelhh
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L108-109
references:
  - DRIFT-SURFACES.md § 4.2
  - vault-curl-schema-validation.md L108-109
tags: [drift]
---

# Elexon · fuelhh: Schema table omits `published_at` row

## Context

The verifier reports `Missing in docs: published_at` for `elexon\datasets\fuelhh.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): `ElexonFuelHH.published_at: datetime | None = None`.

Vault (`quant-vault/30-vendors/elexon/datasets/fuelhh.md`): the metadata block at line ~103 correctly names `published_at` in prose, but the schema table at lines ~107-115 omits the `published_at` row entirely. This is intra-file Drift — neither the verifier nor the build pipeline catches it from the prose block alone; the verifier catches it via schema-table comparison.

Trust chain: Canonical → Vault. The Vault schema table (not the prose) is what the build script renders into the Site's schema column. The missing row means the Site schema section for fuelhh omits this field.

Category: Structural drift (field present in Canonical, absent from Vault schema table).

Per DRIFT-SURFACES.md § 4.2.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/fuelhh.md` schema table is updated to include a `published_at` row with type `datetime | None`, nullable, description matching the Canonical docstring. After Vault edit, re-vendor into `gridflow-front-end/vault/elexon/` and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
