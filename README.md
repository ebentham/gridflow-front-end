# gridflow-front-end

Static documentation site for the [gridflow](https://github.com/EBentham/gridflow) ETL
pipeline (UK/EU energy market data) and the [gridflow-models](https://github.com/EBentham/gridflow-models)
modelling projects. Editorial-quiet portfolio aimed at full-stack data-science recruiters
in energy trading. **Not a product** — no SaaS chrome, no fake live indicators.

Deployed via GitHub Pages from `site/hifi/` on push to `main`.

## Quick start

```bash
# install runtime + build deps
uv pip install -e ".[build]"

# render dataset pages from vault content
gridflow-build

# serve the rendered site locally
gridflow-serve
```

`gridflow-serve` is stdlib-only (Python 3.11+). `gridflow-build` depends on Jinja2,
which lives in the `[build]` extras group only.

## Source of truth

Critical — do not invert without explicit discussion:

1. **gridflow code** (`gridflow/src/gridflow/schemas/*.py`, `silver/**/*.py`,
   `connectors/**/*.py`) — canonical
2. **Live API responses** — verified by `verify_curl_and_silver_schema.py` in the
   gridflow vault
3. **Obsidian Vault** (`<vault>/30-vendors/<vendor>/datasets/*.md` — vendored into
   this repo under `vault/<vendor>/`) — authored docs derived from #1 + #2
4. **On-site rendered pages** (`site/hifi/data-sources/<vendor>/<dataset>.html`) —
   generated from #3 via `gridflow-build`; gitignored

Pages under `site/hifi/data-sources/elexon/` and the vendor hub
`site/hifi/data-sources/elexon.html` are **build outputs** — do not edit them
directly. Edit the source vault file at `vault/elexon/<slug>.md` and re-run
`gridflow-build`.

## Build pipeline

```
vault/elexon/*.md ──┐
                    ├── gridflow-build ── site/hifi/data-sources/elexon/*.html
site/hifi/data/    ─┘                  └── site/hifi/data-sources/elexon.html
  elexon.json
```

### Vault → site mapping

The `gridflow-build` script reads each vault markdown file's YAML frontmatter plus a
fixed set of `## H2` sections, then renders the Jinja2 templates in `templates/`.

| Vault file location                | Template section it feeds                                                          |
|------------------------------------|-------------------------------------------------------------------------------------|
| Frontmatter `last_verified:`       | "Verified against vendor docs: YYYY-MM-DD" micro-line under the hero lede           |
| Frontmatter `dataset_key:`         | URL slug (`<slug>.html`), sidebar self-link, breadcrumb terminal                    |
| `# H1` line                        | Hero `<h1>` title (with optional `(CODE)` parenthetical retained as inline mono)    |
| `## Overview`                      | First paragraph → hero lede; all paragraphs → `#overview` section body              |
| `## API endpoint` (k/v table)      | `Base URL`, `Path`, `Auth` cells in the `#api` section's ENDPOINT card              |
| `## Bronze layer` (k/v block)      | `Bronze path` cell in the `#api` section's BRONZE card                              |
| `## Silver layer` (k/v block)      | `Silver path`, `Transformer class`, `Pydantic schema`, `Dedup key`, `Point-in-time` |
| `### Silver schema` (md table)     | `<table class="schema-table">` rows in the `#schema` section                        |
| `### Silver sample` (fence or md)  | `<table class="data-table">` or `<pre class="code">` in the `#sample` section       |
| `## Known issues and gotchas`      | Numbered caveat list in the `#caveats` section                                      |
| Manifest `site/hifi/data/elexon.json` group entry | `group`, `freq`, `lag`, `rows` in hero stats strip + sibling sidebar + related-grid |

### Manifest

`site/hifi/data/elexon.json` is the structural manifest. Every dataset declared here
must have a matching vault file at `vault/elexon/<id>.md`, or the build aborts.
Datasets in the vault but not in the manifest are tolerated (they are out-of-scope
v1 documents that don't get rendered).

The manifest is also the source for:
- Sidebar sibling list on each dataset page (datasets in the same group)
- Related-card grid at the bottom of each dataset page (up to 4 siblings)
- Catalog hub card grid on `site/hifi/data-sources/elexon.html`
- Dataset count chips and table cells (33 across the milestone)

### Content audit (`gridflow-build --check`)

Two checks run when `--check` is passed:

1. **Idempotence**: build twice, diff outputs. Non-zero exit on drift.
2. **Content audit** (always runs): warn per dataset for missing schema rows /
   sample / caveats / Pydantic class declaration. Fail loud if a vault file has
   no Overview or no API endpoint.

CI runs `gridflow-build --check` after the initial build (see
`.github/workflows/deploy.yml`).

## Repo layout

```
.
├── .github/workflows/deploy.yml      # GitHub Pages deploy on push to main
├── pyproject.toml                    # gridflow-serve (runtime) + gridflow-build ([build] extra)
├── src/gridflow_front_end/
│   ├── serve.py                      # stdlib-only local dev server
│   └── build.py                      # Jinja2 renderer over vault content
├── templates/
│   ├── _partials/                    # shared head + partials
│   ├── dataset.html.j2               # 7-section dataset page template
│   └── vendor-hub.html.j2            # vendor catalog template
├── vault/
│   └── elexon/*.md                   # 33 vendored Elexon dataset specs
└── site/
    └── hifi/                         # deploy artefact (uploaded to GitHub Pages)
        ├── index.html                # hand-authored
        ├── architecture.html         # hand-authored
        ├── data-sources.html         # hand-authored
        ├── data-sources/             # build outputs (gitignored except hub stubs)
        ├── data/elexon.json          # structural manifest
        ├── assets/theme.css          # shared stylesheet
        ├── assets/site.js            # chrome injection + scroll-spy + tabs
        └── assets/charts.js          # deterministic seeded SVG charts
```

## Planning artifacts

The full project context lives under `.planning/`:

- `PROJECT.md` — project framing, audience, core value, locked decisions
- `REQUIREMENTS.md` — 50 REQ-IDs across 11 categories
- `ROADMAP.md` — phase breakdown with per-phase success criteria
- `BUILD-DIFFS.md` — intentional diffs from the byte-equivalence baseline (Phase 3)
- `research/` — feature anatomy, stack rationale, pitfalls
- `codebase/` — current-state analysis

## License

MIT. See [LICENSE](LICENSE).
