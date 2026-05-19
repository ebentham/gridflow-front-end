---
status: open
created: 2026-05-19
vendor: elexon
dataset: windfor
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L156-159
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L158-159
tags: [drift]
---

# Elexon · windfor: `settlement_date` and `settlement_period` nullability not marked

## Context

The verifier reports `Nullable mismatch: settlement_date, settlement_period` for `elexon\datasets\windfor.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): `ElexonWindFor.settlement_date` and `ElexonWindFor.settlement_period` are nullable.

Vault (`quant-vault/30-vendors/elexon/datasets/windfor.md`): schema table rows for these fields do not mark them as nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability annotation for two fields.

Separate finding from 06 (windfor published_at) because different fix path: 06 renames a field; this finding updates the nullable flag on two existing rows.

New finding (not in baseline 2026-05-16).

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/windfor.md` schema table rows for `settlement_date` and `settlement_period` are updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
