---
status: open
created: 2026-05-19
vendor: entsog
dataset: methane_content
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L52
references:
  - DRIFT-SURFACES.md § 4.5
  - vault-curl-schema-validation.md L52
tags: [drift]
---

# ENTSO-G · methane_content: HTTP 404 — endpoint removed by vendor

## Context

The verifier reports `failed` for `entsog\datasets\methane_content.md:60` — HTTP=404. The ENTSO-G API endpoint for methane content has been taken down by the vendor.

The silver schema check also reports `no_silver_schema_table`.

Trust chain: Live API → Vault. Referential drift: Vault documents a removed endpoint.

Per DRIFT-SURFACES.md § 4.5.

## Acceptance

Closed when `quant-vault/30-vendors/entsog/datasets/methane_content.md` is either deleted or updated with a `removed: true` frontmatter flag. After Vault edit, re-vendor and rebuild.

## Comments

<!-- empty until 07-03 acts on this -->
