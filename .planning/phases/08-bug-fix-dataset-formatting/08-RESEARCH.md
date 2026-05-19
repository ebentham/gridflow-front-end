---
phase: 8
slug: bug-fix-dataset-formatting
status: complete
created: 2026-05-19
research_budget: ~15% (bug fix, D-04 light pass)
---

# Phase 8 — Research

> Bounded per CONTEXT.md D-04: confirm or refute the provisional diagnosis in
> CONTEXT.md `<specifics>` D-S-01; surface any contributing CSS rule missed.
> Surfaces inspected verbatim per D-04 brief: `templates/dataset.html.j2` lines
> 1-70 + `site/hifi/assets/theme.css` rules covering `.container`,
> `.page-layout`, hero-area selectors, and the media queries at ≤1100px,
> ≤720px, ≤480px. No fan-out to `build.py` or vault frontmatter — see
> "Surfaces ruled out" below.

---

## Bug confirmation

The user-reported top-of-page glitch on `site/hifi/data-sources/elexon/fuelhh.html`
is **a desktop-only CSS layout defect** in the rendered hero region (the block
between the breadcrumb and the stats strip). The defect originates entirely in
`src/gridflow_front_end/templates/dataset.html.j2` lines 18-65 — specifically
the outer hero grid declaration on line 18 — and is **not** an artefact of
`build.py`, vault frontmatter, or any CSS rule in `theme.css`. `theme.css` is
victim, not cause: it correctly handles the hero at ≤720px (see line 821-829)
and ≤480px (line 977-979), but it has **no desktop-width rule** that would
override the inline-style declaration on template line 18.

## Root cause — two co-contributing causes (both confirmed; D-S-01 hypotheses hold)

### Cause #1: `align-items: end` on the outer hero grid

`templates/dataset.html.j2` line 18:
```jinja
<div style="display:grid; grid-template-columns: 1fr auto; gap: 48px; align-items: end;">
```

The `align-items: end` declaration anchors the right (metadata) column to the
**bottom** of the row. Because the left column (eyebrow chips + H1 + `.lede`
with `max-width:660px` + verified micro-line) is taller than the right column
(6-cell metadata grid), the right column floats to the bottom-right of the
row, leaving a tall empty rectangle above it. This is the dominant visible
glitch in the user's screenshot.

**Confirmed by reading:** template line 18, no `theme.css` rule overrides
`align-items` on this inline-style block at any breakpoint. The `body[data-page="dataset"]
[style*="grid-template-columns: 1fr auto"]` rule at theme.css line 821 only
fires at `max-width: 720px` and only changes `grid-template-columns` (not
`align-items`). Desktop `align-items: end` is unchallenged.

### Cause #2: `grid-template-columns: 1fr auto` + unwrapped long mono string

Same template line 18 declares `grid-template-columns: 1fr auto`. The `auto`
right column expands to fit its widest unwrapped content. The widest content
is the SILVER PATH string rendered in `.mono.small` (template line 42):

For `fuelhh`: `data/silver/elexon/fuelhh/year=YYYY/month=MM/fuelhh_YYYYMMDD.parquet`
— ~75 characters at the rendered font size (12px JetBrains Mono per theme.css
line 88). With `font-family: var(--mono)` + `font-size: 12px` and **no
word-break or overflow-wrap on `.mono`, `.small`, or any ancestor** (confirmed
via grep — no `word-break` / `overflow-wrap` / `word-wrap` anywhere in
theme.css), this string consumes ~520px of column width before the column will
even consider stretching the inner `1fr 1fr` metadata grid.

Combined with the inner grid's `min-width: 340px` floor (template line 39),
the right column claims ~520-560px of the ~1152px content area (1280px
`--site-max` − 2 × 64px `--site-pad`), leaving the left `1fr` column ~590px.
The H1 ("Half-Hourly Generation Outturn by Fuel Type (FUELHH)") then wraps at
that constrained width, but the dominant visible artefact is still the
vertical mis-alignment from cause #1; cause #2 is the *amplifier* that makes
the empty rectangle look especially wide.

**Confirmed by reading:** template lines 18, 39, 42; theme.css lines 86-88
(`.small` and `.mono` declarations); theme.css full-file grep for
`word-break|overflow-wrap|word-wrap` returns zero matches.

## Contributing rules NOT found — surfaces ruled out

The D-04 brief asked the researcher to surface anything the provisional
diagnosis missed. Surfaces inspected and ruled out:

- **Tablet breakpoint ≤1100px** (theme.css line 758-781): only mutates `:root
  --site-pad`, `.display-*` font sizes, `h1`, `.stack-md`, `.footer-grid`,
  `.kpi-row`. **Does not touch the hero block** — so the bug is present at
  both desktop (≥1101px) AND tablet (721-1100px) widths. The fix must
  therefore work at both ranges. The ≤720px breakpoint already stacks the
  hero vertically (theme.css line 821-829) and zeroes the inner `min-width:
  340px` (line 827-829), so the bug does NOT appear on phone.
- **`.page-layout` / `.sidebar` / `.main-content`** (theme.css lines 691-730):
  these style the BELOW-hero content region (sidebar + main). The hero block
  lives in a separate `<div class="container">` ABOVE `.page-layout` — the
  two are sibling layouts with no interaction. Confirmed by reading template
  lines 6-67 (hero) vs lines 68+ (post-hero content). No bleed-through.
- **`.container`** (theme.css line 106-110): max-width 1280px, side padding
  via `--site-pad` (64px desktop, 40px tablet, 20px phone). Normal
  centered-content primitive; not the cause.
- **`.stats-strip`** (theme.css line 277-286): the strip BELOW the hero, also
  unrelated.
- **`build.py`** (CONTEXT.md `<canonical_refs>` Files the fix likely touches —
  "build.py: only relevant if the researcher finds a build transform
  corrupting hero data. Default assumption is no"): confirmed default
  assumption holds. `build.py` lines 223-253 read `silver_path` from vault
  frontmatter and pass through unchanged into the template render context
  (line 565). No CSS or template-text transform happens; `build.py` is
  read-only for Phase 8.
- **Vault frontmatter** (CONTEXT.md same section — "vault/elexon/fuelhh.md:
  only relevant if the researcher decides the bug originates in the data
  layer rather than the template/CSS. Default assumption is no — bug is
  rendering-only"): confirmed. Spot-check of `vault/elexon/fuelhh.md` shows
  ordinary frontmatter (source, dataset_key, vendor, last_verified,
  layer_coverage); the long silver path string is a faithful copy of an Elexon
  reality, not a vault formatting bug. Vault is read-only for Phase 8.

## Fix candidates evaluated (per D-S-01 alternatives)

The D-S-01 list of candidates (a / b / c / d) is the right framing. The
researcher evaluation:

| Candidate | Description | Kills cause #1 | Kills cause #2 | Introduces new bug | Verdict |
|-----------|-------------|----------------|----------------|---------|---------|
| (a) | `align-items: end` → `align-items: start` (or remove) | ✓ | ✗ | no | **Recommended.** Single-line minimal patch; fixes the dominant visible glitch (empty rectangle). The amplifier remains — left column still narrower than ideal on long-silver-path datasets — but the result is "merely awkward H1 wrap" not "broken empty-rectangle hero". |
| (b) | Outer grid → `grid-template-columns: 1fr 420px` | partially | apparently (see arithmetic) | **YES — see arithmetic below** | **Rejected.** |
| (c) | (a) + (b) together | ✓ | apparently | **YES (inherits b's overflow)** | **Rejected.** |
| (d) | `word-break: break-all` on `.mono.small` | ✗ | ✓ | possible elsewhere | Out of scope: `.mono.small` is used in many places across the template (API_PATH, PRIMARY KEY, vault references in `_partials`). A site-wide style change to kill a hero-specific bug violates D-01 minimal-patch scope. **Rejected.** |

### Why (b) and (c) were rejected on a second look

Initial draft of this research recommended candidate (c) (both edits together
as "most defensive"). On re-examination of the inner-grid sizing arithmetic
the recommendation flipped to (a). The arithmetic:

- Pin the right column at 420px (candidate (b)/(c)'s premise).
- Inner metadata grid is `grid-template-columns: 1fr 1fr` (template line 39) →
  each inner cell ≈ 210px wide.
- Inner cell has `padding: 16px 18px` (template line 40) → ~174px of usable
  content width.
- SILVER PATH for `fuelhh` is 75 characters
  (`data/silver/elexon/fuelhh/year=YYYY/month=MM/fuelhh_YYYYMMDD.parquet`).
- `.mono` is JetBrains Mono 12px (theme.css line 88). At ~7.2px per glyph that
  string measures ~540px unwrapped.
- `.mono` and `.small` carry no `word-break`, `overflow-wrap`, or `word-wrap`
  (confirmed via grep — zero matches in theme.css). The string contains `/`
  and `=` characters but those are not soft-wrap opportunities without an
  explicit `overflow-wrap: anywhere` or `word-break: break-all`.
- Result: 540px of content rendered into a 174px cell with no wrap policy →
  the mono string **overflows the cell border** (default `overflow: visible`).

That trades the empty-rectangle bug for a text-bleeds-out-of-card bug. Worse
for recruiter optics; harder to caveat in a commit message; outside D-01's
"make the visible glitch go away" spirit because it introduces a *new* visible
glitch. Candidates (b) and (c) are therefore unviable without also adopting
candidate (d) (which is itself rejected for site-wide scope creep).

### Updated researcher recommendation: candidate (a)

Single-line edit on `templates/dataset.html.j2` line 18:
`align-items: end` → `align-items: start`. Leaves
`grid-template-columns: 1fr auto` unchanged.

Properties of this fix:
- Kills cause #1 entirely (the dominant visible glitch). Metadata grid
  top-aligns with the text column; no empty rectangle.
- Leaves cause #2 (left column narrower than ideal on long-silver-path
  datasets). Per CONTEXT.md `<specifics>` D-S-01, the user/Claude explicitly
  characterized this residual as "the narrow title column is only awkward not
  catastrophic." Acceptable.
- **Does NOT require a theme.css edit.** The existing mobile-stack selector
  at theme.css line 821-822 (`[style*="grid-template-columns: 1fr auto"]`)
  still matches the unmodified `1fr auto` column declaration, so the v1
  ≤720px stacking behaviour is preserved with zero theme.css change. This is
  more aligned with D-01 minimal-patch than candidate (c) would have been.
- Total fix surface: 1 file, 1 line. The planner should pick (a).

## Validation Architecture

Phase 8 is a bug-fix phase with a rendering-only surface, not a code-logic
phase. The "test" pyramid for this phase is therefore unconventional — a
user-eyeball checkpoint per D-02 plus the three v1 CI gates. Source: CONTEXT.md
`<decisions>` D-02 (verification breadth) + D-03 (regression prevention).

### Validation surface (D-02 + D-03)

| Layer | What it checks | Tool | When |
|-------|----------------|------|------|
| Visual (manual, user-verified) | Desktop hero on `fuelhh.html`, 1 random Elexon page, ENTSO-E `actual_generation.html` | Browser eyeball at native desktop (≥1280px viewport) | After `gridflow-build` re-renders all 34 pages |
| Mobile (manual, user-verified) | `fuelhh.html` at ≤720px and ≤480px breakpoints | Browser devtools viewport resize | After `gridflow-build` re-renders all 34 pages |
| Structural (automated) | HTML-shape validity | `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` (exits 0) | Locally before commit AND in `.github/workflows/deploy.yml` |
| Link validity (automated) | All internal anchors resolve | `lychee --offline --include-fragments site/hifi/**/*.html` (exits 0) | Locally before commit AND in CI |
| Build determinism (automated) | Idempotence of template re-render | `gridflow-build --check` (exits 0; no diff on second run) | Locally before commit AND in CI |

### Coverage map

| Requirement | Validation layer | Manual or automated |
|-------------|------------------|---------------------|
| BUG-01 (root-cause + named location) | Commit message + PR body cite `templates/dataset.html.j2:18` | Manual (writing) |
| BUG-02 (fix applied + spot-check) | Visual + Mobile (user-verified, D-02) | Manual (user checkpoint) |
| BUG-03 (CI gates green) | Structural + Link + Build determinism | Automated |

### Why no automated visual regression

Visual-regression infrastructure (snapshot tests, baseline images) is
explicitly v2-out-of-scope per `PROJECT.md` "Out of Scope" and CONTEXT.md
D-03. The bug class (CSS layout glitch) is not catchable by `htmlhint`
(HTML-shape validator) or `lychee` (link checker) or `gridflow-build --check`
(idempotence on a deterministic render) — so the user-eyeball checkpoint at
D-02 is the v2 regression boundary. v3 may revisit if recurring layout bugs
become a pattern across the 163-page expansion (see CONTEXT.md `<deferred>`).

### Sampling cadence

- Per-task: tasks 1-2 (read + edit + build + diff) need no automated test
  beyond the post-edit `gridflow-build --check` already in task 2.
- Per-wave: only one wave in this plan; per-wave verification is the user
  checkpoint at task 3.
- Before phase complete: full CI command set (task 4) runs locally to ensure
  green before commit.

---

## RESEARCH COMPLETE

Root cause confirmed: `align-items: end` (cause #1, dominant) +
`grid-template-columns: 1fr auto` × unwrapped long mono content (cause #2,
amplifier) on `templates/dataset.html.j2` line 18. No contributing CSS rule
missed; no build/data-layer involvement. Recommended fix: **candidate (a) only**
— change `align-items: end` → `align-items: start` on the same template line
(one file, one line); leave `grid-template-columns: 1fr auto` unchanged.
Candidates (b) and (c) initially looked attractive but the inner-grid sizing
arithmetic (right column 420px → inner 1fr 1fr → 174px usable per cell vs
~540px unwrapped SILVER PATH content) shows they introduce a text-overflow
regression. Candidate (a) leaves a known residual (narrow H1 column on
long-silver-path datasets) that CONTEXT.md `<specifics>` D-S-01 characterized
as "only awkward not catastrophic" — acceptable per D-01 minimal-patch. The
plan should not edit `theme.css` (existing mobile-stack selector still
matches the unchanged `1fr auto` declaration). Validation Architecture
provided for VALIDATION.md generation per Nyquist Dimension 8.
