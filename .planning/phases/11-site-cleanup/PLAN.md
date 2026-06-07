---
plan_id: 11-01
phase: 11
title: Site cleanup — fix audit findings before closing the v2 milestone
status: ready_to_execute
autonomous: false
executor_model: opus
expected_commits: 8-12
findings_source: RESEARCH.md (18 actionable, adversarially verified) + _liveness-prework.md
blocks_on: []
decisions_locked: 2026-06-07
---

## Decisions — LOCKED 2026-06-07 (user chose all recommended)

- **D-1 = (a) Un-freeze sacred refs** for the 3 non-visual a11y fixes (`<main>`, sidebar
  `aria-label`, `th scope`). fuelhh.html + system_prices.html ARE edited, in a dedicated
  reviewed commit; their **visual rendering must stay byte-identical** (only non-visual
  attributes change — verify the rendered diff is attribute-only). No bulk-pass exclusion
  needed for these three transforms.
- **D-2 = (a) Cleanup-only** — remove dead `.nav-search` CSS + neutralize decorative chips.
  No search feature.
- **D-3 = All HIGH + MEDIUM + LOW**, including F-C4 (meta descriptions) and F-A7 (breadcrumb
  a11y). F-I1 (data-screen-label) optional/last.
- **D-4 = Branch `fix/phase-11-site-cleanup` off the current `feat/phase-10-four-vendor` HEAD.**


# Phase 11 / Plan 11-01 — Site cleanup

## Goal

Close the 18 verified audit findings so the site is a11y-correct, internally consistent,
and free of fake-freshness/dead-affordance cruft — then close the v2 milestone. No new
features (cleanup only, per D-2). All three CI gates stay green; the two sacred reference
pages are protected by a *verified* guard, not an intention.

## Decisions — USER GATE (resolve before any execution)

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **D-1** | Sacred refs `fuelhh.html` + `system_prices.html` share F-A1/F-A2/F-A6 (no `<main>`, no sidebar `aria-label`, no `th scope`). These are **non-visual** attributes — rendered appearance is byte-unchanged visually. | (a) un-freeze to apply the 3 non-visual a11y fixes (full compliance; relaxes the "byte-identical" letter but preserves visual fidelity); (b) keep frozen (these 2 pages stay a11y-non-compliant; bulk edits exclude them) | **(a)** — they're the flagship showcase pages and the attrs don't alter rendering. But it relaxes a locked invariant, so it's your call. If (b), I exclude them and note the divergence. |
| **D-2** | No search bar exists; chips are decorative. | (a cleanup-only) remove dead `.nav-search` CSS + neutralize the decorative chips; (b feature) build a vanilla-JS client-side search/filter over the 162-dataset catalog | **(a)** — "cleanup before milestone close" ≠ build a feature. Client-side search is a v3 candidate. |
| **D-3** | LOW/optional scope. | Fix all HIGH+MEDIUM+LOW (recommended); the two heavier LOWs are F-C4 (meta descriptions ×164 pages) and F-A7 (breadcrumb standardization). INFO items (F-I1 data-screen-label) optional. | Do all HIGH+MEDIUM+LOW; **include** F-C4 + F-A7; treat F-I1 as optional. |
| **D-4** | Branch. | (a) new branch off current `feat/phase-10-four-vendor` HEAD (carries Phase-10 work, avoids index.html conflicts); (b) off `main` after PR #24 merges | **(a)** `fix/phase-11-site-cleanup` off the current HEAD, unless you'd rather merge #24 first. |

> Execution does not begin until D-1..D-4 are answered. The task list below assumes the
> recommended answers; I will adjust if you choose differently.

## Hard rules (carried from project agreements)

- **Never auto-commit / never push without explicit ack.** Stage → show → ask.
- **Sacred-ref guard is a verified step:** after every bulk pass,
  `git diff --stat -- authored-pages/elexon/fuelhh.html authored-pages/elexon/system_prices.html`
  MUST be empty (unless D-1=(a), in which case those two are edited deliberately and reviewed).
  A naïve `authored-pages/*/*.html` glob hits them — every scripted pass must explicitly exclude
  them (or include-by-design under D-1a).
- Conventional commits, **one atomic commit per transform-type** (uniform reviewable diffs;
  any optional item can be dropped without unpicking others).
- Generated `site/hifi/data-sources/` is gitignored — fixes land in **source**
  (`authored-pages/`, the 3 static top-level pages, or `assets/`), then rebuild.
- After each commit's transform: re-grep to prove the change applied everywhere intended +
  run the 3 CI gates (`gridflow-build --check`, `htmlhint`, `lychee --offline --include-fragments`).

## Mechanism (settled with advisor): edit the source, not build-time injection

The 162 dataset pages are individually authored (no shared template), so the bulk a11y fixes
are **idempotent scripted edits over the authored source files** — NOT a build.py transform
layer (which would leave the source artifacts wrong and break the verbatim-copy model). Two
traps, both verified:
- **`<div class="main-content">` → `<main class="main-content">` is safe:** `.main-content` is
  only ever class-selected (`body[data-page="dataset"] .main-content`, theme.css L730/L818),
  never `div.main-content`, and not referenced in site.js. No selector/JS breaks.
- **`--ink-faint` is shared text+border:** 9 `color:` uses but also 3 `border-*` uses (L92,
  L189, L250) + `.dot.idle` background + `.arrow` + code-comment. F-A3 must **split** it into a
  darker AA text token, leaving the lighter value for borders/decorative — not a blind darken.

---

## Tasks

### Wave 1 — Top-level content + link fixes (surgical; highest recruiter value, zero risk)

**T1 · index.html** — (F-C1) vendor-grid chips: ENTSO-E 14→49, ENTSO-G 1→33, GIE 2→8,
Open-Meteo 2→6, NESO 1→33 (Elexon 33 ✓); (F-C3) heading "Seven feeds, one warehouse" →
"Six feeds…"; (F-X2) L366 "Static snapshot · refreshed nightly" → "Static snapshot · illustrative".
**T2 · architecture.html** — (F-L1) L1157 `href="https://github.com"` → `https://github.com/EBentham/gridflow`;
(F-C2) L1091 "ENTSO-E Transparency (14 datasets)" → 49, and verify ALL repo-tree per-vendor
annotations (L1090+) against 33/49/33/8/33/6.
**T3 · assets/site.js** — (F-X1) drop "· last updated 2026-05-18" from the injected footer (L48).
*Commit:* `fix(site): correct stale homepage/arch counts + remove fake-freshness chrome`.

### Wave 2 — Global CSS a11y (theme.css, one file, whole site)

**T4 · theme.css** — (F-A3) introduce `--text-faint: #736b5f` (verify ≥4.5:1 on cream) and
repoint the 9 `color: var(--ink-faint)` text uses (`.tiny`, `.sidebar a.muted`, label colors
L563/660/710/728, `.arrow`, code-comment `.c`) to it; keep `--ink-faint` for the 3 borders +
`.dot.idle`. (F-A4) add `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`
+ a light-on-dark variant for ink/gold cards. Verify contrast ratios.
*Commit:* `fix(a11y): AA contrast for faint text + visible focus indicator`.

### Wave 3 — Bulk dataset-page a11y (scripted, idempotent, sacred-guarded; 1 commit per transform)

Each task: scripted edit over `authored-pages/<vendor>/<slug>.html` (sacred handling per D-1) →
re-grep proves N pages changed and 0 missed → `gridflow-build` → 3 gates → sacred `git diff --stat` check.
- **T5** (F-A1) `<div class="main-content">` → `<main class="main-content">`.
- **T6** (F-A2) sidebar `<nav class="sidebar">` → add `aria-label="On this page"`.
- **T7** (F-A6) `<th>` in `thead` → add `scope="col"` (dataset pages + the 3 top-level tables).
- **T8** (F-A8) decorative seeded chart host → `aria-hidden="true"` (or have charts.js set it on the generated `<svg>` — single charts.js edit covers all; prefer that).
*Commits:* `fix(a11y): main landmark…` / `…sidebar nav label…` / `…th scope…` / `…hide decorative charts from AT`.

### Wave 4 — Targeted small fixes

- **T9** (F-C5) `authored-pages/neso/carbon_intensity.html` `<title>` "· NESO ·" → "· NESO Carbon Intensity ·".
- **T10** (F-L2) `authored-pages/neso/_landing.html` vendor-doc CTA → `carbon-intensity.github.io/api-definitions/` (matches the 33 dataset pages, the real docs).
- **T11** (F-A5 + F-I2, per D-2a) neutralize decorative chips (remove `cursor:pointer`/hover/active affordance + `aria-hidden`/inert on Sort/Export/facet/time-range chips); remove dead `.nav-search` CSS (theme.css L176–191, L891). Optional borderline: point GIE pages' `agsi.gie.eu/api` CTA at `agsi.gie.eu/`.
- **T11b** (F-X3) **delete `site/hifi/data/vendors.json`** — tracked orphan (referenced by no code/page), carries fake `lastFetch` "live" timestamps (anti-goal) + all-stale counts. Confirm zero references (`grep -rl 'vendors\.json'`) immediately before `git rm`. Supersedes background task `task_756eb27c`. *(If you'd rather keep it, fallback: strip every `lastFetch` + correct counts to 33/49/33/8/33/6 with unified `gie`.)*
- **T12** (D-3; F-C4 + F-A7 + optional F-I1) meta descriptions on dataset pages + the 2 top-level pages; standardize breadcrumb `<nav aria-label="Breadcrumb">` + trailing `aria-current="page"` + `aria-hidden` `.sep`; (optional) normalize/drop `data-screen-label`.
*Commits:* grouped — `fix(site): NESO title/docs-url consistency`, `chore(a11y): retire dead search CSS + decorative-chip affordances`, `feat(seo): meta descriptions + breadcrumb a11y`.

### Wave 5 — Verify, review, ship

Cold rebuild + 3 CI gates; re-run the audit greps (counts, `<main>` coverage, contrast token,
chip handlers); **functional smoke re-check** via preview (tabs switch / copy fires / mobile
toggle / no new console errors) to confirm no regression; sacred-ref byte check; `/code-review`
on the diff; write `11-01-SUMMARY.md`; stage → show → **ask before commit/push**; fold into the
v2 milestone (PR).

---

## Why each disputed finding is in scope (not padding)

The "disputed" tier = 1-of-2 verifier votes, but in every case the split was the **materiality
lens lowering severity**, not the correctness lens denying the issue exists:
- **F-A1** (main landmark) — correctness verifier confirmed 0/162 with strong evidence; the split was "is it high or medium." Real.
- **F-A4** (focus) — confirmed no `:focus` rules exist; split = "browser default exists." Real (keyboard a11y).
- **F-X1 / F-X2** (last-updated / refreshed-nightly) — both strings verified present; split = "is a date/`nightly` really fake-live." Real per the locked anti-goal.
- **F-C4** (meta desc) — verified none exist; split = "SEO nice-to-have." Kept as LOW.
- **F-L2** (NESO URL) — inconsistency verified; split = "both resolve." Kept as LOW.

## Out of scope (rejected by verification — do NOT fix)

Desktop-first viewport (intentional); facet double-count (by design); "Open to roles" footer
(acceptable); "Shipped" badges (honest); Open-Meteo azimuth / forecast_solar provenance
(pages correct); system-prices `-settlementDate-` placeholder (legit). Plus: building a real
search feature (D-2b) unless you opt in.

## Risk / rollback

All edits are on a feature branch, reversible. Bulk passes are idempotent and re-grep-verified.
The only invariant-relaxing choice is D-1(a); if chosen, the two sacred files get a dedicated
reviewed commit so the visual-vs-byte tradeoff is explicit and revertible in isolation.
