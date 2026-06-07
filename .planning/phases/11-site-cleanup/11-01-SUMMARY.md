---
plan_id: 11-01
phase: 11
title: Site cleanup — fix audit findings before closing the v2 milestone
status: complete
executor_model: opus
commits: 12
branch: fix/phase-11-site-cleanup
base: 7034dec (Phase-10 HEAD)
date: 2026-06-07
---

# Phase 11 / Plan 11-01 — Summary (site cleanup)

## Outcome

**Complete.** All **19 verified audit findings** (12 confirmed + 6 disputed-but-real + the
`vendors.json` orphan) are resolved. The site is now WCAG-cleaner (landmarks, labels, table
header scope, AA-contrast faint text, a visible focus ring, hidden decorative charts),
internally consistent (vendor counts reconciled everywhere, no stale/fake-freshness strings),
and free of dead affordances/CSS. All three CI gates stay green. **14 atomic commits.**
The two sacred reference pages keep byte-identical **HTML** (only the 3 D-1 attrs) and identical
**static layout** — but the shared stylesheet's AA-contrast + honest-affordance fixes *do* reach
them (faint text darkened, one decorative chip lost its hover). That is an **open D-1 sign-off
item** surfaced by the code review (see below), not a silent change.

## Findings resolved (by wave)

**Wave 1 — top-level content + links** (`e6d4817`)
- F-C1 homepage vendor-grid counts → 49/33/8/6/33 (Elexon 33 already correct)
- F-C3 "Seven feeds, one warehouse" → "Six…"
- F-X2 hero "Static snapshot · refreshed nightly" → "…· illustrative"
- F-C2 architecture repo-tree connector counts made uniform (entsoe 14→49; added 33/8/6/33 to
  entsog/gie/openmeteo/neso). Silver-layer transformer counts deliberately left untouched
  (separate claim about the gridflow repo = SoT #1, unverifiable without that checkout).
- F-L1 architecture "Read the full source" button: bare `github.com` → `/EBentham/gridflow`
- F-X1 site.js footer: dropped hardcoded "last updated 2026-05-18"

**Wave 2 — global CSS a11y** (`5836575`)
- F-A3 contrast: `--ink-faint` (#a8a194, ~2.1–2.4:1) failed WCAG 1.4.3. Introduced
  `--text-faint` (#6d655a) for the 7 text uses; verified ≥4.5:1 on all three cream surfaces
  (paper 5.10 / paper-card 5.37 / paper-deep 4.62). `--ink-faint` kept for 3 borders + `.dot.idle`.
- F-A4 focus: added `:focus-visible { outline: 2px solid var(--accent); … }` + a light-ring
  variant on `.card.ink` (accent-on-ink-strong was only 2.9:1, below the 3:1 non-text minimum).

**Wave 3 — bulk dataset-page a11y** (`711f7dd`, `9d28f5c`, `cef4c24`, `99f4eae`)
- F-A1 `<div class="main-content">` → `<main>` on 162 pages (close located by comment-aware
  div-depth counting, not a parser — preserves byte-identity)
- F-A2 sidebar `<nav>` → `aria-label="On this page"` (disambiguates the site.js "Primary navigation")
- F-A6 `scope="col"` on all 1915 `<th>` (verified all in `<thead>`, 0 row-headers) — 162 pages + data-sources.html
- F-A8 decorative seeded charts hidden from AT via a single charts.js dispatcher edit

**Wave 4 — targeted fixes** (`9f1812b`, `bdb71b9`, `ab10e3b`, `2d19516`, `d0313e6`)
- F-C5 NESO `carbon_intensity.html` title "· NESO ·" → "· NESO Carbon Intensity ·"
- F-L2 NESO hub "Vendor docs" CTA → `carbon-intensity.github.io/api-definitions/` (matches the 33 dataset pages)
- F-A5 / F-I2 removed dead `.nav-search` CSS; neutralized decorative `span.chip.btn-like`
  affordance (cursor/hover) while **preserving the 486 functional `button.chip.btn-like` API tabs**
  (scoped `:hover` to `button`; buttons keep inline `cursor:pointer`)
- F-X3 deleted orphan `site/hifi/data/vendors.json` (0 refs; carried 7 fake `lastFetch` timestamps + stale counts)
- F-C4 meta descriptions on 160 dataset pages (lede-derived, vault-accurate) + data-sources.html + architecture.html
- F-A7 breadcrumbs → `<nav aria-label="Breadcrumb">` + `aria-current="page"` + `aria-hidden` separators
  across 160 dataset pages **+ all 6 hubs** (completed the 5 hubs that already had nav, fixed the 1 elexon hub that didn't)

## Decisions honored

- **D-1a** — sacred-ref *HTML* un-frozen ONLY for the 3 non-visual attrs (`<main>`, sidebar
  `aria-label`, `th scope`). Verified `git diff 7034dec..HEAD` for fuelhh/system_prices shows
  exactly those three. They were deliberately **excluded** from meta descriptions (F-C4) and
  breadcrumb nav (F-A7) since those exceed D-1 scope. *(2 pages therefore lack a meta description +
  breadcrumb landmark — trivial to extend if you widen the un-freeze.)* **Caveat the review caught:**
  the HTML-only guard (`git diff --stat` on the two files) is blind to **shared-asset** changes —
  theme.css's AA-contrast (`--text-faint`) and chip-affordance edits reach these pages via the single
  shared stylesheet, so their faint text is darker and one decorative chip lost its hover. Static
  layout is unchanged; this is an a11y/honesty improvement that relaxes the "byte-identical visual"
  letter → **D-1 sign-off received 2026-06-07: ACCEPTED site-wide** — the two flagship pages are now
  AA-compliant and free of the fake affordance.
- **D-2a** — cleanup-only: dead search CSS removed, decorative chips neutralized; **no search feature built.**
- **D-3** — all HIGH + MEDIUM + LOW done, including F-C4 + F-A7. (F-I1 `data-screen-label`
  normalization left as INFO/optional — inert, unused by site.js.)
- **D-4** — branched `fix/phase-11-site-cleanup` off the Phase-10 HEAD `7034dec`.

## Verification (cold rebuild, 2026-06-07)

- `gridflow-build` → 162 pages + 6 hubs; `--check` idempotent.
- `htmlhint` → 172 files, 0 errors. `lychee --offline --include-fragments` → 0 errors (444 external excluded by design).
- Per-finding grep sweep: 19/19 resolved (counts, `<main>`×162, sidebar label×162, scope×1915,
  charts aria-hidden, `--text-faint` 0 text uses on `--ink-faint`, `:focus-visible` present,
  nav-search gone, vendors.json removed, meta×162, breadcrumb nav×166).
- Functional smoke-check (preview): site.js chrome injects, footer = "6 vendors · 162 datasets"
  (no "last updated"), 7/7 charts render, **mobile-nav toggle works, 0 console errors**. API tabs
  confirmed unaffected (inline `onclick`/`setTab` untouched; CSS scoping preserves button affordance).
  *(Preview is sandboxed to `/` and persistently serves cached pre-Phase-11 assets, so live
  `aria-hidden`/`:focus-visible` couldn't be observed there — both verified correct in source;
  production serves fresh assets.)*
- Sacred-ref guard: `git diff --stat` for fuelhh/system_prices limited to the 3 D-1 attrs
  throughout. *(HTML-scoped; the review correctly noted it cannot see shared-CSS visual drift — see D-1a.)*

## Notes / non-issues

- **CRLF**: authored `.html` are CRLF in the working tree; git normalizes to LF on commit
  (`.gitattributes`/autocrlf). All diffs are content-only — no line-ending flips.
- **Silver-transformer counts** in architecture.html ("28 transformers" / "14 transformers")
  left as-is: a claim about the gridflow *code* (SoT #1), not the front-end catalogue, and
  unverifiable from this repo. Candidate follow-up when the gridflow checkout is available.

## Commit range

`7034dec` (Phase-10 HEAD) → `6e90b7f`. 14 commits, one concern each:
`docs(phase-11)` · `fix(site)` ×2 · `fix(a11y)` ×7 · `chore`/`chore(a11y)` ×2 · `feat(seo)` ×1 ·
`fix(content)` ×1. (Last two = code-review remediation: `9e94648` models-page a11y miss,
`6e90b7f` silver-count reconciliation.)

## Code review (adversarial, 5 dimensions × 2 verifiers/finding)

13 raw findings → **6 confirmed**, 7 dismissed (pre-existing nits, `.planning` doc drift, a
correctly-rejected "hide the demand-forecast fan chart" that would have hidden *informative* content).

**Remediated (2 commits):**
- **#6 (med)** F-A6/F-A7 had missed a 4th tracked top-level page, `models/demand-forecast.html`
  (linked from index + site.js). → scoped its 4 th + breadcrumb nav. `9e94648`.
- **#3 (med) + #4 (low)** the connector-count fix surfaced a silver-block self-contradiction
  ("49 datasets" vs "14 transformers / one per dataset") + an impossible "34" stat. → reconciled
  to gridflow SoT (33/26, stat 67, honest "shared-family" annotation). `6e90b7f`.

**Escalated → RESOLVED (accepted 2026-06-07):**
- **#2 (med) + #5 (med)** the shared-stylesheet AA-contrast + chip-affordance fixes reach the two
  sacred refs (faint text darker; one decorative chip lost hover) — relaxes the "byte-identical
  visual" letter of D-1. **User accepted site-wide:** the two flagship pages are now AA-compliant
  and free of the fake affordance; layout unchanged. No code change.

**Deferred follow-up (documented, not done):**
- **#1 (low)** F-A3 fixed the 7 CSS-rule faint-text uses but ~679 **inline** `style="color:var(--ink-faint)"`
  spans (chart axis labels, snapshot micro-text — 132 pages) still compute <4.5:1. Pre-existing;
  **not** a clean mechanical sweep (some sit inside now-`aria-hidden` decorative charts; blind
  darkening would alter chart visual design — per-context judgment). Logged for a follow-up phase
  so F-A3 is not overclaimed as "site-wide AA."

## D-1 sign-off — RESOLVED (accepted 2026-06-07)

The AA-contrast + honest-chip fixes apply to the two sacred refs via the shared stylesheet
(user-accepted). Net effect: fuelhh + system_prices are now AA-compliant and free of the fake
chip affordance; HTML + static layout unchanged. The "byte-identical visual" letter of D-1 is
relaxed to **"byte-identical HTML + static layout; shared-asset a11y improvements permitted."**

## Status

**Complete.** Execution + code review done, 6/6 confirmed findings remediated-or-resolved, all
gates green, D-1 signed off (accept), user ack to push received → pushing the branch and opening
the v2-line PR.
