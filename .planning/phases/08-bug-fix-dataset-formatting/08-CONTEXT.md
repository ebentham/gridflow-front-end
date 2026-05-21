# Phase 8: Dataset-page formatting bug fix - Context

**Gathered:** 2026-05-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Root-cause and fix the top-of-page (hero) formatting bug confirmed on `fuelhh.html` before scaling 129 new pages off the same template. Whatever the offending location (Jinja2 template / shared `theme.css` / vault `.md` frontmatter / build-script transform), it gets named and corrected in **one place**; the fix propagates via `gridflow-build` to all 34 existing pages (33 Elexon + 1 ENTSO-E) with zero regression on the v1 honesty / a11y / mobile guarantees.

This phase is gating for the content phases (9 — ENTSO-E full coverage, 10 — four-vendor batch): shipping 163 pages off a broken template multiplies the defect by 163×. Independent of Phase 7 (Reconciliation) per ADR-0001 D-03 — the bug is in the rendering layer (Jinja2 template / `theme.css` / build script), not the Vault content layer (Phase 7's surface).

**In scope:**
- Confirm or correct the provisional diagnosis (see `<specifics>` below)
- Apply the fix in the single named location
- Run `gridflow-build` and re-render all 34 existing pages
- User-verified spot-check (visual) per BUG-02 success criterion
- v1 CI gates (`htmlhint`, `lychee --offline --include-fragments`, `gridflow-build --check` idempotence) all green on the post-fix output (BUG-03)

**Out of scope:**
- Any new visual design / aesthetic change (cream + Fraunces stays; "no new visual identity" per PROJECT.md Out of Scope)
- Visual-regression infrastructure (snapshot testing, baseline screenshots) — v2 explicitly skips per PROJECT.md scope discipline; existing CI gates (`htmlhint` + `lychee` + `gridflow-build --check`) are the structural guard
- `fuelhh` fuel-pill grid restoration — explicit v3 candidate per PROJECT.md Out of Scope
- Per-dataset related-card blurbs — explicit v3 candidate
- Pydantic schema drift closure — explicit v3 candidate
- Template-wide hygiene pass beyond what's required to kill the bug (no opportunistic inline-style extraction, no restructuring of unrelated sections)
- Any Vault content edits — Phase 7's surface, finished 2026-05-19
- Any vendor expansion work — Phases 9 and 10 own that

</domain>

<decisions>
## Implementation Decisions

### Fix-scope discipline

- **D-01:** **Minimal patch only.** The ROADMAP goal explicitly says "the offending location...gets named and corrected in **one place**." If the researcher finds 2+ contributing causes that together produce the same visible bug (e.g., `align-items: end` + `auto`-column expansion at the same template grid), fix the minimum set required to make the visible glitch go away. Do NOT opportunistically extract inline styles to a `.dataset-hero` class, do NOT audit other inline-style blocks, do NOT clean adjacent CSS while we're here.
  - **Why:** Aligns with the user's "the problem is clear" + ROADMAP-quote stance during discuss-phase. Recruiter-portfolio velocity > template hygiene; v1 Phase 2 already did the structural CSS extraction, and Phase 8 is a *bug-fix* phase, not a *refactor* phase. Hygiene work would inflate the PR review surface and risk regression on the 34 shipped pages with no recruiter-visible payoff.
  - **How to apply:** Planner produces a minimal PLAN.md (likely 1 plan, ≤4 tasks). Each task names a specific change (CSS property, template line, vault frontmatter key, build transform) with a one-line justification tying back to the root cause. If a task crosses into refactoring territory, defer to `<deferred>`.

### Verification breadth

- **D-02:** **fuelhh + 1 random Elexon page + ENTSO-E `actual_generation`** on desktop, plus a mobile-breakpoint check at ≤720px and ≤480px on `fuelhh`. The BUG-02 success criterion mandates fuelhh + 1 random; we extend by one ENTSO-E page (the only non-Elexon shipped dataset page) because Phase 9 will scale 48 new ENTSO-E pages off this template — if the fix interacts with ENTSO-E's different schema-table shape, we want to know now. Mobile-breakpoint check enforces the "zero regression on v1 mobile guarantees" constraint in the ROADMAP goal.
  - **Why:** Lean coverage that protects the recruiter-facing surface without ballooning verification time. Three desktop pages × 2 mobile breakpoints = 5 user-eyeball checks total — under 10 minutes. v1 Phase 5 already laid the mobile CSS; this confirms the bug fix doesn't undo it.
  - **How to apply:** Plan includes an explicit user-checkpoint task after `gridflow-build` re-renders: "Open `/data-sources/elexon/fuelhh.html` at desktop, 720px, and 480px viewports; open `/data-sources/elexon/<random>.html` at desktop; open `/data-sources/entsoe/actual_generation.html` at desktop. User confirms no remaining hero glitch and no new mobile regression before plan proceeds." This is `autonomous: false` per the BUG-02 "user-verified" criterion.

### Regression prevention

- **D-03:** **No new structural guard.** Existing v1 CI gates (`htmlhint` + `lychee --offline --include-fragments` + `gridflow-build --check` idempotence) are the regression boundary. The bug class (CSS layout glitch in a hero grid) is not catchable by `htmlhint` (HTML-shape validator) or `lychee` (link checker) or build idempotence — visual-regression infrastructure (snapshot tests, baseline images) is the right tool for that, but it is explicitly v2-out-of-scope (PROJECT.md scope discipline + "no Node toolchain" anti-goal). For v2, the regression boundary is the user-checkpoint in D-02.
  - **Why:** Aligns with v2's strict scope discipline (PROJECT.md Key Decisions row 11 — "no related blurbs, no fuel-pill restoration"; same scope-discipline pattern applies here). Adding screenshot baselines now would commit us to maintaining them across the 129-page expansion in Phases 9/10 — a non-trivial side-quest. The bug, once fixed in the template, doesn't have a recurrence vector other than future template edits — and Phases 9/10 are content/manifest work, not template work.
  - **How to apply:** No new CI workflow files. No new lint rules. No screenshot dirs added. The fix commit includes a brief in-template comment ONLY IF the root cause is non-obvious to a future reader (e.g., `/* DO NOT set align-items: end here — collapses metadata to bottom-right, see commit <sha> */`); inline comments are otherwise discouraged per the user's universal preferences (CLAUDE.md "No comments that restate what the code does — only WHY when non-obvious"). Planner decides if a comment is warranted; default is none.

### Diagnosis-approval gate

- **D-04:** **Light research pass — confirm or refute the provisional diagnosis, then plan.** The provisional diagnosis (see `<specifics>` D-S-01) is strong but unverified. Spawn the researcher with a narrow brief: "Open `templates/dataset.html.j2` lines 1-70 and `site/hifi/assets/theme.css` rules covering `.page-layout`, `.container`, hero-area selectors; confirm that the visible bug in the supplied fuelhh.html screenshot is caused by (a) `align-items: end` on line 18 + (b) `grid-template-columns: 1fr auto` letting the SILVER PATH mono string stretch the right column. Surface any contributing CSS rule I missed." Do NOT spawn full domain research — Phase 8 is a bug fix, not a new feature; the research budget should be ~15% of normal.
  - **Why:** The screenshot + my template scout produced a strong hypothesis but I'm 1 LLM with 1 reading of the codebase. A light researcher pass catches cases where the bug has additional contributing causes (e.g., a media query at a specific breakpoint, a `theme.css` rule overriding the inline style) that would make a one-line fix insufficient. Cost is small (~10 minutes wall, ~3% planner context budget); the downside of skipping is "ship a half-fix that still glitches on some screen widths" — worse than the cost.
  - **How to apply:** Plan-phase invocation should be `/gsd-plan-phase 8 --skip-ui` (no `--skip-research`). The researcher prompt is bounded to the surfaces named above; the planner should NOT fan out to investigate the build script or vault frontmatter unless the researcher explicitly flags one of those as a contributing cause.

### Claude's Discretion

- **Exact filename for the plan(s)** — likely a single `08-01-PLAN.md`; planner picks per project convention (Phase 7 used `07-01..07-04`; v1 used `00-01-PLAN.md`). Single-plan is appropriate since the work is one logical concern.
- **Where the fix lives (template inline vs `theme.css` class)** — default: minimal inline edit at `dataset.html.j2:18` (matches existing pattern — that block already uses inline styles). If the researcher surfaces that the bug bleeds across multiple template files, planner reconsiders. No mandate to extract to a class.
- **Exact CSS values for the fix** — likely `align-items: start;` replacing `align-items: end;`, plus a constraint on the right column to prevent unbounded `auto` expansion (e.g., `max-width: 420px;` on the inner metadata grid, or `min-width: 0;` + `word-break: break-all;` on `.mono.small`, or `grid-template-columns: 1fr 420px;` on the outer grid). Planner picks the smallest change that kills the visible bug across the verification set (D-02).
- **Whether to add a one-line WHY comment near the fix** — planner judges based on whether the root cause is obvious to a future reader; default is none (CLAUDE.md prefers no comments).
- **PR title and commit-message wording** — planner picks; must follow Conventional Commits (`fix(08-01):` prefix per project convention). Should name the offending location in the commit body to satisfy BUG-01 success criterion ("named in writing — commit message or PR body").

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope authority

- `.planning/ROADMAP.md` § "Phase 8: Dataset-page formatting bug fix" — the goal statement quoted in `<domain>` above; the 3 success criteria (named location + spot-check verification + CI green) are the contract.
- `.planning/REQUIREMENTS.md` § "Dataset-page formatting bug (BUG)" — BUG-01, BUG-02, BUG-03 with their acceptance text.
- `.planning/PROJECT.md` § "Key Decisions" — especially row 11 (strict scope discipline) and the editorial-aesthetic / honesty / a11y / mobile guarantees that must not regress.
- `.planning/PROJECT.md` § "Out of Scope" — `fuelhh` fuel-pill grid, related-card blurbs, Pydantic drift, Node SSGs are all explicitly out; do not let scope creep pull them in.

### Cross-phase context (carried forward)

- `.planning/phases/07-reconciliation/07-CONTEXT.md` § "D-03: Per-Vendor gating; bug-fix is independent of Reconciliation" — confirms Phase 8 is independent of Phase 7; bug is in the rendering layer, not the Vault layer.
- `.planning/MILESTONE-COMPLETE.md` — v1 success criteria audit, including the v1 CI gates (`htmlhint`/`lychee`/`gridflow-build --check`) that BUG-03 reuses; the editorial / a11y / mobile guarantees that must hold.

### Files the fix likely touches (researcher MUST read)

- `templates/dataset.html.j2` (lines 1-70 are the hero region — the provisional bug surface). The whole template is ~300 lines; researcher reads the hero region in detail, scans the rest for unrelated touched code.
- `site/hifi/assets/theme.css` — rules covering `.container` (line 106), the hero area (no dedicated class today — inline styles), `.page-layout` (line 691), `.main-content` (line 730), `.stats-strip` (line 277), and the mobile media queries (~line 760+ for ≤720px, ~line 786+ for ≤480px).
- `site/hifi/data-sources/elexon/fuelhh.html` — current rendered output (the broken state in the user's screenshot). Visual reference for verification.
- `site/hifi/data/elexon.json` (manifest for fuelhh's `freq`, `lag`, `rows`) and `vault/elexon/fuelhh.md` (vault frontmatter — `silver_path`, `dedup_key`, etc.) — only relevant if the researcher decides the bug originates in the data layer rather than the template/CSS. Default assumption is no — bug is rendering-only.
- `src/gridflow_front_end/build.py` — only relevant if the researcher finds a build transform corrupting hero data. Default assumption is no — build.py is read-only for Phase 8.

### Working agreements (overrides defaults)

- `CLAUDE.md` (project root) § "Working agreements" — Conventional Commits required (`fix(08-01):` for this phase); one concern per commit; never commit to `main`; never auto-commit unless asked.
- `CLAUDE.md` (project root) § "Tech stack (current — pre-build-script)" and "Tech stack (post-Phase-3)" — confirms the static HTML5 + CSS3 + vanilla JS rendering layer, no transpilation, no module system. Fix must stay within this stack.
- `~/.claude/CLAUDE.md` § "Universal preferences" — no comments unless WHY is non-obvious; no emojis in files; prefer editing existing files over creating new ones.

### Agent-skill protocols (informational)

- `docs/agents/issue-tracker.md` — local-markdown issue tracker convention; not directly used by this phase (no findings to triage), but the canonical place to look if Phase 8's verification surfaces an adjacent issue worth deferring.
- `docs/agents/triage-labels.md` — canonical labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`); used if the researcher surfaces adjacent issues.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **`templates/dataset.html.j2`** — the Jinja2 template that generates all 34 existing dataset pages. The hero block (lines 7-67) is the provisional bug surface. The template uses inline `style="..."` attributes on the hero grid (lines 18, 39) rather than a `.dataset-hero` class — matches the existing pattern from v1 Phase 3. Fix lands here.
- **`site/hifi/assets/theme.css`** — single shared stylesheet (v1 Phase 2 extraction). Hero region is *not* in a dedicated class today; if D-01 (minimal patch) holds, the fix likely stays inline in the template and theme.css is not modified.
- **`gridflow-build` CLI** (`src/gridflow_front_end/build.py`) — re-renders all 34 pages from one template change. v1 Phase 3 already proved the build is idempotent; Phase 8 reuses this. No build.py edits expected.
- **v1 CI gates** in `.github/workflows/deploy.yml` — `htmlhint --config .htmlhintrc`, `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence all run before `actions/upload-pages-artifact@v3`. Phase 8 reuses; no workflow edits expected.

### Established Patterns

- **Inline styles allowed in templates** — `dataset.html.j2` uses inline `style="..."` for layout-specific tuning (hero grid, padding overrides). v1 Phase 2 extracted *duplicated* `<style>` blocks across pages but left page-anatomy-specific inline styles in the template. Phase 8's fix can stay inline; extracting to a class is opportunistic scope per D-01.
- **Conventional Commits with phase prefix** — `fix(08-01): <subject>` matches Phase 7's `fix(07-XX): ...` and v1's `fix(00-01): ...` patterns.
- **No `setTab` / inline scroll-spy** — v1 Phase 2 killed these. Phase 8 must not reintroduce inline page-specific JS.
- **Honest by construction** — `dataset.html.j2` never emits `chip live`, `LAST FETCH`, etc. (v1 HON-01). Phase 8 fix MUST NOT alter this.
- **Editorial aesthetic locked** — cream + forest-green + Fraunces. Fix MUST NOT change palette / font stack / chip styling.

### Integration Points

- **`gridflow-build` regenerates all 34 pages from template edit** — single template change → 34 page rewrites → `gridflow-build --check` confirms idempotence. Standard v1 pipeline; no new integration.
- **GitHub Pages deploys built artifact** — `.github/workflows/deploy.yml` runs `gridflow-build` then `actions/upload-pages-artifact@v3`. Standard v1 pipeline; no new integration.
- **No cross-repo coupling** — Phase 8 touches only `gridflow-front-end`. Vault snapshot under `vault/<vendor>/` is read-only for Phase 8 (Phase 7's surface). Upstream `quant-vault` is untouched. Gridflow main repo is untouched.

</code_context>

<specifics>
## Specific Ideas

### Provisional diagnosis (D-S-01)

From scouting `templates/dataset.html.j2` lines 7-67 + `site/hifi/assets/theme.css` (`--site-max: 1280px`, `--site-pad: 64px`), the hero block has this structure:

```jinja
<div style="display:grid; grid-template-columns: 1fr auto; gap: 48px; align-items: end;">
  <div>  <!-- LEFT col: breadcrumb, eyebrow, title, lede, verified line -->
  <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 0; ... min-width: 340px;">
    <!-- RIGHT col: 6-cell metadata grid (SILVER PATH / API PATH / FREQUENCY / PUBLICATION LAG / VOLUME / PRIMARY KEY) -->
  </div>
</div>
```

**Hypothesised contributing causes (likely both, possibly more):**

1. **`align-items: end`** on the outer grid (line 18) anchors the metadata grid to the **bottom** of the row. The left text column is taller (title + 4-line lede + verified micro-line) than the metadata grid, so the metadata grid floats to the bottom-right while the top-right stays empty — the tall blank rectangle in the user's screenshot.

2. **`grid-template-columns: 1fr auto`** + the SILVER PATH long mono string (e.g., `data/silver/elexon/fuelhh/year=YYYY/month=MM/fuelhh_YYYYMMDD.parquet` rendered in `.mono.small` — no word-break) expands the `auto` column to fit the unwrapped string, squeezing `1fr` (the left column) narrow. With ~1152px content width and ~600-700px stolen by the metadata column, the title column gets ~400-450px, forcing the H1 to wrap "Half-/Hourly/Generation/Outturn by/Fuel Type/(FUELHH)" awkwardly.

**Fix candidates (planner picks the minimum that works, validated by D-04 light research):**

- (a) Change `align-items: end` → `align-items: start` (or remove). Fixes #1; leaves #2 unaddressed — but the metadata grid would then sit top-right (no blank space), and the narrow title column is only awkward not catastrophic. Smallest possible change.
- (b) Change outer grid to `grid-template-columns: 1fr 420px` (fixed metadata column width). Fixes #2 directly; #1 becomes irrelevant because the columns are equal-height-able. More predictable across vendors with varying silver-path lengths.
- (c) Both (a) + (b). Most defensive.
- (d) Other (researcher may surface a `theme.css` media-query interaction or a `min-width` chain I missed).

### Specific behaviours wanted

- **The 6 metadata cells must remain visible and readable.** Don't collapse them, don't truncate, don't `display: none` any cells.
- **The "Illustrative snapshot" chip stays in the top-row of the left column** alongside the eyebrow and frequency chip. Don't move chips into the right column as part of the fix.
- **The `verified-against-vendor-docs:` micro-line stays at the bottom of the left column** below the lede. Don't move it.
- **Mobile breakpoints** (≤720px and ≤480px) must continue to stack the hero vertically (single column). v1 Phase 5 already handles this via `theme.css` media queries; fix must not undo it.
- **Commit-message wording** must name the offending location to satisfy BUG-01 (e.g., `fix(08-01): correct dataset hero alignment — align-items: end at dataset.html.j2:18`).

</specifics>

<deferred>
## Deferred Ideas

### Within the v2 milestone (next phases)

- **Hero-grid CSS extraction to `.dataset-hero` class** — if Phase 9/10 review feedback ever flags the inline-style block as a maintenance pain, extract during a content phase that already touches `theme.css`. Not Phase 8 work per D-01.
- **Adjacent template inline-style audit** — `dataset.html.j2` has several other inline `style="..."` blocks (e.g., on the H1, on section padding). If any of them are similarly fragile, log as `needs-triage` findings under `.planning/issues/` rather than fixing in Phase 8.

### v2.1 / v3 candidates

- **Visual-regression infrastructure (snapshot tests, baseline images)** — explicit v2 anti-scope (PROJECT.md). v3 candidate if recurring layout bugs become a pattern across the 163-page expansion. Tools to consider then: Playwright + percy.io, BackstopJS, reg-suit. Each commits us to a Node toolchain — PROJECT.md anti-goal — so the v3 conversation must justify that tradeoff.
- **Per-vendor longest-silver-path audit + max-width discipline** — if Phase 9 (ENTSO-E) surfaces another auto-column expansion bug with even longer ENTSO-E paths, the fix may be generalised. Not Phase 8 scope.

### Discussion artefacts

- **Multi-question gray-area discussion was condensed** — the user pasted the ROADMAP goal verbatim in response to the multiSelect "which areas to discuss" question, signalling "the ROADMAP IS the decision basis, don't bikeshed." All four candidate gray areas (fix-scope discipline, verification breadth, regression prevention, diagnosis-approval gate) were resolved by Claude with defaults anchored to the ROADMAP success criteria and v2 scope discipline. User can override any of D-01..D-04 by editing this CONTEXT.md before plan-phase.

</deferred>

---

*Phase: 08-bug-fix-dataset-formatting*
*Context gathered: 2026-05-19*
