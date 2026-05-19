---
status: open
created: 2026-05-19
vendor: elexon
dataset: windfor
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L156-159
references:
  - DRIFT-SURFACES.md § 4.1
  - vault-curl-schema-validation.md L156-159
tags: [drift]
---

# Elexon · windfor: Schema table uses `issue_time` instead of `published_at`

## Context

The verifier reports `Missing in docs: published_at` and `Extra in docs: issue_time` for `elexon\datasets\windfor.md`. This finding was NOT present in the baseline (2026-05-16) and appeared in this run for the first time.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): The ElexonWindFor Pydantic class declares `published_at` (not `issue_time`) as the publication timestamp field.

Vault (`quant-vault/30-vendors/elexon/datasets/windfor.md`): the schema table names the field `issue_time`, which is neither the Canonical field name nor the live API response field name. Same pattern as ndf/ndfd findings 01/02.

Trust chain: Live API → Canonical → Vault → Site. The Vault table has the wrong field name — Structural drift.

New finding in this run (not in baseline 2026-05-16). Root cause: same `issue_time` naming convention applied inconsistently across Elexon forecast datasets.

Per DRIFT-SURFACES.md § 4.1 (same pattern, different dataset).

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/windfor.md` schema table row is changed from `issue_time` to `published_at`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
