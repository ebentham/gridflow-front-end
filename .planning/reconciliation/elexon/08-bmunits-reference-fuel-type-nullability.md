---
status: open
created: 2026-05-19
vendor: elexon
dataset: bmunits_reference
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L102-103
references:
  - vault-curl-schema-validation.md L102-103
tags: [drift]
---

# Elexon · bmunits_reference: `fuel_type` nullability not marked in schema table

## Context

The verifier reports `Nullable mismatch: fuel_type` for `elexon\datasets\bmunits_reference.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): The BM units reference Pydantic class declares `fuel_type` as nullable — not every BM unit has an assigned fuel type.

Vault (`quant-vault/30-vendors/elexon/datasets/bmunits_reference.md`): schema table row for `fuel_type` does not mark it as nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability.

No corresponding curl failure — the curl example passed; only the silver schema comparison fails.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/bmunits_reference.md` schema table row for `fuel_type` is updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
