---
status: wontfix
reason: v3-candidate
created: 2026-05-19
vendor: elexon
dataset: agpt
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L96-97
references:
  - DRIFT-SURFACES.md § 4.3
  - vault-curl-schema-validation.md L96-97
tags: [drift]
---

# Elexon · agpt: No importable Pydantic schema (`manual_transformer_schema`)

## Context

The verifier reports `manual_transformer_schema` for `elexon\datasets\agpt.md`: no importable Pydantic class is declared in the dataset note. The verifier cannot compare the Vault schema table against a Canonical Pydantic class because none exists.

Closing this gap requires declaring `ElexonAGPT` in `gridflow/src/gridflow/schemas/elexon.py` — a cross-repo change in the gridflow Canonical code. This is explicitly out of scope for v2 per **PROJECT.md § Out of Scope** and per **ADR-0001 Consequences** ("declaring `ElexonAGPT`, `ElexonAGWS`, etc. cross-repo work").

Trust chain: if no Canonical Pydantic class exists, the Vault cannot be verified against it. The Vault is derivative of the Canonical — Referential drift (missing Canonical reference).

## Acceptance

Documented and not actioned in v2. Closes when `ElexonAGPT` Pydantic class lands in `gridflow/src/gridflow/schemas/elexon.py` per v3 planning. Reference: PROJECT.md § Out of Scope.

## Comments

<!-- v3-candidate; no action in Phase 7 -->
