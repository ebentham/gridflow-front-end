---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsog
dataset: interruptions
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L51
references:
  - DRIFT-SURFACES.md § 4.5
  - vault-curl-schema-validation.md L51
tags: [drift]
---

# ENTSO-G · interruptions: HTTP 404 — endpoint removed by vendor

## Context

The verifier reports `failed` for `entsog\datasets\interruptions.md:46` — HTTP=404. The ENTSO-G API endpoint for interruptions has been taken down by the vendor.

The silver schema check also reports `no_silver_schema_table`.

Trust chain: Live API → Vault. Referential drift: Vault documents a removed endpoint.

Per DRIFT-SURFACES.md § 4.5.

## Acceptance

Closed when `quant-vault/30-vendors/entsog/datasets/interruptions.md` is either deleted or updated with a `removed: true` frontmatter flag. After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
