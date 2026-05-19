# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 7 (Reconciliation) context gathered; ready for planning. Milestone rescoped 2026-05-19 per ADR-0001 to front-load a Reconciliation phase before content phases ship.

## Current Position

**Phase:** 7 — Reconciliation (CONTEXT.md captured 2026-05-19; 4 plans created + verified same day)
**Plan:** 1/4 complete — 07-01 verifier wrap DONE; next: 07-02 run Verification + triage
**Status:** Executing Phase 7 (`/gsd-execute-phase 7` — 07-01 complete)
**Last activity:** 2026-05-19 — 07-01-verifier-wrap executed: renamed `verify_curl_and_silver_schema.py` → `gridflow_drift_check.py`, fixed two Windows portability blockers, exposed `gridflow-drift-check` console script via gridflow-front-end `pyproject.toml`. RECON-01 satisfied.

```
[███░░░░░░░░░░░░░░░░░] 15% — Phase 7 plan 1/4 complete
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

**Last action:** 07-01-verifier-wrap executed 2026-05-19. Two commits: `739c2ed` (refactor, quant-vault) + `87f0234` (feat, gridflow-front-end). RECON-01 satisfied. Summary at `.planning/phases/07-reconciliation/07-01-SUMMARY.md`.
**Next action:** Execute 07-02 (run Verification across all 6 Vendors + triage). Wave 1 continues. `gridflow-drift-check` is installed; run without `--help` (no argparse in verifier).
**Resume from:** `.planning/phases/07-reconciliation/07-02-run-verification-and-triage-PLAN.md` (Wave 1 continuation). All 4 plans + CONTEXT + DISCUSSION-LOG live under `.planning/phases/07-reconciliation/`.

---

*State updated 2026-05-19 — 07-01-verifier-wrap executed. RECON-01 satisfied. 07-02-run-verification-and-triage is next.*
