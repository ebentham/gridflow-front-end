# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 8 (dataset-page formatting bug fix) planned 2026-05-19. RESEARCH.md confirmed both hypothesised causes at `dataset.html.j2:18` (`align-items: end` dominant + `grid-template-columns: 1fr auto` × unwrapped SILVER PATH mono amplifier); candidates table reviewed and recommendation revised from (c) to **(a) only** after inner-grid sizing arithmetic surfaced a text-overflow regression in (b)/(c). Single plan `08-01-PLAN.md` (4 tasks, 2 commits expected): Task 1 single-token template edit `end` → `start`, Task 2 re-render 34 pages, Task 3 user-verified checkpoint (3 desktop + 2 mobile per D-02 — `autonomous: false`), Task 4 v1 CI gates. theme.css intentionally untouched. Next: `/gsd-execute-phase 8`.

## Current Position

**Phase:** 8D — Vendor landing-page briefs (5 hubs) — **COMPLETE 2026-05-20**
**Plan:** 1/1 — 5 vendor-hub briefs at `content-briefs/<vendor>/_landing.md` (entsoe, entsog, gie, neso, openmeteo); build.py `build_vendor` override extended to check `authored-pages/<vendor>/_landing.html`; SUMMARY committed
**Status:** Phase 8D complete. Next: Phase 9 (ENTSO-E per-dataset briefs, 49 datasets) — `/gsd-plan-phase 9`
**Last activity:** 2026-05-20 — Sonnet 4.6 background executor ran Tasks 02-08 to completion (hit usage limit during Task 09 verification; recovery was a single-commit fix for an in-flight transformer-count correction in gie brief + ROADMAP progress table update). All 5 briefs pass 10 structural checks; 15 cross-source discrepancies surfaced; per-dataset row counts match vault (49/33/8/33/6 — NESO is 33 not 34, README.md inflated the plan's expected count).

```
[████████████████████] 42% — Phase 8D complete (13/31 v2 REQ-IDs delivered cumulative; BUG-01/BUG-02/BUG-03 satisfied through 8C+8D)
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

### Phase 7 resolved items

All Phase 7 open items resolved during execution:
- Sub-plan filenames: `07-01..07-04` (per project convention)
- JSON schema: verifier reports committed to quant-vault at `vault-curl-schema-validation.{json,md}` (Q-DD-17 default lean)
- Finding file format: YAML frontmatter with `status:` + `reason:` + `vendor:` + `dataset:` + `drift_category:` + `verifier_finding_id:` + `references:` + `tags:` (established in 07-02)
- `[drift]` extras: in `gridflow-front-end/pyproject.toml` (Q-DD-16 lean confirmed — quant-vault has no pyproject.toml)
- Sequencing: 07-01 → 07-02 → 07-03 → 07-04 (sequential Wave 1 then Wave 2)
- LICENSE: MIT (inertia from gridflow-front-end; planner decision in 07-04)

## Session Continuity

**Last action:** Phase 8D execution complete 2026-05-20. 5 vendor-hub briefs committed (entsoe 49/6, entsog 33/5, gie 8/2, neso 33/4, openmeteo 6/2); build.py override extended for vendor hubs; SUMMARY + ROADMAP updated. 8 `docs(08D):` + `fix(08D):` commits on branch `docs/v2-milestone-start`. BRIEF-LOG.md has one logged false positive (NESO Check 7 regex needs `[a-z0-9_]+` to handle numeric slug suffixes).
**Next action:** Plan Phase 9 — ENTSO-E per-dataset briefs (49 datasets following the 8C pattern). Run `/gsd-plan-phase 9`.
**Resume from:** Phase 9 plan (`/gsd-plan-phase 9`). ENTSO-E entitlement decision (33 HTTP 401 datasets deferred from Phase 7 per D-06) must be resolved in the discuss-phase before content build proceeds. Phase 10 also unblocked (4-vendor batch: 80 per-dataset briefs).

**Branch state as of Phase 8D completion (~88 commits ahead of main, NOT pushed):**
- `content-briefs/elexon/` — 33 files (Phase 8C, committed)
- `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/_landing.md` — 5 files (Phase 8D, committed)
- `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/<one_slug>.md` — 5 sample per-dataset briefs (pre-Phase-8D, committed)
- `authored-pages/elexon/` — 33 files (Phase 8B, committed)
- `src/gridflow_front_end/build.py` — both per-dataset (8B) and per-hub (8D) override paths wired
- Untracked: `.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, `.planning/research/*.md` (pre-existing, gitignored-intent)
- Modified (pre-existing user work, not from this session's agents): `CLAUDE.md`

---

*State updated 2026-05-19 — Phase 8 plan-phase complete. 1 plan / 4 tasks / 2 commits / 1 user-checkpoint. 5/31 v2 REQ-IDs delivered (Phase 7 RECON-01..RECON-05). Next: /gsd-execute-phase 8.*
