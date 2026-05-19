---
status: open
created: 2026-05-19
vendor: entsoe
dataset: redispatching_internal
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L217
references:
  - vault-curl-schema-validation.md L217
tags: [drift]
---

# ENTSO-E · redispatching_internal: No silver schema table in Vault markdown

## Context

The verifier reports `no_silver_schema_table` for `entsoe\datasets\redispatching_internal.md`. Schema section present but table absent.

Trust chain: Canonical → Vault. Structural drift.

## Acceptance

Closed when the Vault markdown schema table is populated from the Canonical Pydantic class. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
