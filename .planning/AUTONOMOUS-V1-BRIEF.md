# V1 Milestone Autonomous Execution Brief

**Created:** 2026-05-17 (executes 2026-05-18+)
**Type:** Deep autonomous execution, NO human input mid-run, NO checkpoints
**Audience:** Fresh Claude Code instance with zero prior context
**Estimated runtime:** Multi-hour to multi-session; design for context resilience

---

## Mission

Execute the entire **v1 cleanup milestone (Phases 0–6, 50 REQ-IDs)** end-to-end autonomously. The user is unavailable for the entire run and will review the finished site at the end. You must make every decision yourself using the planning artifacts as your source of authority. **You may NOT ask the user any questions; if `AskUserQuestion` is your instinct, you've misread the brief.**

The deliverable is a deployed v1 site on GitHub Pages that satisfies all 21 success criteria across the 7 phases in `.planning/ROADMAP.md`.

---

## Critical authorizations (explicit user overrides)

The following normal-default behaviors are **explicitly waived** for this run:

| Default | Override for this run | Source |
|---------|----------------------|--------|
| "Never commit to main — feature branches only" (`CLAUDE.md`) | **You are authorized to merge PRs into main autonomously** using `gh pr merge <branch> --merge` (create-merge-commit strategy). User has waived this gate for v1 execution. | User instruction 2026-05-17 |
| Plan-phase is interactive (`gsd-plan-phase` asks `AskUserQuestion`) | **Skip the `/gsd-plan-phase` slash command entirely** for Phases 1–6. Plan inline based on the ROADMAP + REQUIREMENTS + research artifacts. | This brief |
| Plan-checker iteration loops | **Skip them.** Trust the inline plan and execute. Verify only against ROADMAP success criteria. | This brief |
| GSD checkpoint:human-action tasks | **Treat as `gate="none"`.** Phase 0 Task 9 has already been modified for this. For any other checkpoint task in any phase, execute autonomously using the CLI equivalent of the manual instructions. | This brief |
| `AskUserQuestion` to clarify scope | **NEVER USE.** If ambiguous, decide using the "Decision-making framework" below and document your choice in the relevant commit message. | This brief |

If you have a strong instinct to pause for user input, **resist it.** Document the decision and continue.

---

## Context

### What gridflow-front-end is

Static documentation site for the `gridflow` ETL pipeline (UK/EU energy market data). Editorial-quiet portfolio aimed at full-stack data-science recruiters in energy trading. **Not a product** — no fake-live indicators, no SaaS chrome, no dashboard framing.

### Repos involved

- **This repo** (you are here): `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\`
- **Vault** (read-only; Phase 3 reads vault `.md` files): `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`
- **Gridflow main repo** (read-only; for schema cross-references): `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\`

### Locked decisions (do NOT relitigate)

| # | Decision | Source |
|---|----------|--------|
| 1 | Templating: Python + Jinja2 + `gridflow-build` CLI; Jinja2 in `[build]` extras; runtime `gridflow-serve` stays stdlib-only | `.planning/PROJECT.md` |
| 2 | Elexon scope: 33 datasets | `.planning/PROJECT.md` |
| 3 | Vault → site direction | `.planning/PROJECT.md` |
| 4 | ENTSO-E cross-vendor proof: Generation by PSR type | `.planning/PROJECT.md` |
| 5 | Editorial aesthetic: cream-forest + Fraunces + Inter + JetBrains Mono | `.planning/PROJECT.md` |
| 6 | Kill all "live" framing site-wide | `.planning/PROJECT.md` |
| 7 | Recruiter-first audience: full-stack DS in energy trading | `.planning/PROJECT.md` |
| 8 | Core value: domain depth | `.planning/PROJECT.md` |

---

## Required reading (read ALL of these before starting Phase 0)

You MUST read each of these in full before beginning execution. Read them in parallel where possible (single message, multiple `Read` calls).

### Project-level artifacts
1. `CLAUDE.md` (repo root) — working agreements, SoT hierarchy, anti-goals, tech stack
2. `.planning/PROJECT.md` — full project context, key decisions
3. `.planning/REQUIREMENTS.md` — 50 REQ-IDs across 11 categories with traceability to phases
4. `.planning/ROADMAP.md` — 7 phases, dependencies, per-phase success criteria
5. `.planning/STATE.md` — current state; Phase 0 marked "Ready to execute"
6. `.planning/config.json` — workflow configuration

### Research artifacts (load-bearing for Phases 3–5)
7. `.planning/research/SUMMARY.md` — synthesized findings
8. `.planning/research/STACK.md` — Stack recommendation (Jinja2 build script)
9. `.planning/research/FEATURES.md` — dataset page anatomy contract
10. `.planning/research/ARCHITECTURE.md` — build mechanism design
11. `.planning/research/PITFALLS.md` — load-bearing risks (especially Pitfall 0, 1, 2, 6, 9, 10)

### Codebase intel
12. `.planning/codebase/CONCERNS.md` — uncommitted refactor inventory + structural issues
13. `.planning/codebase/CONVENTIONS.md` — code conventions to follow
14. `.planning/codebase/INTEGRATIONS.md` — cross-repo touch points

### Phase 0 specifics (the only phase with a full PLAN.md)
15. `.planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md` — Phase 0 locked decisions D-01 through D-05
16. `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md` — 11-task execution plan (Phase 0)

---

## Execution plan

### Pre-flight (do once, before Phase 0)

1. Read all 16 artifacts above (parallel Read calls)
2. Verify cross-repo paths are accessible:
   ```bash
   ls "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/" | wc -l    # expect ~33
   ls "C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/"                          # expect Pydantic .py files
   ```
   If either path is inaccessible, write `STUCK.md` (see "Error handling" below) and stop. Do not proceed to Phase 3 without verified vault access.
3. Verify GitHub CLI is authenticated:
   ```bash
   gh auth status
   ```
4. Confirm current branch is `docs/codebase-map` (per STATE.md):
   ```bash
   git branch --show-current
   ```

### Phase 0 — Execute existing PLAN.md

Phase 0 has a complete 11-task PLAN.md. Execute it task-by-task in order:

```
Read .planning/phases/00-commit-in-flight-refactor/00-PLAN.md task definitions
For each task in order (Task 0 → Task 10):
  - Read the <action> section
  - Execute each step
  - Run <verify><automated> check
  - Confirm <done> criteria met
  - Continue to next task
```

Task 9 is the autonomous PR merge (already modified from `gate="blocking"` to `gate="none"`). Task 10 verifies GitHub Pages deployed correctly.

**Exit Phase 0 only when:** `git status` shows clean working tree, `git log origin/main` shows the merge commit, GitHub Pages serves the post-Phase-0 site (verified by curl checks in Task 10).

### Phases 1–6 — Plan inline + execute

For Phases 1 through 6, **NO PLAN.md exists yet.** You must plan inline (in your head) by:

1. Reading the phase entry in `.planning/ROADMAP.md` (goal, dependencies, REQ-IDs, success criteria)
2. Reading each REQ-ID listed for that phase in `.planning/REQUIREMENTS.md`
3. Reading any phase-relevant sections of `research/` and `codebase/`
4. Drafting a TodoWrite list of concrete steps
5. Executing them
6. Committing per Conventional Commits (one concern per commit)
7. Opening a feature branch + PR + autonomous merge
8. Verifying every ROADMAP success criterion is TRUE before moving on

**Use TodoWrite aggressively** — it's your scratchpad for each phase's inline plan.

---

## Per-phase guidance

### Phase 1 — Trivial bug fixes (parallelizable with Phase 2)

**Branch:** `chore/phase-1-trivial-fixes` (from `main` post-Phase-0 merge)

**REQ-IDs:** MOB-01, HON-04, A11Y-06

**Concrete steps:**
1. **MOB-01 — Viewport fix:** Run `git grep -l "width=1280" site/hifi/` to get the file list (should be ~22 files after Phase 0 fixed 2). Replace `width=1280` with `width=device-width, initial-scale=1` in every match. Commit as `fix(mobile): correct viewport on N pages`.
2. **HON-04 — LICENSE file:** Read PROJECT.md for the license decision; if undecided, **default to MIT** (most permissive, lowest friction for portfolio). Add `LICENSE` at repo root. Grep for `MIT|Apache|GPL` across `site/hifi/` and `src/` and align any contradictory mentions. Commit as `docs(license): add LICENSE file and align inline strings`.
3. **A11Y-06 — `rel="noopener"`:** Grep `target="_blank"` across `site/hifi/`. Find any without `rel="noopener"` (CONCERNS.md notes ~2 in `architecture.html` and `data-sources/elexon.html`). Add `rel="noopener"` to each. Commit as `fix(a11y): add rel="noopener" to external target=_blank links`.

PR + merge after all 3 commits land.

**Success gate:** All 3 ROADMAP §1 success criteria TRUE (grep verifications).

### Phase 2 — Shared CSS/JS extraction (parallelizable with Phase 1)

**Branch:** `refactor/phase-2-shared-assets`

**REQ-IDs:** REF-01, REF-02, REF-03, A11Y-05

**Concrete steps:**
1. Identify the duplicated `<style>` block on dataset pages (`site/hifi/data-sources/elexon/*.html`). It's the ~30-line block under a `/* dataset pages */` comment per CONCERNS.md.
2. Extract to `site/hifi/assets/theme.css` under a new `/* dataset pages */` section. Preserve `.fuel-grid` rules in `fuelhh.html` only (they're page-specific).
3. Remove the inline `<style>` block from each dataset page.
4. Identify per-page `setTab(...)` inline declarations and `onclick="setTab(...)"` handlers. Migrate to the existing `[data-tabs]` convention read by `site.js`.
5. Identify inline scroll-spy IIFEs. Consolidate into one `IntersectionObserver` in `site.js`, gated by `.sidebar a[href^="#"]` presence.
6. Fix the sidebar inactive-item hover bug: remove inline `color:var(--ink-faint)` from dataset pages; replace with a CSS class that lets `:hover` override.

Commit per file group, then PR + merge.

**Success gate:** All 4 ROADMAP §2 success criteria TRUE.

### Phase 3 — Build mechanism + Elexon dataset depth

**This is the most substantial phase. ~40% of total REQ-IDs (20 of 50).**

**Branch:** `feat/phase-3-build-mechanism`

**REQ-IDs:** BUILD-01–08, VAULT-01–04, ELX-01–08

**Concrete steps:**

#### Step A — Build script foundation
1. Add `[build]` extras to `pyproject.toml` with `jinja2>=3.1,<4.0`. Keep `[project]` runtime deps stdlib-only.
2. Create `src/gridflow_front_end/build.py` exposing `gridflow-build` console script in `[project.scripts]`.
3. Build CLI accepts `--vault-path` arg (default `$GRIDFLOW_VAULT_PATH` env var, fallback to `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/`).
4. Use `uv` for all dep management (`uv pip install -e ".[build]"` per user preferences in `~/.claude/CLAUDE.md`).

#### Step B — Templates
1. Create `templates/` at repo root (NOT under `site/hifi/`).
2. Author `templates/dataset.html.j2` — the 7-section dataset page template (hero · metadata grid · stats strip · sticky sidebar · overview · snapshot chart · schema · sample · API tabs · caveats · related). Use the existing `fuelhh.html` as the structural reference.
3. Author `templates/vendor-hub.html.j2` — vendor catalog page template.
4. Author `templates/vendor-coming-soon.html.j2` — visually-distinct stub template per Pitfall 9 (no sidebar, no chart container, single-screen layout, "Planned · F<n>" stage chip).
5. Author `templates/_partials/*.j2` for the head, top-nav, footer (re-use the runtime injection contract from `site.js`).

#### Step C — Vault reader
1. Read `<vault>/30-vendors/elexon/datasets/*.md` (33 files).
2. Parse YAML frontmatter + body sections into a Python dataclass (`DatasetDoc`).
3. Cross-reference each dataset's Pydantic class name against `<gridflow>/src/gridflow/schemas/elexon.py`; **fail loudly if a class name doesn't resolve** (this is the drift-canary even pre-v2).

#### Step D — Idempotent generation
1. Generate the 6 "byte-equivalent" pages first (`fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`). Diff against the pre-Phase-3 committed files. If diffs are non-trivial, investigate the template until they match (or document the intentional diffs in a `BUILD-DIFFS.md`).
2. Generate the remaining 27 Elexon dataset pages.
3. Generate `site/hifi/data-sources/elexon.html` from `vendor-hub.html.j2` over `site/hifi/data/elexon.json`.
4. Add generated paths to `.gitignore` under `site/hifi/data-sources/elexon/` (per ELX-07 / BUILD-08).
5. Update `.github/workflows/deploy.yml` to run `gridflow-build` before `actions/upload-pages-artifact@v3`.

#### Step E — Count reconciliation
1. Update `site/hifi/data/elexon.json` to show 33 datasets.
2. Update the index.html stat strip to show "33 Elexon datasets".
3. Footer build-version string: drop. Replace with documentation-site framing.
4. Grep for `\b22\b|\b25\b|\b28\b` in dataset-count-adjacent contexts and replace.

#### Step F — Per-dataset enrichment
1. Every dataset page must show:
   - `verified-against-vendor-docs: YYYY-MM-DD` micro-line linking to the specific Elexon BMRS doc page (read the URL from vault frontmatter)
   - Pydantic class name reference as inline `<code>` (e.g., `gridflow/schemas/elexon.py · ElexonFuelHH`)
2. All 6 sidebar anchors (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) resolve to real `<section id>` on each page (per Phase 3 SC#2 — Pitfall 2 prevention).

Commit in logical groups (script foundation, templates, vault reader, generation, reconciliation, enrichment). PR + merge.

**Success gate:** All 5 ROADMAP §3 success criteria TRUE, including:
- Running `gridflow-build` twice produces zero diff (idempotence)
- All 33 dataset pages render with 6 resolving sidebar anchors
- Number `33` appears in footer, index stat strip, elexon.json, elexon hub catalog — no 22/25/28 anywhere

### Phase 4 — Cross-vendor proof + dead-link real fix

**Branch:** `feat/phase-4-cross-vendor`

**REQ-IDs:** VEND-01–05, PAGE-03

**Concrete steps:**
1. Author vault content for ENTSO-E "Generation by PSR type" if it doesn't already exist (check `<vault>/30-vendors/entsoe/datasets/` first).
2. Add `site/hifi/data/entsoe.json` manifest (vendor metadata).
3. Run `gridflow-build` with ENTSO-E support; generates `site/hifi/data-sources/entsoe.html` and `site/hifi/data-sources/entsoe/<psr-slug>.html`.
4. Generate 5 coming-soon stubs (ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO) via `vendor-coming-soon.html.j2`. Each gets a unique "Planned · F<n>" stage chip (use F6, F7, F8, F9, F10 sequentially — these are not load-bearing labels).
5. Grep `site/hifi/data-sources.html` for `href="#"`. Replace every match with a real link to either a vendor hub or a coming-soon stub. Zero `href="#"` remaining post-phase.

PR + merge.

**Success gate:** All 3 ROADMAP §4 success criteria TRUE.

### Phase 5 — Honesty sweep + a11y + mobile CSS + main-page polish

**Branch:** `chore/phase-5-honesty-a11y-mobile`

**REQ-IDs:** HON-01–03, MOB-02–03, A11Y-01–04, PAGE-01, PAGE-02, PAGE-04

**Concrete steps:**

#### Step A — Honesty sweep (atomic; Pitfall 1 prevention)
Run the grep checklist in ONE pass. Every match must be eliminated in this phase:
- `chip live` → remove the class and the chip
- `class="dot live"` → remove
- `LAST FETCH` → remove
- `last sync` → remove
- `last fetch` → remove
- ` min ago` / ` s ago` → remove
- `live · ` → remove
- `Live chart` → "Illustrative snapshot"
Each chart container instead carries an explicit "Illustrative snapshot" chip.

#### Step B — Mobile CSS
Add mobile breakpoints (`@media (max-width: 480px)` and `@media (max-width: 720px)`) to `theme.css`. Every page must render mobile-functional: no horizontal scroll, sidebar collapses, hero stacks vertically, stats strip reflows, mobile menu toggle reaches every page.

#### Step C — A11y
- Every page wraps primary content in `<main>`
- Top-nav `<nav>` gets `aria-label="Primary navigation"`; sidebar `<nav>` gets `aria-label="Page sections"` (or similar distinguishing labels)
- Active nav link gets `aria-current="page"`
- Active sidebar link gets `aria-current="location"` (or `="true"`)
- Decorative icons (arrows, dots, hamburger, chip-dots) get `aria-hidden="true"`

#### Step D — Main page polish
- `site/hifi/index.html`: editorial/quiet voice, no fake-live chrome, no "Shipping" badges, "33 Elexon datasets" in stat strip
- `site/hifi/architecture.html`: polish pass on writing + diagrams (structure stays)
- `site/hifi/data-sources.html`: complete the honest framing pivot

**Editorial taste decisions:** Defer to existing copy patterns. When in doubt, make the change MORE conservative (smaller diff, more aligned with existing voice). The user has locked the editorial aesthetic in PROJECT.md — your job is to align with it, not reinvent it.

PR + merge.

**Success gate:** All 4 ROADMAP §5 success criteria TRUE.

### Phase 6 — CI validation

**Branch:** `ci/phase-6-validation`

**REQ-IDs:** CI-01, CI-02, CI-03

**Concrete steps:**
1. Add `htmlhint` step to `.github/workflows/deploy.yml` before `upload-pages-artifact@v3`. Configure `.htmlhintrc` for the structural-HTML class of issues (broken stubs, unclosed tags).
2. Add `lychee` step (link checker). Use `lychee-action@v2` or similar. Configure to check internal links only (skip external to avoid flakiness).
3. Add build-idempotence smoke test: run `gridflow-build` twice, fail if `git diff` on output dir is non-empty.

PR + merge.

**Success gate:** All 3 ROADMAP §6 success criteria TRUE. CI run on the merge produces green deploy.

---

## Decision-making framework

When you encounter a decision that isn't pre-locked in PROJECT.md / ROADMAP.md / CONTEXT files:

1. **Defer to existing patterns first.** If similar code/copy exists, match it.
2. **Defer to the locked aesthetic** (editorial-quiet, cream-forest + Fraunces, no SaaS chrome).
3. **Prefer smaller diffs.** Conservative changes < ambitious refactors.
4. **Prefer reversible decisions.** When stuck between options, pick the one that's easier to change later.
5. **Document the decision in the relevant commit message.** "Why" goes in the commit body so the user can review during end-of-milestone audit.
6. **If you're truly stuck** (can't pick a path; would normally call AskUserQuestion): write to `STUCK.md` (see Error handling) — do NOT block on a question.

---

## Error handling

### Test/verification failure within a phase
- Investigate root cause. Do NOT bypass with `--no-verify` or skip tests.
- If a fix is obvious: apply it, commit, continue.
- If not obvious: spend reasonable time (~20 min equivalent) debugging. If still stuck after that, escalate via `STUCK.md`.

### CI failure on a merged PR
- Investigate the failure log via `gh run view`.
- If the fix is < 10 lines: open a `fix/<short-desc>` branch, fix, PR, merge.
- If larger: escalate via `STUCK.md`.

### `STUCK.md` protocol
If genuinely blocked and unable to proceed without user input:
1. Write `.planning/STUCK.md` with:
   - Current phase and task
   - What you tried
   - Why you're stuck
   - 2-3 plausible paths forward + your recommendation
   - Exact resume instructions for when user returns
2. Commit `STUCK.md` on whatever branch you're on
3. Stop. Print a stdout summary saying "STUCK — see `.planning/STUCK.md`".

`STUCK.md` is your **only** escape hatch from the no-interaction rule. Use it sparingly — once per run at most under normal circumstances.

### Cross-repo access failure
If vault or gridflow paths become inaccessible mid-run, treat as STUCK.

---

## Context resilience

This run will produce thousands of tool calls. To survive long context:

1. **Use TodoWrite as your durable scratchpad.** Each phase: write the full task list at the start, mark items complete as you go. If your context window compresses, the TodoWrite state survives.
2. **Commit frequently.** Each logical chunk is a separate commit. Git history is your second durable scratchpad.
3. **Update `.planning/STATE.md` at every phase boundary.** This is the resume point if you crash. Format:
   ```
   ## Current Position
   **Phase:** N — <name>
   **Status:** Complete | In progress at <task>
   **Last commit:** <sha>
   **Next:** <concrete next step>
   ```
4. **Spawn subagents (general-purpose, Explore) for parallelizable read-heavy work** to keep your main context focused on decisions and writes. Especially useful in Phase 3 when reading 33 vault `.md` files.
5. **Use parallel tool calls aggressively.** Independent reads, independent greps — batch them.

---

## Termination

After Phase 6 success criteria are TRUE and the green deploy has shipped to GitHub Pages:

1. Update `.planning/STATE.md` to show milestone complete:
   ```
   **Status:** v1 milestone complete · 7/7 phases · 50/50 REQ-IDs
   ```
2. Write `.planning/MILESTONE-COMPLETE.md` with:
   - Phases completed with commit SHA ranges
   - Success criteria verification (one line per SC, each TRUE)
   - Deployed site URL
   - Any decisions made via the Decision-making framework (so user can review)
   - Any deviations from the plan (and why)
   - Any deferred items that should land in v2
3. Commit on `main` (or last PR's branch + merge): `docs(milestone): v1 cleanup complete`
4. Print stdout summary: phase count, REQ-ID count, deployed URL, total commit count, key decisions, link to MILESTONE-COMPLETE.md
5. **STOP.** Do NOT start v2. Do NOT trigger drift-detection research (that's a separate brief at `.planning/research/post-v1/drift-detection/RESEARCH-BRIEF.md` and will be initiated separately).

---

## Hard constraints

- **NO `AskUserQuestion` calls.** Zero. Document decisions in commits or `STUCK.md`.
- **NO `--no-verify` or hook-skipping** on commits/pushes.
- **NO destructive git operations** (`reset --hard`, `push --force`, branch deletion of unmerged work) without first investigating root cause.
- **NO scope creep beyond the 50 REQ-IDs.** If you see something worth doing that isn't a REQ-ID, use `mcp__ccd_session__spawn_task` to flag it for a separate session and continue.
- **NO modifications to the research brief or its outputs.** `.planning/research/post-v1/` is owned by the separate research run.
- **NO touching `quant-vault` or `gridflow` repos.** Read-only across both.
- **YES to autonomous PR merges** (explicitly authorized — see "Critical authorizations" above).
- **YES to inline planning** without `/gsd-plan-phase` for Phases 1–6.
- **YES to skipping plan-checker loops, verifier loops, and UI-checker loops.** Verify only against ROADMAP success criteria.
- **YES to TodoWrite + STATE.md updates as durable progress markers.**

---

## What "done" looks like

- 7 phases shipped (Phase 0 already partially planned; 1–6 planned inline)
- 50/50 REQ-IDs delivered (verify each via the ROADMAP success criteria)
- GitHub Pages deploy green; deployed site matches working tree
- `git status` clean on `main` at end
- `.planning/MILESTONE-COMPLETE.md` exists and is accurate
- `.planning/STATE.md` shows milestone complete
- No `STUCK.md` (or if present, it's the one and only blocker)
- Stdout summary printed
- User can return, read `MILESTONE-COMPLETE.md`, open the deployed URL, and verify the recruiter-test goal is met (or surface the gap)

---

*End of brief. Begin pre-flight reading immediately upon receiving this prompt.*
