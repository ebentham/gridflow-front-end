# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 7 (Reconciliation) context gathered; ready for planning. Milestone rescoped 2026-05-19 per ADR-0001 to front-load a Reconciliation phase before content phases ship.

## Current Position

**Phase:** 7 — Reconciliation (just-rescoped; CONTEXT.md captured 2026-05-19)
**Plan:** — (4 sub-plans planned: `07a` verifier wrap · `07b` run Verification + triage · `07c` fix open bucket · `07d` push Vault to GitHub)
**Status:** Context gathered; ready for `/gsd-plan-phase 7`
**Last activity:** 2026-05-19 — `/gsd-discuss-phase 7` completed; 7 binding decisions from the grill carried forward; 3 open items resolved (Vault repo name = `EBentham/quant-vault`; ENTSO-E entitlement deferred to Phase 9; Phase 7 split into 4 sub-plans per logical step)

```
[█░░░░░░░░░░░░░░░░░░░] 5% — Phase 7 context gathered, planning next
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

**Last action:** `/gsd-discuss-phase 7` completed 2026-05-19. Created `07-CONTEXT.md` capturing the 7 binding decisions from the grill plus 3 newly-resolved open items (Vault repo name, ENTSO-E entitlement deferral, Phase 7 task granularity). Updated PROJECT.md / ROADMAP.md / REQUIREMENTS.md for the rescope: new Phase 7 (Reconciliation) inserted with 5 RECON-* REQ-IDs; existing Phases 7/8/9 renumbered to 8/9/10; "no upfront audit" decision marked overridden by ADR-0001.
**Next action:** Run `/gsd-plan-phase 7` to produce the 4 sub-plans for Phase 7 (Reconciliation): `07a` verifier wrap · `07b` run Verification + triage · `07c` fix open bucket · `07d` push Vault to GitHub.
**Resume from:** `.planning/phases/07-reconciliation/07-CONTEXT.md`. Required prior reading for the planner: `V2-PHASE-7-HANDOFF.md`, ADR-0001, ADR-0002, project-root `CONTEXT.md`, `research/post-v1/drift-detection/SUMMARY.md`, `research/post-v1/drift-detection/DRIFT-SURFACES.md`.

---

*State updated 2026-05-19 — Phase 7 (Reconciliation) context gathered after milestone rescope per ADR-0001.*
