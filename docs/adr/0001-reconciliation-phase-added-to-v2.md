# ADR-0001: Reconciliation phase added to v2; "no upfront audit" decision overridden

Status: accepted (2026-05-19)
Supersedes: STATE.md § Decisions Pending #2 ("Assume vault content complete; no upfront audit phase — let `gridflow-build --check` surface gaps")

## Context

The v2 milestone was scoped on 2026-05-18 with three phases (bug fix, ENTSO-E coverage, four-vendor batch) and an explicit decision to **skip an upfront vault audit**, relying instead on `gridflow-build --check` to surface gaps reactively during content build.

Subsequent review surfaced two facts that invalidate that decision:

1. `gridflow-build --check` is an *idempotence* check (builds twice; diffs the outputs), not a content-accuracy check. It catches non-deterministic builds; it does not catch wrong column names, stale endpoint URLs, vendor-doc drift, or schema-table mismatches.
2. The existing drift-detection research package (`.planning/research/post-v1/drift-detection/`) documents real shipped Drift on the live Site today — `ndf` / `ndfd` / `fuelhh` schema-table omits `published_at`; 33 ENTSO-E datasets return HTTP 401 from the current API token; ENTSO-G `physical_flows` has a 35-field mismatch in one Vault file.

`PROJECT.md § Constraints` says: *"Schema, primary keys, frequencies, lags, caveats must match vendor docs. The site loses all credibility if a recruiter spot-checks against the real Elexon API and finds drift."* That is a content-accuracy mandate. The locked v2 decision was in tension with it.

## Decision

Insert a new **Phase 7 (Reconciliation)** at the start of v2, front-loaded across all 6 Vendors, before any content phase.

Phase 7 wraps `verify_curl_and_silver_schema.py` as a `gridflow-drift-check` console script (per the drift-research MVP architecture); runs Verification across all 6 Vendors; surfaces findings as `.planning/reconciliation/<vendor>/<NN>-<slug>.md` files; fixes Drift in the upstream Vault for fixable findings; documents `wontfix-v3` reasons for un-fixable findings; and commits the upstream Vault to a private GitHub repo (see ADR-0002).

Existing content phases renumber: current Phase 7 (bug fix) → Phase 8; current Phase 8 (ENTSO-E) → Phase 9; current Phase 9 (4-vendor batch) → Phase 10.

## Considered Options

- **Per-Vendor interleaving** — Reconciliation done immediately before each Vendor's content phase. Rejected: user preference for a clean "verify everything → then build everything" split.
- **Status quo (no upfront audit)** — rejected per Context above.

## Consequences

- v2 now has 4 phases instead of 3. Phase 7 is plausibly the largest of the four.
- Content phases ship from a Vault layer that has been verified once, eliminating a class of recruiter-spot-check failures.
- Some Drift findings will be un-fixable in v2 (need gridflow code changes, e.g. declaring `ElexonAGPT` / `ElexonAGWS` Pydantic classes for the 22 `manual_transformer_schema` cases). Those are documented and explicitly deferred to v3.
- Ongoing drift detection (post-Phase-7) remains manual — see ADR-0002 for the cross-repo CI implications.
