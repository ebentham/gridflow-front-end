---
status: wontfix
created: 2026-05-19
wontfix-at: 2026-05-19
vendor: entsoe
dataset: net_positions
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L198
references:
  - vault-curl-schema-validation.md L198
tags: [drift]
---

# ENTSO-E · net_positions: No silver schema table in Vault markdown

## Context

The verifier reports `no_silver_schema_table` for `entsoe\datasets\net_positions.md`. The silver schema section exists but contains no table.

Trust chain: Canonical → Vault. Structural drift: schema table absent from the section.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/net_positions.md` silver schema section is populated with a table matching the Canonical Pydantic class. After Vault edit, re-vendor and rebuild.

## Comments

D-01 constraint: No canonical Pydantic class exists for this dataset in `gridflow/src/gridflow/schemas/`. The verifier's `no_silver_schema_table` / `no_silver_section` finding cannot be resolved by a Vault edit — adding a schema table without a canonical class to anchor it would introduce unverifiable documentation. Re-triaged as `wontfix/v3-candidate`: a canonical class must be added to gridflow first (v3 scope), then a vault schema table can be authored.
