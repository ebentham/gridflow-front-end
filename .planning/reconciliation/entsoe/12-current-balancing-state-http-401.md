---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: current_balancing_state
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L25
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L25
tags: [drift]
---

# ENTSO-E · current_balancing_state: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\current_balancing_state.md:71` — HTTP=401. Token does not have entitlement. Per DRIFT-SURFACES.md § 4.4 and Q-DD-04. Deferred to Phase 9 per D-06.

Delta note: the baseline (2026-05-16) showed `failed` HTTP=0 getaddrinfo for this dataset; it now returns HTTP=401. The change from network-unreachable to entitlement-blocked represents the same triage outcome (defer-entitlement).

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` per D-06.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
