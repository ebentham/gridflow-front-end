# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v2 full-vendor-coverage
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Defining v2 requirements and roadmap.

## Current Position

**Phase:** Not started (defining requirements)
**Plan:** —
**Status:** Defining requirements
**Last activity:** 2026-05-18 — Milestone v2 started (`/gsd-new-milestone v2-full-vendor-coverage`)

```
[░░░░░░░░░░░░░░░░░░░░] 0% — v2 requirements in progress
```

## Accumulated Context

### Decisions Locked (validated in v1, carried into v2)

| # | Decision | Locked in |
|---|----------|-----------|
| 1 | Templating mechanism: Python + Jinja2 + `gridflow-build` CLI (Option B), CI build, generated HTML gitignored | PROJECT.md (v1) |
| 2 | Source-of-truth direction: vault → site (build reads vault `.md`, renders to site HTML) | PROJECT.md (v1) |
| 3 | Vault vendored in-repo at `vault/<vendor>/` (CI cannot clone upstream `quant-vault`) | PROJECT.md (v1) |
| 4 | Editorial aesthetic kept: cream-forest + Fraunces | PROJECT.md (v1) |
| 5 | Kill "live" framing site-wide; templates born honest | PROJECT.md (v1) |
| 6 | Recruiter-first audience: full-stack DS in energy trading | PROJECT.md (v1) |
| 7 | Core value: domain depth | PROJECT.md (v1) |
| 8 | Pydantic class drift policy: render-with-flag (closing the gap is a v3 candidate) | PROJECT.md (v1) |

### Decisions Pending (v2)

| # | Decision | Source |
|---|----------|--------|
| 1 | Phase shape: bug fix + ENTSO-E + batch the rest (3 phases) | This milestone (user selection) |
| 2 | Assume vault content complete; no upfront audit phase — let `gridflow-build --check` surface gaps | This milestone (user selection) |
| 3 | Strict scope discipline — no Pydantic drift fix, related blurbs, or fuel-pill restoration in v2 | This milestone (user selection) |

### Open Todos / Carry-overs from v1

- Drift-detection research package at `.planning/research/post-v1/drift-detection/` is post-v2 — ignore for now
- v3 candidates catalogued in `PROJECT.md § Out of Scope` and `MILESTONE-COMPLETE.md § Deferred to v2`

## Session Continuity

**Last action:** v2 milestone scoped (3 phases, phase numbering 7–9). PROJECT.md updated with v1 validated items + v2 active items. STATE.md reset. Working on requirements next.
**Next action:** Define v2 requirements (REQ-IDs continuing from v1's last numbering), then spawn roadmapper.
**Resume from:** Continue this `/gsd-new-milestone` flow — next step is requirements then roadmap. After roadmap approval, use `/gsd-discuss-phase 7` or `/gsd-plan-phase 7` to start Phase 7 (bug fix).

---

*State reset 2026-05-18 for v2 milestone start.*
