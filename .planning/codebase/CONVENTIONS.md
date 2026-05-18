# Coding Conventions

**Analysis Date:** 2026-05-17

This codebase is a static HTML/CSS/JS site (`site/hifi/`) plus a tiny Python dev-server package (`src/gridflow_front_end/`). The HTML pages are hand-authored — there is no template engine, build step, or framework. Conventions are therefore enforced by copy-paste, so consistency depends on following the established patterns exactly.

For canonical examples reference:
- **Dataset page (full / responsive):** `site/hifi/data-sources/elexon/fuelhh.html`
- **Dataset page (stub / typical Elexon page):** `site/hifi/data-sources/elexon/agpt.html`
- **Top-level page:** `site/hifi/index.html`
- **Shared CSS:** `site/hifi/assets/theme.css`
- **Shared JS:** `site/hifi/assets/site.js`, `site/hifi/assets/charts.js`
- **Python:** `src/gridflow_front_end/serve.py`

## Naming Patterns

**Files:**
- HTML: kebab-case for multi-word top-level pages (`data-sources.html`, `demand-forecast.html`); short lowercase slugs for dataset detail pages (`agpt.html`, `fuelhh.html`, `system_prices.html`). Dataset slugs mirror the Elexon dataset id and may contain underscores when the upstream id does (e.g. `system_prices`).
- CSS: single shared stylesheet `assets/theme.css`.
- JS: single shared chrome script `assets/site.js`, single chart renderer `assets/charts.js`.
- JSON data: lowercase vendor id, plain extension (`data/elexon.json`, `data/vendors.json`).
- Python module: snake_case (`serve.py`, package `gridflow_front_end`).

**HTML id / fragment slugs:**
- Section ids are kebab-case lowercase nouns: `#overview`, `#live-chart`, `#schema`, `#sample`, `#api`, `#caveats`, `#related` (`site/hifi/data-sources/elexon/agpt.html:156-398`).
- In-page anchors in the sidebar match section ids verbatim.

**CSS class names:**
- BEM-ish kebab-case with a hyphen-separated component prefix, no double-underscore/double-dash. Examples: `.pillar-num`, `.pillar-title`, `.pillar-arrow` (`site/hifi/index.html:36-50`); `.schema-table`, `.col-name`, `.col-type`, `.pk-badge` (`site/hifi/data-sources/elexon/agpt.html:13-27`).
- State / modifier classes are single words appended with a space, not joined: `chip live`, `chip btn-like ink`, `card flush`, `card deep`, `card ink`, `card accent` (`site/hifi/assets/theme.css:226-262`).
- Layout helpers are short lowercase: `.container`, `.row`, `.col`, `.between`, `.center`, `.stack-sm`, `.stack-md`, `.gap-8`, `.mb-16`, `.mt-24` (`site/hifi/assets/theme.css:105-114`).
- Typography helpers are semantic: `.eyebrow`, `.small`, `.tiny`, `.mono`, `.lede`, `.display-1`/`-2`/`-3`, `.italic`, `.fg-accent`, `.fg-soft` (`site/hifi/assets/theme.css:67-103`).

**JS identifiers:**
- `camelCase` for functions and locals (`stackedArea`, `setTab`, `navHTML`, `footerHTML` in `site/hifi/assets/site.js` and `site/hifi/assets/charts.js`).
- `UPPER_SNAKE` for module-level constant tables (`PALETTE` in `site/hifi/assets/charts.js:7-21`).
- Private leading underscore for module-private helpers in Python (`_SilentHandler`, `_open_browser`, `_PACKAGE_DIR`, `_SITE_DIR` in `src/gridflow_front_end/serve.py:20-48`).

**Data attributes (load-bearing — do not invent new keys):**
- `data-page` — page-type key consumed by `site.js`. Allowed values: `home`, `architecture`, `sources`, `vendor`, `dataset`, `model`, `about` (`site/hifi/assets/site.js:84-93`).
- `data-root` — relative path back to `site/hifi/` root, used to prefix nav/footer hrefs. Empty string at the hifi root, `../` one level deep, `../../` two levels deep (`site/hifi/assets/site.js:7`, `site/hifi/data-sources/elexon/agpt.html:49`).
- `data-screen-label` — human-readable label used during visual review (e.g. `"06 Dataset · agpt"`, `site/hifi/data-sources/elexon/agpt.html:49`). Not consumed by JS; kept stable so screenshots stay diffable.
- `data-chart` / `data-opts` — render hooks for `charts.js` (`site/hifi/index.html:332`). `data-opts` is a JSON object encoded inline; quote it with single quotes so the inner JSON keeps double quotes.
- `data-tabs`, `data-tab-group`, `data-tab-panel` — paired attributes for the inline tab widget (`site/hifi/data-sources/elexon/agpt.html:290-296`).

## Code Style

**HTML formatting:**
- 2-space indent.
- Lowercase tag names; `<!doctype html>` lowercase (not `<!DOCTYPE>`).
- Self-closing for void elements is written as ` />` with a space (`<meta charset="utf-8" />`, `<link ... />`).
- Attribute values in double quotes.
- Section dividers use ASCII box-drawing comments in `index.html` for navigation: `<!-- ════════════════ HERO ════════════════ -->` (`site/hifi/index.html:302`, repeated throughout).

**CSS formatting (`site/hifi/assets/theme.css`):**
- 2-space indent.
- One declaration per line in canonical blocks; short rules are single-line when they fit (`site/hifi/assets/theme.css:67-73`).
- Section headers use a comment banner pattern: `/* ── buttons & chips ────────────────────────── */` (`site/hifi/assets/theme.css:200`).
- Custom-property tokens grouped on `:root` by purpose: paper, ink, accent, type, layout (`site/hifi/assets/theme.css:5-36`).

**JS formatting:**
- 2-space indent.
- Semicolons present.
- Double quotes for strings, backticks for templates (`site/hifi/assets/site.js:9-31`).
- Arrow functions for callbacks; `function` keyword only for named top-level helpers (`stackedArea`, `setTab`).
- Each entry-point script is wrapped in an IIFE: `(function () { ... })();` (`site/hifi/assets/site.js:5`, `site/hifi/assets/charts.js:6`).

**Python formatting (`src/gridflow_front_end/serve.py`):**
- 4-space indent (PEP 8).
- `from __future__ import annotations` at the top of every module (`serve.py:8`, `__init__.py:2`).
- Imports grouped: stdlib only, alphabetised within group, one per line (`serve.py:10-17`).
- 88-100 col line budget in practice; long error strings broken across lines inside `sys.exit(...)` (`serve.py:71-74`).

## Linting / Formatting Tools

- **Not configured.** No `.eslintrc`, `.prettierrc`, `.editorconfig`, `ruff.toml`, `mypy.ini`, or `pre-commit` config exists. No `[tool.ruff]` / `[tool.black]` / `[tool.mypy]` sections in `pyproject.toml`.
- Per user global preferences, future Python edits should pass `ruff check` and `ruff format`; `mypy --strict` is not currently enforced by config but type hints already meet that bar in `serve.py`.

## Import / Asset Loading

**HTML asset order (every page):**
1. `<meta charset>` then `<title>` then `<meta viewport>` (and optional `<meta name="description">`).
2. Google Fonts preconnect pair, then the Fraunces+Inter+JetBrains Mono CSS link (`site/hifi/index.html:8-10`).
3. `<link rel="stylesheet" href="…/assets/theme.css" />` with `…` adjusted for depth (`assets/theme.css` at root, `../assets/theme.css` one level deep, `../../assets/theme.css` under `data-sources/elexon/`).
4. Optional inline `<style>` block for page-local rules (e.g. `.pillar` styles in `site/hifi/index.html:12-298`; `.schema-table`, `.sidebar`, `.page-layout` in dataset pages).
5. Body content.
6. Just before `</body>`: `<script src="…/assets/charts.js"></script>` then `<script src="…/assets/site.js"></script>`. Inline `<script>` IIFEs follow if the page has per-page behaviour (e.g. scroll-spy on dataset pages, `site/hifi/data-sources/elexon/agpt.html:406-433`).

**Python imports:**
- Stdlib only. The package has zero runtime dependencies (`pyproject.toml:10`: `dependencies = []`).
- Order: `from __future__` → stdlib `import …` lines (one per module) → stdlib `from … import …` (`serve.py:8-17`).

## CSS Architecture

**Design tokens — always reference via `var(--…)`:**
- Paper / ink / accent palette is defined on `:root` (`site/hifi/assets/theme.css:5-26`). Never hard-code these hex values inline — exception: deliberate per-page chart accents (e.g. `#c45a3a` rust, `#8fbf9c` muted-green, `#26221d` dark-table-row) are used as one-offs when the design token would change meaning.
- Type stacks: `--serif` (Fraunces), `--sans` (Inter), `--mono` (JetBrains Mono) (`site/hifi/assets/theme.css:28-30`). Always reference via the variable.
- Layout tokens: `--site-max` 1280px, `--site-pad` 64px, `--gutter` 32px.

**Component classes (vocabulary used throughout):**
- Surfaces: `.card`, `.card.deep`, `.card.ink`, `.card.accent`, `.card.flush` (`site/hifi/assets/theme.css:253-262`).
- Chips: `.chip`, `.chip.ink`, `.chip.accent`, `.chip.live` (auto-prepends a green dot), `.chip.btn-like` (cursor pointer).
- Buttons: `.btn`, `.btn.primary`, `.btn.ghost`, `.btn.accent`, `.btn.sm` (`site/hifi/assets/theme.css:201-224`).
- Tables: `.etable` (editorial / lede), `.schema-table` (column docs, defined per dataset page), `.data-table` (dark sample-data table, defined per dataset page).
- Strips: `.stats-strip` for KPI rows, `.scope-strip` for index page.
- Code: wrap `<pre class="code">` in `<div class="code-wrap">` to enable the auto-injected copy button (`site/hifi/assets/site.js:119-133`).

**Class vs inline-style policy:**
- Reusable visual primitives live in `theme.css` as classes.
- One-off positioning / overrides / per-instance grid templates are written as `style="…"` directly on the element (`site/hifi/index.html:305`, `site/hifi/data-sources/elexon/agpt.html:62`). This is intentional — there is no Tailwind / utility framework, and adding a class for a one-off would bloat the stylesheet.
- Per-page rules that recur on that page (e.g. `.schema-table` shared across all dataset pages) live in a `<head><style>` block at the top of each file. **This is duplicated across pages** and is a known drift point — see `.planning/codebase/CONCERNS.md`.

**Page-specific CSS blocks:**
Dataset pages each duplicate ~30 lines defining `.schema-table`, `.data-table`, `.page-layout`, `.sidebar`, `.sidebar-section`, `.caveat-item`, `.related-grid` (`site/hifi/data-sources/elexon/agpt.html:12-47`). When editing one, update all. When adding a new dataset, copy from `agpt.html` verbatim.

## JavaScript Patterns

**Module / module-system:**
- No bundler, no `import`/`export`, no `<script type="module">`. Plain `<script src>` tags, executed top-to-bottom.
- Each script is wrapped in an IIFE so it leaks no globals (`site/hifi/assets/site.js:5-148`, `site/hifi/assets/charts.js:6-261`).
- `setTab(group, tab, btn)` is intentionally global because dataset pages call it from `onclick="setTab('agpt','url',this)"` attributes (`site/hifi/data-sources/elexon/agpt.html:292`, definition at `:424-433`).

**Chrome injection (`site/hifi/assets/site.js`):**
- Reads `document.body.dataset.page` and `document.body.dataset.root` and uses them to build `navHTML` / `footerHTML` template literals.
- `insertAdjacentHTML("afterbegin", …)` for nav, `("beforeend", …)` for footer.
- Marks the active nav link by mapping `data-page` → nav-key (`site.js:84-98`).
- Wires up: mobile menu toggle, code-block copy buttons, and tab switcher (`[data-tabs]` group).

**Chart rendering (`site/hifi/assets/charts.js`):**
- Pure SVG. No canvas, no D3, no chart library.
- Render functions accept an element and an `opts` object: `stackedArea(el, opts = {})`. Called by a dispatcher reading `data-chart` and `data-opts` from each chart placeholder (`site/hifi/index.html:332` uses `data-chart="donut"`, `data-opts='{"data":[…]}'`).
- Deterministic data: a seeded `rng(seed)` PRNG is used so charts look "real" but render identically on every visit (`charts.js:23-30`).
- Palette is centralised in `PALETTE` const (`charts.js:7-21`).

**Per-page inline scripts (dataset pages):**
- Scroll-spy IIFE using `IntersectionObserver` to highlight the active sidebar anchor (`site/hifi/data-sources/elexon/agpt.html:406-421`). Copy verbatim when adding a new dataset page; selectors are tied to `.sidebar a[href^='#']`.
- `setTab(group, tab, btn)` tab switcher for the API/SQL/Python code examples (`agpt.html:423-433`). Identical across files.

**Browser-API contract:**
Targets evergreen browsers — uses `document.body.dataset`, `Element.insertAdjacentHTML`, `navigator.clipboard?.writeText` with optional chaining, template literals, `IntersectionObserver`, `URLSearchParams`-free DOM. No polyfills.

## HTML Document Structure

**Required `<head>`:**
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{Page title} · {Section} · Gridflow</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="…" />  <!-- index + model pages only -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..600,30..100&family=Inter:wght@300..600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{depth}/assets/theme.css" />
  <style>/* page-local rules */</style>
</head>
```

**Title convention:** Pipe-separated reverse hierarchy with `·` as separator: `agpt · Elexon BMRS · Gridflow` (`site/hifi/data-sources/elexon/agpt.html:5`), `Day-ahead demand forecast · Models · Gridflow` (`site/hifi/models/demand-forecast.html:5`), `Gridflow · A research platform for European power markets` (`site/hifi/index.html:5`).

**Viewport:** Top-level pages and the canonical responsive dataset page (`fuelhh.html`) use `width=device-width, initial-scale=1`. Most other dataset pages (21 of 22) use the non-responsive `width=1280` — this is a known drift; new pages should use `device-width, initial-scale=1`.

**Required `<body>` attributes:**
```html
<body data-page="…" data-root="…" data-screen-label="NN Label">
```
Without `data-page` and `data-root`, the global nav and footer will not be injected, and links inside them will be broken.

**Page-type values for `data-page`:**
- `home` (index)
- `architecture` (architecture.html)
- `sources` (data-sources.html)
- `vendor` (per-vendor pages like data-sources/elexon.html)
- `dataset` (per-dataset pages under data-sources/elexon/)
- `model` (models/*.html)
- `about` (about anchor / dedicated about page)

## Error Handling

**Python (`src/gridflow_front_end/serve.py`):**
- Narrow exceptions only — `OSError` is caught for the bind failure (`serve.py:84-88`), `KeyboardInterrupt` for graceful Ctrl-C (`serve.py:98-100`). No bare `except:`.
- Failures are reported via `sys.exit(message)` with a multi-line user-facing message that suggests a remediation (`serve.py:71-74`, `serve.py:85-88`). Do not raise into the user's terminal.
- The `_SilentHandler` overrides `log_message` to suppress per-request noise but still surfaces real errors via `log_error` to `stderr` (`serve.py:26-35`).

**JavaScript:**
- Defensive null guards rather than try/catch: `if (toggle && links)`, `if (panel)`, `if (link)`, `navigator.clipboard?.writeText(…)` (`site/hifi/assets/site.js:103-117`, `:127`).
- No error reporting / Sentry / console.error calls. Failed copies silently succeed/fail; failed nav-link lookups simply don't apply the active class.

## Logging

- Python: prints to stdout for the banner only (`serve.py:90-91`); errors go to stderr via the `log_error` override; per-request logs are intentionally suppressed.
- JavaScript: no logging. Do not add `console.log` to shipped code.

## Comments

**When to comment:**
- Module-level docstrings in Python explain the entry-point and CLI usage (`serve.py:1-7`).
- Class / function docstrings cover non-obvious behaviour (`serve.py:27`, `:38-42`). Single-line Google-style is fine for the small surface here.
- CSS section banners delimit themed groups: `/* ── buttons & chips ────────────────── */` (`theme.css:200`).
- HTML uses ASCII-box section markers in long files: `<!-- ════════════════ HERO ════════════════ -->` (`site/hifi/index.html:302`).
- JS uses `// ──` section dividers and short rationale comments before non-obvious blocks (`charts.js:23`, `:32`).

**When not to comment:**
- Do not restate what the code does. Comments should explain *why* — e.g. `# The delay gives the server socket time to bind before the browser hits it.` (`serve.py:41-42`).
- A `# TODO:` exists in `site/hifi/index.html:808` ("replace 'E. Bentham' with your full legal name"); leave it until the user resolves it.

## Function / Module Design

**Python:**
- Module-private helpers are prefixed `_` and never re-exported.
- The public surface is a single `main()` entry-point wired through `[project.scripts]` (`pyproject.toml:13`).
- Type-annotate every parameter and return; use `from __future__ import annotations` to defer evaluation (`serve.py:29`, `:33`, `:38`, `:51`).

**JavaScript:**
- One IIFE per file; everything else closed over its locals.
- Render functions take `(el, opts = {})` with defaults destructured at the top (`charts.js:34-36`).
- Use `Array.from({ length: N }, (_, i) => …)` for fixed-length generation (`charts.js:60`).

## Common Patterns — Dataset Pages

A dataset page under `site/hifi/data-sources/elexon/` follows this exact structure. Use `site/hifi/data-sources/elexon/agpt.html` as the reference and copy it when adding a new dataset.

1. **`<head>`** (`agpt.html:1-48`):
   - Standard meta + fonts + theme.css link at `../../assets/theme.css`.
   - Per-page `<style>` block defining `.schema-table`, `.data-table`, `.page-layout`, `.sidebar`, `.sidebar-section`, `.sidebar-section-title`, `.main-content`, `.caveat-item`, `.caveat-num`, `.related-grid`.

2. **`<body>` attributes** (`agpt.html:49`):
   ```html
   <body data-page="dataset" data-root="../../" data-screen-label="NN Dataset · {slug}">
   ```

3. **Hero block** (`agpt.html:51-102`):
   - Bordered container with `padding-top:40px; padding-bottom:40px;`.
   - Breadcrumbs `.crumbs`: Gridflow / Data sources / Elexon BMRS / `<span class="here">{slug}</span>`.
   - Two-column grid: left = `.eyebrow` (category · vendor · layer) + `.chip` (cadence) + `<h1 class="display-2">` with mono slug above an italic tagline; right = 6-cell metadata grid (SILVER PATH, API PATH, PARAM STYLE, EARLIEST DATA, VOLUME, LAST FETCH).

4. **Stats strip** (`agpt.html:104-128`):
   - `.stats-strip` with 5 `<div>` cells, each `.stat-n` + `.stat-l`.

5. **Two-column page layout** (`agpt.html:130-401`):
   - `.page-layout` grid: 220px sticky `<nav class="sidebar">` + `.main-content`.
   - Sidebar has two sections: "On this page" (anchor list) and "Elexon BMRS" (sibling dataset links, current page marked `class="active"`, others dimmed via `style="color:var(--ink-faint);"`).

6. **Sections in `.main-content`** (in this order, each with an id):
   - `#overview` — three short paragraphs with inline `<code class="mono">` for identifiers.
   - `#live-chart` (optional) — `<div class="chart">` wrapping a `<div data-chart="…" data-opts='…'>` placeholder.
   - `#schema` — `<table class="schema-table">` with columns: name (`.col-name` with optional `<span class="pk-badge">PK</span>`), type (`.col-type`), nullable (`—` or `null`), description.
   - `#sample` — `<table class="data-table">` with 5-10 example rows; cell classes `.num` / `.date` / `.str`.
   - `#api` — endpoint and param-style cards, then a tab group with three panels: Example URL, DuckDB SQL, Python parquet. Uses `data-tab-group="{slug}"` / `data-tab-panel="{slug}-{key}"` and `onclick="setTab('{slug}','{key}',this)"`.
   - `#caveats` — `.caveat-item` rows numbered `01`, `02`, `03`.
   - `#related` — `.related-grid` of four `<a class="row-link card flush">` cards linking sibling datasets.

7. **Script tags** (`agpt.html:404-433`):
   - `<script src="../../assets/charts.js"></script>`
   - `<script src="../../assets/site.js"></script>`
   - Inline IIFE with `IntersectionObserver` for scroll-spy on `.sidebar a[href^='#']`.
   - Inline `function setTab(group, tab, btn)` for the API/SQL/Python tab switcher.

**Closing tag discipline:** The sidebar uses `<nav class="sidebar">` — close it with `</nav>`. Stub-format pages (`boal.html`, `freq.html`, `indo.html`, `system_prices.html`, etc.) close it with `</div>` instead, which is a markup defect tracked in CONCERNS.md.

---

*Convention analysis: 2026-05-17*
