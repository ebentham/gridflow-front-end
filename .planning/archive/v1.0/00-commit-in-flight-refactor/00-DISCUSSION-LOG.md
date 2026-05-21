# Phase 0: Commit in-flight refactor - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `00-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-17
**Phase:** 0-commit-in-flight-refactor
**Areas discussed:** Chunk 4 scope, Untracked files policy, Landing strategy, Renormalization commit

---

## Chunk 4 scope

| Option | Description | Selected |
|--------|-------------|----------|
| Lump into chunk 4 (broader) | Treat elexon.html (and the other cross-phase bits like index.html hero rewrite + WIP-bar removal) as chunk 4 'remaining tweaks'. Pragmatic: Phase 0 commits ALL the in-flight work, even if some of it previews Phase 5. Costs: chunk 4 carries Phase 5 honesty work; Phase 5 later has to know elexon.html is already partially honest. Benefits: zero work lost, working tree truly clean, no revert. | ✓ |
| Split into more commits (>4) | Add chunks 5–7 for the cross-phase work: e.g. 5 = elexon.html honesty pivot, 6 = index.html hero rewrite, 7 = viewport-fixes on fuelhh+elexon. Strict commit-per-concern. Costs: violates ROADMAP success criterion 'shows 4 commits titled per the four logical chunks' — the criterion would need to update. Benefits: cleanest log; each commit maps to one REQ-ID. | |
| Revert cross-phase work to working tree | Keep the typography sweep + pillar-status + fuelhh honesty edits, but reset elexon.html, index.html cross-phase bits, fuelhh+elexon viewport fixes, demand-forecast typo-only edits. Stash the reverts for Phase 1/5 to consume. Costs: working tree NOT clean after Phase 0 (Success criterion 1 'zero modified files' breaks); risk of lost work via stash drop. Benefits: each commit lives in its proper phase. | |

**User's choice:** Lump into chunk 4 (broader)
**Notes:** Zero work lost was the deciding factor. The Phase 0 working-tree-clean success criterion is load-bearing for unblocking everything else — risking work in a stash to be "phase-pure" was the wrong tradeoff. Downstream Phase 1 and Phase 5 plan-phase calls will need to read `00-CONTEXT.md` and adjust file lists / grep checklists accordingly (the integration-points section of CONTEXT calls this out).

---

## Untracked files policy

| Option | Description | Selected |
|--------|-------------|----------|
| Add to .gitignore in Phase 0 | Append `.claude/` and `.codex-assessment-shots/` to .gitignore as part of the `.gitattributes` commit (or as a separate small commit). Working tree becomes truly clean — `git status` shows nothing. Cost: tiny. Benefit: future status checks aren't polluted; matches the 'clean working tree is the gating prerequisite' spirit of Phase 0. | ✓ |
| Leave untracked, ignore manually | Don't touch .gitignore. User remembers to ignore them. `git status` will keep showing them. Cost: every Phase 0+ verification step has to filter them out. Benefit: zero work. | |
| Add `.claude/` to .gitignore but keep codex shots for portfolio | Treat .claude/ as private settings (ignore), but track .codex-assessment-shots/ as docs (commit the PNGs). Suggests the shots are useful project artefacts. Cost: shots committed to git history; if they're large or sensitive, downsides. Benefit: portfolio gets visual record of what Codex saw. | |

**User's choice:** Add to .gitignore in Phase 0
**Notes:** The codex shots are tooling artefacts, not portfolio content. Working-tree cleanliness for downstream phase verification was the priority.

### Follow-up: Where does the `.gitignore` update land?

| Option | Description | Selected |
|--------|-------------|----------|
| Bundle with .gitattributes commit | One `chore: add .gitattributes and .gitignore entries for tooling artefacts` commit. Both are repo-hygiene infrastructure; bundling keeps total commit count low. Cost: commit message has two concerns. Benefit: fewer 'chore' commits cluttering the log. | ✓ |
| Separate commit | Two distinct commits: `chore: add .gitattributes for line endings` and `chore: gitignore .claude/ and .codex-assessment-shots/`. Strict one-concern-per-commit. Cost: +1 commit. Benefit: clearer log; each commit is reversible independently. | |
| Fold into chunk 4 | Add the .gitignore entries to the catch-all chunk 4 commit. Cost: chunk 4 already carries multiple concerns; adding repo hygiene muddles it further. Benefit: zero extra commits. | |

**User's choice:** Bundle with .gitattributes commit
**Notes:** Both are repo-hygiene infrastructure; the slight commit-message impurity is worth the lower commit count.

---

## Landing strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Add commits to current branch, one PR for everything | Make the 4 cleanup commits + chore commit on top of the current `docs/codebase-map` branch. Open one PR (`docs/codebase-map` → `main`) that contains all 7 planning commits + 5 cleanup commits = 12 commits. Single review surface. Cost: planning and cleanup ride together — reviewer (you) sees both at once. Benefit: simplest mechanically, no branch juggling, GitHub Pages catches up in one merge. | ✓ |
| Branch fresh from main for cleanup, two PRs | `git checkout main && git checkout -b chore/phase-0-commit-in-flight-refactor`. Cleanup commits land via PR #1 (cleanup → main). Then `docs/codebase-map` rebases on the updated main and lands via PR #2 (planning → main). Cost: branch juggling; the working-tree edits need to move with the branch switch (stash or `git restore --source`). Benefit: cleanup lands first and Pages catches up before planning PR; PRs reviewable independently. | |
| Branch off `docs/codebase-map` for cleanup, two PRs in sequence | `git checkout -b chore/phase-0-commit-in-flight-refactor` (branches off current). Cleanup commits stack on top of planning. PR #1 (planning) lands first; PR #2 (cleanup) opens against the freshly-merged main. Cost: PR #2 has to wait for PR #1 to merge or rebase. Benefit: both PRs are 'pure' (planning vs cleanup); cleanup PR is reviewable in isolation. | |

**User's choice:** Add commits to current branch, one PR for everything
**Notes:** Solo project, solo reviewer — branch-juggling overhead isn't justified by review separation. Note the actual PR will contain 13 commits, not 12, once the 6th renormalization commit is included (4 cleanup chunks + 2 chore commits + 7 planning).

### Follow-up: Merge strategy when the PR lands on `main`?

| Option | Description | Selected |
|--------|-------------|----------|
| Merge commit (preserve all 12 commits) | Use 'Create a merge commit' on the PR. All 12 commits (7 planning + 5 cleanup) stay in the main log; `git log --oneline` shows the 4 in-flight-refactor chunks distinctly. Consistent with the 'commit-per-concern' discipline of Phase 0 — squashing it defeats the whole point. Benefit: bisect works at concern granularity post-merge. | ✓ |
| Rebase + merge (linear, preserve commits) | Use 'Rebase and merge'. Same end state as merge commit but no merge-commit node. Linear history. Benefit: log stays clean; cost: re-writes commit SHAs vs the local branch, so any local references to those SHAs are now stale. | |
| Squash (collapse to one commit) | Squash all 12 commits into one. Cost: defeats the entire point of the 4-chunk split (bisect dies, review-ability gone). Recommend NOT this. Benefit: log is one line per PR. | |

**User's choice:** Merge commit (preserve all 12 commits)
**Notes:** Bisect-at-concern-granularity was the deciding factor. The 4-chunk discipline is purpose-built for incremental review and rollback; squashing defeats it.

---

## Renormalization commit

| Option | Description | Selected |
|--------|-------------|----------|
| Separate `chore: renormalize line endings` commit (6th commit) | After the .gitattributes commit lands, run `git add --renormalize .` and commit any resulting changes as `chore: renormalize line endings after .gitattributes`. Cost: 6 commits in Phase 0 instead of 5 — success criterion 1 ('4 commits') needs to be read generously. Benefit: cleanest — history shows exactly what .gitattributes did to existing files; future Linux/Windows commits stay calm. | ✓ |
| Bundle renormalization into the .gitattributes commit | Run `git add --renormalize .` BEFORE committing .gitattributes/.gitignore; everything ships as one `chore: add .gitattributes + .gitignore + renormalize line endings` commit. Cost: that commit is much larger (touches every committed file with CRLF) — harder to review. Benefit: one commit, not two. | |
| Skip renormalization — let files normalize as touched | Don't renormalize. New commits use the .gitattributes rules; old committed files keep their existing line endings until next edit. Cost: Phase 1+ commits will show line-ending churn for files that were already LF-committed but get touched. Benefit: smallest Phase 0 diff. | |

**User's choice:** Separate `chore: renormalize line endings` commit (6th commit)
**Notes:** Reviewability of the renormalize commit (vs a bundled mega-commit) was the deciding factor. The total commit count ratchet to 6 is acknowledged in CONTEXT D-03 — ROADMAP §0 Success Criterion 1 wording is left to the planner to decide whether to update or read generously.

---

## Claude's Discretion

- Exact conventional-commit messages (chunks 1–6). Constraint: `<type>: <one-line summary>` per `CLAUDE.md`. Suggested types — chunk 1 `refactor:`, chunk 2 `chore:`, chunks 3+4 `docs:`, chunks 5+6 `chore:`. Planner finalizes wording.
- `.gitattributes` exact content beyond the locked `text eol=lf` rule. Planner picks: explicit per-extension list from PITFALLS (`*.html`, `*.css`, `*.js`, `*.json`, `*.py`) plus likely additions (`*.md`, `*.yml`/`*.yaml`, `*.toml`), OR a blanket `* text=auto eol=lf` rule.
- PR title and body wording.
- Whether to update ROADMAP §0 Success Criterion 1 to say "6 commits" explicitly.

## Deferred Ideas

- Updating ROADMAP §0 Success Criterion 1 wording to acknowledge 6-commit total. Planner decides.
- `* text=auto eol=lf` blanket vs explicit per-extension `.gitattributes`. Planner picks after a quick audit of repo content.
- `.github/workflows/deploy.yml` structural check (`htmlhint`) before `upload-pages-artifact@v3` — that's Phase 6 (CI-01); out of scope here.
- Author photos / CV link / contact details — out of scope per `PROJECT.md § Out of Scope`; came up only as a hypothetical "portfolio behind-the-scenes" framing for `.codex-assessment-shots/`, which the user explicitly rejected.
