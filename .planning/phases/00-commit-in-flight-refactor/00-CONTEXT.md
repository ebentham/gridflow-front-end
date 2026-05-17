# Phase 0: Commit in-flight refactor - Context

**Gathered:** 2026-05-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Land the 27 uncommitted modified files (per `git status` at session start — actual count is 27, not the 26 noted in `.planning/codebase/CONCERNS.md § In-Flight Refactor (Uncommitted)`; the file CONCERNS omits from its prose enumeration is `site/hifi/data-sources/elexon.html` — which is the heart of chunk 4 below) as a focused set of logical commits, plus `.gitattributes` + `.gitignore` repo-hygiene, and land them on `main` so GitHub Pages catches up to the working tree. This is the gating prerequisite for every other phase per `.planning/research/PITFALLS.md § Pitfall 0`.

In scope:
- Splitting the in-flight refactor into 4 logical cleanup commits (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks).
- Adding `.gitattributes` with `text eol=lf` rules to stop CRLF/LF churn between Windows-edits and Linux-CI deploys.
- Adding `.gitignore` entries for `.claude/` and `.codex-assessment-shots/` so future `git status` checks are clean.
- A renormalization pass (`git add --renormalize .`) so already-committed files conform to the new rules.
- Landing everything on `main` via PR + merge so GitHub Pages picks up the changes.

Out of scope:
- Phase 1's broader viewport find-and-replace across the remaining 21 broken pages (`MOB-01`). Note: 2 of the 23 viewport-broken pages (`fuelhh.html`, `elexon.html`) get their viewport fix in this phase as a side-effect of chunk 4 — see Decision D-04.
- Phase 5's full honesty sweep (`HON-01`). Note: 2 surfaces (the `elexon.html` hub honesty pivot and the `index.html` WIP-bar/hero rewrite) get done in chunk 4 as a side-effect of "commit what's in the working tree" — see Decision D-04. Phase 5 still owns the other 4 surfaces and the cross-page grep verification.
- Any NEW code (new templates, new vault wiring, new pages). Phase 0 is purely git hygiene + landing what's already in the working tree.

</domain>

<decisions>
## Implementation Decisions

### Commit chunking

- **D-01:** The 4 cleanup chunks from `.planning/research/PITFALLS.md § Pitfall 0` are the spine: (1) typography sweep `fg-accent → italic` across all touched files, (2) pillar-status removal on `index.html`, (3) `fuelhh.html` honesty edits, (4) remaining tweaks. Commit ordering: 1 → 2 → 3 → 4. Conventional Commits prefix convention applies per `CLAUDE.md` (the planner picks the exact verb; `refactor:`, `docs:`, `chore:` are all viable for chunk 4 depending on framing).

- **D-02:** Cross-phase work that previews Phase 1 or Phase 5 is **lumped into chunk 4 (broad)**, not split or reverted. Concretely, chunk 4 contains:
  - `site/hifi/data-sources/elexon.html` — everything except the typography line (chunk 1 covers that): viewport fix (`width=1280 → width=device-width, initial-scale=1`), `LAST FETCH → TIMEZONE` swap, stat-card overhaul (categories + settlement-runs replace fetch-success + median-freshness), `Live · fuelhh → Snapshot · fuelhh` framing, `snapshot-note` chip added, "Right now" → "Sample window" metric-card rewrite, footer `SP 28 · 14:02 UTC → silver.fuelhh`, full `HEALTH` section deletion.
  - `site/hifi/index.html` — everything except typography (chunk 1) and pillar-status removal (chunk 2): hero copy rewrite (`European energy markets, tidied` → `A pipeline and catalogue for UK & European energy data`), removal of the `wip-bar` section.
  - `site/hifi/data-sources/elexon/fuelhh.html` viewport-fix line (the other lines in fuelhh's diff are chunk 1 typography + chunk 3 honesty edits).
  - Rationale: zero work lost, working tree truly clean after Phase 0; the alternative (revert and re-do in proper phases) violates Phase 0 Success Criterion 1 (`zero modified files`) and risks lost work via stash drop. The alternative (split into >4 commits) was rejected because the user wants to keep the recipe at 4 chunks.

- **D-03:** Chunks 5 and 6 are repo-hygiene commits (separate from the 4 cleanup chunks), not part of the "4 logical chunks" the ROADMAP success criterion names:
  - **Chunk 5 (`chore:`):** `.gitattributes` + `.gitignore` entries bundled into one commit. `.gitattributes` carries `text eol=lf` rules for `*.html`, `*.css`, `*.js`, `*.json`, `*.py`, `*.md` (planner finalizes exact extension list — `*.yml`/`*.yaml`/`*.toml` are candidates). `.gitignore` adds `.claude/` and `.codex-assessment-shots/`.
  - **Chunk 6 (`chore:`):** `chore: renormalize line endings after .gitattributes` — runs `git add --renormalize .` after chunk 5 lands and commits whatever Git produces. Cleanest separation: history shows exactly which files the new rules touched.
  - Total Phase 0 commit count = **6** (not 4). The ROADMAP §0 Success Criterion 1 reads "4 commits titled per the four logical chunks" — that criterion was written before this discussion and should be read as "4 cleanup chunks + repo-hygiene commits as needed." Planner may update the ROADMAP wording to remove the ambiguity, OR keep it and let the verifier read it generously.

### Landing on main

- **D-04:** All 6 Phase 0 commits stack on top of the existing `docs/codebase-map` branch (currently 7 `.planning/`-only commits ahead of `main`). **No new branch.** One PR (`docs/codebase-map → main`) contains all 13 commits (7 planning + 6 cleanup). Merge strategy = "Create a merge commit" — preserve all 13 commits in `main`'s history. NOT "Squash" (would defeat the entire point of the 4-chunk split). NOT "Rebase + merge" either (SHAs would mismatch the local branch). The merge commit on `main` makes `bisect` work at concern-granularity post-merge. GitHub Pages (`.github/workflows/deploy.yml`, push-to-`main` trigger) catches up to working tree the moment the merge lands.

### Untracked files policy

- **D-05:** `.claude/settings.local.json` and `.codex-assessment-shots/*.png` (4 screenshots) get added to `.gitignore` as part of chunk 5. After Phase 0, `git status` should show zero modified files AND zero untracked files. The `.codex-assessment-shots/` images were considered as "portfolio behind-the-scenes content" but rejected — they're tooling artefacts, not portfolio content.

### Claude's Discretion

- Exact wording of conventional-commit messages (chunks 1–6) — planner/executor picks. Constraint: each message follows `<type>: <one-line summary>` per `CLAUDE.md`. Suggested types: `refactor:` (chunk 1), `chore:` (chunk 2), `docs:` (chunks 3, 4 — both are documentation honesty), `chore:` (chunks 5, 6).
- Exact `.gitattributes` content beyond the `text eol=lf` rules already locked. Planner reads `https://git-scm.com/docs/gitattributes` and picks the minimal set covering the file types in this repo. Blanket `* text=auto eol=lf` is acceptable IF the planner has confidence it won't normalize binary files (current binaries: PNGs in `site/hifi/`, presumably none in repo root — `.codex-assessment-shots/` PNGs are about to be gitignored).
- PR title and body wording. Suggested: `chore(phase-0): commit in-flight refactor + repo hygiene` with body listing the 6 commits.
- Whether to update ROADMAP §0 Success Criterion 1 to say "6 commits" explicitly, or leave it at "4 commits titled per the four logical chunks" with a note that repo-hygiene commits don't count. Planner decides; both are defensible.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and intent
- `.planning/ROADMAP.md` § "Phase 0: Commit in-flight refactor" — goal, dependencies, REQ-IDs (HYG-01, HYG-02), 3 success criteria
- `.planning/REQUIREMENTS.md` § "Repo hygiene (HYG)" — the 2 REQ-IDs in detail: HYG-01 (4 logical commits, push), HYG-02 (`.gitattributes` with `text eol=lf` for `.html`, `.css`, `.js`, `.json`, `.py`)
- `.planning/PROJECT.md` § "Active" → "Bug & a11y fallout" → bullet "Finish & commit the in-flight refactor" — original project-level framing

### Pitfall and concern context
- `.planning/research/PITFALLS.md` § "Pitfall 0: Compounding cleanup on top of the uncommitted in-flight refactor" — the **load-bearing** rationale for this phase; defines the 4-chunk recipe and warns against `git reset --hard`/stash-drop scenarios
- `.planning/codebase/CONCERNS.md` § "In-Flight Refactor (Uncommitted)" — enumerates the 4 chunks of detected refactor pattern and the `.gitattributes`/LF-CRLF problem. Note count discrepancy: CONCERNS says 26 files; actual `git status` is 27 (`models/demand-forecast.html` is the +1)

### Working agreements (override defaults)
- `CLAUDE.md` (project root) § "Working agreements" — Conventional Commits required; one concern per commit; never commit to `main`
- `C:\Users\Bobbo\.claude\CLAUDE.md` § "Workflow" — Conventional Commits enumerated (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`, `docs:`)

### Source-of-truth files
- `site/hifi/data-sources/elexon.html` — chunk 4's biggest single-file diff (92 line changes; full honesty pivot + HEALTH section deletion + viewport fix)
- `site/hifi/data-sources/elexon/fuelhh.html` — chunk 3's only file (25 line changes; LAST FETCH → PRIMARY KEY, median lag → resolution, Live chart → Snapshot chart, viewport fix bleeds into chunk 4)
- `site/hifi/index.html` — split across chunks 1, 2, 4 (33 line changes total; typography + pillar-status + hero rewrite + WIP-bar removal)

### Deploy contract
- `.github/workflows/deploy.yml` — GitHub Pages deploy on push to `main`; PRs don't trigger deploy; merge into `main` is the trigger. Phase 0 PR merge is what realigns Pages with working tree.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Pre-existing `.gitignore`** (Python-build patterns: `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, `build/`, `.idea/`). Phase 0 appends two entries (`.claude/`, `.codex-assessment-shots/`); does not rewrite.
- **`docs/codebase-map` branch state**: 7 planning commits ahead of `main`, all `.planning/`-only. Phase 0 cleanup commits stack on top; one PR merges all 13 commits.
- **Initial commit `351c580`**: the baseline the ROADMAP success criterion #1 references when it says "git log --oneline since `351c580` shows 4 commits". Planner can use this commit as the verification baseline. (Note: 7 planning commits have landed between `351c580` and `HEAD` on `docs/codebase-map`. Verifier should compare against the merge-base or against pre-cleanup state, not against `351c580` literally.)

### Established Patterns
- **Conventional Commits** already in use — see `git log --oneline | head -10`: `docs:`, `chore:`, `feat:` prefixes throughout. The 4 cleanup chunks must follow.
- **Cross-platform line endings** problem — `git diff HEAD` emits 25+ `warning: in the working copy of '...', LF will be replaced by CRLF the next time Git touches it` lines. `.gitattributes` with `text eol=lf` is the canonical Git solution; documented in `https://git-scm.com/docs/gitattributes`.
- **No CI on PR open** — `.github/workflows/deploy.yml` triggers only on push to `main`. So PR merges land + deploy; no pre-merge build to wait for.

### Integration Points
- Phase 1 (MOB-01) inherits a working tree where `fuelhh.html` and `elexon.html` already have the correct viewport (fixed in chunk 4). The Phase 1 planner should NOT trust the "23 broken pages" number in `PROJECT.md` or `CONCERNS.md` (those reflect pre-refactor state and have minor count inconsistencies). Instead: run `git grep width=1280 site/hifi` post-merge to get the ground-truth file list. As of 2026-05-17 working tree, that grep returns **22** files (`site/hifi/data-sources.html` plus the 21 elexon dataset pages that aren't `fuelhh.html`).
- Phase 5 (HON-01) inherits a working tree where the `elexon.html` hub honesty pivot is already complete (chunk 4) and the `index.html` WIP-bar is gone + hero is rewritten. Phase 5 still owns: the other 5 `chip live` surfaces (footer "last sync" in `site.js`, per-page `chip live` chrome on the dataset pages that weren't `fuelhh`, related-card live chips, etc.). Plan-phase for Phase 5 must read this CONTEXT and adjust the grep checklist's denominator.
- Phase 5's existing `data-sources/elexon.html`-as-target reference still works, but the diff Phase 5 produces is now smaller.

</code_context>

<specifics>
## Specific Ideas

- **Merge strategy = "Create a merge commit"** explicitly (GitHub UI option). User rejected "Squash" and "Rebase + merge".
- **Chunk 4 is one commit**, not split. The user rejected "Split into more commits" as Option B in the chunk 4 discussion.
- **`.gitattributes` extension list**: the explicit list from `.planning/research/PITFALLS.md § Pitfall 0` is `*.html text eol=lf` plus the same for `*.css`, `*.js`, `*.json`, `*.py`. Planner's discretion to extend with `*.md`, `*.yml`/`*.yaml`, `*.toml` per repo content audit; or to use blanket `* text=auto eol=lf` if confident no binaries get normalized.
- **Renormalization is a separate (6th) commit**, not bundled into the `.gitattributes` commit. User explicitly rejected the bundled option.
- **`.codex-assessment-shots/` PNGs are gitignored**, not committed. User explicitly rejected the "commit them as portfolio behind-the-scenes" option.

</specifics>

<deferred>
## Deferred Ideas

- **Updating ROADMAP §0 Success Criterion 1 wording** to acknowledge the 6-commit total (vs the originally-written 4). Planner decides — both "update the criterion" and "leave it and have the verifier read generously" are valid paths.
- **`* text=auto eol=lf` blanket rule** for `.gitattributes` vs explicit per-extension. Planner picks based on a quick audit of repo content.
- **Whether to bump `.github/workflows/deploy.yml`** to add a structural check before `upload-pages-artifact@v3` (e.g. an `htmlhint` smoke test). That's Phase 6 (CI-01); explicitly out of scope here.
- **Author photos / CV link / contact details** — out of scope per `PROJECT.md § Out of Scope`. Came up only as a hypothetical "portfolio behind-the-scenes" framing during the .codex-assessment-shots discussion; user explicitly rejected that direction.

</deferred>

---

*Phase: 0-commit-in-flight-refactor*
*Context gathered: 2026-05-17*
