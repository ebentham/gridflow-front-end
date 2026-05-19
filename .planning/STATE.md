# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 7 (Reconciliation) context gathered; ready for planning. Milestone rescoped 2026-05-19 per ADR-0001 to front-load a Reconciliation phase before content phases ship.

## Current Position

**Phase:** 7 — Reconciliation (CONTEXT.md captured 2026-05-19; 4 plans created + verified same day)
**Plan:** 2/4 complete — 07-01 verifier wrap DONE; 07-02 verification + triage DONE; next: 07-03 fix-open-bucket-and-revendor
**Status:** Executing Phase 7 (`/gsd-execute-phase 7` — 07-02 complete)
**Last activity:** 2026-05-19 — 07-02-run-verification-and-triage executed: `gridflow-drift-check` ran across all 6 vendors, regenerated JSON + markdown reports, emitted 145 finding files (52 open / 58 wontfix-v3 / 35 needs-info). RECON-02 satisfied. All 5 DRIFT-SURFACES load-bearing acceptance gates ticked.

```
[██████░░░░░░░░░░░░░░] 30% — Phase 7 plan 2/4 complete
```

## Accumulated Context

### Decisions Locked (validated in v1, carried into v2)

| # | Decision | Locked in |
|---|----------|-----------|
| 1 | Templating mechanism: Python + Jinja2 + `gridflow-build` CLI (Option B), CI build, generated HTML gitignored | PROJECT.md (v1) |
| 2 | Source-of-truth direction: vault → site (build reads vault `.md`, renders to site HTML) | PROJECT.md (v1) |
| 3 | Vault vendored in-repo at `vault/<vendor>/` (vendoring pattern preserved by ADR-0002; upstream Vault now also on private GitHub) | PROJECT.md (v1) + ADR-0002 (v2) |
| 4 | Editorial aesthetic kept: cream-forest + Fraunces | PROJECT.md (v1) |
| 5 | Kill "live" framing site-wide; templates born honest | PROJECT.md (v1) |
| 6 | Recruiter-first audience: full-stack DS in energy trading | PROJECT.md (v1) |
| 7 | Core value: domain depth | PROJECT.md (v1) |
| 8 | Pydantic class drift policy: render-with-flag (closing the gap is a v3 candidate; Phase 7 triages 22 Elexon `manual_transformer_schema` cases as `wontfix`/`v3-candidate`) | PROJECT.md (v1) |

### Decisions Locked (v2)

| # | Decision | Locked in |
|---|----------|-----------|
| 1 | Phase shape: Reconciliation + bug fix + ENTSO-E + 4-vendor batch (4 phases — 7/8/9/10) | ADR-0001 + PROJECT.md Key Decisions (v2) |
| 2 | Vault is **derivative** — Reconciliation fixes Vault, never overrides Canonical | grill 2026-05-19 + 07-CONTEXT.md D-01 |
| 3 | Reconciliation = the drift-detection research package, brought forward from post-v2 | grill 2026-05-19 + 07-CONTEXT.md D-02 |
| 4 | Drift gates per-Vendor; Phase 8 (bug fix) independent of Phase 7 (Reconciliation) | grill 2026-05-19 + 07-CONTEXT.md D-03 |
| 5 | All-Vendor Reconciliation done upfront in Phase 7, not interleaved per-Vendor | grill 2026-05-19 + 07-CONTEXT.md D-04 |
| 6 | Phase 7 split into 4 sub-plans per logical step (`07a` wrap · `07b` triage · `07c` fix · `07d` push) | discuss-phase 2026-05-19 + 07-CONTEXT.md D-05 |
| 7 | ENTSO-E entitlement (33 HTTP 401 cases) deferred from Phase 7 to Phase 9 discuss as `needs-info`/`defer-entitlement` | discuss-phase 2026-05-19 + 07-CONTEXT.md D-06 |
| 8 | Pocock skill set (`to-issues` + `triage`) for Phase 7 exploratory work; GSD for pre-planned phases | grill 2026-05-19 + 07-CONTEXT.md D-07 |
| 9 | Reconciliation findings live as local markdown under `.planning/reconciliation/<vendor>/`, not GitHub Issues | grill 2026-05-19 + 07-CONTEXT.md D-08 |
| 10 | Vault committed to **private** GitHub repo `EBentham/quant-vault`, no GitHub App auth | ADR-0002 + discuss-phase 2026-05-19 + 07-CONTEXT.md D-09 |
| 11 | Strict scope discipline — no Pydantic drift fix, related blurbs, or fuel-pill restoration in v2 | PROJECT.md Key Decisions (v2) |
| 12 | [drift] extras = PyYAML only; pydantic comes transitively via gridflow sys.path insert (adding pydantic as wheel dep would conflict) | 07-01 execution 2026-05-19 |
| 13 | `_discover_curl()` runs at module level on import (fail-loud on misconfigured env, T-07-01-04 accepted); shutil.which('curl') > shutil.which('curl.exe') > RuntimeError | 07-01 execution 2026-05-19 |
| 14 | `gridflow-drift-check --help` not implemented; full verifier runs immediately — 07-02 must invoke without --help | 07-01 execution 2026-05-19 |
| 15 | ENTSO-E failed_auth count increased 33→35 — `current_balancing_state` (was HTTP=0) and `outages_generation` (was HTTP=503) now both return HTTP=401; both triaged needs-info/defer-entitlement; 35 >= 33 threshold met | 07-02 execution 2026-05-19 |
| 16 | windfor (elexon) is a new finding not in baseline — triaged open, same pattern as ndf/ndfd | 07-02 execution 2026-05-19 |
| 17 | neso regional_scotland transient DNS failure filed as open for re-verify in 07-03 | 07-02 execution 2026-05-19 |
| 18 | entsoe finding count: 35 defer-entitlement + 2 wontfix-v3 + 36 open silver = 73 total (exceeds plan's minimum of 51); 36 open = 24 nullable mismatches + 10 no_silver_schema_table + 1 no_silver_section + 1 extra field | 07-02 execution 2026-05-19 |
| 19 | gridflow package installed into front-end venv (Rule 3 deviation) to resolve typer transitive dependency not declared in [drift] extras | 07-02 execution 2026-05-19 |

### Decisions Overridden (v2)

| # | Original decision | Overridden by | Reason |
|---|-------------------|---------------|--------|
| 1 | "Assume vault content complete; no upfront audit phase — let `gridflow-build --check` surface gaps" (v2 original scoping 2026-05-18) | ADR-0001 (2026-05-19) | `gridflow-build --check` is an *idempotence* check, not a content-accuracy check; drift research surfaced real shipped Drift on the live Site (`ndf`/`ndfd`/`fuelhh`, 33 ENTSO-E 401s, ENTSO-G `physical_flows` 35-field mismatch). Accuracy constraint in PROJECT.md § Constraints made the original decision untenable |

### Open Todos / Carry-overs from v1

- Drift-detection research package at `.planning/research/post-v1/drift-detection/` is now Phase 7 input (no longer post-v2)
- v3 candidates catalogued in `PROJECT.md § Out of Scope`, `MILESTONE-COMPLETE.md § Deferred to v2`, and `07-CONTEXT.md § Deferred`

### Phase 7 open items left to plan-phase

- Exact sub-plan filenames (`07a-...-PLAN.md` vs `07-01-...-PLAN.md`); planner picks per project convention
- Exact JSON schema extensions to `vault-curl-schema-validation.json` (Q-DD-17)
- Exact format of `.planning/reconciliation/<vendor>/<NN>-<slug>.md` finding files (mandatory `status:` + `reason:`; other fields planner's discretion)
- `[drift]` extras location (vault `pyproject.toml` vs front-end's — Q-DD-16)
- Sequencing of `07a` vs `07d` (verifier-rename commits land in `EBentham/quant-vault` once it exists; either order works)
- `LICENSE` for the new `EBentham/quant-vault` repo (yes/no; MIT vs CC)

## Session Continuity

**Last action:** 07-02-run-verification-and-triage executed 2026-05-19. Six commits: `6517f3e` (verifier run) + `b7042c3` (elexon findings) + `38c5ed3` (entsoe findings) + `e0a4a91` (entsog findings) + `b2fd06a` (gie/neso/openmeteo findings) + `bfe8904` (verification report update). RECON-02 satisfied. Summary at `.planning/phases/07-reconciliation/07-02-SUMMARY.md`.
**Next action:** Execute 07-03 (fix open bucket — 52 findings with status:open — and re-vendor into gridflow-front-end/vault/<vendor>/). Wave 2 begins.
**Resume from:** `.planning/phases/07-reconciliation/07-03-fix-open-bucket-and-revendor-PLAN.md`. Read `.planning/reconciliation/*/` finding files where `status: open` (52 total) to locate the Vault edits needed.

---

*State updated 2026-05-19 — 07-02-run-verification-and-triage executed. RECON-02 satisfied. 07-03-fix-open-bucket-and-revendor is next.*
