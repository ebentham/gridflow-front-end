---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: total_capacity_allocated
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L44
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L44
tags: [drift]
---

# ENTSO-E · total_capacity_allocated: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\total_capacity_allocated.md:64` — HTTP=401. Token does not have entitlement. Per DRIFT-SURFACES.md § 4.4 and Q-DD-04. Deferred to Phase 9 per D-06.

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` per D-06.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
