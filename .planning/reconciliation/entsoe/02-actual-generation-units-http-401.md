---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: actual_generation_units
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L15
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L15
tags: [drift]
---

# ENTSO-E · actual_generation_units: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\actual_generation_units.md:55` — HTTP=401. The ENTSO-E API token does not have entitlement for this endpoint.

Per DRIFT-SURFACES.md § 4.4 and Q-DD-04: token works for 11 ENTSO-E endpoints; not this one. Resolution deferred to Phase 9 discuss-phase per D-06: extend access vs `skip-with-warn`.

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` per D-06.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
