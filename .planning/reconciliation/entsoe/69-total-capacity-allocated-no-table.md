---
status: open
created: 2026-05-19
vendor: entsoe
dataset: total_capacity_allocated
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L218
references:
  - vault-curl-schema-validation.md L218
tags: [drift]
---

# ENTSO-E · total_capacity_allocated: No silver schema table in Vault markdown

## Context

The verifier reports `no_silver_schema_table` for `entsoe\datasets\total_capacity_allocated.md`. Schema section present but table absent.

Trust chain: Canonical → Vault. Structural drift.

## Acceptance

Closed when the Vault markdown schema table is populated from the Canonical Pydantic class. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
