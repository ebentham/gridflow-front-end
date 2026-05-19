---
status: open
created: 2026-05-19
vendor: elexon
dataset: boal
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L104-105
references:
  - vault-curl-schema-validation.md L104-105
tags: [drift]
---

# Elexon · boal: Schema table missing `bid_offer_acceptance_number` field

## Context

The verifier reports `Missing in docs: bid_offer_acceptance_number` for `elexon\datasets\boal.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): The BOAL (Bid-Offer Acceptance Level) Pydantic class declares `bid_offer_acceptance_number` as a field.

Vault (`quant-vault/30-vendors/elexon/datasets/boal.md`): the schema table does not include a row for `bid_offer_acceptance_number`.

Trust chain: Canonical → Vault. Structural drift: field present in Canonical, absent from Vault schema table.

No curl failure (the curl example passed). Only the schema table comparison fails.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/boal.md` schema table is updated to include a `bid_offer_acceptance_number` row with the correct type, nullable flag, and description from the Canonical Pydantic definition. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
