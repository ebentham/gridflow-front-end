# Phase 11 — Site cleanup: RESEARCH (audit findings)

**Date:** 2026-06-07 · **Method:** `/effort ultracode` multi-agent audit (8 dimensions ×
review → 2 adversarial verifiers per finding) + orchestrator external-URL liveness pass +
search-bar investigation. Raw 35 findings → **12 confirmed, 6 disputed, 17 rejected**.
Surface: 162 dataset pages + 6 hubs + 3 top-level pages (index/data-sources/architecture)
+ 3 assets (site.js, charts.js, theme.css) + vault SoT.

The adversarial pass cleared several false alarms (desktop-first viewport = intentional;
facet double-count = by design; "Open to roles" footer = acceptable, not a hire-me CTA;
"Shipped" model badges = honest). Those are NOT in scope below.

---

## Answering the four questions you asked

1. **Does the search bar work?** → **There is no search bar.** Functionally verified via a
   headless preview (`site.js`-injected DOM): `input[type=search]`/`.nav-search`/`[role=search]`
   count = **0**, total inputs on the page = **0**. `theme.css` defines a `.nav-search`
   component (L176–191, with a ⌘K-style `kbd` hint) but `site.js` never injects a search input
   — only orphaned CSS remains from an earlier design. The catalog's `Sort: alphabetical` /
   `Export CSV` controls and the category/region facet chips are **static `<span>`s with no
   handlers** (decorative). So findability across 162 datasets is browse-only. → **Decision D-2.**

   **Functional smoke-check (the rest of the interactivity, since the audit's interactivity
   agent failed):** on a live page all real behaviors WORK — API **tabs switch** on click
   (panel 0→1, button gets `.active`), **code-copy fires** (label → "Copied", no error),
   **mobile nav toggle** opens (`nav-links`→`nav-links open`), and `site.js` chrome injection
   (top nav + footer) renders correctly. So interactivity is healthy; the only interaction
   defects are the absent search and the decorative dead chips (F-A5 / F-I2).
2. **Is the format correct across all pages?** → Mostly yes, but two systemic gaps: no
   `<main>` landmark and no distinguishing sidebar `aria-label` on the 162 dataset pages
   (F-A1, F-A2). Desktop-first viewport is intentional (cleared). 
3. **Do all embedded URLs work?** → All vendor-doc links are **live** (liveness pass below).
   One broken-intent CTA (F-L1: bare `github.com`) and one minor URL inconsistency (F-L2).
4. **Is everything consistent with the vault?** → Yes for the sampled pages; no SoT
   inversions survived verification (the two vault-consistency flags were both rejected on
   re-read). The bigger consistency problem is **internal**: stale per-vendor counts the
   Phase-10 reconciliation missed (F-C1, F-C2).

---

## Findings (severity after adversarial calibration)

### HIGH

- **F-A1 · No `<main>` landmark on 162 dataset pages** (a11y; disputed→real). Dataset pages
  wrap content in `<div class="main-content">`; 0/162 have `<main>`/`role="main"`. Hubs +
  top-level pages do. site.js injects nav/footer but no main. *Fix:* `<div class="main-content">`
  → `<main class="main-content">` across `authored-pages/<vendor>/<slug>.html` + rebuild.
  Sacred refs share the flaw (see D-1). *(small)*
- **F-A2 · Sidebar `<nav>` lacks a distinguishing `aria-label`** (a11y; confirmed). Dual
  nav landmarks (global + page TOC) are ambiguous to AT. *Fix:* `<nav class="sidebar"
  aria-label="On this page">` across dataset pages + rebuild. *(small)*
- **F-A3 · `--ink-faint` (#a8a194) fails WCAG 1.4.3 contrast (~2.1:1)** site-wide (theme.css
  L17). Hits `.tiny`, sidebar titles, footer provenance, muted links on all 168 pages.
  *Fix:* darken to ~#736b5f (≈4.5:1) — one stylesheet edit. `--ink-soft` (#6b6358) already
  passes. *(trivial)*
- **F-C1 · Homepage "Seven feeds" grid ships stale per-vendor counts** (content; confirmed).
  `index.html` L585 ENTSO-E `14`→49, L602 ENTSO-G `1`→33, L618 GIE `2`→8, L635 Open-Meteo
  `2`→6, L651 NESO `1`→33 (Elexon L569 `33` ✓). **Missed by the Phase-10 count fix** (which
  only touched the stat strip + pillar). Self-contradicts the page's own "162 total". *(trivial)*
- **F-L1 · architecture.html "Read the full source on GitHub →" → bare `https://github.com`**
  (links; confirmed). L1157. Dumps recruiters on GitHub's homepage. *Fix:* →
  `https://github.com/EBentham/gridflow` (the ETL repo this page documents). *(trivial)*

### MEDIUM

- **F-A4 · No visible focus indicator anywhere** (a11y; disputed→real). theme.css has no
  `:focus`/`:focus-visible`. *Fix:* add `:focus-visible { outline: 2px solid var(--accent);
  outline-offset: 2px; }` (+ dark-surface variant). One edit, site-wide. *(trivial)*
- **F-A5 · Interactive-looking chips are non-focusable `<span>`s** (a11y; confirmed) — the
  time-range/API/facet/Sort/Export chips present a false affordance (cursor:pointer + hover)
  but aren't keyboard-reachable. *Fix:* given they're decorative-only, remove the
  pointer/hover affordance + add `aria-hidden`/inert; OR (D-2) make them real `<button>`s. *(small)*
- **F-X1 · site.js footer injects hardcoded "last updated 2026-05-18"** (anti-goals;
  disputed→real). site.js L48. Fake-freshness stamp on every page; silently rots. *Fix:*
  drop the "· last updated 2026-05-18" clause (do NOT replace with `new Date()`). *(trivial)*
- **F-X2 · Homepage hero "Static snapshot · refreshed nightly"** (anti-goals; disputed→real).
  index.html L366 — "refreshed nightly" is fake-live on a chart the same card labels "shape
  only · seeded SVG" (L338). *Fix:* → "Static snapshot · illustrative" (match the rest of
  the site). *(trivial)*
- **F-C2 · architecture.html repo-tree "ENTSO-E Transparency (14 datasets)"** (content;
  confirmed). L1091 `14`→49. Verify ALL per-vendor annotations in the tree (L1090+) against
  33/49/33/8/33/6. *(trivial)*
- **F-X3 · `site/hifi/data/vendors.json` is a tracked orphan with fake-live data + stale
  counts** (anti-goals + content). *Missed by the audit* (it's a data file, not a page/asset,
  so the dimension agents never scanned it; surfaced separately via a spawned task chip and
  folded in here). Referenced by NO code/page (`grep` = 0). Carries 7 fake `lastFetch`
  timestamps (`"00:01:42"`, …) — a direct "kill all live framing" anti-goal violation — and
  all-stale per-vendor `datasets` counts (28/14/1/1/1/2/1; also the retired `gie_agsi`/
  `gie_alsi`/`open_meteo` split naming). *Fix:* **delete the file** (it's dead; removal also
  kills the anti-goal-violating timestamps); if a future use is wanted instead, strip every
  `lastFetch` and correct counts to 33/49/33/8/33/6 with unified `gie`. *(trivial)* — supersedes
  background task `task_756eb27c`.
- **F-C3 · "Seven feeds, one warehouse" heading over a 6-vendor grid** (content; confirmed).
  index.html L555 "Seven"→"Six". *(trivial)*

### LOW

- **F-A6 · Table `<th>` lack `scope`** (schema/sample/at-a-glance tables) — WCAG 1.3.1.
  *Fix:* `scope="col"` on `thead th` across dataset-page template + top-level. *(small)*
- **F-A7 · Breadcrumb / `aria-current` inconsistent** older vs newer pages. *Fix:* standardise
  `<nav aria-label="Breadcrumb">` + trailing `aria-current="page"` + `aria-hidden` on `.sep`. *(small/medium)*
- **F-A8 · Seeded decorative charts lack `aria-hidden`** (index/data-sources/dataset pages).
  *Fix:* `aria-hidden="true"` on the chart host (or charts.js sets it on the `<svg>`). *(trivial)*
- **F-C4 · No meta description** on 162 dataset pages + data-sources.html + architecture.html
  (disputed→low). *Fix:* add a one-line description to the dataset template + 2 top-level pages. *(small)*
- **F-C5 · NESO `carbon_intensity.html` `<title>` uses "· NESO ·"** vs the other 32 NESO
  pages' "· NESO Carbon Intensity ·". *Fix:* align the title segment. *(trivial)*
- **F-L2 · NESO vendor-doc URL inconsistent** (disputed→low): hub links `carbonintensity.org.uk`,
  all 33 dataset pages link `carbon-intensity.github.io/api-definitions/`. *Fix:* point the
  hub at `carbon-intensity.github.io/api-definitions/` (the real docs) — `authored-pages/neso/_landing.html`. *(trivial)*

### INFO / optional

- **F-I1 · `data-screen-label` format inconsistent but inert** (unused by site.js). Normalise
  or drop. Lowest priority.
- **F-I2 · Dead `.nav-search` CSS** in theme.css (L176–191, L891) for a search bar that is
  never rendered. Remove if not building search (D-2).

---

## External-URL liveness pass (CI runs lychee `--offline`, so externals are never gated)

All six vendors' documentation CTAs resolve: `elexonportal.co.uk` (current, not legacy),
`carbon-intensity.github.io/api-definitions/` (official NESO docs), `open-meteo.com/en/docs`,
`transparency.entsog.eu` + `transparency.entsoe.eu` + `bmrs.elexon.co.uk` (JS SPAs, live).
GitHub repo is **public** + issues enabled → the "Suggest a source" issue link is valid.
LinkedIn 301-redirects to `uk.linkedin.com/in/elliot-bentham` (valid). Detail in
`_liveness-prework.md`. Two findings folded in above: **F-L1** (bare github.com) and a
borderline note that GIE pages link the `agsi.gie.eu/api` endpoint (returns a raw JSON
auth-error to click-through visitors — consider pointing the human CTA at `agsi.gie.eu/`).

---

## Rejected by adversarial verification (NOT in scope — recorded for transparency)

Desktop-first viewport width=1280 (intentional design); facet chips double-counting GIE/NESO
(by design, numerically coherent); "Open to roles…" footer (acceptable quiet-portfolio, not a
hire-me CTA); "Shipped/shipping" model badges (honest); Open-Meteo azimuth=180 "south-facing"
(page correct on re-read); forecast_solar sample provenance label (correct); Elexon system-prices
`-settlementDate-` API-doc placeholder (legit Elexon path param); "31/33 Elexon pages omit
caveats" (rejected — re-confirm during execution if desired); NESO "mix · live"/"now" snapshot
chips (cleared as not overstating). Duplicate framings of F-A1/F-A2 under the code-quality
dimension were deduped into the accessibility findings above.

---

## Decisions for the user (resolve before execution)

- **D-1 · Sacred refs.** `authored-pages/elexon/fuelhh.html` + `system_prices.html` are
  byte-frozen visual references, but they share F-A1/F-A2/F-A6 (no `<main>`, no sidebar
  aria-label, no `th scope`). These are **non-visual** a11y attributes — rendering stays
  visually identical. Options: **(a)** un-freeze to fix them too (recommended — visual
  fidelity preserved, full a11y compliance, no page left behind), or **(b)** keep them
  frozen (2 pages remain non-compliant; bulk edits exclude them).
- **D-2 · Search / findability.** No search exists; chips are decorative. Options: **(a
  cleanup-only, recommended for this phase)** remove dead `.nav-search` CSS + neutralise the
  decorative chips (F-A5/F-I2) — honest, editorial-quiet; or **(b feature)** build a real
  vanilla-JS client-side search/filter over the 162-dataset catalog (larger scope, arguably
  valuable for 162 datasets, but it's a feature not cleanup).
- **D-3 · Scope cut.** Recommend fixing **all HIGH + MEDIUM + LOW** this phase (most are
  trivial/small). F-C4 (meta descriptions ×164) and F-A7 (breadcrumb standardisation) are
  the only larger LOWs — include or defer? INFO items optional.
- **D-4 · Branch.** New branch `fix/phase-11-site-cleanup` off the current
  `feat/phase-10-four-vendor` HEAD (so it carries the merged Phase-10 work and avoids
  index.html conflicts), or off `main` after PR #24 merges.
