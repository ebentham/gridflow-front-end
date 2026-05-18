# Codebase Structure

**Analysis Date:** 2026-05-17

## Directory Layout

```text
gridflow-front-end/
├── .github/
│   └── workflows/
│       └── deploy.yml             # GitHub Pages deploy on push to main
├── .gitignore                     # Ignores .venv/, __pycache__/, *.egg-info, etc.
├── pyproject.toml                 # Python package metadata + `gridflow-serve` script
├── src/
│   └── gridflow_front_end/
│       ├── __init__.py            # Empty package marker (docstring only)
│       └── serve.py               # `gridflow-serve` CLI (stdlib http.server)
└── site/
    └── hifi/                      # The deployed site root (Pages artefact path)
        ├── index.html             # L1 home
        ├── architecture.html      # L2 design document
        ├── data-sources.html      # L2 catalogue hub
        ├── assets/
        │   ├── theme.css          # Shared design tokens + layout primitives
        │   ├── site.js            # Injects nav + footer per page; wires tabs/copy/menu
        │   └── charts.js          # Deterministic seeded inline-SVG renderers
        ├── data/
        │   ├── vendors.json       # 7-vendor manifest (reference, not consumed at runtime)
        │   └── elexon.json        # Elexon datasets grouped by category
        ├── data-sources/
        │   ├── elexon.html        # L3 vendor hub (only vendor with one today)
        │   └── elexon/            # L4 per-dataset pages
        │       ├── agpt.html
        │       ├── agws.html
        │       ├── boal.html
        │       ├── disbsad.html
        │       ├── fou2t14d.html
        │       ├── freq.html
        │       ├── fuelhh.html      # most fully fleshed-out reference page
        │       ├── fuelinst.html
        │       ├── indo.html
        │       ├── indod.html
        │       ├── itsdo.html
        │       ├── mid.html
        │       ├── ndf.html
        │       ├── ndfd.html
        │       ├── netbsad.html
        │       ├── nonbm.html
        │       ├── pn.html
        │       ├── system_prices.html   # note: snake_case (matches Elexon code)
        │       ├── temp.html
        │       ├── tsdf.html
        │       ├── uou2t14d.html
        │       └── windfor.html         # 23 dataset pages total
        └── models/
            └── demand-forecast.html     # L2 model case study (kebab-case slug)
```

## Directory Purposes

**`.github/workflows/`:**
- Purpose: GitHub Actions workflows.
- Contains: `deploy.yml` only.
- Key files: `.github/workflows/deploy.yml` — uploads `site/hifi` as the Pages artefact on push to `main`.

**`src/gridflow_front_end/`:**
- Purpose: The Python package that ships the `gridflow-serve` console script.
- Contains: `__init__.py` (just a docstring) and `serve.py` (the CLI).
- Key files: `src/gridflow_front_end/serve.py` (~100 lines, stdlib only).

**`site/`:**
- Purpose: Container for the static site. Only `hifi/` exists today; the directory name reserves a slot for a future `site/lofi/` sibling.
- Contains: `hifi/`.

**`site/hifi/`:**
- Purpose: The actual deployed site root. Both the dev server (`serve.py:23`) and the Pages deploy (`.github/workflows/deploy.yml:30`) target exactly this directory.
- Contains: Top-level HTML pages + `assets/` + `data/` + `data-sources/` + `models/`.
- Key files: `site/hifi/index.html`, `site/hifi/architecture.html`, `site/hifi/data-sources.html`.

**`site/hifi/assets/`:**
- Purpose: Shared CSS and JS for the whole site. Every page links exactly these three files.
- Contains: `theme.css`, `site.js`, `charts.js`.
- Key files: `site/hifi/assets/theme.css` (design tokens, layout primitives, typography), `site/hifi/assets/site.js` (chrome injection), `site/hifi/assets/charts.js` (SVG charts).

**`site/hifi/data/`:**
- Purpose: JSON catalogue manifests. Reference-only — no HTML or JS file in the repo references them.
- Contains: `vendors.json`, `elexon.json`.
- Key files: `site/hifi/data/vendors.json` (7 vendors with auth, base URL, dataset count), `site/hifi/data/elexon.json` (Elexon datasets grouped by category).

**`site/hifi/data-sources/`:**
- Purpose: Per-vendor pages. Currently only `elexon.html` and its `elexon/` dataset directory exist.
- Contains: `elexon.html` (vendor hub) and `elexon/` (dataset pages).
- Key files: `site/hifi/data-sources/elexon.html`.

**`site/hifi/data-sources/elexon/`:**
- Purpose: One HTML page per Elexon BMRS dataset. 23 files today; the manifest (`data/elexon.json`) describes 25 IDs — `remit`, `bmunits_reference`, `soso` from the manifest do not yet have pages.
- Contains: 23 `.html` files.
- Key files: `site/hifi/data-sources/elexon/fuelhh.html` (621 lines — the canonical reference layout to copy from).

**`site/hifi/models/`:**
- Purpose: Model case-study pages.
- Contains: `demand-forecast.html` only (the one "shipping" model).
- Key files: `site/hifi/models/demand-forecast.html`.

## Key File Locations

**Entry Points:**
- `src/gridflow_front_end/serve.py`: `gridflow-serve` CLI entry; `main()` at line 51.
- `site/hifi/index.html`: HTTP entry — the home page served at `/`.
- `.github/workflows/deploy.yml`: CI/CD entry — Pages publish trigger.

**Configuration:**
- `pyproject.toml`: Python package metadata, `requires-python = ">=3.11"`, console script declaration (`gridflow-serve = "gridflow_front_end.serve:main"`), `[tool.setuptools.packages.find] where = ["src"]`.
- `.gitignore`: standard Python ignores (`.venv/`, `__pycache__/`, `*.egg-info/`, `dist/`, `build/`, `.idea/`).

**Core Logic:**
- `src/gridflow_front_end/serve.py`: site-dir resolution (line 23), argparse parser (lines 56-67), browser-launch thread (lines 38-48), silent request handler (lines 26-35), main loop (lines 82-100).
- `site/hifi/assets/site.js`: nav/footer template literals (lines 9-77), page → active-link map (lines 86-93), mobile menu toggle (lines 101-115), copy-button wiring (lines 118-133), tab group wiring (lines 135-147).
- `site/hifi/assets/charts.js`: deterministic `rng(seed)` (lines 24-30), per-chart-type renderers (e.g. `stackedArea`, line 33+).

**Page Templates (by-convention, not real templates):**
- `site/hifi/data-sources/elexon/fuelhh.html`: reference dataset page (621 lines, most complete sections).
- `site/hifi/data-sources/elexon.html`: reference vendor page (712 lines).
- `site/hifi/models/demand-forecast.html`: reference model page.

**Shared chrome contract:**
- Every HTML page sets three `<body>` attributes consumed by `site.js`:
  - `data-page`: one of `home`, `architecture`, `sources`, `vendor`, `dataset`, `model`, `about`.
  - `data-root`: relative prefix back to `site/hifi/` (`""`, `"../"`, or `"../../"`).
  - `data-screen-label`: `"NN Type · slug"` (design-tool / assessment metadata, e.g. `"04 Dataset · fuelhh"`).

## Naming Conventions

**Files:**
- HTML pages: lowercase, kebab-case for multi-word slugs (`data-sources.html`, `demand-forecast.html`).
- Elexon dataset pages: filename = lowercase Elexon API dataset code, no spaces. Underscores are kept when the underlying code uses them (`system_prices.html`); compact codes stay compact (`fuelhh.html`, `agpt.html`, `uou2t14d.html`).
- Python modules: `snake_case.py` (`serve.py`).
- Configuration: standard tool names (`pyproject.toml`, `.gitignore`, `deploy.yml`).

**Directories:**
- All lowercase, kebab-case where multi-word: `data-sources/`, `gridflow_front_end/` (Python's `snake_case` rule applies to the Python package only).
- Vendor subdirectories under `data-sources/` are bare vendor slugs (`elexon/`, will be `entsoe/`, `entsog/`, `gie/`, `openmeteo/`, `neso/` when added).

**HTML internal anchors / IDs:**
- Section IDs are lowercase, hyphenless or kebab-case (`#overview`, `#schema`, `#sample`, `#caveats`, `#related`, `#datasets`, `#diagram`, `#medallion`, `#trace`, `#decisions`, `#repo`).

**`data-page` values:** `home` · `architecture` · `sources` · `vendor` · `dataset` · `model` · `about` (the full vocabulary, defined in `site/hifi/assets/site.js:86-93`).

**`data-screen-label` format:** `"NN Type · slug"` where `NN` is a zero-padded sequence number (`01 Home`, `02 Data sources`, `03 Vendor · Elexon`, `04 Dataset · fuelhh`, ...). The numbers are sequence IDs for an external screenshot harness; they are not load-bearing for the runtime but should stay roughly monotonic.

**Vendor / dataset code conventions in JSON manifests:**
- `site/hifi/data/vendors.json` `id`: lowercase, underscore for multi-word providers (`gie_agsi`, `gie_alsi`, `open_meteo`).
- `site/hifi/data/elexon.json` dataset `id`: matches the Elexon BMRS API code exactly (`fuelhh`, `system_prices`, `fou2t14d`).

## Where to Add New Code

**New Elexon dataset page** (e.g. `boalf`):
1. Create `site/hifi/data-sources/elexon/boalf.html`. Easiest start: copy `site/hifi/data-sources/elexon/fuelhh.html` as the template.
2. In the new file:
   - Update `<title>` to `<slug> · Elexon BMRS · Gridflow`.
   - Keep `<link rel="stylesheet" href="../../assets/theme.css" />`.
   - On `<body>`, set `data-page="dataset"`, `data-root="../../"`, and a fresh `data-screen-label="NN Dataset · <slug>"` (pick the next unused `NN`).
   - Update breadcrumbs (`Gridflow / Data sources / Elexon BMRS / <slug>`).
   - Fill the hero, metadata grid, stats strip, sidebar nav, and sections (Overview, Snapshot chart, Schema, Sample, Caveats, Related).
3. Update the vendor hub `site/hifi/data-sources/elexon.html`: add an `<a href="elexon/<slug>.html" class="row-link card flush" ...>` card under the matching category (`#generation`, `#prices-balancing`, `#demand-forecasts`, `#system-reference`).
4. Update the manifest `site/hifi/data/elexon.json`: add `{ "id": "<slug>", "title": "...", "freq": "...", "lag": "...", "rows": "..." }` to the matching group's `datasets` array.
5. Update sibling-dataset sidebars on the existing dataset pages if you want the new slug to appear in their sidebar nav lists.

**New vendor (e.g. `entsoe`):**
1. Create `site/hifi/data-sources/entsoe.html`. Copy `site/hifi/data-sources/elexon.html` as the template.
2. In the new file: set `data-page="vendor"`, `data-root="../"`, `data-screen-label="NN Vendor · ENTSO-E"`, update breadcrumbs, hero, metadata, stats strip, and the per-category card grids.
3. Create the directory `site/hifi/data-sources/entsoe/` and seed it with the first dataset page (using the Elexon dataset HTML as a starting point, with `data-root="../../"`).
4. Update `site/hifi/data-sources.html`: replace the stub `<a href="#entsoe">` (currently at `data-sources.html:93`) with `<a href="data-sources/entsoe.html">`.
5. Update `site/hifi/data/vendors.json`: bump the `datasets` count and `lastFetch` for the new vendor entry, or add the entry if missing.
6. If you need new home-page coverage, update the catalogue preview row on `site/hifi/index.html` (currently around `index.html:569`, which points at `data-sources.html#entsoe`).

**New model case study (e.g. `wind-forecast`):**
1. Create `site/hifi/models/wind-forecast.html` (kebab-case slug). Copy `site/hifi/models/demand-forecast.html` as the template.
2. In the new file: set `data-page="model"`, `data-root="../"`, `data-screen-label="Wind forecast"`. Keep `<link rel="stylesheet" href="../assets/theme.css" />`.
3. The site nav's "Models" link is hard-coded to `models/demand-forecast.html` at `site/hifi/assets/site.js:19`. To surface the new model in the top nav, either:
   - Change `site.js:19` to point at the new canonical entry, or
   - Promote a `site/hifi/models.html` index and update `site.js:19` to link there, then update `site.js:86-93` if you introduce a new `data-page` value.
4. Update the models list on `site/hifi/index.html` (the `.model-row` block around `index.html:686`) to include a row for the new model.

**New asset or shared widget:**
- New CSS rules → append to `site/hifi/assets/theme.css` (single shared stylesheet). Avoid adding inline `<style>` blocks per page when the rules will be reused.
- New JS behaviour (interactive widget) → append to `site/hifi/assets/site.js` (keep it inside the existing IIFE) so it ships everywhere automatically.
- New chart type → add a renderer function to `site/hifi/assets/charts.js` following the existing pattern (read `opts`, draw SVG via string template, inject into `el.innerHTML`).

**New JSON manifest:**
- Place under `site/hifi/data/`. Today nothing reads these files — if you intend the new manifest to drive the site, also add a `fetch('data/<file>.json')` wiring step inside `site/hifi/assets/site.js`.

**Python-side changes to the dev server:**
- `src/gridflow_front_end/serve.py` is the only Python file with logic. New flags go on the argparse parser (`serve.py:56-67`); new handler behaviour goes on `_SilentHandler`. If the deployed site root ever changes, update `_SITE_DIR` at `serve.py:23` and the `path:` value at `.github/workflows/deploy.yml:30` together.

## Special Directories

**`.venv/`:**
- Purpose: local Python virtual environment.
- Generated: yes (created by `uv venv` or `python -m venv`).
- Committed: no (listed in `.gitignore`).

**`.idea/`:**
- Purpose: JetBrains IDE workspace metadata.
- Generated: yes.
- Committed: no (listed in `.gitignore`).

**`.claude/`, `.codex-assessment-shots/`:**
- Purpose: AI-tooling working directories (Claude Code state; screenshot harness output).
- Generated: yes.
- Committed: not relevant — local-only.

**`.planning/`:**
- Purpose: GSD planning artefacts.
- Generated: written by the GSD commands (this file lives at `.planning/codebase/STRUCTURE.md`).
- Committed: depends on the workflow; `codebase/` is git-ignored per `.gitignore`.

**`dist/`, `build/`, `*.egg-info/`:**
- Purpose: Python build artefacts (only appear if `python -m build` or similar is run).
- Generated: yes.
- Committed: no (all listed in `.gitignore`).

---

*Structure analysis: 2026-05-17*
