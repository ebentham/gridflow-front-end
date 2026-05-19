---
status: open
created: 2026-05-19
vendor: entsoe
dataset: countertrading
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L181
references:
  - vault-curl-schema-validation.md L181
tags: [drift]
---

# ENTSO-E · countertrading: No silver schema table in Vault markdown

## Context

The verifier reports `no_silver_schema_table` for `entsoe\datasets\countertrading.md`. The silver schema section exists but contains no table (or an empty table) — the verifier cannot extract field rows to compare against the Canonical Pydantic class.

Trust chain: Canonical → Vault. Structural drift: schema table missing from the section.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/countertrading.md` silver schema section is populated with a table matching the Canonical Pydantic class fields and their types/nullability. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
