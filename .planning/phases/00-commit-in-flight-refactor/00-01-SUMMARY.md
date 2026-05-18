---
phase: 00-commit-in-flight-refactor
plan: 01
status: complete
completed: 2026-05-18
---

# Summary — Phase 0 Plan 01: Commit in-flight refactor + repo hygiene

## What was built

The 27 uncommitted in-flight modified files have been landed as 6 atomic concern-per-commit cleanups, the line-ending churn between Windows-edits and Linux-CI deploys has been stopped permanently via `.gitattributes`, and the docs/codebase-map branch has been merged into main with a merge-commit (preserving 4-chunk bisect granularity per CONTEXT D-04). GitHub Pages catches up to the new editorial framing on push.

## Commits landed on main (via PR [#3](https://github.com/EBentham/gridflow-front-end/pull/3))

Beyond the 9 prior planning commits already on `docs/codebase-map`, this plan added:

1. `023169b` — `docs(research): seed post-v1 drift-detection research brief` (pre-Task-0 baseline reconciliation: unanticipated untracked file from a future-milestone research seed)
2. `30556f8` — `docs(00): record phase 0 plan` (Task 0 planner-record)
3. `732e463` — `refactor(typography): drop fg-accent class from display italics` (chunk 1 — 27 files, 40 ins / 40 del)
4. `dcebb8b` — `chore(index): remove false pillar-status Shipping badges` (chunk 2 — 3 deletions)
5. `cd32f14` — `docs(fuelhh): pivot to honest static-snapshot framing` (chunk 3 — 7 substitutions)
6. `6086daa` — `docs(site): consolidate cross-page honesty + viewport tweaks` (chunk 4 — D-02 cross-phase bundle: 3 files, 27 ins / 83 del)
7. `26ed2f2` — `chore(repo): add .gitattributes and gitignore tooling artefacts` (chunk 5)
8. `f8835bf` — `chore(repo): renormalize line endings after .gitattributes (no-op)` (chunk 6 — empty audit commit; renormalize had nothing to change because git autocrlf had already been normalizing)
9. `1c99a75` — `docs(roadmap): reconcile phase 0 SC#1 with 6-commit reality` (Task 7 — C1 Option A)
10. `f87bda1` — `Merge pull request #3 from EBentham/docs/codebase-map` (merge commit per D-04)

## Key files modified

**Site (27 HTML files):**
- `site/hifi/architecture.html`, `site/hifi/data-sources.html`, `site/hifi/index.html`, `site/hifi/models/demand-forecast.html`
- `site/hifi/data-sources/elexon.html` (load-bearing — chunks 1 + 4 with HEALTH section deletion + Right now → Sample window rewrite)
- `site/hifi/data-sources/elexon/fuelhh.html` (load-bearing — chunks 1 + 3 + 4 with full honesty pivot)
- 22 other Elexon dataset pages — typography-only edits (chunk 1)

**Repo hygiene:**
- `.gitattributes` (new) — 9 per-extension `text eol=lf` rules
- `.gitignore` — appended `.claude/` and `.codex-assessment-shots/`

**Planning:**
- `.planning/ROADMAP.md` — Phase 0 progress-table entry + `**Plans**: 1 plan` + SC#1 reconciliation
- `.planning/STATE.md` — flipped to "Ready to execute"
- `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md` — 1465-line consolidated 11-task plan
- `.planning/research/post-v1/drift-detection/RESEARCH-BRIEF.md` — committed pre-Task-0 to restore baseline

## Verification artifacts (Phase 0 SC traceability)

**SC#1 (working tree clean + 6 commits in documented order):**
- `git status --porcelain` on main returns empty ✓
- `git log main --oneline` shows the 6 cleanup chunks in correct order (`refactor(typography)` oldest → `chore(repo): renormalize` newest) plus the Task-0 record + ROADMAP reconciliation ✓

**SC#2 (.gitattributes lands with required extensions):**
- `.gitattributes` at repo root with 9 lines ✓
- Per-extension rules cover `.html`, `.css`, `.js`, `.json`, `.py` (HYG-02 wording) plus `.md`, `.yml`, `.yaml`, `.toml` (planning + workflow + pyproject extras)

**SC#3 (GitHub Pages-deployed site matches working tree):**
- Pages workflow `Deploy to GitHub Pages` run `26009662063` — completed `success` in 16s ✓
- `https://ebentham.github.io/gridflow-front-end/` serves the new hero ("A pipeline and catalogue for UK & European energy data") ✓
- `https://ebentham.github.io/gridflow-front-end/data-sources/elexon/fuelhh.html` serves `PRIMARY KEY` (chunk-3 honesty pivot live) ✓
- `https://ebentham.github.io/gridflow-front-end/data-sources/elexon.html` no longer serves `Pipeline health` (chunk-4 HEALTH deletion live) ✓ — also confirms `Sample window` and `TIMEZONE` strings present

## Deviations from plan

1. **Pre-Task-0 commit added** — An unanticipated untracked file (`.planning/research/post-v1/drift-detection/RESEARCH-BRIEF.md` — a research seed for a post-v1 milestone) existed in the working tree. Per user direction at the orchestrator gate, committed it via `docs(research):` ahead of Task 0 to restore the planning-time baseline (29M + 3??).

2. **Task 1 — index.html had 5 typography occurrences, not 4** — Plan said `<span class="italic fg-accent">` appeared 4 times in index.html; actual count was 5 (4 occurrences in pillars 2-4 + 1 in the hero `tidied.` span). The replace_all sed pattern handled all 5 correctly; net file diff was unaffected.

3. **Task 6 was a no-op renormalize** — `git add --renormalize .` produced no staged changes because git's autocrlf had already been normalizing files on commit (we'd been seeing `warning: LF will be replaced by CRLF` throughout). Committed `--allow-empty` per the plan's documented no-op fallback, preserving the audit checkpoint for the chunk-6 documented intent.

4. **Task 10 verification used PowerShell** — `curl -v` started failing with `CRYPT_E_NO_REVOCATION_CHECK` Schannel errors (Windows cert revocation pending). Verification succeeded via PowerShell's `Invoke-WebRequest` which uses native Windows TLS. All 5 deployed-content checks passed (hero present, old hero absent, PRIMARY KEY present, Pipeline health absent, Sample window + TIMEZONE present).

5. **Task 9 ran autonomously** — STATE.md described Task 9 as a human-gated PR-merge checkpoint, but the user explicitly directed at the orchestrator gate to "execute autonomously without inputs". Plan file's `<task type="auto" gate="none">` was authoritative for this run; merge succeeded with `--merge` strategy (merge-commit, not squash/rebase) per D-04.

## Self-Check: PASSED

All 11 task `<done>` checklists verified inline. Phase 0 SC#1, SC#2, SC#3 all verified TRUE against the merged main branch + deployed Pages site. Requirements HYG-01 + HYG-02 satisfied.

## What this enables

Phase 0 is the gating prerequisite per all four research streams. With the working tree clean and concern-per-commit history landed, every subsequent phase can:

- Be planned/executed without entangling with three concurrent refactors
- Land commits without LF/CRLF warnings (Windows-edited files normalize on commit)
- Bisect at concern granularity if a post-Phase-0 regression appears

Phase 1 (Trivial bug fixes) and Phase 2 (Shared CSS/JS extraction) are now unblocked and can run in parallel.
