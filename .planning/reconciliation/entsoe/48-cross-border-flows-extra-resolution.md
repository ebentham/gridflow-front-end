---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsoe
dataset: cross_border_flows
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L182-183
references:
  - vault-curl-schema-validation.md L182-183
tags: [drift]
---

# ENTSO-E · cross_border_flows: Schema table has extra `resolution` field not in Canonical

## Context

The verifier reports `Extra in docs: resolution` for `entsoe\datasets\cross_border_flows.md`. The Vault schema table includes a `resolution` row, but the Canonical Pydantic class for cross_border_flows does NOT declare a `resolution` field.

Trust chain: Canonical → Vault. Structural drift: Vault table has a field that doesn't exist in the Canonical class.

This dataset also has a 401 HTTP finding (finding 10) — the silver schema comparison is done against the Canonical class regardless.

## Acceptance

Closed when the `resolution` row is removed from the `quant-vault/30-vendors/entsoe/datasets/cross_border_flows.md` schema table. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
