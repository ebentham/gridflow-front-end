---
status: needs-info
reason: defer-entitlement
created: 2026-05-19
vendor: entsoe
dataset: actual_generation
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L14
references:
  - DRIFT-SURFACES.md § 4.4
  - vault-curl-schema-validation.md L14
tags: [drift]
---

# ENTSO-E · actual_generation: HTTP 401 — entitlement blocked

## Context

The verifier reports `failed_auth` for `entsoe\datasets\actual_generation.md:56` — HTTP=401. The ENTSO-E API token in `.env` does not have entitlement for this endpoint.

Per DRIFT-SURFACES.md § 4.4: the current token works for 11 ENTSO-E endpoints but returns 401 for 35 datasets (this is one of them). Q-DD-04 analysis: "fix the API token first then enable fail-loud" — but ENTSO-E entitlement requests are not 24-hour turnarounds. Resolution deferred to Phase 9's discuss-phase per D-06.

Body: Token works for 11 ENTSO-E endpoints (vault-amendment-plan.md:60-71); not this one. Resolution path deferred to Phase 9 discuss-phase per D-06: extend access vs `skip-with-warn`.

Category: Temporal × Referential — entitlement drift (cannot verify currency of data because access is blocked).

## Acceptance

Phase 9 discuss-phase decides: extend ENTSO-E API access vs accept `skip-with-warn` for this dataset per D-06. No action in Phase 7.

## Comments

<!-- Phase 9 discuss-phase acts on this -->
