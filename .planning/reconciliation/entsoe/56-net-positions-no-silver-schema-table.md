---
status: open
created: 2026-05-19
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

<!-- empty until 07-03 acts on this -->
