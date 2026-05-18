<!-- refreshed: 2026-05-17 -->
# Architecture

**Analysis Date:** 2026-05-17

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        Author / Editor                              │
│  Edits hand-written HTML in `site/hifi/**.html` + assets             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Static site source (the artefact)                │
│  `site/hifi/`  — HTML pages · `assets/` (theme.css, site.js,         │
│                  charts.js) · `data/` (JSON manifests)               │
└────────────┬─────────────────────────────────┬──────────────────────┘
             │ local                            │ on push to `main`
             ▼                                  ▼
┌─────────────────────────────┐   ┌─────────────────────────────────────┐
│  Python dev server          │   │  GitHub Pages deploy                │
│  `gridflow-serve` CLI       │   │  `.github/workflows/deploy.yml`     │
│  `src/gridflow_front_end/   │   │  uploads `site/hifi` as the         │
│   serve.py`                 │   │  Pages artefact                     │
│  → `http://localhost:8765`  │   │  → public Pages URL                 │
└──────────────┬──────────────┘   └─────────────────────┬───────────────┘
               │                                        │
               └────────────────────┬───────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            Browser                                  │
│  Loads any page → at runtime `assets/site.js` reads the body        │
│  `data-page` / `data-root` attributes and injects nav + footer.     │
│  `assets/charts.js` walks `[data-chart]` elements and draws         │
│  deterministic inline SVG charts. `assets/theme.css` is the         │
│  single shared stylesheet.                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Dev server CLI | Bind a `SimpleHTTPRequestHandler` to a port, chdir into the site root, open a browser. Logs are silenced except for errors. | `src/gridflow_front_end/serve.py` |
| Package shell | Names the Python package; ships an empty `__init__.py` (no runtime logic). | `src/gridflow_front_end/__init__.py` |
| Package metadata | Declares the `gridflow-serve` console script entry point and `setuptools` config. | `pyproject.toml` |
| GitHub Pages deploy | On push to `main`, upload `site/hifi/` directly as the Pages artefact. | `.github/workflows/deploy.yml` |
| Site root / home | Hero, pillar tiles, architecture preview, catalogue preview, models list, query examples, about. | `site/hifi/index.html` |
| Architecture page | Long-form design document for the `gridflow` data pipeline (the project the site documents). | `site/hifi/architecture.html` |
| Catalogue hub | Cross-vendor index linking through to each vendor page. | `site/hifi/data-sources.html` |
| Vendor hub | Per-vendor landing with metadata, featured chart, and a card grid of that vendor's datasets. | `site/hifi/data-sources/elexon.html` |
| Dataset page | Full per-dataset reference: hero, stats strip, sidebar layout, overview, schema, sample, caveats, related. | `site/hifi/data-sources/elexon/<slug>.html` (×23) |
| Model case study | Long-form write-up for one model (currently demand forecast). | `site/hifi/models/demand-forecast.html` |
| Shared chrome | Reads `body[data-page]` / `body[data-root]` and injects `<nav>` + `<footer>` with correctly-prefixed links; marks the active nav item; wires copy buttons, tabs, and the mobile menu toggle. | `site/hifi/assets/site.js` |
| Chart renderer | Walks `[data-chart]` elements and renders deterministic, seeded inline SVG (stacked area, sparkline, donut, etc.). No interactivity. | `site/hifi/assets/charts.js` |
| Theme | Single shared stylesheet — design tokens (`--paper`, `--ink`, `--accent`), typography, layout primitives (`.container`, `.block`, `.row`, `.stack-*`, `.card`, `.chip`, `.btn`, `.crumbs`). | `site/hifi/assets/theme.css` |
| Catalogue manifests | JSON ground-truth listings for vendors and Elexon datasets. Not consumed by any HTML or JS at runtime — kept as authoritative reference next to the hand-written cards. | `site/hifi/data/vendors.json`, `site/hifi/data/elexon.json` |

## Pattern Overview

**Overall:** Hand-written static HTML site with a thin runtime-templating layer (one JS file) that injects shared chrome from a per-page data-attribute contract. Served locally by a 100-line Python wrapper around `http.server`; deployed by GitHub Pages directly off `site/hifi/`.

**Key Characteristics:**
- Zero build step. There is no bundler, no SSG (Astro/11ty/Hugo), no Jinja, no markdown pipeline. HTML files are the source.
- Single asset bundle. Every page loads exactly one stylesheet (`assets/theme.css`) and two scripts (`assets/site.js`, `assets/charts.js`).
- Body-data-attribute contract is the template engine. Each page declares `data-page`, `data-root`, and `data-screen-label` on `<body>`; `site.js` reads those and injects the nav + footer with correct relative paths.
- Charts are deterministic SVG drawn from `data-opts` seeds — no live data, no fetches, no canvas.
- Deploy target is exactly the `site/hifi/` subtree — the Python package and `src/` are not deployed.
- Naming pre-allocates `hifi/` for a future `lofi/` sibling; only `hifi/` currently exists.

## Layers

**Source / authoring (filesystem):**
- Purpose: The HTML pages, assets, and JSON manifests that constitute the site.
- Location: `site/hifi/`
- Contains: HTML pages, `assets/` (CSS + JS), `data/` (catalogue manifests)
- Depends on: nothing
- Used by: the dev server, the GitHub Pages deploy

**Dev server (Python, optional):**
- Purpose: One-command local preview with auto-browser-open.
- Location: `src/gridflow_front_end/serve.py`
- Contains: argparse CLI, `SimpleHTTPRequestHandler` subclass that silences per-request logs, browser launcher.
- Depends on: Python 3.11+ stdlib only (no third-party deps, see `pyproject.toml`).
- Used by: the developer via `gridflow-serve` (console script declared in `pyproject.toml`).

**Deploy (GitHub Actions → Pages):**
- Purpose: Publish the static site on push to `main`.
- Location: `.github/workflows/deploy.yml`
- Contains: `actions/configure-pages`, `actions/upload-pages-artifact` (with `path: site/hifi`), `actions/deploy-pages`.
- Depends on: `site/hifi/` existing in the repo.
- Used by: the public Pages URL.

**Runtime (browser, per page load):**
- Purpose: Resolve relative paths, inject nav/footer, render charts, wire interactive widgets.
- Location: `site/hifi/assets/site.js`, `site/hifi/assets/charts.js`
- Contains: nav/footer template strings, copy-button + tab handlers, deterministic SVG chart functions.
- Depends on: each page exposing `data-page`/`data-root` on `<body>` and the expected DOM containers (`[data-chart]`, `[data-tabs]`, `.code-wrap`).
- Used by: every HTML page that includes both scripts.

## Data Flow

### Local preview path

1. User runs `gridflow-serve` (or `gridflow-serve --port 9000`) — entry point declared in `pyproject.toml:13` → `gridflow_front_end.serve:main`.
2. `main()` parses args, validates that `_SITE_DIR = <project>/site/hifi` exists, and `os.chdir(_SITE_DIR)` (`src/gridflow_front_end/serve.py:23,77`).
3. A `_SilentHandler` (a `SimpleHTTPRequestHandler` with `log_message` silenced) is bound to the port (`serve.py:26-35,83`).
4. A daemon thread waits 0.5 s and opens the default browser at `http://localhost:<port>/` unless `--no-open` was passed (`serve.py:38-48,93`).
5. The browser requests `/` → `site/hifi/index.html` is served.
6. Browser resolves `<link rel="stylesheet" href="assets/theme.css">` and `<script src="assets/site.js">` / `assets/charts.js` against the current URL.

### Page-load chrome injection

1. Browser parses an HTML page; `<body>` carries `data-page="<type>"`, `data-root="<relative prefix>"`, and `data-screen-label="<NN Type · slug>"`.
2. `assets/site.js` (IIFE) reads `document.body.dataset.page` and `document.body.dataset.root` (`site.js:6-7`).
3. Template literals construct `navHTML` and `footerHTML`, each prefixing every internal `href` with `${root}` so links resolve correctly from any depth (root, `../`, or `../../`) (`site.js:9-77`).
4. `insertAdjacentHTML("afterbegin", navHTML)` and `("beforeend", footerHTML)` graft them into the document (`site.js:80-81`).
5. The active nav item is set by mapping `data-page` → `data-key` and toggling `.active` (`site.js:84-99`).
6. Mobile menu toggle, copy buttons on `.code-wrap`, and tab groups on `[data-tabs]` are wired (`site.js:101-147`).

### In-page chart rendering

1. After `site.js` runs, `assets/charts.js` walks the DOM for `[data-chart]` elements and reads each one's `data-opts` JSON (e.g. `data-chart="stackedArea" data-opts='{"width":880,"height":280}'`, `index.html:332`).
2. A deterministic seeded RNG (`rng(seed)`, `charts.js:24-30`) produces stable values so charts render identically across reloads.
3. Inline SVG is constructed and injected into the element. There is no streaming, no live data, no fetch.

### Page hierarchy and navigation

```text
L1   site/hifi/index.html                          (home, data-page="home", data-root="")
       │
       ├─ L2 site/hifi/architecture.html           (data-page="architecture", data-root="")
       │
       ├─ L2 site/hifi/data-sources.html           (catalogue hub, data-page="sources", data-root="")
       │       │
       │       ├─ L3 site/hifi/data-sources/elexon.html
       │       │       (vendor hub, data-page="vendor", data-root="../")
       │       │       │
       │       │       └─ L4 site/hifi/data-sources/elexon/<slug>.html  (×23)
       │       │             (data-page="dataset", data-root="../../")
       │       │
       │       └─ stubs for entsoe, entsog, gie, openmeteo, neso
       │             (in-page anchors `#entsoe` etc.; per-vendor pages not yet authored)
       │
       └─ L2 site/hifi/models/demand-forecast.html (data-page="model", data-root="../")
```

**State Management:**
- None at the application level. Every page is a fresh load; there is no client-side router, no SPA shell, no `history.pushState`, no localStorage usage.
- Per-page interactive state (active tab, mobile menu open/closed) lives in DOM classes added by `site.js`.

## Key Abstractions

**The `body[data-page]` / `body[data-root]` contract:**
- Purpose: A page declares its identity and its depth-back-to-root; `site.js` uses both to inject nav/footer with correctly-prefixed `href`s and to highlight the active nav item.
- Allowed `data-page` values (mapped in `site.js:86-93`): `home`, `architecture`, `sources`, `vendor`, `dataset`, `model`, `about`.
- `data-root` values: `""` for files directly in `site/hifi/`; `"../"` for `site/hifi/data-sources/elexon.html` and `site/hifi/models/demand-forecast.html`; `"../../"` for `site/hifi/data-sources/elexon/<slug>.html`.
- `data-screen-label` follows `"NN Type · slug"` (e.g. `"04 Dataset · fuelhh"`, `fuelhh.html:113`) — sequence identifiers used by the design-tool screenshot harness, not load-bearing for the runtime.
- Examples: `index.html:300`, `architecture.html:257`, `data-sources.html:12`, `data-sources/elexon.html:12`, `data-sources/elexon/fuelhh.html:113`, `models/demand-forecast.html:232`.

**Dataset page section template (informal, by convention):**
- Each `site/hifi/data-sources/elexon/<slug>.html` repeats the same skeleton:
  1. Breadcrumbs (`Gridflow / Data sources / Elexon BMRS / <slug>`)
  2. Hero: eyebrow + display title + lede + metadata card (silver path, API path, param style, earliest data, volume, primary key / last fetch)
  3. Stats strip (5 cells: resolution, lag, rows/month, history, ...)
  4. Two-column sidebar layout (`.page-layout` → `.sidebar` + `.main-content`)
  5. Sections: Overview, Snapshot chart, Schema, Sample data, (Fuel types / category-specific), API & ingestion, Caveats, Related datasets
- Sidebar navigates within-page (`#overview`, `#schema`, ...) and lists sibling datasets.
- Reference example: `site/hifi/data-sources/elexon/fuelhh.html` (621 lines, the most fully fleshed-out variant).

**The two catalogue manifests:**
- `site/hifi/data/vendors.json` — array of 7 vendor objects (id, name, region, domain, auth, dataset count, rate limit, base URL, tagline, earliest, rows/day, last fetch).
- `site/hifi/data/elexon.json` — Elexon datasets grouped by category (Generation, Prices & Balancing, Demand & Forecasts, System & Reference).
- Status: not referenced by any `.html` or `.js` file in the repo. They exist as the authoritative spec while the corresponding HTML cards remain hand-written.

**Pre-allocated `hifi/` namespace:**
- The site root is `site/hifi/`, not `site/`. There is no `site/lofi/`. The naming reserves a sibling slot for a future low-fidelity variant; today the deploy and the dev server both point exclusively at `site/hifi/`.

## Entry Points

**Local dev server CLI:**
- Location: `src/gridflow_front_end/serve.py:51-100` (`main()`); console script `gridflow-serve` declared at `pyproject.toml:13`.
- Triggers: developer invocation (`gridflow-serve`, optionally `--port`, `--no-open`).
- Responsibilities: validate the site dir exists, chdir into it, bind a silent `HTTPServer`, optionally open the browser, serve until `Ctrl+C`.

**GitHub Pages deploy workflow:**
- Location: `.github/workflows/deploy.yml`
- Triggers: `push` to `main`, or manual `workflow_dispatch`.
- Responsibilities: checkout, `actions/configure-pages`, upload `site/hifi` as the Pages artefact, deploy.

**Site entry HTML:**
- Location: `site/hifi/index.html`
- Triggers: a browser hitting `/` against the dev server or the deployed Pages URL.
- Responsibilities: hero, the three "pillar" tiles linking to architecture / catalogue / model, scope strip, architecture preview, vendor preview, models list, query-examples tab group, about section.

## Architectural Constraints

- **No build step.** Every change is a hand-edit to an HTML file. There is no compile, no template render, no minification. The `pyproject.toml` declares zero runtime dependencies (`pyproject.toml:10`).
- **Python 3.11+ for the dev server.** `requires-python = ">=3.11"` (`pyproject.toml:9`). Stdlib only.
- **Deploy path is hard-coded to `site/hifi/`.** Both `serve.py:23` (`_SITE_DIR = _PROJECT_ROOT / "site" / "hifi"`) and `deploy.yml:30` (`path: site/hifi`). Moving the site root requires editing both.
- **Per-page relative paths must match `data-root`.** Every `<link rel="stylesheet">` and `<script src=...>` in a dataset page (`../../assets/theme.css`) and every internal `<a href>` must match the depth implied by `data-root`. Get this wrong and chrome injection produces broken links.
- **Nav is hardcoded in JS, not driven by content.** `site.js:17-20` lists `architecture`, `sources`, `model`, `about` and the model link is pinned to `models/demand-forecast.html`. Adding new top-level sections or new models requires editing `site.js`.
- **Stub vendor links.** On `data-sources.html`, only the Elexon card links to a real vendor page; ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO use in-page anchors (`href="#entsoe"` etc.) and have no per-vendor pages. (`data-sources.html:93,569` and similar.)
- **Charts are static visuals.** `charts.js` uses deterministic seeded RNG to produce identical SVG on every render. There is no live data path; the "live" chips in the UI are aspirational labels.
- **No global mutable state.** Each page starts from a clean DOM; `site.js` runs once in an IIFE and exposes nothing on `window`.
- **No client-side router or SPA shell.** Every navigation is a full page load.

## Anti-Patterns

### Inline `<style>` blocks duplicated across dataset pages

**What happens:** Each `site/hifi/data-sources/elexon/<slug>.html` carries a near-identical inline `<style>` block defining `.schema-table`, `.data-table`, `.fuel-pill`, `.page-layout`, `.sidebar`, `.main-content`, `.caveat-item`, `.related-grid`. Compare `data-sources/elexon/agpt.html:12-47` with `data-sources/elexon/boal.html:12-41` — same rules, repeated.
**Why it's wrong here:** Touching a dataset-page style means editing every Elexon dataset HTML file. Drift between pages is hard to spot.
**Do this instead:** Move shared dataset-page styles into `site/hifi/assets/theme.css` (e.g. under a new `/* ── dataset pages ── */` section) and delete the inline blocks. Page-specific tweaks can stay inline.

### Stub vendor anchors instead of pages

**What happens:** `site/hifi/data-sources.html` advertises 7 vendors but only Elexon has a real page. The others link to in-page anchors (`href="#entsoe"`, `href="#entsog"`, `href="#gie"`, etc., `data-sources.html:93,569`) and have no `data-sources/<vendor>.html` file.
**Why it's wrong here:** Users following the catalogue land on `#anchor` and discover the page just scrolls — there is no vendor detail or dataset list for them.
**Do this instead:** Mirror the Elexon pattern. Create `site/hifi/data-sources/<vendor>.html` (with `data-page="vendor"` and `data-root="../"`) and update the link on the catalogue hub. For datasets, create `site/hifi/data-sources/<vendor>/<slug>.html` files.

### Hardcoded model link in the nav

**What happens:** `site/hifi/assets/site.js:19` pins the "Models" nav link to `${root}models/demand-forecast.html`. Adding a second model means picking which one is the canonical destination or hand-editing `site.js`.
**Why it's wrong here:** The nav doesn't reflect what's in `models/` — it reflects what the JS literal happens to point at.
**Do this instead:** Either promote a top-level `site/hifi/models.html` index and link the nav at that, or accept the constraint that `models/demand-forecast.html` is the entry while there is only one model.

### Catalogue manifests not wired to the cards

**What happens:** `site/hifi/data/vendors.json` and `site/hifi/data/elexon.json` enumerate the same vendors and datasets that are repeated in HTML cards across `data-sources.html`, `data-sources/elexon.html`, and the home page. Both must be edited together; nothing enforces this.
**Why it's wrong here:** The manifests look authoritative but are inert. Adding a dataset in JSON has zero effect on the rendered site.
**Do this instead:** Either remove the manifests, or generate the vendor / dataset cards from them at runtime (a small `fetch('data/vendors.json')` pass in `site.js`) so JSON becomes the single source of truth.

## Error Handling

**Strategy:** Best-effort and explicit-exit for the Python server; the static site has no runtime error surface to handle.

**Patterns:**
- `gridflow-serve` exits non-zero with a human-readable message when `site/hifi/` is missing (`serve.py:70-74`) or when the port is taken (`serve.py:84-88`).
- `_SilentHandler.log_error` writes `[gridflow-serve] ERROR: ...` to stderr but `log_message` is intentionally silent (`serve.py:29-35`).
- `KeyboardInterrupt` triggers a clean `server.server_close()` and a "Stopped." message (`serve.py:97-100`).
- The browser-side scripts (`site.js`, `charts.js`) wrap nothing — they assume the DOM contract holds. Bad `data-opts` JSON would throw at `JSON.parse` time.

## Cross-Cutting Concerns

**Logging:** Dev server silences per-request lines and only surfaces errors to stderr (`serve.py:29-35`). Browser scripts log nothing.
**Validation:** None at runtime. The author validates page structure by eye in the browser; the body-data-attribute contract is unenforced — a missing `data-root` produces silently-broken chrome links.
**Authentication:** None. The dev server is unauthenticated; the deployed Pages site is fully public.
**Asset versioning:** None. There are no cache-busting query strings on `theme.css` / `site.js` / `charts.js`; redeploys rely on browser cache invalidation by `actions/deploy-pages`.

---

*Architecture analysis: 2026-05-17*
