---
status: open
created: 2026-05-19
vendor: entsoe
dataset: commercial_schedules_net_positions
drift_category: Structural
verifier_finding_id: vault-curl-schema-validation.md L176
references:
  - vault-curl-schema-validation.md L176
tags: [drift]
---

# ENTSO-E · commercial_schedules_net_positions: No silver schema section in Vault markdown

## Context

The verifier reports `no_silver_section` for `entsoe\datasets\commercial_schedules_net_positions.md`. The Vault markdown file for this dataset does not contain a silver schema section at all — the verifier cannot find the section header it expects.

Trust chain: Canonical → Vault. Structural drift: the Vault page for this dataset is missing its schema section entirely.

Distinct from `no_silver_schema_table` (where the section exists but the table is absent): `no_silver_section` means the section header itself is missing.

## Acceptance

Closed when `quant-vault/30-vendors/entsoe/datasets/commercial_schedules_net_positions.md` is updated to include a silver schema section with a table matching the Canonical Pydantic class fields. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
