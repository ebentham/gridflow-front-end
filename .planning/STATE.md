# State

## Project Reference

**Project:** gridflow-front-end
**Milestone:** v1 cleanup — credibility-recovery pass
**Core Value:** When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Domain depth wins every tradeoff.
**Current Focus:** Phase 0 planned; ready to execute.

## Current Position

**Phase:** 0 — Commit in-flight refactor
**Context:** `.planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md`
**Plan:** `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md` (1 plan, 11 tasks across Wave 1; Task 9 is a human-gated PR-merge checkpoint per CLAUDE.md "never commit to main")
**Status:** Ready to execute — next step: `/gsd-execute-phase 0`
**Progress:** Milestone 0/7 phases complete.

```
[░░░░░░░░░░░░░░░░░░░░] 0% — 0/7 phases · 0/50 REQ-IDs delivered
```

## Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| REQ-IDs total | 50 | HYG·2 PAGE·4 BUILD·8 VAULT·4 ELX·8 VEND·5 HON·4 A11Y·6 MOB·3 REF·3 CI·3 |
| REQ-IDs delivered | 0 | |
| Phases total | 7 | 0–6, standard granularity |
| Phases complete | 0 | |
| Phase 0 gating | yes | Blocks all other phases; commit the 26-file in-flight refactor first |
| Parallelisation | Phase 1 ‖ Phase 2 | Both after Phase 0; independent of each other |

## Accumulated Context

### Decisions Locked (from PROJECT.md § Key Decisions)

| # | Decision | Rationale | Locked in |
|---|----------|-----------|-----------|
| 1 | Templating mechanism: Python + Jinja2 + `gridflow-build` CLI (Option B), CI build, generated HTML gitignored | All four research streams converge; Python-first repo; 30-min migration path to 11ty later if needed; recruiter-friendly signal | PROJECT.md |
| 2 | Elexon dataset scope: 33 (matches `gridflow` connector + vault reality) | User picked "Match reality (33)" after vault audit; 22/25/28 stale counts retired | PROJECT.md, REQUIREMENTS.md |
| 3 | Source-of-truth direction: vault → site (build reads vault `.md`, renders to site HTML) | Vault is authored content layer; site is published view; gridflow code remains canonical | PROJECT.md |
| 4 | ENTSO-E cross-vendor proof: Generation by PSR type | Template-stretching (quarter-hour settlement, PSR-type taxonomy) over familiar shape | PROJECT.md |
| 5 | Editorial aesthetic kept: cream-forest + Fraunces | User-confirmed; serves the purpose; redesign deferred | PROJECT.md |
| 6 | Kill "live" framing site-wide | Charts/numbers are illustrative; site is documentation, not a SaaS product | PROJECT.md |
| 7 | Recruiter-first audience: full-stack DS in energy trading | User explicitly prioritised | PROJECT.md |
| 8 | Core value: domain depth | User chose depth from explicit options | PROJECT.md |

### Open Decisions Deferred to Plan-Phase

| Decision | Where it surfaces | Lean |
|----------|-------------------|------|
| Commit-generated-HTML vs build-in-CI (already locked to **CI build, gitignored** per Decision #1) — open sub-question: how is the build environment configured if vault is in a separate repo (vendor-copy at build-time, configurable path, symlinked checkout)? | Phase 3 plan (VAULT-02) | Configurable path env var (`GRIDFLOW_VAULT_PATH`) with CI checking out both repos |
| Per-dataset content verification cadence in CI vs manual | Phase 6 plan | Out-of-scope for v1 milestone (machinery only; cadence is post-v1 discipline) |
| Exact "Planned · F<n>" labels per deferred vendor (F6 / F7 / F8 / etc.) | Phase 4 plan | TBD when stub is authored |

### Todos / Blockers

- [ ] **Phase 0 first** — Cannot start any other work until the 26-file in-flight refactor is committed in 4 logical chunks + `.gitattributes` lands. Any structural cleanup commit on top of the current working tree entangles with three concurrent refactors and breaks bisect.

### Known Risks (from research/PITFALLS.md)

- **Pitfall 1** — Partial honesty pivot. Scoped *before* Phase 3 (grep checklist defined in Phase 5 success criteria); executed *after* Phase 4 so newly-shipped pages are cleaned in the same atomic pass.
- **Pitfall 2** — Phantom coverage (sidebar over-promises). Phase 3 success criterion 2 enforces every sidebar anchor resolves to a real `<section id>`; Phase 6 CI link-check provides defence-in-depth.
- **Pitfall 6** — Hand-edit-22 vs SSG false dichotomy. Resolved by Decision #1 (Option B); locked before Phase 3 begins.
- **Pitfall 9** — Coming-soon stubs reading as half-done vendor pages. Phase 4 success criterion 2 enforces visually-distinct layout via `vendor-coming-soon.html.j2`.
- **Pitfall 10** — Mobile fix is viewport-only. Split across Phase 1 (viewport tag) and Phase 5 (mobile CSS in `theme.css`).

## Session Continuity

**Last action:** Phase 0 planned. Single consolidated `00-PLAN.md` (1443 lines) with 11 sequential tasks: Task 0 records the plan as a `docs(00):` commit, Tasks 1-4 are the 4 cleanup chunks, Tasks 5-6 are repo-hygiene (`.gitattributes` + renormalize), Task 7 reconciles ROADMAP §0 SC#1 wording, Task 8 opens the PR, Task 9 is the human-gated PR merge (`checkpoint:human-action`), Task 10 verifies GitHub Pages catches up. Plan passed gsd-plan-checker on the second iteration (2 BLOCKERs found and fixed in iteration 1: stale baseline counts + stale commit math).
**Next action:** Run `/gsd-execute-phase 0` to execute the 11-task plan. After Task 8 the executor pauses for the human merge gate.
**Resume from:** Phase 0 execution. Phase 0 inputs: `00-PLAN.md` (11 tasks), `00-CONTEXT.md` (decisions D-01 through D-05), PROJECT.md, REQUIREMENTS.md (HYG-01, HYG-02), research/PITFALLS.md § Pitfall 0, codebase/CONCERNS.md § In-Flight Refactor.

### Phase 0 — Locked Decisions (from `00-CONTEXT.md`)

| # | Decision | Notes |
|---|----------|-------|
| D-01 | 4 cleanup chunks: typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks | Ordering 1→2→3→4 per PITFALLS Pitfall 0 |
| D-02 | Chunk 4 lumps cross-phase work (elexon.html honesty pivot + index.html hero/WIP-bar + viewport fixes on fuelhh/elexon) | Working tree truly clean post-Phase-0; Phase 1 / Phase 5 plan-phase reads CONTEXT to adjust their denominators |
| D-03 | 2 additional `chore:` commits beyond the 4 chunks: (5) `.gitattributes` + `.gitignore` bundled, (6) renormalize line endings | Total = 6 commits in Phase 0; ROADMAP §0 Success Criterion 1 ("4 commits") read generously OR updated by planner |
| D-04 | Stack 6 cleanup commits on `docs/codebase-map`; one PR (13 commits) → main; merge commit (not squash, not rebase) | Pages catches up on merge |
| D-05 | `.gitignore` adds `.claude/` and `.codex-assessment-shots/`; `.gitattributes` carries `text eol=lf` for `.html`, `.css`, `.js`, `.json`, `.py`, `.md` (planner finalizes extension list) | Post-Phase-0 `git status` shows zero modified AND zero untracked |

---
*State initialised 2026-05-17 after roadmap creation. Updated 2026-05-17 after Phase 0 context gathering.*
