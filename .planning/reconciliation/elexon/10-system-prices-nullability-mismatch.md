---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: elexon
dataset: system_prices
drift_category: Semantic
verifier_finding_id: vault-curl-schema-validation.md L146-147
references:
  - vault-curl-schema-validation.md L146-147
tags: [drift]
---

# Elexon · system_prices: `price_derivation_code` and `run_type` nullability not marked

## Context

The verifier reports `Nullable mismatch: price_derivation_code, run_type` for `elexon\datasets\system_prices.md`.

Canonical (`gridflow/src/gridflow/schemas/elexon.py`): The ElexonSystemPrices Pydantic class declares `price_derivation_code` and `run_type` as nullable — these can be absent from certain settlement run types.

Vault (`quant-vault/30-vendors/elexon/datasets/system_prices.md`): schema table rows for these fields do not mark them as nullable.

Trust chain: Canonical → Vault. Semantic drift: incorrect nullability on two fields.

No curl failure. Only the silver schema comparison fails.

## Acceptance

Closed when `quant-vault/30-vendors/elexon/datasets/system_prices.md` schema table rows for `price_derivation_code` and `run_type` are updated to show `Nullable: Yes`. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
