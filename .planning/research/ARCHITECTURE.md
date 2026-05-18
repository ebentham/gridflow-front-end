# Architecture Research

**Domain:** Editorial portfolio + data-documentation site (static HTML/CSS/JS, ~25-50 dataset pages per vendor)
**Researched:** 2026-05-17
**Confidence:** HIGH for ecosystem patterns and reference-site anatomy; MEDIUM-HIGH for the build-vs-runtime recommendations (verified against current codebase metrics, but the LOC numbers are estimates from current files).

## Executive Recommendation

**Option B — "Tiny build script."** A ~150-line Python script that reads `site/hifi/data/elexon.json` + per-dataset content partials + a single canonical HTML template, and emits the 23 Elexon dataset pages (and the 1 ENTSO-E dataset) into the existing `site/hifi/data-sources/<vendor>/` directory tree. GitHub Pages still deploys `site/hifi/` unchanged; the generator runs in CI (or locally) and writes generated `.html` files into the same path that exists today.

This is **not** "adopt 11ty/Astro/Hugo." It is closer to "give yourself shared partials in Python because HTML has no `<include>`." The output remains plain static files, deployable by the existing Pages workflow with zero changes to `deploy.yml`. If the project later wants a real SSG, this script becomes a 30-minute migration to 11ty (its data + pagination model is the same shape).

The roadmap can override and pick Option A (disciplined copy-paste) if author bandwidth for the cleanup milestone is tighter than expected — that path also works but pays a perpetual maintenance tax of editing 22 files for every cross-cutting structural change.

## Standard Architecture

### System Overview (Recommended — Option B)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       Author / Editor                                │
│   Edits manifest + per-dataset content partials + template           │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Source of truth                               │
│  site/hifi/data/elexon.json        — structure: groups, ids, freq    │
│  site/hifi/data/entsoe.json        — same shape, new vendor          │
│  site/hifi/data/vendors.json       — vendor metadata                 │
│  build/content/elexon/<slug>.md    — per-dataset prose (overview,    │
│                                      caveats) + schema rows + sample │
│                                      rows; YAML frontmatter for hero │
│  build/templates/dataset.html      — ONE canonical layout            │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  build step (local or CI)
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Tiny build script (Python)                      │
│  src/gridflow_front_end/build.py                                     │
│   1. read manifest + per-dataset partials                            │
│   2. for each dataset, render template → write HTML                  │
│   3. for vendor hubs, render template → write HTML                   │
│   4. compute counts (vendors, datasets) from manifests               │
│   5. inject counts into index/footer/data-sources via placeholder    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ writes
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│            Deployed artefact — site/hifi/  (unchanged path)          │
│  Generated:                              Hand-authored:              │
│   data-sources/elexon/*.html (×25)        index.html                 │
│   data-sources/elexon.html                architecture.html          │
│   data-sources/entsoe/*.html (×1+)        data-sources.html         │
│   data-sources/entsoe.html                models/*.html              │
│  Shared:                                                             │
│   assets/theme.css, site.js, charts.js (single source)              │
│   data/elexon.json, vendors.json (committed; used by build)         │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ on push to main
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  GitHub Pages — .github/workflows/deploy.yml                         │
│  (unchanged: path: site/hifi)                                        │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Browser — same runtime as today (site.js injects chrome,            │
│  charts.js renders seeded SVG, theme.css styles everything)          │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Manifest (`elexon.json`, `vendors.json`)** | Authoritative list of vendors and datasets with structural metadata (id, title, freq, lag, rows, category). Single source for counts and category groupings. | JSON. Stay flat — no nesting beyond groups → datasets. |
| **Per-dataset content partials** | The prose, schema rows, sample rows, and caveats specific to one dataset. ~80% of the variation between two dataset pages lives here. | Markdown + YAML frontmatter, or a `.html.partial` fragment, or a per-dataset JSON. Pick one and stick with it. |
| **Canonical template** | One HTML layout file declaring hero / stats strip / sidebar / overview / chart / schema / sample / caveats / related, with placeholders for each section's content. | A single `dataset.html` template using `{{slug}}` / `{{title}}` placeholders or a Python `str.format`-equivalent. |
| **Build script** | Read manifest + partials + template, emit one `.html` per dataset, plus the vendor hub. Inject counts into hand-authored pages where requested via a marker comment. | ~150-line Python script; stdlib only to match the existing `gridflow-serve` constraint. |
| **Hand-authored pages** | Home, architecture, data-sources hub, model case studies. These have one-off editorial structure; templating them is overkill. | Stay as hand-edited `.html`. The build can still inject manifest-derived counts into them via a marked region. |
| **Shared chrome injector (`site.js`)** | Unchanged. Reads `body[data-page]` / `data-root`, injects nav + footer. The build emits HTML that already has the correct attributes. | Existing IIFE. |
| **Shared theme (`theme.css`)** | Absorbs the duplicated dataset-page styles (currently inline ×22). Single stylesheet for the whole site. | Existing file with new `/* ── dataset pages ── */` section added. |
| **Shared interactions (`site.js`)** | Absorbs the duplicated scroll-spy script and the per-page `setTab` global. Use the existing `[data-tabs]` convention so dataset pages don't need any inline JS. | Existing IIFE. |
| **Chart renderer (`charts.js`)** | Unchanged. Walks `[data-chart]` and renders seeded SVG. | Existing IIFE. |
| **Dev server** | Unchanged. Serves `site/hifi/` (the generated output). For build-during-edit ergonomics, optionally add a `--watch` flag that re-runs the build before reload. | Existing `gridflow-serve` Python CLI, stdlib only. |

## Recommended Project Structure (Option B)

```
gridflow-front-end/
├── pyproject.toml
├── README.md
├── LICENSE                              # NEW — resolve MIT/Apache contradiction
├── .gitattributes                       # NEW — eol=lf for *.html, *.css, *.js, *.json, *.py
├── .github/workflows/
│   ├── deploy.yml                       # unchanged — uploads site/hifi/
│   └── validate.yml                     # NEW — htmlhint + lychee on push
├── src/gridflow_front_end/
│   ├── __init__.py
│   ├── serve.py                         # gridflow-serve (unchanged)
│   └── build.py                         # NEW — gridflow-build CLI
├── build/                               # NEW — build inputs only, not deployed
│   ├── templates/
│   │   ├── dataset.html                 # canonical dataset page template
│   │   └── vendor-hub.html              # canonical vendor hub template
│   └── content/
│       ├── elexon/
│       │   ├── fuelhh.md                # per-dataset prose + schema rows
│       │   ├── system_prices.md
│       │   └── …                        # 25 files matching elexon.json IDs
│       └── entsoe/
│           └── day-ahead-prices.md
└── site/
    └── hifi/                            # deploy artefact, mostly unchanged
        ├── index.html                   # hand-authored
        ├── architecture.html            # hand-authored
        ├── data-sources.html            # hand-authored (build injects counts)
        ├── assets/
        │   ├── theme.css                # absorbs duplicated dataset styles
        │   ├── site.js                  # absorbs scroll-spy + tabs helpers
        │   └── charts.js                # unchanged
        ├── data/
        │   ├── vendors.json             # source of truth for vendor counts
        │   └── elexon.json              # source of truth for Elexon datasets
        ├── data-sources/
        │   ├── elexon.html              # GENERATED from vendor-hub.html
        │   ├── elexon/
        │   │   ├── fuelhh.html          # GENERATED from dataset.html
        │   │   └── …                    # 25 files (manifest count)
        │   ├── entsoe.html              # GENERATED
        │   └── entsoe/
        │       └── day-ahead-prices.html # GENERATED
        └── models/
            └── demand-forecast.html     # hand-authored
```

### Structure Rationale

- **`build/` lives at repo root, not inside `site/`.** The artefact `site/hifi/` must stay deployable as-is; build inputs are not deployed. This also keeps the Pages workflow trivial (no need to ignore `build/` from the upload path).
- **Generated HTML lives in the same path it lives today.** No move; `data-sources/elexon/fuelhh.html` is still served at the same URL. This protects existing bookmarks and external links.
- **Per-dataset content stays separate from the template.** Editing `boal.html`'s overview prose means editing `build/content/elexon/boal.md`, not the template. Editing the dataset-page layout means editing `dataset.html` once.
- **Manifest stays inside `site/hifi/data/`.** It is also a deployable artefact (so a curious visitor or another tool can fetch it). The build reads it from there; the site can also fetch it at runtime for client-side enhancements later. Same file, two consumers.

## Reference Architecture: How Mature Data-Doc Sites Compose Pages

Three sites were inspected for their dataset/endpoint reference-page anatomy. The convergent pattern is **three-column layout, content-defined sections, sibling-sidebar navigation**.

### Stripe API Reference ([docs.stripe.com/api](https://docs.stripe.com/api))

**Layout:** Three-column.

- **Left column:** Hierarchical sidebar — top-level resource → endpoint → object. Sticky. Tree expands/collapses; the active leaf is highlighted. Sibling endpoints of the same resource are visually grouped.
- **Center column:** Page anatomy in order — eyebrow ("Core resources / Customers"), display title, lede paragraph, **parameters table** (column / type / required / description), **returns** description block, **error codes** mini-table.
- **Right column:** Live, runnable code samples. Locked-in-place while the center column scrolls. Language switcher (Python / Node / Ruby / Go / cURL / .NET / Java / PHP) at the top; the entire page's samples switch together.

**Lessons for this site:**
- The Stripe right column is the same idea as our `#sample` and `#api` sections, but compressed into one persistent rail. Probably overkill here; left+center is enough for portfolio scope.
- The Stripe sidebar groups by resource, exactly mirroring our `elexon.json` `groups` shape (Generation / Prices & Balancing / Demand & Forecasts / System & Reference). Adopt this — it is what users expect.

### Cloudflare Developer Docs ([developers.cloudflare.com](https://developers.cloudflare.com/))

**Layout:** Two-column main + secondary on-this-page rail.

- **Left column:** Product sidebar driven by frontmatter (`sidebar.order`, `sidebar.label`, `sidebar.badge`). Pages can declare themselves as "navigation pages" — sub-landing pages that route deeper.
- **Center column:** H1 + lede + sections (Overview → Setup → API reference → Examples → Troubleshooting). Sections have anchor IDs and the page is scroll-spied.
- **Right column ("On this page"):** Auto-generated TOC of the current page's H2/H3 headings.

**Lessons for this site:**
- The frontmatter-driven sidebar maps directly to our `elexon.json` manifest. Cloudflare's pattern is: the data file decides sidebar order and label; the page just renders. This is exactly the Option B build-script pattern.
- Vendor hubs should be "navigation pages" — Cloudflare's `hideChildren` / `group.hideIndex` distinctions are useful precedent for "Elexon BMRS" itself being a real page (not a redirect) but listing all its datasets.

### Elexon BMRS Insights Solution ([bmrs.elexon.co.uk/api-documentation](https://bmrs.elexon.co.uk/api-documentation/introduction))

**Layout:** Two-column (left sidebar tree + center content). The actual API source-of-truth this site documents.

- **Left:** Endpoint tree grouped by category (Datasets / Reference / Generation / Demand / Balancing / etc.). Each leaf links to one endpoint page.
- **Center per endpoint page:** Endpoint URL, HTTP verb, parameters list (with type / required / description / example value), response example (JSON / XML / CSV with format toggle), inline "try-it" form.

**Lessons for this site:**
- Elexon's own docs are organised exactly the way our `elexon.json` groups them — this is not coincidence; we should align with the source.
- The Elexon page does NOT have a chart section, a caveats section, or a related-datasets section. Our `fuelhh.html` adds three sections of editorial value that Elexon does not. This is the differentiator the portfolio is built on; preserve it.

### Convergent anatomy

The reference sites agree on the spine of a reference page:

1. **Breadcrumbs** (site → catalogue → vendor → dataset)
2. **Hero** (eyebrow + title + lede + key metadata card)
3. **Stats strip** (numerical at-a-glance facts)
4. **On-this-page sidebar** + **sibling-in-category sidebar** (left rail)
5. **Overview / What this is** (prose)
6. **Schema / Parameters / Returns** (table)
7. **Sample** (example payload or row)
8. **Caveats / Gotchas** (editorial)
9. **Related** (cross-links)
10. **API & ingestion details** (code samples, optional)

This is the `fuelhh.html` anatomy verbatim — the existing template is correct. The work is to bring the other 16 stubs to it and extract it as a real template.

## Architectural Patterns

### Pattern 1: Manifest-as-build-input (recommended)

**What:** A committed JSON file (`elexon.json`) is the single source of truth for the structural facts (list of datasets, their categories, their frequencies). At build time, the script reads it and emits HTML. The HTML files are still committed to the repo so the deploy is unchanged.

**When to use:** When the same structural data needs to appear in 3+ places (sidebar, related-grid, counts in the hero, counts in the footer, vendor hub categories) and there is no SSG.

**Trade-offs:**
- Pro: Source of truth becomes literal. Adding a dataset is one JSON edit + one content partial; the build emits the page, the sidebar entries on sibling pages, the related-grid, the counts. Zero hand-sync.
- Pro: Manifest discrepancy (22 on disk · 25 in manifest · 28 in catalog UI) becomes structurally impossible — the manifest count and the on-disk count are tautologically equal.
- Con: Adds a build step. Pages deploy still works (we commit the output), but contributors must remember to run `gridflow-build` before committing structural changes.
- Con: One layer of indirection. Editing the overview prose for `fuelhh` is now editing `build/content/elexon/fuelhh.md`, not `data-sources/elexon/fuelhh.html`.

**Example:**

```python
# build.py — sketch
from pathlib import Path
import json, re

MANIFEST = json.loads(Path("site/hifi/data/elexon.json").read_text())
TEMPLATE = Path("build/templates/dataset.html").read_text()

for group in MANIFEST["groups"]:
    siblings = [d["id"] for d in group["datasets"]]
    related = group["datasets"]  # for the related-grid
    for dataset in group["datasets"]:
        slug = dataset["id"]
        partial = Path(f"build/content/elexon/{slug}.md").read_text()
        # extract frontmatter (--- yaml ---) and body
        fm, body = parse_frontmatter(partial)
        html = TEMPLATE
        html = html.replace("{{SLUG}}", slug)
        html = html.replace("{{TITLE}}", dataset["title"])
        html = html.replace("{{FREQ}}", dataset["freq"])
        html = html.replace("{{LAG}}", dataset["lag"])
        html = html.replace("{{ROWS}}", dataset["rows"])
        html = html.replace("{{OVERVIEW}}", fm["overview"])
        html = html.replace("{{SIDEBAR_SIBLINGS}}", render_siblings(siblings, slug))
        html = html.replace("{{RELATED_GRID}}", render_related(related, slug))
        html = html.replace("{{SCHEMA_ROWS}}", fm["schema_html"])
        html = html.replace("{{SAMPLE_ROWS}}", fm["sample_html"])
        html = html.replace("{{CAVEATS}}", render_caveats(fm["caveats"]))
        Path(f"site/hifi/data-sources/elexon/{slug}.html").write_text(html)
```

This is intentionally crude string replacement — no Jinja, no third-party deps, fits the "Python 3.11+ stdlib only" constraint.

### Pattern 2: Body-data-attribute contract (existing — keep)

**What:** Each page declares `body[data-page]` / `body[data-root]` / `body[data-screen-label]`. `site.js` reads these at runtime and injects the nav + footer with correctly-prefixed `href`s. Active nav highlighting comes from the `data-page` value.

**When to use:** Already in place. Works. Keep it; the build script writes correct values into the template.

**Trade-offs:**
- Pro: Decouples chrome from page content. The build script can emit dataset pages without needing to know about the nav structure.
- Pro: Mistakes are local — a wrong `data-root` only breaks chrome on that one page.
- Con: Unenforced. The contract is implicit; a typo silently disables active-link highlighting. Mitigation: build-time validation that `data-root` matches the file's directory depth.

### Pattern 3: Inline-SVG charts with seeded RNG (existing — keep)

**What:** `charts.js` walks `[data-chart]` elements, parses `data-opts` JSON, and renders deterministic SVG into the element. No fetch, no canvas, no live data.

**When to use:** Already in place. Works. The "static, illustrative snapshot" framing required by the honesty sweep is structurally honest with this approach — there is no live data path to mislabel.

**Trade-offs:**
- Pro: Reproducible. Page renders identically across reloads.
- Pro: No build-time pre-rendering needed. Charts stay client-rendered, no inline SVG bloat in source HTML.
- Con: Each chart is rendered after page load → a brief layout shift. Acceptable for portfolio scope; not for a customer-facing dashboard.

### Pattern 4: Shared chrome by injection (existing — keep)

**What:** Nav and footer are template literals inside `site.js`. Every page is missing them in source; `site.js` injects them on load.

**When to use:** Already in place. Works because there is only one nav and one footer site-wide. Don't break this.

**Trade-offs:**
- Pro: Zero duplication of chrome HTML across pages.
- Pro: First Paint is fast — only the per-page content is in HTML.
- Con: Pages briefly render without chrome before `site.js` runs. Acceptable; the duration is sub-frame in practice.
- Con: SEO crawlers that don't run JS see no nav. Acceptable here — the site is a portfolio, not an SEO target.

### Anti-Pattern: Runtime fetch of `elexon.json` to render dataset cards

**Why it's tempting:** The manifest already exists. Wiring `site.js` to `fetch('data/elexon.json').then(render)` is fewer LOC than a build script.

**Why it's wrong here:**
- Each page would render with an empty card grid for ~100 ms, then a card grid appears. Worse perceived performance than today.
- Sidebar and related-grid content would not be in the source HTML — bad for view-source debugging, bad for any crawler.
- Counts would still need to be injected (footer "49 datasets", `data-sources.html` "7 vendors") — can be done client-side, but doubles the fetch cost.
- Search-engine and view-source UX assumes content-in-HTML. The portfolio audience may include recruiters who view-source.

**Do this instead:** Build-time generation. The manifest is consumed once, at build, and the output HTML has all the cards inline. The manifest stays as a committed file that other tools (a vault sync script, an external dashboard) can still consume.

## Data Flow

### Authoring flow (recommended)

```
Author wants to add a new Elexon dataset (e.g. "boalf"):

1. Edit site/hifi/data/elexon.json:
     append { "id": "boalf", "title": "Bid-offer acceptance final",
              "freq": "30 min", "lag": "~5 min", "rows": "1.0M / mo" }
     to the "Prices & Balancing" group.

2. Create build/content/elexon/boalf.md:
     ---
     hero_eyebrow: "Prices · elexon · silver"
     hero_lede:    "Final bid-offer acceptances..."
     silver_path:  "silver.boalf"
     api_path:     "/datasets/BOALF"
     param_style:  "settlementDate"
     earliest:     "2014-04-01"
     primary_key:  "settlement_date, period, bm_unit_id"
     schema_rows:
       - { name: "settlement_date", type: "date",      pk: true,  desc: "..." }
       - { name: "settlement_period", type: "int",     pk: true,  desc: "..." }
       - ...
     sample_rows: [ ... ]
     caveats:
       - "Late-arriving rows up to T+5 days; query with publish_date_to=now."
     ---

     ## Overview prose paragraph 1.

     ## Overview prose paragraph 2.

3. Run `gridflow-build`. This writes:
     site/hifi/data-sources/elexon/boalf.html      (new)
     site/hifi/data-sources/elexon.html            (regenerated — gains boalf card)
     site/hifi/data-sources/elexon/{all siblings}.html
         (regenerated — their sidebar sibling-list and related-grid update)
     site/hifi/data-sources.html
         (regenerated, OR: hand-edited with a marker; build injects 26-datasets count)

4. Commit the changes (manifest, partial, all regenerated HTML).
5. Push. Pages workflow runs `actions/upload-pages-artifact path: site/hifi`.
```

### Build-time data flow

```
   site/hifi/data/elexon.json          build/content/elexon/<slug>.md    build/templates/dataset.html
   site/hifi/data/vendors.json         build/content/entsoe/<slug>.md    build/templates/vendor-hub.html
            │                                   │                                   │
            └───────────────┬───────────────────┴───────────────────────────────────┘
                            ▼
                   src/gridflow_front_end/build.py
                            │
                            ├─ counts:  len(elexon datasets) → 25
                            │           sum(vendors[i].datasets) → 49 (or computed)
                            ├─ siblings: per group, list other datasets for sidebar
                            ├─ related:  per group, build the related-grid
                            │
                            ▼
            site/hifi/data-sources/elexon/<slug>.html   (×25)
            site/hifi/data-sources/elexon.html
            site/hifi/data-sources/entsoe/<slug>.html   (×1+)
            site/hifi/data-sources/entsoe.html
            site/hifi/data-sources.html (optional re-emit, or marker-region injection)
            site/hifi/index.html        (optional marker-region injection for counts)
```

### Runtime data flow (unchanged)

```
   Browser loads page (already-complete HTML with cards, sidebar, related-grid baked in)
            │
            ▼
   site.js IIFE
     reads body[data-page] + body[data-root]
     injects <nav> + <footer> with correctly-prefixed hrefs
     marks active nav link from data-page → key map
     wires .code-wrap copy buttons
     wires [data-tabs] groups
     (NEW after refactor) wires scroll-spy on .sidebar a[href^="#"]
            │
            ▼
   charts.js IIFE
     walks [data-chart] elements
     reads data-opts JSON
     renders seeded SVG into the element
            │
            ▼
   Done. Page is static after this. No further fetches.
```

### Key Data Flows

1. **Adding a dataset:** Manifest → partial → build → output HTML in all sibling pages. One source-of-truth edit propagates everywhere.
2. **Updating a count:** Manifest is the source. Either the build re-emits the pages that mention counts, or those pages have a marker region like `<!-- BUILD:dataset_count -->25<!-- /BUILD -->` that the build script updates in place.
3. **Vault sync (cross-repo):** On-site content is authored truth (per PROJECT.md). The vault sync direction is **on-site → vault**. After the refactor: the operational source is `build/content/elexon/<slug>.md` + `site/hifi/data/elexon.json`. The vault sync should read from these (vendor-doc-aligned, structured), not from generated HTML. Suggested direction: `build/content/*` → vault. The manifest stays subordinate to vendor docs (Elexon BMRS docs remain absolute truth).

## Build Order Implications for the Roadmap

The cleanup milestone has eight workstreams. Their dependencies are not flat — here is the sequence that minimises rework.

### Phase 0 — Commit the in-flight refactor (blocking everything)

26 files are modified, uncommitted. Any structural extraction will conflict-merge into this. The advisor flagged this and it is correct: **commit first, then refactor.**

Sub-steps:
1. Split into 4 conventional commits per the diff pattern (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks).
2. Add `.gitattributes` with `*.html text eol=lf` (also `.css`, `.js`, `.json`, `.py`, `.md`) before any cross-platform commits.
3. Push so Pages catches up.

### Phase 1 — Bug fixes that don't depend on architecture (parallelisable)

These have no architectural blockers and can ship before any extraction work:
- Mobile viewport fix on 23 pages (`width=1280` → `width=device-width, initial-scale=1`).
- `LICENSE` file at repo root + align inline strings (MIT vs Apache-2.0).
- `rel="noopener"` on the two missing `target="_blank"` links.
- Replace dead `href="#"` placeholders with non-link "Coming soon" chips (provisional — see Phase 4 for the real fix).

### Phase 2 — CSS/JS extraction (must precede page regeneration)

Before generating any page from a template, the template must be free of inline duplicated styles and per-page script declarations:
- Move the duplicated dataset-page `<style>` block (~30 lines × 22 files = ~660 lines) into `theme.css` under a `/* ── dataset pages ── */` section.
- Move the scroll-spy IIFE into `site.js`, gated by the presence of `.sidebar a[href^="#"]`.
- Migrate dataset-page tabs from the global `setTab(...)` + inline `onclick` pattern to the existing `[data-tabs]` convention from `site.js`. Delete the 22 `setTab` declarations.
- Fix the sidebar hover bug by replacing inline `style="color:var(--ink-faint)"` with a CSS class (e.g. `.sidebar a.muted`) defined in `theme.css`.

This phase is valuable on its own — even without Phase 3+, it removes the worst duplication.

### Phase 3 — Extract the canonical template + build script (the architectural pivot)

This is the Option B work proper:
1. Hand-author `build/templates/dataset.html` by reducing `fuelhh.html` to a template with `{{}}` placeholders. The template is just `fuelhh.html` minus the prose, schema rows, and sample rows.
2. Hand-author `build/content/elexon/fuelhh.md` containing the prose, schema rows, sample rows, caveats, and frontmatter for `fuelhh`. Run the build and diff the output against the existing `fuelhh.html`. Reconcile.
3. Hand-author `build/content/elexon/<slug>.md` for the 5 other complete pages (`fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`). Run the build; verify.
4. Once 6 complete pages regenerate cleanly, hand-author the 16 stub partials by porting the partial content + filling the missing Overview/Schema/Sample sections. Each is a content task, not a structural one.
5. Decide on `remit`, `bmunits_reference`, `soso` (the 25-vs-22 reconciliation). Recommendation: include them — the manifest is authoritative; the build will emit 25 pages, so a partial must exist for each of the 25 IDs. If they are truly out of scope for this milestone, remove them from the manifest first.

### Phase 4 — Vendor hubs + ENTSO-E cross-vendor proof

The build script already generalises. Adding ENTSO-E is:
1. Add `site/hifi/data/entsoe.json` mirroring the `elexon.json` shape.
2. Add `build/content/entsoe/<slug>.md` for the one dataset chosen.
3. Add `build/content/entsoe/<vendor-hub-fields>.md` if vendor hubs also use partials (recommended — vendor hubs have prose too).
4. Run the build. Outputs `site/hifi/data-sources/entsoe.html` and `site/hifi/data-sources/entsoe/<slug>.html`.
5. For the 5 "coming soon" vendor stubs (ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO): mint a stub vendor hub for each with the same template but a `coming_soon: true` flag that the template uses to render a different body. Replace the `<a href="#">` stubs in `data-sources.html` with real links to these.

### Phase 5 — Honesty sweep + a11y

Now that pages are template-generated, the honesty sweep is a single template edit:
- Replace "live · 30 min" chips with "snapshot" framing in the template hero.
- Remove "X min ago" from the metadata card; replace with `last_updated_label` from frontmatter ("Snapshot from 2026-04-30").
- Strip "last sync" from `site.js` footer.

A11y additions also become template edits:
- Wrap content in `<main>` in the template.
- Add `aria-label="On this page"` to the sidebar `<nav>`.
- Add `aria-current="page"` in `site.js` next to the existing `.active` class.
- Add `aria-hidden="true"` to decorative `.arrow` / `.dot` spans in the template.

### Phase 6 — Vault sync (cross-repo)

The on-site content source is now `build/content/elexon/<slug>.md` — structured, with frontmatter. Write a sync script that reads these and updates `quant-vault/30-vendors/elexon/datasets/<slug>.md` in the `gridflow` repo. The frontmatter shape was designed in Phase 3 to align with the `anthropic-skills:gridflow-dataset-spec` skill, so this is a structural mapping not a content migration.

### Phase 7 — Validation in CI

Cheap insurance after all the structural work:
- `htmlhint site/hifi/**/*.html` on push.
- `lychee site/hifi` to catch broken internal links.
- Build script idempotence check: run build twice, diff — no changes second time.

### Dependency graph

```
Phase 0 (commit in-flight)
   │
   ├── Phase 1 (viewport, license, rel=noopener, dead links)        [parallel; no architecture dep]
   │
   └── Phase 2 (CSS/JS extraction)
          │
          └── Phase 3 (template + build script + 22 partials)
                 │
                 ├── Phase 4 (ENTSO-E + 5 vendor stubs)
                 │
                 ├── Phase 5 (honesty + a11y, template edits)
                 │
                 ├── Phase 6 (vault sync)
                 │
                 └── Phase 7 (CI validation)
```

## Trade-offs: Stay Static vs Build Script vs Full SSG

Concrete numbers, ranges from current codebase state.

### Option A — Stay static (disciplined copy-paste)

Extract duplicated CSS to `theme.css`. Extract duplicated scroll-spy + tabs to `site.js`. Fix the 16 stubs by hand-editing each to match `fuelhh.html`. Leave the manifest as reference-only documentation.

| Metric | Delta vs today |
|---|---|
| LOC removed | ~660 CSS (dataset-page block × 22) + ~200 JS (scroll-spy + setTab × 22) = ~860 lines |
| LOC added | 0 |
| New infrastructure | None |
| One-time cleanup effort | Medium — 22 stubs × ~150 lines each to author |
| Per-future-dataset effort | High — hand-edit 4-5 files (new page + vendor hub + N sibling-sidebar updates + manifest) |
| Risk of drift | High — 22-vs-25-vs-28 problem will recur |
| Wins when | Cleanup milestone is one-off, no second vendor planned for 6+ months |

### Option B — Tiny build script (recommended)

Add ~200 LOC of Python build script + a single `dataset.html` template + 23 per-dataset partials. Generated HTML lives at the same paths.

| Metric | Delta vs today |
|---|---|
| Duplication removed | ~660 CSS + ~200 JS extracted to shared assets. Per-dataset page bodies (~150-210 LOC × 22) move from hand-edited to generated-from-template + partial. |
| LOC added | ~200 build script + 1 × ~250-line template + 25 × ~80-line partial = ~2,250 lines of new build inputs. |
| Net LOC | **Roughly neutral** — generated HTML is still committed (review surface) so raw LOC count does not collapse. The real win is **single-source-of-truth maintenance**, not file size. |
| Maintenance win | One template edit propagates to 25 dataset pages. One manifest edit updates the sidebar / related-grid on every sibling page. Counts cannot drift. |
| New infrastructure | `gridflow-build` CLI (stdlib only), `build/` directory |
| One-time cleanup effort | Medium-high — author the template once, then mostly content authoring (filling 22 partials, similar effort to A) |
| Per-future-dataset effort | Low — edit manifest + one partial, run build, commit |
| Risk of drift | Low — counts derive from manifest, sidebars derive from manifest |
| Wins when | Cross-vendor work is real (ENTSO-E + 5 stubs in this milestone alone) and author bandwidth for future maintenance matters |

### Option C — Full SSG (11ty / Astro / Hugo)

Adopt a real SSG. Markdown content with frontmatter. Build emits `_site/` which becomes the Pages artefact.

| Metric | Delta vs today |
|---|---|
| LOC removed | Roughly same as B |
| LOC added | Less than B (the SSG handles templating) |
| New infrastructure | npm or Hugo dependency; learning curve; new conventions (Nunjucks templates, frontmatter, collections) |
| One-time cleanup effort | High — port everything to SSG conventions, learn the SSG, restructure repo |
| Per-future-dataset effort | Lowest — frontmatter + content, no build script to maintain |
| Risk of drift | Lowest |
| Wins when | More page types are coming (case studies, deep-dive posts, blog), or markdown authoring is preferred over HTML/string-replacement |
| Doesn't win here because | PROJECT.md constraint "Python 3.11+ stdlib only" implies the author prefers minimal deps; the audience (recruiter spending 30s) doesn't care about the difference between B and C; the migration effort is non-trivial and not part of the current cleanup milestone scope |

**Why B over C:** The portfolio is not growing fast enough to amortise an SSG learning curve. Python is already in the repo for the dev server. A 150-line Python script is reviewable in 10 minutes; an 11ty migration is a multi-week project that competes with content authoring for time.

**Why B over A:** ENTSO-E is in this milestone. Five more vendor stubs are in this milestone. Whatever pattern lands here is the pattern for the next milestone's "fill in ENTSO-G datasets" work, the milestone after that's "ENTSO-E coverage to 14 datasets", etc. Option A pays the duplication tax forever; Option B retires it in this milestone.

**When to revisit:** If the site adds a fourth content type (e.g. a blog), revisit Option C. Until then, Option B is the right size.

## Build-vs-Runtime Per Concern (Q6)

The question is per-concern, not blanket. This table is what the roadmap will key off.

| Concern | Currently | Build wins? | Runtime wins? | Recommendation |
|---|---|---|---|---|
| **Inline SVG charts** (stackedArea, sparkline, donut) | Runtime via `charts.js` with seeded RNG | No — would bloat HTML | **Yes** — fast, deterministic, cached | Keep runtime. No change. |
| **Sample data rows** (the "what a row looks like" table) | Hardcoded HTML, hand-typed | Tie — author-controlled prose, not derived | No — pointless to fetch | Keep hand-authored in **per-dataset partial**. The build embeds them in source HTML, not at runtime. |
| **Schema rows** (column / type / nullable / desc) | Hardcoded HTML, hand-typed × 22 | **Yes if** there is a canonical source (gridflow's Pydantic schemas). Otherwise keep per-partial. | No — would be a runtime fetch of structured data the user already sees as a table | Phase 1: per-partial frontmatter. Phase 2 (future milestone): generate from `gridflow` Pydantic schemas at build time, cross-repo. |
| **Hero metadata card** (silver path / API path / param style / earliest / volume / PK) | Hardcoded HTML × 22 | **Yes** — partly from manifest (freq/lag/rows), partly from per-partial frontmatter (paths, PK). | No | Build-time. Manifest provides freq/lag/rows; partial frontmatter provides silver_path, api_path, primary_key. |
| **Stats strip** (5 numerical cells in hero) | Hardcoded HTML × 22 | **Yes** — same shape across all datasets | No | Build-time, from manifest + partial frontmatter. |
| **On-this-page sidebar links** | Hardcoded HTML × 22 (and broken on 16 of them — the sidebar lists anchors that don't exist) | **Yes** — derive from template's section list | No | Build-time. The template knows which sections it renders; the sidebar can be generated from the template's own structure. Or: per-partial frontmatter `sections: [overview, schema, sample, caveats, related]` so the build conditionally emits sidebar links matching content present. |
| **Sibling-datasets sidebar list** ("← All datasets" + ~5 sibling slugs) | Hardcoded × 22, manually synced | **Yes** — derived from `elexon.json` by category | Maybe — could be runtime fetch of manifest | Build-time. Runtime fetch adds a network round-trip for content that's the same on every reload. Build-time bakes it into source HTML for free. |
| **Related datasets grid** (cards at bottom of page) | Hand-curated × 22 | **Yes** — derived from `elexon.json` category | No | Build-time. Same logic as sibling sidebar. |
| **Vendor hub category card grids** | Hardcoded × 1 (elexon.html) | **Yes** — derived from `elexon.json` groups | No | Build-time. The "28 datasets" count on the vendor hub also derives from `len(manifest)`. |
| **Dataset / vendor counts** (footer "49 datasets", index "7 Vendors / 49 Datasets", catalog hub "28 datasets") | Hardcoded × 3 (drift!) | **Yes** — derived from manifests | No | Build-time. Either re-emit the pages that mention counts, or use a marker-region pattern (`<!-- BUILD:count -->25<!-- /BUILD -->`) and have the build update them in place. |
| **Active nav link highlighting** | Runtime via `site.js` data-page → key map | No | **Yes** — already correct | Keep runtime. No change. |
| **Mobile menu toggle, copy buttons** | Runtime via `site.js` | No | **Yes** | Keep runtime. No change. |
| **Footer link list** (Project / Catalogue / Code) | Runtime via `site.js` template literal | No | **Yes** — single source already | Keep runtime. Could move to build-time, but no win — it is already centralised. |
| **Breadcrumbs** | Hardcoded HTML × 22 | **Yes** — derive from page path | No | Build-time. The template renders breadcrumbs from `{{vendor_name}}` + `{{slug}}`. |

**Summary:** Almost everything that today is "hand-curated and duplicated across 22 files" wins at build-time. Things that are already centralised (`site.js`, `theme.css`, `charts.js`) stay at runtime. The roadmap's structural cleanup is largely a one-time build-time migration.

## Scaling Considerations

| Scale | Architecture approach |
|---|---|
| **1 vendor, 22 datasets (today)** | Option A (stay-static) and Option B (build script) both work. The duplication tax of A is felt but manageable. |
| **2-3 vendors, 30-50 datasets (this milestone + next)** | Option B comfortably; Option A becomes painful (every new dataset means editing N sibling pages). |
| **5-7 vendors, 100+ datasets (multi-milestone future)** | Option B still works; Option C (real SSG) starts to win on convenience but is not yet mandatory. |
| **Author left, someone new contributes** | Option B's `build/content/<vendor>/<slug>.md` + `elexon.json` shape is self-explanatory in minutes. Option A's "edit 22 files in sync" is institutional knowledge. |

### First bottleneck

The thing that breaks first is not performance — pages already load fast. It is **author velocity per dataset added**. Today, adding a dataset is: create HTML, copy from `fuelhh.html`, edit 22 places in surrounding pages, update manifest, hope none drift. That is ~30-60 minutes per dataset for a content-only addition.

Under Option B: edit manifest, edit one partial, run build. ~10 minutes per dataset, no drift possible.

### Second bottleneck

After velocity, the next bottleneck is **content alignment between on-site and the Obsidian Vault** (PROJECT.md mentions this as a milestone item). Today there is no shared structure; sync is manual. Under Option B with frontmatter-driven content, the sync becomes a structural mapping not a content rewrite.

## Anti-Patterns

### Anti-Pattern 1: Generating pages with a fetch on every page load

**What people do:** Make the HTML pages empty shells; `site.js` fetches the manifest and renders the cards/sidebar/related-grid on load.

**Why it's wrong here:**
- Every page render becomes "blank → flash of content". Worse perceived performance than today.
- Recruiters who view-source see no content. (Audience matters: this site explicitly targets recruiters.)
- Adds dependency between the manifest JSON and `site.js` — and that wiring is non-trivial (categories, siblings-by-category, related-grid layout).
- Saves nothing vs build-time generation; gains nothing except avoiding a build step.

**Do this instead:** Build-time generation. Manifest is consumed once at build; output HTML has the content baked in. Same input, better output, no runtime cost.

### Anti-Pattern 2: SSG migration as a "while we're at it" addition to the cleanup milestone

**What people do:** Adopt 11ty / Astro / Hugo as part of fixing the duplication, on the theory that "if we have to refactor anyway, do it properly."

**Why it's wrong here:**
- Multiplies the milestone's risk. The cleanup is already non-trivial (22 stubs to author content for + ENTSO-E + vault sync); adding "learn an SSG" doubles down on novelty.
- New conventions (Nunjucks, frontmatter dialects, collections, permalinks) all have a learning tail.
- The author's primary deliverable is portfolio content; tooling should not eat that bandwidth.
- The migration can happen later if it ever needs to. Option B's structure is a pre-migration of half the work — partials are partials in any SSG.

**Do this instead:** Option B now. Revisit Option C if a fourth content type emerges (blog, deep-dive posts) or if the author finds themselves spending time wrangling Python string-replacement instead of writing content.

### Anti-Pattern 3: Multiple sources of truth for counts

**What people do:** Hardcode "28 datasets" in `data-sources.html`, "49 datasets" in `site.js`, "7 Vendors / 49 Datasets" in `index.html`. Forget that the manifest says 25.

**Why it's wrong here:** Already broken today. CONCERNS.md documents three inconsistent counts.

**Do this instead:** Manifest is the operational source of truth. Every count is derived: `len(load(elexon.json).groups.flatMap(g, g.datasets))` is **the** Elexon count. The build emits this number into every HTML page that mentions it. The "28" claimed today is a fiction (the manifest enumerates 25; the disk has 22). Pick the manifest, fix the manifest if it's wrong, and let everything derive from there.

### Anti-Pattern 4: Two scroll-spy variants, one minified, one not

**What people do:** Already done — 16 of 22 pages have a hand-minified scroll-spy IIFE; 6 have the un-minified version; both are inline in every page. (CONCERNS.md.)

**Why it's wrong here:** Bug fixes apply twice. Identical functionality exists in two near-duplicate forms.

**Do this instead:** Move the scroll-spy into `site.js`, gated by presence of `.sidebar a[href^="#"]`. Delete from all 22 pages. This is part of Phase 2.

## Integration Points

### External services

| Service | Integration | Notes |
|---|---|---|
| GitHub Pages | `actions/upload-pages-artifact path: site/hifi` (unchanged) | The build emits into `site/hifi/`; the deploy uploads `site/hifi/`. No change to the workflow. |
| Google Fonts | `<link>` tags in every HTML, with `?display=swap` | Pre-existing. Site claims "0 cloud deps" in index.html which contradicts this — flag for the honesty sweep. Optionally self-host the three families under `site/hifi/assets/fonts/`. |

### Internal boundaries

| Boundary | Communication | Notes |
|---|---|---|
| **Manifest ↔ build script** | Build reads JSON from disk | Manifest is the source of truth for structural facts (id, category, freq, lag, rows). |
| **Build script ↔ generated HTML** | Build writes HTML to disk | The build is idempotent: running it twice produces the same bytes. CI can validate this. |
| **Generated HTML ↔ site.js** | DOM contract: `body[data-page]`, `body[data-root]` | Build emits correct values into the template; runtime injects chrome from them. |
| **Generated HTML ↔ charts.js** | DOM contract: `[data-chart]` elements with `data-opts` JSON | Build emits the chart container element; charts.js renders into it. |
| **Generated HTML ↔ theme.css** | CSS class names | Build emits classes that match `theme.css` rules. No inline styles in dataset pages after the refactor. |
| **`build/content/<vendor>/<slug>.md` ↔ vault** | File-level sync (script in a separate milestone) | The frontmatter shape designed in Phase 3 should align with `anthropic-skills:gridflow-dataset-spec`. |

## If-SSG-Then-X / If-Stay-Static-Then-Y Branching

The planning phase can pick the path. Both work; the architecture below adapts.

### If Option B (tiny build script — recommended):

- New top-level directories: `build/templates/`, `build/content/<vendor>/`.
- New entry point: `src/gridflow_front_end/build.py` exposing a `gridflow-build` console script via `pyproject.toml`.
- `pyproject.toml` adds `gridflow-build = "gridflow_front_end.build:main"` next to `gridflow-serve`. No new dependencies (stdlib only).
- `serve.py` optionally gains a `--build-on-reload` flag.
- `.github/workflows/deploy.yml` optionally runs `gridflow-build` before the upload step — or doesn't (commit the generated HTML and let the workflow upload as-is). Recommendation: commit generated HTML. It is reviewable in PRs and the deploy stays a single-step upload.
- **Consequence of committing generated HTML:** manifest-touching PRs will show diffs in every page where the sibling-sidebar or related-grid changes — PR review surface balloons on cross-cutting changes. The alternative (generate-in-CI, don't commit output) trades that cost for a Pages workflow build step and no rendered-output diff to review in PRs. Either is workable; the planning phase should pick deliberately.
- The 16 stub dataset pages get rewritten from their partials; the 6 complete ones are diff-validated against their existing forms.

### If Option A (stay-static — fallback):

- No new directories, no build script.
- `theme.css` absorbs the dataset-page styles (Phase 2 of the roadmap).
- `site.js` absorbs the scroll-spy and the tabs migration (Phase 2).
- All 22 stub fixes are hand-edits, copying from `fuelhh.html`.
- The manifest stays as reference-only. Counts continue to be hand-synced; the discrepancy is fixed once (manually align to 25, the manifest's count) and re-policed on every dataset addition.
- The "Hardcoded duplicated catalogue counts" anti-pattern is accepted as a maintenance tax.

### If Option C (full SSG — deferred):

- Repo restructure: `src/` content directory, `_site/` build output, SSG config file.
- `deploy.yml` upload-pages-artifact `path` changes to `_site/`.
- Markdown-based authoring; frontmatter conventions become the SSG's defaults.
- The `gridflow-serve` Python CLI may stay (it serves `_site/` instead of `site/hifi/`) or get replaced by the SSG's dev server.
- Out of scope for this milestone per PROJECT.md Constraints.

## Sources

### Reference data-doc sites

- [Stripe API Reference](https://docs.stripe.com/api) — three-column reference page layout; sidebar tree + center content + persistent right-rail code samples.
- [Stripe's new API reference documentation (Rohit Eddy / Medium)](https://medium.com/the-oxford-comma/stripes-new-api-reference-documentation-e6b1fc46896d) — design discussion of the three-column layout.
- [Why Stripe's API Docs Are the Benchmark (apidog blog)](https://apidog.com/blog/stripe-docs/) — anatomy breakdown.
- [Cloudflare Developer Docs — Sidebar style guide](https://developers.cloudflare.com/style-guide/frontmatter/sidebar/) — frontmatter-driven sidebar pattern; closest match to the manifest-as-source-of-truth approach recommended here.
- [Cloudflare Developer Docs — Navigation content type](https://developers.cloudflare.com/style-guide/documentation-content-strategy/content-types/navigation/) — "navigation pages" as sub-landing pages (vendor hub equivalent).
- [Elexon BMRS API Documentation Portal](https://bmrs.elexon.co.uk/api-documentation/introduction) — the source of truth this site documents.
- [Elexon BMRS — REMIT endpoint reference page](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/REMIT) — example endpoint page anatomy from the vendor.

### Static-site + partials patterns

- [The Simplest Ways to Handle HTML Includes (CSS-Tricks)](https://css-tricks.com/the-simplest-ways-to-handle-html-includes/) — survey of options when HTML lacks native includes. Confirms there is no built-in answer and the build-script approach is the most portable.
- [Building A Static Site With Components Using Nunjucks (Smashing Magazine)](https://www.smashingmagazine.com/2018/03/static-site-with-nunjucks/) — partial-based authoring pattern that informs the `build/content/<vendor>/<slug>.md` shape.
- [Writing a static site generator in a single file (herluf-ba.github.io)](https://herluf-ba.github.io/writing-a-static-site-generator-in-a-single-file.html) — proof that the Option B "tiny build script" approach is well-trodden.
- [DIY Static Site Generation (Harley's Blog)](https://www.harleylang.com/blog/2022/diy-ssg/index.html) — pragmatic build-script patterns.

### SSG comparison (informing why not Option C now)

- [Eleventy — Create Pages From Data](https://www.11ty.dev/docs/pages-from-data/) — the canonical "pages from JSON" pattern. The Option B build script implements a subset of this; migration to 11ty later is a structural mapping not a rewrite.
- [Eleventy — Global Data Files](https://www.11ty.dev/docs/data-global/) — the `_data` directory pattern, equivalent to keeping `elexon.json` and `vendors.json` in `site/hifi/data/`.

### API reference anatomy

- [Response example and schema — Step 5 of the API ref tutorial (idratherbewriting)](https://idratherbewriting.com/learnapidoc/docapis_doc_sample_responses_and_schema.html) — best practices for the schema + sample sections; confirms our anatomy is conventional.

---

*Architecture research for: editorial portfolio + data-documentation site*
*Researched: 2026-05-17*
