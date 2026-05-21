---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: outages_generation
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L37
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L37
tags: [drift]
---

# ENTSO-E · outages_generation: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\outages_generation.md:57` — HTTP=401. Token does not have entitlement. Per DRIFT-SURFACES.md § 4.4 and Q-DD-04. Deferred to Phase 9 per D-06.

Delta note: the baseline (2026-05-16) showed `failed` HTTP=503 (Service Unavailable) for this dataset; it now returns HTTP=401. The change means the endpoint is reachable but entitlement-blocked — same triage (defer-entitlement).

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` per D-06.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
