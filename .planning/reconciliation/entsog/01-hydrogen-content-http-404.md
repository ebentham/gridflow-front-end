---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: entsog
dataset: hydrogen_content
drift_category: Referential
verifier_finding_id: vault-curl-schema-validation.md L50
references:
  - DRIFT-SURFACES.md § 4.5
  - vault-curl-schema-validation.md L50
tags: [drift]
---

# ENTSO-G · hydrogen_content: HTTP 404 — endpoint removed by vendor

## Context

The verifier reports `failed` for `entsog\datasets\hydrogen_content.md:60` — HTTP=404. The ENTSO-G API endpoint for hydrogen content has been taken down by the vendor.

The silver schema check also reports `no_silver_schema_table` — the dataset page exists in the Vault but the schema table is absent.

Trust chain: Live API → Vault. Referential drift: the Vault documents an endpoint that no longer exists at the vendor.

Per DRIFT-SURFACES.md § 4.5: 4 ENTSO-G endpoints return HTTP 404; the vendor took them down; the Vault still describes them.

## Acceptance

Closed when `quant-vault/30-vendors/entsog/datasets/hydrogen_content.md` is either:
1. Deleted (preferred if no other Vault content references it), or
2. Updated with a `removed: true` frontmatter flag that the build template renders distinctly (e.g., "This dataset was removed by the vendor").

After Vault edit, re-vendor and rebuild.

## Comments

Closed 2026-05-19 in plan 07-03. Vault file updated in quant-vault (Task 1) and re-vendored byte-identically to gridflow-front-end/vault/ (Task 2). Fix anchored to D-01: Canonical Pydantic schema is the source of truth; Vault table now matches.
