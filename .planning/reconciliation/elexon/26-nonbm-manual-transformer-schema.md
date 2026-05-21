---
status: wontfix
reason: v3-candidate
created: 2026-05-19
vendor: elexon
dataset: nonbm
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L140-141
references:
  - DRIFT-SURFACES.md § 4.3
  - vault-curl-schema-validation.md L140-141
tags: [drift]
---

# Elexon · nonbm: No importable Pydantic schema (`manual_transformer_schema`)

## Context

The verifier reports `manual_transformer_schema` for `elexon\datasets\nonbm.md`: no importable Pydantic class declared. Cross-repo Canonical work out of scope for v2 per **PROJECT.md § Out of Scope** and **ADR-0001 Consequences**.

## Acceptance

Documented and not actioned in v2. Closes when `ElexonNonBM` Pydantic class lands in `gridflow/src/gridflow/schemas/elexon.py` per v3 planning. Reference: PROJECT.md § Out of Scope.

## Comments

<!-- v3-candidate; no action in Phase 7 -->
