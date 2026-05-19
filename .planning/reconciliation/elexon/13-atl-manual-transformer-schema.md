---
status: wontfix
reason: v3-candidate
created: 2026-05-19
vendor: elexon
dataset: atl
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L100-101
references:
  - DRIFT-SURFACES.md § 4.3
  - vault-curl-schema-validation.md L100-101
tags: [drift]
---

# Elexon · atl: No importable Pydantic schema (`manual_transformer_schema`)

## Context

The verifier reports `manual_transformer_schema` for `elexon\datasets\atl.md`: no importable Pydantic class declared. Closing the gap requires declaring `ElexonATL` in `gridflow/src/gridflow/schemas/elexon.py` — cross-repo Canonical work out of scope for v2 per **PROJECT.md § Out of Scope** and **ADR-0001 Consequences**.

## Acceptance

Documented and not actioned in v2. Closes when `ElexonATL` Pydantic class lands in `gridflow/src/gridflow/schemas/elexon.py` per v3 planning. Reference: PROJECT.md § Out of Scope.

## Comments

<!-- v3-candidate; no action in Phase 7 -->
