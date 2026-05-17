# Codebase Concerns

**Analysis Date:** 2026-05-17

## In-Flight Refactor (Uncommitted)

**26 modified files with no commit since `351c580` initial commit:**
- Issue: `git status` shows `M` flag on every page in `site/hifi/data-sources/elexon/*.html` (22 files) plus `site/hifi/architecture.html`, `site/hifi/data-sources.html`, `site/hifi/index.html`, `site/hifi/models/demand-forecast.html`. The Merge PR `c6696c3` and feature `7642b57` produced the current `HEAD`, and substantial work has accumulated on top without any commit.
- Files: All under `site/hifi/`.
- Impact:
  - Work is not durable — a stash drop, branch switch, or `git reset --hard` loses everything.
  - Reviewers cannot see incremental intent; the next commit will be a single megacommit if not split.
  - GitHub Pages deploy (`.github/workflows/deploy.yml`, triggered on push to `main`) still serves the older committed version, so live and working-tree are diverged.
- Detected pattern of the refactor (from `git diff HEAD`):
  - Stripping the `fg-accent` class from `<span class="italic fg-accent">…</span>` in display headings (architecture, index, fuelhh, every elexon page).
  - Removing the `<span class="pillar-status">Shipping</span>` blurbs from the three pillar tiles on `site/hifi/index.html` (lines 425, 446, 472 of the old version).
  - On `site/hifi/data-sources/elexon/fuelhh.html`, flipping `LAST FETCH / "42 s ago"` to `PRIMARY KEY / settlement_date, period, fuel_type` and changing "Live chart · last 24h" to "Static snapshot · live wiring planned" — i.e. retreating from "this site is live" framing toward honest "static snapshot" framing.
- Fix approach: Commit in small chunks per concern: (1) the `fg-accent → italic` typography sweep, (2) removal of false-live pillar status, (3) fuelhh honesty edits, (4) the remaining per-page tweaks. Push so Pages catches up.
- Also: every modified file shows the `warning: LF will be replaced by CRLF` warning. The repo has no `.gitattributes` enforcing line endings, so future Linux-built deploys will see line-ending churn against Windows-edited files. Add a `.gitattributes` with `*.html text eol=lf` (plus `.css`, `.js`, `.json`, `.py`).

## Tech Debt

### 16 of 22 Elexon dataset pages are broken stubs

- Issue: The "small" dataset pages (~160 lines each) are missing the `#overview`, `#schema`, `#sample`, and `#api` sections, plus the structural wrapping around them. Only 6 pages have a `<section id="overview">` and `<section id="schema">`: `agpt.html`, `agws.html`, `fuelhh.html`, `fuelinst.html`, `nonbm.html`, `windfor.html`. The other 16 jump straight from the sidebar nav to a stray `<div class="card" style="padding:20px;"><div class="tiny mb-8">PARAM STYLE</div>…` block followed by `</div>` and the API/caveats/related sections — but the surrounding `<section id="api">`, `<div class="main-content">`, and `</nav>` close tags are missing entirely.
- Files (broken):
  - `site/hifi/data-sources/elexon/boal.html`
  - `site/hifi/data-sources/elexon/disbsad.html`
  - `site/hifi/data-sources/elexon/fou2t14d.html`
  - `site/hifi/data-sources/elexon/freq.html`
  - `site/hifi/data-sources/elexon/indo.html`
  - `site/hifi/data-sources/elexon/indod.html`
  - `site/hifi/data-sources/elexon/itsdo.html`
  - `site/hifi/data-sources/elexon/mid.html`
  - `site/hifi/data-sources/elexon/ndf.html`
  - `site/hifi/data-sources/elexon/ndfd.html`
  - `site/hifi/data-sources/elexon/netbsad.html`
  - `site/hifi/data-sources/elexon/pn.html`
  - `site/hifi/data-sources/elexon/system_prices.html`
  - `site/hifi/data-sources/elexon/temp.html`
  - `site/hifi/data-sources/elexon/tsdf.html`
  - `site/hifi/data-sources/elexon/uou2t14d.html`
- Concrete examples:
  - `site/hifi/data-sources/elexon/boal.html` line 101–104: closing `</div>` for sidebar, then immediately a dangling `<div class="card" style="padding:20px;"><div class="tiny mb-8">PARAM STYLE</div>…` — no `</nav>`, no `<div class="main-content">`, no `<section id="overview">`.
  - Same pattern in `site/hifi/data-sources/elexon/indo.html` lines 103–106.
  - The sidebar links to `#overview`, `#schema`, `#sample`, `#api` (`site/hifi/data-sources/elexon/boal.html` lines 83–87) — all four anchors are dangling, so clicking them does nothing.
- Impact: The 16 broken pages will render with broken DOM (browser will auto-close some tags, but layout breaks — sidebar and main column run together). Sidebar navigation jumps land nowhere. Scroll-spy `IntersectionObserver` (lines 149–153 of `boal.html`) observes only `#caveats` and `#related`, so the "active" indicator misbehaves.
- Impact: site claims "28 datasets" (`site/hifi/data-sources/elexon.html` line 162) but only 22 dataset pages exist; of those, 6 are complete and 16 are partial. Real coverage is ~21% complete.
- Fix approach: Extract a Jinja-style template (or static-site generator like 11ty/Hugo) and re-render every page from the JSON manifest in `site/hifi/data/elexon.json` (which already enumerates all 28 datasets with id/title/freq/lag/rows). Until then: at minimum, fix DOM by adding the missing `</nav>`, `<div class="main-content">`, `<section id="overview">…</section>`, `<section id="schema">…</section>`, `<section id="sample">…</section>`, `<section id="api">…</section>` wrappers to the 16 stubs.

### Massive duplication of inline CSS across dataset pages

- Issue: Every one of the 22 `site/hifi/data-sources/elexon/*.html` files inlines a near-identical ~30-line `<style>` block defining `.schema-table`, `.data-table`, `.page-layout`, `.sidebar`, `.sidebar-section`, `.sidebar-section-title`, `.sidebar a`, `.main-content`, `.caveat-item`, `.caveat-num`, `.related-grid`. Compare `site/hifi/data-sources/elexon/boal.html` lines 12–41, `site/hifi/data-sources/elexon/indo.html` lines 12–41, `site/hifi/data-sources/elexon/system_prices.html` lines 12–41 — line-for-line identical.
- The `site/hifi/data-sources/elexon/fuelhh.html` version (lines 11–111) is a "long-form" but functionally equivalent superset that adds whitespace and a few extra rules (`.fuel-grid`, `.fuel-pill`).
- Files: All 22 files in `site/hifi/data-sources/elexon/`.
- Impact: ~660 lines of duplicated CSS. Any visual change to schema tables or sidebar requires editing 22 files. The in-flight refactor already hits this (every dataset page is in `git status M`).
- Fix approach: Move the dataset-page block into `site/hifi/assets/theme.css` (already injected on every page). Remove the inline `<style>` block from each dataset page. Leave only page-specific rules (e.g. `.fuel-grid` in `fuelhh.html`) inline if any.

### Hardcoded duplicated catalogue counts

- Issue: "7 vendors · 49 datasets" appears in three places that must be kept in sync by hand:
  - `site/hifi/assets/site.js` line 73 (footer): `last sync 2026-04-30 14:02 UTC · 7 sources · 49 datasets`
  - `site/hifi/data-sources.html` line 25: `Catalog · 7 vendors · 49 datasets`
  - `site/hifi/index.html` line 369–377: stat strip with "7 Vendors / 49 Datasets"
- Elexon-specific: "28 datasets" appears in `site/hifi/data-sources/elexon.html` lines 40, 82, 162; in `site/hifi/data-sources.html` line 79, 253; and `site/hifi/data/vendors.json` line 9. The on-disk evidence is 22 `.html` files (under `site/hifi/data-sources/elexon/`) for those 28 entries — the gap is undocumented.
- Impact: Counts drift from reality. The `site/hifi/data/elexon.json` manifest lists 25 dataset IDs in 4 groups (`fuelhh, fuelinst, agpt, agws, windfor, nonbm, system_prices, mid, boal, disbsad, netbsad, pn, indo, itsdo, indod, ndf, ndfd, tsdf, fou2t14d, uou2t14d, freq, temp, remit, bmunits_reference, soso`), but the catalog UI shows 28, and 22 pages exist. Three inconsistent counts.
- Fix approach: Generate `vendors.json` and `elexon.json` at build time and have the HTML compute counts from them (currently neither JSON is `fetch()`ed by any HTML — see "Unused JSON manifests" below).

### Unused JSON manifests

- Issue: `site/hifi/data/elexon.json` and `site/hifi/data/vendors.json` are static, hand-maintained, but **never fetched**. A grep for `fetch(` and the strings `vendors.json`/`elexon.json` across `site/` returns zero hits. The only place `fetch()` appears is inside an English sentence inside `site/hifi/architecture.html` line 1139 (`<code>fetch(dataset, start, end)</code>` describing the Python pipeline, not a JS call).
- Files: `site/hifi/data/elexon.json`, `site/hifi/data/vendors.json`.
- Impact: Dead data. Either the manifests were the planned source-of-truth and HTML rendering was never wired up, or they are a documentation artifact masquerading as data. Either way they will drift silently against the HTML.
- Fix approach: Either (a) delete and let the HTML be the source of truth, or (b) wire `site.js` to render the catalogue rows from JSON. Option (b) compounds nicely with template extraction (see "Massive duplication" above).

## Bugs

### Non-responsive viewport on 23 of 27 pages (mobile is broken)

- Issue: 23 pages set `<meta name="viewport" content="width=1280" />`, locking the layout to 1280px on mobile devices. Only 5 pages use the correct `<meta name="viewport" content="width=device-width, initial-scale=1" />`: `site/hifi/index.html` (line 6), `site/hifi/architecture.html` (line 6), `site/hifi/models/demand-forecast.html` (line 6), `site/hifi/data-sources/elexon.html` (line 6), `site/hifi/data-sources/elexon/fuelhh.html` (line 6).
- Broken pages (use `width=1280`): `site/hifi/data-sources.html` (line 6), and all 21 of the small/stub elexon dataset pages — `agpt.html, agws.html, boal.html, disbsad.html, fou2t14d.html, freq.html, fuelinst.html, indo.html, indod.html, itsdo.html, mid.html, ndf.html, ndfd.html, netbsad.html, nonbm.html, pn.html, system_prices.html, temp.html, tsdf.html, uou2t14d.html, windfor.html`. All at line 6.
- Impact: On phones and small tablets these pages render at 1280px wide and the user must pinch-zoom. The mobile CSS in `site/hifi/assets/theme.css` (`@media (max-width: 720px)` at line 634, `@media (max-width: 480px)` at line 716) and `site/hifi/index.html` (`@media (max-width: 720px)` at line 281) never fires for these pages because the viewport is forced to 1280.
- This is doubly bad because `site/hifi/assets/site.js` lines 101–116 carefully wires up a mobile menu toggle that will only appear under the mobile media query — i.e. nav becomes unusable on phones for 23 pages.
- Fix approach: Find-and-replace `width=1280` → `width=device-width, initial-scale=1` across all 23 files. Trivial and high-value.

### Footer "Catalogue · Carbon" link does not jump to a Carbon section

- Issue: `site/hifi/assets/site.js` line 62 emits `<a href="${root}data-sources.html#carbon">Carbon</a>` for every page footer. `site/hifi/data-sources.html` has no `id="carbon"` section; its three section IDs are `electricity` (line 56), `gas` (line 139), `weather` (line 191). The string `carbon` only appears as `id="carbon"` on the NESO vendor row inside the Electricity section (`site/hifi/data-sources.html` line 115) — so the link lands on a single card mid-page, not a section header.
- There is also no Gas page anywhere; `data-sources.html#gas` lands at section 02 of `data-sources.html` but none of the gas vendor rows link out: `site/hifi/data-sources.html` lines 146 and 167 both have `href="#"`.
- Files: `site/hifi/assets/site.js` (lines 59–62), `site/hifi/data-sources.html`.
- Impact: Footer navigation appears comprehensive but only Electricity is real.

### Many placeholder `href="#"` links

- Issue: Stub links that go nowhere:
  - `site/hifi/data-sources.html` line 93 — ENTSO-E vendor row: `<a href="#" id="entsoe">`. The card is the destination of its own self-anchor.
  - `site/hifi/data-sources.html` line 115 — NESO vendor row: `<a href="#" id="carbon">`.
  - `site/hifi/data-sources.html` line 146 — ENTSO-G: `<a href="#" id="entsog">`.
  - `site/hifi/data-sources.html` line 167 — GIE: `<a href="#" id="gie">`.
  - `site/hifi/data-sources.html` line 198 — Open-Meteo (no vendor page).
  - `site/hifi/data-sources.html` lines 630, 649, 668 — Elexon "remit", "bmunits_reference", "soso" dataset rows have `href="#"` (no dataset pages exist).
  - `site/hifi/data-sources.html` line 231 — `<span class="chip btn-like">Export CSV</span>` (purely cosmetic, no handler).
  - `site/hifi/data-sources.html` line 323 — "Suggest a new source →" `<a href="#">`.
- Impact: ~10 prominent navigation links that look interactive but do nothing. Misleads visitors about coverage.
- Fix approach: Either build the missing pages or replace `<a>` with a non-link element ("Coming soon" chip) so visitors aren't tricked.

### Sidebar self-link inconsistency

- Issue: In every elexon dataset stub, the sidebar lists a fixed subset of sibling datasets (varies by category), and the "current page" anchor uses `class="active"`. But the inactive siblings are styled `style="color:var(--ink-faint);"` which on hover only changes via `.sidebar a:hover { color: var(--ink); }` — the inline color overrides the `:hover` rule because inline style has higher specificity. Result: hovering inactive nav items in dataset sidebars produces no color change. See `site/hifi/data-sources/elexon/indo.html` lines 94–101 (the inline `color:var(--ink-faint)` wins over the CSS `:hover`).
- Files: All 22 dataset HTML files use the same pattern.
- Impact: Sidebar hover affordance is dead on dataset pages.
- Fix approach: Drop the inline `color` and add a CSS class (e.g. `.sidebar a.muted`) defined in `theme.css`.

### License contradicts itself

- Issue: `site/hifi/index.html` line 872 says `This site · static · MIT`, but `site/hifi/assets/site.js` line 72 (injected into every page footer) says `© 2026 E. Bentham · Personal project · Apache-2.0`.
- Impact: Reusers cannot tell which licence applies. There is also no `LICENSE` file in the repo root.
- Fix approach: Pick one; add a top-level `LICENSE`; align both strings.

### Hardcoded "live" timestamps that aren't live

- Issue: The site brands extensively as live but everything is static:
  - `site/hifi/index.html` line 329: hero card shows `2026-04-30 14:02 UTC` as a hardcoded timestamp.
  - `site/hifi/assets/site.js` line 73: footer hardcodes `last sync 2026-04-30 14:02 UTC` on every page.
  - 22 dataset pages each hardcode a "LAST FETCH" value: `boal.html:70` says `10 min ago`, `freq.html:70` says `1 min ago`, `indo.html:70` says `5 min ago`, etc. None of these are updated by any code.
  - Each dataset page also wears a `<span class="chip live" style="font-size:11px;">live · 30 min</span>` style badge (e.g. `site/hifi/data-sources/elexon/system_prices.html` line 56).
  - Only `site/hifi/data-sources/elexon/fuelhh.html` (post-edit, currently uncommitted) and `site/hifi/data-sources/elexon.html` line 121 admit "Static snapshot · live wiring planned".
  - `site/hifi/assets/site.js` line 48 hardcodes `v0.4.2 · build 2026.04.30` in the footer.
- Impact: A visitor in May 2026 (today) sees timestamps from 30 Apr 2026 still labelled "live" and "X minutes ago". Credibility hit.
- Fix approach: Two paths: (a) commit fully to honesty — relabel all `chip live` to `chip snapshot`, replace "X min ago" with "snapshot from YYYY-MM-DD", drop the "last sync" footer; or (b) actually wire a build-time injection of `Date.now()` into the templates. The in-flight `fuelhh.html` and the existing `site/hifi/index.html` line 357 (`Static snapshot · refreshed nightly`) suggest path (a) is the chosen direction.

## Security Considerations

### Static site, but XSS-style hardening would still be appropriate

- `site/hifi/assets/site.js` lines 80–81 use `document.body.insertAdjacentHTML("afterbegin", navHTML)` and `("beforeend", footerHTML)` where the templated strings only interpolate `root` (taken from `document.body.dataset.root`). The dataset values are author-controlled in the HTML (`data-root=""`, `data-root="../"`, `data-root="../../"`), not user input — so this is not exploitable. Worth noting in case future code starts reading query params or `location.hash` into the same template.
- `site/hifi/assets/charts.js` lines 113, 119, 142, 166, 199, 219, 247 all assign `el.innerHTML = svg`, where `svg` is built from `opts` parsed via `JSON.parse(el.dataset.opts)` (line 257). Same caveat: opts are author-controlled today, but the pattern is XSS-prone if those data attributes ever come from user input.
- Risk: Low today; flag if interactivity is added.

### Two `target="_blank"` links missing `rel="noopener"`

- Issue: Standard tab-jacking risk (the opened page can use `window.opener` to navigate this site).
  - `site/hifi/architecture.html` line 1156: `<a href="https://github.com" target="_blank" class="btn ghost">` — no `rel`.
  - `site/hifi/data-sources/elexon.html` line 41: `<a href="https://bmrs.elexon.co.uk/" target="_blank" class="btn ghost">` — no `rel`.
- The other 5 cross-origin links (`site/hifi/index.html` line 830, `site/hifi/models/demand-forecast.html` line 266, `site/hifi/assets/site.js` lines 66–68) do include `rel="noopener"`.
- Files: as above.
- Impact: Minor security/UX risk on those two links.
- Fix approach: Add `rel="noopener"` (or `rel="noopener noreferrer"`) to both.

### `gridflow-serve` is HTTP only, listens on all interfaces

- Issue: `src/gridflow_front_end/serve.py` line 83 binds `("", args.port)` — i.e. `0.0.0.0`. The intent (from the docstring at lines 1–7) is "one-command local server", and the browser is opened to `http://localhost:{port}/` (line 79). But the bind exposes the site to any other host on the LAN.
- Files: `src/gridflow_front_end/serve.py`.
- Impact: Low (the site is static and public anyway), but unexpected. Could be sharing localhost-only artifacts in the future.
- Fix approach: Bind to `("127.0.0.1", args.port)` by default; add `--host 0.0.0.0` opt-in flag.

### No secrets present

- Verified: No `.env` file, no `credentials.*`, no `*.pem`, no inline `API_KEY` strings. `.gitignore` covers `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, `build/`, `.idea/`. Currently no risk.

## Performance Bottlenecks

### Each dataset page reloads Google Fonts and the asset bundle

- Issue: Every HTML file has its own `<link>` to Google Fonts (3 families combined into one stylesheet URL — `Fraunces`, `Inter`, `JetBrains+Mono`) and to `assets/theme.css`. With browser caching this is fine, but cold loads do 4 round-trips before first render (`preconnect` + fonts CSS + font files + theme.css), and the fonts stylesheet imports several font weight variants per family.
- Files: every `.html` in `site/hifi/`.
- Impact: ~1–2 s cold-load TTI penalty over a slow link. First Contentful Paint blocked on font CSS.
- Fix approach: Add `font-display: swap` via the Google Fonts URL (`&display=swap` is already there, OK). Consider self-hosting the fonts under `site/hifi/assets/fonts/` to drop the cross-origin round-trips.

### Inline SVGs and big single-page HTML

- Issue: `site/hifi/architecture.html` is 1178 lines (the architecture SVG alone in lines around 338 is large) and `site/hifi/models/demand-forecast.html` is 938 lines; `site/hifi/index.html` is 883 lines. These pages all inline CSS, decorative SVG, and content into one document.
- Files:
  - `site/hifi/architecture.html` — 1178 lines.
  - `site/hifi/models/demand-forecast.html` — 938 lines.
  - `site/hifi/index.html` — 883 lines.
  - `site/hifi/data-sources/elexon.html` — 751 lines.
  - `site/hifi/data-sources/elexon/fuelhh.html` — 648 lines.
- Impact: ~50–100 KB initial HTML payload (uncompressed) per page. Not critical for a static site but worth flagging.
- Fix approach: Most inline SVG (e.g. the chart helpers in `site/hifi/assets/charts.js`) is rendered into elements with `data-chart="…"` markers, which is fine. The architecture system diagram could move to a standalone `.svg` file linked via `<img>` if it's ever re-used elsewhere.

## Fragile Areas

### "Schema/sample/api" sections only exist on 6 pages, sidebar always offers all 6 anchors

- Issue: The dataset page sidebar template (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) is hard-coded across all 22 pages. On the 16 stub pages the first four anchors lead nowhere because the sections were never written. See `site/hifi/data-sources/elexon/boal.html` lines 83–88 for the sidebar definition; lines 131–144 for the only sections that actually exist (`#caveats`, `#related`).
- Files: All 22 dataset pages.
- Why fragile: Anyone fixing one stub by hand also needs to remember to add the matching anchors. The sidebar `IntersectionObserver` (e.g. `boal.html` lines 149–153) also assumes every observed section exists.
- Safe modification: Treat the dataset page as a template; do not edit pages individually for structural changes. Or: convert the sidebar so it only shows links for sections that exist (would need JS — currently it's hard-coded HTML).
- Test coverage: None — there is no HTML lint, no link checker, no Playwright smoke test. The deploy workflow `.github/workflows/deploy.yml` simply uploads `site/hifi/` to Pages.

### Sidebar sibling lists are hand-curated per page

- Issue: Every dataset page's sidebar repeats the list of sibling datasets in its category, manually. `boal.html` lines 92–99 lists 6 sibling links; `indo.html` lines 94–101 lists 8. When a new dataset is added, every page in that category must be edited.
- Files: All 22 dataset pages.
- Why fragile: Synchronisation burden grows with the number of datasets.
- Safe modification: Either generate the sidebar from `site/hifi/data/elexon.json` at build time, or move the per-category navigation into a client-side `site.js` helper that reads the JSON manifest.

### `data-page` / `data-root` body attributes drive navigation injection

- Issue: `site/hifi/assets/site.js` lines 6–7 reads `document.body.dataset.page` and `data-root` to build nav and footer. If either is wrong, navigation breaks subtly:
  - Wrong `data-root="../"` on a depth-2 page → broken nav links.
  - Wrong `data-page="dataset"` (used to highlight the "Catalogue" nav item, per `site.js` lines 84–93) — currently no schema is enforced; misspelling silently disables active-link highlighting.
- Files: every page sets these in its `<body>` tag (e.g. `site/hifi/data-sources/elexon/boal.html` line 43: `<body data-page="dataset" data-root="../../" data-screen-label="12 Dataset · boal">`).
- Why fragile: Two manual config strings per page, easy to mis-paste during the kind of bulk refactor in flight.
- Safe modification: Add a JS sanity check at the top of `site.js` that warns in the console if `data-root` doesn't resolve to a known file (e.g. `index.html` 404s).

### Two scroll-spy snippets, one minified, one not

- Issue: 16 of the stub dataset pages embed a hand-minified scroll-spy:
  ```html
  <script>(function(){const s=document.querySelectorAll("section[id]"),l=document.querySelectorAll(".sidebar a[href^='#']"),o=new IntersectionObserver(...)})();</script>
  ```
  (See `site/hifi/data-sources/elexon/indo.html` line 150.)
  The 6 complete pages embed the **un-minified** variant:
  ```html
  <script>(function(){const sections=document.querySelectorAll("section[id]");...})();</script>
  ```
  (See `site/hifi/data-sources/elexon/boal.html` lines 148–154 — though `boal.html` is itself in the broken group, it has the un-minified script. So actually both variants are scattered.)
- Files: All 22 dataset pages, two variants of the same script.
- Why fragile: Bug fixes have to be applied twice.
- Fix approach: Move the helper into `site/hifi/assets/site.js` and gate by `data-page="dataset"` or by the presence of `.sidebar`.

### Tabs implemented with global `setTab(group, tab, btn)` plus inline `onclick`

- Issue: 22 dataset pages define `setTab(group, tab, btn)` as a global function at the bottom of the file (e.g. `site/hifi/data-sources/elexon/boal.html` lines 156–166, `indo.html` lines 153–163) and call it via inline `onclick="setTab('boal','url',this)"` (e.g. `boal.html` lines 107–109). Every page redeclares the same function.
- Files: All 22 dataset pages.
- Why fragile: Bug fixes have to be applied 22 times. The home page (`site/hifi/index.html`) uses a different tab system (`[data-tabs]` discovered by `site.js` lines 136–147) so the two patterns diverge.
- Fix approach: Convert dataset-page tabs to the same `[data-tabs]` convention and delete the per-page `setTab` declarations and inline `onclick` handlers.

## Scaling Limits

### Manual dataset-page authoring scales O(N×regions)

- Issue: Each new vendor multiplies the manual page-authoring burden — Elexon alone has 22 partial pages and a vendor index. Adding ENTSO-E (14 datasets), ENTSO-G, GIE, Open-Meteo, NESO at the same fidelity is roughly 49 dataset pages × ~150–650 lines each.
- Files: anticipated under `site/hifi/data-sources/{entsoe,entsog,gie,openmeteo,neso}/*.html`.
- Impact: At the current per-page style this is several thousand more lines of duplicated HTML.
- Scaling path: A static-site generator (11ty, Astro, Hugo, or even a small Python script that templates against `site/hifi/data/*.json`) becomes essentially mandatory before adding a second vendor.

## Accessibility Gaps

### Missing `<main>`, `<header>`, `<aside>` landmarks

- Issue: Pages use `<section class="block">` rather than semantic landmarks. There is no `<main>` element on any page. Screen readers get a flat document. The only semantic landmark is `<nav>` (injected by `site.js`) and `<footer>` (also injected). The sidebar in dataset pages uses `<nav class="sidebar">` (e.g. `site/hifi/data-sources/elexon/boal.html` line 80), which is technically two `<nav>` elements per dataset page without `aria-label` to distinguish them.
- Files: every HTML page in `site/hifi/`.
- Impact: Screen-reader and keyboard navigation are degraded.
- Fix approach: Wrap the primary page content in `<main>`. Label both `<nav>`s (`aria-label="Site"` for the injected one, `aria-label="On this page"` for the sidebar).

### No `aria-current` on active nav links

- Issue: `site/hifi/assets/site.js` line 97 marks the active link with `link.classList.add("active")` but never sets `aria-current="page"`. Screen readers cannot tell which page is current. Same on the sidebar (`boal.html` line 83 — class `active`, no `aria-current="location"`).
- Files: `site/hifi/assets/site.js`, all dataset pages.
- Impact: A11y violation (WCAG 2.4.8).

### Decorative SVG and icon spans lack `aria-hidden`

- Issue: Many icon-only spans (e.g. `<span class="arrow">→</span>` repeated dozens of times in `site/hifi/data-sources.html`, `site/hifi/data-sources/elexon.html`, and dataset pages) carry visible right-arrow glyphs but no `aria-hidden="true"`. Screen readers will read out "right arrow" for each card. Same for `<span class="dot live">` chips and the inline `<svg>` icons in `site/hifi/assets/site.js` (nav-toggle hamburger lines 23–27).
- Files: every page.
- Impact: Verbose, noisy reading order for screen-reader users.
- Fix approach: Decorate purely-cosmetic icons with `aria-hidden="true"`.

### Single `aria-labelledby` usage

- `site/hifi/architecture.html` line 338 sets `role="img" aria-labelledby="arch-title arch-desc"` on one SVG. Good. The pattern is not applied elsewhere.

### No `<img alt>` because no `<img>`

- Verified: zero `<img>` tags in the entire site. All visuals are inline SVG, CSS gradients, or coloured `<div>`s. No `alt` audit needed.

### No `<title>` strategy / no favicon

- Issue: No `<link rel="icon">`, no `apple-touch-icon`, no `theme-color` meta. Bookmarks show a default browser icon.
- Files: every HTML page.
- Fix approach: Add `site/hifi/assets/favicon.svg` (single colour to match `--accent`) and a `<link rel="icon">` to each page (or inject via `site.js`).

### Color-only signalling

- Issue: The "Shipping" vs "Planned" status on `site/hifi/index.html` lines 681 and 694 differs only by colour (`.stage.ship { color: var(--accent); }` versus default `color: var(--ink-soft);`). The dot is present in both cases. Same story on chip-live vs chip — same shape, only colour separates them.
- Files: `site/hifi/index.html`, theme.css.
- Impact: Users with red-green or low-contrast colour vision cannot tell shipping from planned.
- Fix approach: Add a glyph or text suffix (e.g. "(live)" or a different icon) for live status.

## Documentation Gaps

### No top-level README

- Issue: No `README.md`, no `LICENSE`, no `CONTRIBUTING.md`. The repo root has only `pyproject.toml`, `site/`, `src/`. A visitor cloning the repo has no entry-point doc.
- Fix approach: Add a minimal `README.md` describing `gridflow-serve`, the `site/hifi/` layout, and how to deploy.

### `# TODO` in About blurb

- Issue: `site/hifi/index.html` line 808: `<!-- TODO: replace 'E. Bentham' with your full legal name -->`.
- Impact: The placeholder is visible to maintainers but the page already renders "E. Bentham, here." — it's unclear if this is the final form. The same name appears in three other places without a TODO (`site/hifi/assets/site.js` line 72, `site/hifi/index.html` line 829's `https://github.com/EBentham`, etc.). Decide and clean up the TODO.

### Documentation drift / contradictions

- `site/hifi/index.html` line 384 says `0 Cloud deps` but `site/hifi/assets/site.js` line 71 says `© 2026 E. Bentham · Personal project · Apache-2.0` and `site.js` loads Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`) from `site/hifi/index.html` lines 8–10. Two cross-origin cloud dependencies (fonts CDN) exist.
- Fix approach: Either self-host fonts to make the "0 cloud deps" claim true, or refine the wording (e.g. "0 build/CI cloud dependencies").

## Test Coverage Gaps

### Zero tests, zero CI other than deploy

- Issue: No `tests/`, no `pytest` invocation in `pyproject.toml`, no lint config (`ruff`, `eslint`, `htmlhint`), no link checker, no HTML validator. The only workflow is `.github/workflows/deploy.yml` (lines 1–34) which uploads `site/hifi/` to GitHub Pages with zero validation.
- Files: missing — see absence of `tests/`, `.github/workflows/*.yml` besides `deploy.yml`.
- Risk: Broken pages ship to production. The 16 broken dataset pages would have been caught by a trivial HTML validator or by a Playwright smoke test that visits each page and checks for the expected `#overview` heading.
- Priority: High — adds confidence cheaply.
- Fix approach: Add a workflow that runs `htmlhint site/hifi/**/*.html` and a linkchecker (`lychee site/hifi`) on every push. Optional: a Playwright job that loads each page and asserts the title-tag, the presence of `<footer>` (since `site.js` injects it), and that no anchor href resolves to a 404.

### No Python tests for `gridflow_front_end.serve`

- Issue: `src/gridflow_front_end/serve.py` has no test file. Risk areas: `_SITE_DIR` path-resolution (line 23) — if the package is installed elsewhere via uv, the `_PACKAGE_DIR.parent.parent` arithmetic will yield the wrong root.
- Files: `src/gridflow_front_end/serve.py`, `src/gridflow_front_end/__init__.py`.
- Risk: `gridflow-serve` fails when installed as a wheel rather than editable. The error message at lines 70–74 is at least clear.
- Priority: Low (this is a one-off dev server), but a `pytest` smoke test that imports the module and calls `_SITE_DIR.is_dir()` would catch packaging regressions.

---

*Concerns audit: 2026-05-17*
