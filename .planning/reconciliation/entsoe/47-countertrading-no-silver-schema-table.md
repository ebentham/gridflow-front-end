---
status: wontfix
created: 2026-05-19
wontfix-at: 2026-05-19
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

D-01 constraint: No canonical Pydantic class exists for this dataset in `gridflow/src/gridflow/schemas/`. The verifier's `no_silver_schema_table` / `no_silver_section` finding cannot be resolved by a Vault edit — adding a schema table without a canonical class to anchor it would introduce unverifiable documentation. Re-triaged as `wontfix/v3-candidate`: a canonical class must be added to gridflow first (v3 scope), then a vault schema table can be authored.
