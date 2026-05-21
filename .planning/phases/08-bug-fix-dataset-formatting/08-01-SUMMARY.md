---
status: superseded
outcome: failed-then-superseded
plan: 08-01-PLAN.md
superseded_by: Phase 8B (Claude-Design hero rewrite)
date: 2026-05-19
---

# Phase 8 / Plan 08-01 — Summary

## Outcome

**Failed.** Two iterations of the locked minimal-patch CSS fix both failed user visual verification at the BUG-02 checkpoint. Root cause turned out to be **structural**, not alignment-based: the Jinja2 template cannot reproduce the editorial quality the user expected, regardless of which `align-items` value the hero grid uses.

Phase 8 is closed as superseded by **Phase 8B (Claude-Design hero rewrite, hybrid authored/templated)** rather than re-planned in place — the original D-01 minimal-patch decision excluded any visual redesign, and two failed minimal patches in a row is signal that the underlying scope was wrong, not that the patches were wrong.

## What was attempted

### Iteration 1 — planner's diagnosis (commit `2884912`)

- **Fix:** `align-items: end` → `align-items: start` at `templates/dataset.html.j2:18`.
- **Theory:** the hero grid's `auto`-sized right column (the metadata card) was bottom-aligning to a much-taller left column, creating a dead rectangle at the top-right.
- **Result:** moved the dead rectangle from top-right to bottom-right. Visual bug still present.

### Iteration 2 — orchestrator's structural attempt (working-tree, never committed)

- **Fix:** three changes in `templates/dataset.html.j2`:
  1. `align-items: start` → `align-items: stretch` (line 18) — let the metadata card grow to match left column height
  2. `grid-template-rows: repeat(3, 1fr)` on the inner 2×3 metadata grid (line 39) — distribute cells across the stretched height
  3. SILVER PATH value: `{{ doc.silver_path or 'silver.' ~ doc.slug }}` → `silver.{{ doc.slug }}` (line 42) — kill the long partitioned path that was wrapping
- **Theory:** the height mismatch between the long left column (5-line H1, full lede, verified line) and the compact right metadata card couldn't be fixed by aligning to start/end; the card needs to span the full height.
- **Result:** mechanically correct (no dead rectangle), but the user's reference design from Claude Design proved that the visible quality gap was about editorial typography (short H1 tagline, accent-italic styling, prose with inline `<code>` chips), not about alignment. The hand-designed reference uses `align-items: end` with a **short** H1 — a layout the template can't produce from vault data without new vault fields.

## Why the minimal-patch approach failed

Two failed iterations on the same locked scope (D-01: minimal patch only, no visual redesign) showed the scope was wrong. The "bug" was diagnosed as alignment because that's the most visible symptom on `fuelhh.html`, but the actual driver is:

1. **Editorial typography is not in the vault.** The template renders `{{ doc.title_line }}` from the vault H1 (`Half-Hourly Generation Outturn by Fuel Type (FUELHH)` — 5 words, wraps to 4–5 lines). The Claude-Design reference uses `Generation by fuel type, half-hourly.` (5 words, wraps to 2 lines) with an italic accent on the last word. There's no vault field for a short editorial tagline, and adding one is out of D-01 scope.
2. **The dead rectangle bug only exists because no fix is structurally possible.** Any `align-items` value (`start`/`end`/`stretch`) trades one visual artifact for another while the left/right height mismatch remains. The mismatch goes away only when the H1 is short — which requires editorial content not in the vault.
3. **CI gates passed under both iterations.** Idempotence, htmlhint, lychee were all green. The failure was visual, not structural — which is exactly the failure mode that v2 explicitly skipped infrastructure for (no visual regression / snapshot testing per PROJECT.md). User-checkpoint at Task 3 caught it, as designed by D-02.

## What is kept

The Iteration 2 template changes are **left in place on `docs/v2-milestone-start`** for the long-tail templated pages under the Phase 8B hybrid model:

- `align-items: stretch` + `grid-template-rows: repeat(3, 1fr)` is the most structurally honest layout the template can produce for variable-length content. It avoids dead rectangles even if the result looks "engineered" rather than "designed."
- `silver.{{ doc.slug }}` matches editorial intent (the Pythonic reference users actually type, not the partitioned file path).

These changes still go to all ~150 long-tail Elexon + ENTSO-E pages that won't have hand-authored overrides under Phase 8B.

## What is superseded

Phase 8's BUG-01, BUG-02, BUG-03 requirements are **re-mapped to Phase 8B** with the following scope shift:

| Original | Phase 8B re-scoping |
|----------|---------------------|
| BUG-01: name and fix the offending location in one place | Replaced with: hybrid `authored-pages/<vendor>/<slug>.html` override path in build script |
| BUG-02: visual verification on `fuelhh.html` + one randomly-spot-checked page | Carried forward: same verification, but against a hand-authored reference (Claude-Design output for fuelhh, AI-hand-ported or Claude-Design output for the second page) |
| BUG-03: CI gates green | Carried forward unchanged |

## Files touched

- `templates/dataset.html.j2` — modified (lines 18, 39, 42); kept (not reverted)
- `site/hifi/data-sources/elexon/*.html` — 33 pages regenerated; will be re-regenerated under Phase 8B
- `site/hifi/data-sources/entsoe/actual_generation.html` — regenerated; will be re-regenerated under Phase 8B
- `.planning/phases/08-bug-fix-dataset-formatting/08-RESEARCH.md` — kept as historical record of the failed diagnosis
- `.planning/phases/08-bug-fix-dataset-formatting/08-01-PLAN.md` — kept; marked superseded by frontmatter
- `.planning/phases/08-bug-fix-dataset-formatting/08-VALIDATION.md` — kept; carries forward to Phase 8B

## Commits

- `3654a23 docs(08): capture phase context — minimal-patch fix scope locked` (kept)
- `55ff73a docs(08): create phase plan — single-token hero alignment fix` (kept; plan superseded)
- `33375e6 docs(08): correct template path + flag dirty-tree precondition` (kept; planning correction)
- `2884912 fix(08-01): correct dataset hero alignment — dataset.html.j2:18` (Iteration 1; kept on branch — represents the failed first attempt; would have been reverted but the second attempt overrode it)
- *Iteration 2 changes uncommitted at handoff to Phase 8B*

## Learning captured for the project

> When a "bug" requires editorial content that doesn't exist in the source-of-truth layer (here: short H1 taglines in the vault), no rendering-layer patch can fix it. The fix has to expand the source layer or move to a hand-authored override. Lock-scoped minimal patches are appropriate for *bugs in implementation* but not for *gaps in input data* — and the gap shape only became visible after attempting the fix.

This learning becomes Phase 8B's primary justification.
