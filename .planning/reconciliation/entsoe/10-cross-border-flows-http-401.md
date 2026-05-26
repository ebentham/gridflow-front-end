---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: cross_border_flows
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L23
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L23
tags: [drift]
---

# ENTSO-E · cross_border_flows: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\cross_border_flows.md:74` — HTTP=401. Token does not have entitlement. Per DRIFT-SURFACES.md § 4.4 and Q-DD-04. Deferred to Phase 9 per D-06.

Note: this dataset also has a silver schema finding (Extra in docs: resolution — finding 36). The 401 prevents live data verification; the schema finding is filed separately.

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` per D-06.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
