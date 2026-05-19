---
status: closed
created: 2026-05-19
closed-at: 2026-05-19
vendor: neso
dataset: regional_scotland
drift_category: Temporal
verifier_finding_id: vault-curl-schema-validation.md L54
references:
  - vault-curl-schema-validation.md L54
tags: [drift]
---

# NESO · regional_scotland: Transient curl failure (getaddrinfo DNS failure)

## Context

The verifier reports `failed` for `neso\datasets\regional_scotland.md:39` — HTTP=0 curl error (6): getaddrinfo() thread failed to start.

This is a transient DNS resolution failure, not an API change. The endpoint may have been temporarily unreachable at the time of the run. No silver schema failure accompanies this — the schema table comparison passed (or the dataset has no Pydantic class to compare against, in which case no schema failure surfaces).

Trust chain: Live API → Vault. Temporal — the API cannot be verified at this point in time.

Not present in the baseline (2026-05-16) — suggests this is a network flake rather than a persistent failure.

## Acceptance

Closed when the endpoint returns HTTP 200 on a subsequent verification run. If the endpoint is consistently down (3+ consecutive failures), reclassify as `status: open` with `drift_category: Referential` (endpoint removed) and follow the entsog 404 resolution pattern.

## Comments

Closed 2026-05-19 in plan 07-03. Task 3 re-run (07-03 drift check) shows this endpoint
no longer appears in the `failed` list — the DNS resolution failure was transient.
Confirmed by baseline → re-run comparison: 07-02 had `failed: 7`, 07-03 has `failed: 5`;
the two disappeared failures are NESO regional_scotland and Elexon melngc (both were
`getaddrinfo()` thread failures, consistent with transient network issues).
No Vault edit required.
