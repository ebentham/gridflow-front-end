# Stack Research

**Domain:** Editorial portfolio + data-documentation static site (UK/EU energy markets), single author, GitHub Pages deploy
**Researched:** 2026-05-17
**Confidence:** HIGH (versions verified against official sources; recommendation grounded in this repo's constraints)

---

## TL;DR — Go / No-Go on Adopting an SSG

**GO on a build step. NO-GO on a Node/Go ecosystem.**

**Primary recommendation: Python 3.11 + Jinja2 3.1.6 + a `gridflow-build` CLI** that templates against the existing `site/hifi/data/elexon.json` manifest, sibling to the existing `gridflow-serve` CLI. Build output lands in `site/hifi/` (or a sibling `_dist/` mirrored to `site/hifi/` by CI), GitHub Pages still serves a plain static directory.

**Why not 11ty/Astro/Hugo:** All three are excellent SSGs. None of them are *better-aligned* than Jinja2 for this specific repo, which is (a) solo-maintained, (b) Python-first by author preference, (c) already has a JSON manifest in the exact shape pagination needs, and (d) is itself a portfolio piece where "I built a 100-line Python templater over my own data" is a *stronger* signal than "I installed Astro" for a recruiter screening a data/ML role.

**What this solves vs what it doesn't** (be explicit — the roadmap consumer needs this distinction):

| Pain point | Solved by SSG adoption? |
|------------|-------------------------|
| ~660 lines of duplicated `<style>` blocks across 22 files | **No** — solved by moving rules into `theme.css`. 15-minute fix, zero build needed. |
| 16 broken dataset stubs (missing `#overview`/`#schema`/`#sample`/`#api` sections) | **Yes** — regenerate from a single template + manifest is the right answer. |
| Duplicated catalogue counts ("28 datasets" hardcoded in 6 places) | **Yes** — counts derive from `elexon.json` at build time. |
| Two scroll-spy script variants + 22 redeclared `setTab()` globals | **No** — solved by moving into `assets/site.js`. SSG-orthogonal. |
| Sidebar sibling-dataset lists hand-curated per page | **Yes** — generated from the category in `elexon.json`. |
| Scaling to ENTSO-E + 4 more vendors at fuelhh fidelity | **Yes** — a vendor + dataset is one row in JSON, not 600 lines of HTML. |
| Mobile viewport bug (`width=1280` on 23 pages) | **Indirectly** — once pages are generated, fixing one template fixes all. |

The SSG adoption is justified by half the v1 milestone (broken stubs, counts, sidebars, cross-vendor scaling). The other half (CSS extraction, JS consolidation, viewport fix) is independently necessary and should ship first, regardless of SSG decision.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | `>=3.11` | Build-time templating engine, dev server | Already the author's preferred runtime; already required by `pyproject.toml`; sibling projects (`gridflow`, `gridflow-models`) are Python; recruiters reading this site land on Python repos. |
| Jinja2 | `3.1.6` (released 2025-03-05) | HTML templating | Industry-standard Python templating; mature (2008+); zero novelty risk; supports template inheritance, macros, includes — everything the duplication problem needs. Single dependency. Released for Python 3.7+. |
| HTML5 / CSS3 / vanilla JS (ES2017+) | n/a | Deployed site content | Already in use; no transpilation; GitHub Pages serves these directly. No change. |
| GitHub Pages (via Actions) | n/a | Hosting | Already configured (`.github/workflows/deploy.yml` → `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4`). Build step inserts before the upload-artifact step. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uv` | latest | Package management | Per user's global CLAUDE.md preference; install dev/build deps via `uv pip install -e ".[dev]"`. |
| `pytest` | `>=8.0` | Build-output smoke tests | Test that generated HTML has the required sections, that all internal links resolve, that all 25 manifest IDs produce a file. Use `-x -q` per global prefs. |
| `ruff` | latest | Lint + format for the Python builder | Already standard in user's projects; `ruff check` + `ruff format`. |
| `mypy` | latest | Strict typing for the builder (optional but cheap) | The builder is ~150 lines of Python; full annotations are trivial and consistent with the user's `from __future__ import annotations` style. |
| `htmlhint` or `lychee` (link checker) | latest | Pre-deploy validation in CI | Catches the exact class of bug (broken stubs, dead `href="#"` links) that motivated this whole milestone. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `gridflow-serve` (existing) | Local dev server | Stays stdlib-only. No changes. Serves `site/hifi/` post-build. |
| `gridflow-build` (new console script) | Render templates → `site/hifi/` | New entry in `pyproject.toml` `[project.scripts]`. Reads `site/hifi/data/*.json`, renders Jinja templates from `site/hifi/_templates/`, writes to `site/hifi/data-sources/`. |
| Polars (NOT pandas) | If any data transforms creep into the builder | Per user's global preference. The fuelhh.html sample currently shows pandas in its Python example — that's *displayed* code on the site, not used in build. Builder code itself should use Polars if it ever processes tabular data. |

### Installation

```bash
# Existing (no change)
uv pip install -e .

# Add build deps (new [build] extra in pyproject.toml)
uv pip install -e ".[build]"

# Run the builder
uv run gridflow-build           # writes generated pages
uv run gridflow-serve           # serves site/hifi/

# Test
uv run pytest -x -q tests/
uv run ruff check src/ tests/
```

`pyproject.toml` additions:

```toml
[project.optional-dependencies]
build = ["Jinja2>=3.1.6,<4"]
dev   = ["pytest>=8", "ruff", "mypy"]

[project.scripts]
gridflow-serve = "gridflow_front_end.serve:main"
gridflow-build = "gridflow_front_end.build:main"   # new
```

**Critical constraint preserved:** Jinja2 is a *build-time* dependency only. The deployed artifact in `site/hifi/` remains pure static HTML/CSS/JS. The `gridflow-serve` runtime path stays stdlib-only, per the PROJECT.md constraint "Python 3.11+ stdlib only for the dev server. No third-party Python deps in the deployed path."

---

## Alternatives Considered

The full evaluation matrix. Recommendation rationale is the discriminator column.

| Option | Verdict | Rationale |
|--------|---------|-----------|
| **Python + Jinja2 + custom CLI** | **RECOMMENDED** | Stack-aligned; manifest is already in the right shape; ~150 lines of code; reads as deliberate craft for a Python/data portfolio; zero new ecosystem. |
| **Eleventy (11ty) v3.1.5** | Strong alternative | The most natural fit *as an SSG* — pagination over JSON is literally one of its showcase patterns. Loses on: introduces Node 18+ ecosystem to a Python repo; one more thing for the solo author to context-switch into; recruiters viewing a data/ML portfolio don't expect a Node toolchain. |
| **Astro v6** | Overpowered | Excellent framework, but its strengths (islands architecture, partial hydration, MDX, content collections, server endpoints) are anti-goals here. PROJECT.md explicitly rules out interactivity/SaaS framing. Using Astro for this site is like using a torque wrench to hang a picture. |
| **Hugo v0.161.1** | Fast but high-friction | Go templates are unfamiliar to most Python/JS authors; Hugo's data-cascade is powerful but the mental model is heavy for ~50 pages. Build is *very* fast, but build speed is not the bottleneck at this scale. Author has no Go elsewhere in the toolchain. |
| **Stay-static + discipline (no build)** | NO | The 16 broken stubs and 22 duplicated sidebars are direct evidence discipline is not sufficient at this scale. Adding ENTSO-E (≥1 dataset in v1, full coverage later) multiplies the problem. |
| **Build-time `cat` / `sed` partial concatenation** | NO | A "lite" build that just glues HTML fragments together solves the CSS-extraction problem (already solvable in CSS alone) but doesn't solve dataset-page templating. Wrong tool for the actual pain. |

### When the alternatives *would* win

| Recommended | Alternative wins if... |
|-------------|------------------------|
| Jinja2 + custom CLI | The author plans to add MDX-style content authoring (interactive code-fenced examples, live demos) — then **Astro v6**. Not on the v1 roadmap, but a legitimate future pivot. |
| Jinja2 + custom CLI | The author plans to bring on collaborators who already know JS/Node tooling — then **11ty v3**. PROJECT.md says solo, so no. |
| Jinja2 + custom CLI | The site grows to 1000+ pages and incremental build becomes a bottleneck — then **Hugo**. At ~50 pages, Jinja2 builds in under a second. |
| Jinja2 + custom CLI | The author wants a community ecosystem of themes/plugins to draft from — then **11ty** or **Astro**. The author already has a hand-built design system, so this is negative value. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Jekyll** | Default GitHub Pages SSG but: Ruby toolchain (yet another ecosystem); Liquid templating less powerful than Jinja2; community momentum shifted to 11ty/Astro/Hugo; slow builds; legacy energy. | Jinja2 (Python), or 11ty (Node) if SSG-by-default-tooling matters. |
| **Next.js / Nuxt / SvelteKit** | All framework-first; assume an interactive app. Server components, hydration, routing — all anti-goals for a static documentation site. Heavy build output, large JS payloads even when SSG'd. | Astro v6 if you absolutely want a JS-framework SSG; otherwise stick with Jinja2 or 11ty. |
| **Webpack / Vite as the build root** | Bundlers solve a problem this site doesn't have (module graphs, transpilation, code-splitting). Adding one introduces config, lock files, and dependency churn for zero benefit. The JS here is three IIFE files with no module system. | No bundler. Ship JS files as-authored. Use `theme.css` directly. |
| **Tailwind / utility CSS frameworks** | Would invert the current design system (cream + forest + Fraunces is a curated identity with named tokens in `theme.css` — `--paper`, `--ink`, `--accent`, etc.). Tailwind would dilute the editorial aesthetic and create class-soup that fights the existing voice. | Continue with the hand-authored `theme.css` design tokens. |
| **MDX** | Mixes Markdown with JSX/Astro components. PROJECT.md is explicit that interactivity is anti-goal. MDX value is real but orthogonal to this site's purpose. | Plain HTML in templates. If long-form prose grows, Jinja2 can include a Markdown filter (`markdown2` or `mistune`) trivially — but that's a future call. |
| **Pandas (anywhere)** | Per user's global CLAUDE.md: "**DataFrames: Polars only. Never pandas.**" | Polars in any build-time data transforms. Note: the user-facing fuelhh.html shows pandas in a *displayed code example* — that's documentation of the gridflow ETL ecosystem (which itself uses Polars; the on-site example may need updating). |
| **A second JSON file format (TOML/YAML) for data manifests** | The existing `elexon.json` and `vendors.json` are JSON. Mixing formats adds parser surface area and inconsistency. | Stay JSON. Generate `vendors.json` from a `vendors/` tree if hand-maintenance becomes painful. |
| **Self-hosting Google Fonts in v1** | A reasonable optimisation but a *separate* concern from templating. CONCERNS.md flags it as a perf/sovereignty issue ("0 Cloud deps" claim vs Google Fonts reality) — handle it in a follow-up. | Defer to a later milestone or fold into the honesty sweep if scope permits. |

---

## Stack Patterns by Variant

**If we stick with the recommended Jinja2 path:**
- Directory layout:
  - `site/hifi/_templates/` — Jinja templates (gitignored from Pages by putting underscore prefix; or move to `templates/` at repo root and have the builder write into `site/hifi/`)
  - `site/hifi/_templates/dataset.html.j2` — the canonical dataset template (derived from current `fuelhh.html`)
  - `site/hifi/_templates/vendor.html.j2` — the canonical vendor-hub template (derived from current `data-sources/elexon.html`)
  - `site/hifi/_templates/_partials/` — header, footer, sidebar, schema-table, sample-table, caveat-list, related-grid
  - `site/hifi/data/` — keep `elexon.json`, `vendors.json`, plus per-dataset overrides (`elexon/fuelhh.json` with prose/schema/sample/caveats specific to that dataset)
- Build flow: walk `data/`, for each entry render the matching template, write to `data-sources/<vendor>/<dataset>.html`. Idempotent; safe to commit output.
- CI: Run `gridflow-build` in `.github/workflows/deploy.yml` before the upload-artifact step. Or commit generated HTML and skip the CI build (simpler, more auditable, only ~50 files).

**If the author later wants client-side interactivity:**
- Use `Astro v6` islands architecture (selective hydration) for individual widgets.
- Keep the Jinja2 builder for everything else; Astro is overkill for static pages.
- This is a v2+ concern, not v1.

**If a second author joins:**
- Re-evaluate. 11ty has wider community familiarity than "a custom Python build". The trade is worth re-examining the moment the project is no longer solo.

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `Jinja2 3.1.6` | Python `>=3.7` (we use `>=3.11`) | No upper Python bound issues. Pin `Jinja2>=3.1.6,<4` to guard against a hypothetical 4.0 breaking change. |
| `Python 3.11` | `Jinja2`, `pytest`, `ruff`, `mypy`, all current Polars releases | The 3.11 floor matches `pyproject.toml`. |
| `uv` | Any Python version `>=3.8` | No constraint conflict. |
| `actions/upload-pages-artifact@v3` + `actions/deploy-pages@v4` | Any static directory | Already in use; no build-step changes required to the workflow other than inserting `uv run gridflow-build` before the upload step. |

**Cross-stack note (only if the alternative path is taken):**

| Package (alternative path) | Compatible With | Notes |
|----------------------------|-----------------|-------|
| `@11ty/eleventy 3.1.5` | Node `>=18` | If 11ty is chosen, the repo needs `package.json`, `package-lock.json`, and a Node toolchain on dev machines and in CI. Material new surface area. |
| `astro 6.x` | Node `>=18.20` or `>=20.x` | Astro 6 dropped Node 16; ensure CI Node version pinned. |
| `hugo v0.161.1` (extended build for SCSS) | None — single binary | Hugo's appeal is zero-runtime; the extended variant is needed only if SCSS/asset processing is required (not here). |

---

## Confidence Per Recommendation

| Claim | Confidence | Source |
|-------|------------|--------|
| Jinja2 3.1.6 is the current stable, supports Python 3.7+ | HIGH | PyPI release page (2025-03-05 release date) |
| 11ty 3.1.5 is the current stable, requires Node 18+ | HIGH | 11ty official docs |
| 11ty pagination over JSON is the idiomatic pattern for "one page per item" | HIGH | 11ty Pages from Data docs (`pagination.data` / `permalink` / `alias`) |
| Astro 6 is the current major, supports islands + MDX | HIGH | Astro getting-started page |
| Hugo v0.161.1 is the current release (2026-04-29) | HIGH | Hugo GitHub releases |
| Jinja2 + custom CLI is the *best* fit for this specific repo | HIGH | Repo-specific reasoning: existing Python toolchain, existing JSON manifest, single-author scope, portfolio-piece framing for a Python/data audience |
| Adopting an SSG resolves the broken-stub class of bug | HIGH | Direct: regenerating from one template eliminates per-file drift |
| Stay-static is insufficient | HIGH | Direct evidence from CONCERNS.md: 22 files have duplicated `<style>` blocks despite identical content — discipline already failed at N=22 |

---

## Recommendation for the Roadmap Consumer

**Phase the work so the SSG is not a prerequisite for shipping fast wins:**

1. **Before any SSG:** Extract the duplicated `<style>` block into `theme.css`. Consolidate scroll-spy and `setTab` into `assets/site.js`. Fix the `viewport` bug on 23 files. These are ~1-day fixes that need no build infrastructure and unblock everything else. They also reduce the surface area the templates will eventually need to model — fewer per-page variations to template if the CSS is already centralised.

2. **Introduce `gridflow-build` as a thin scaffold:** Start with `vendor.html.j2` and `dataset.html.j2` templates that render *one* of the existing complete pages (e.g. `fuelhh.html`) byte-equivalent to its current state. This validates the templating before regenerating broken pages.

3. **Regenerate the 16 broken stubs from the manifest.** Each needs a per-dataset JSON override file (`site/hifi/data/elexon/<id>.json`) carrying the prose, schema rows, sample rows, and caveats. Writing those JSON files *is* the milestone work; the build is just rendering.

4. **Add the ENTSO-E hub + 1 dataset using the same templates.** This is the cross-vendor proof. If the templates can't handle ENTSO-E with light parameterisation, the abstraction is wrong.

5. **CI smoke test (optional but cheap):** After build, run `htmlhint site/hifi/**/*.html` and a link checker. Catches the exact regression class the milestone is solving.

**One blocking constraint to respect throughout:** Jinja2 goes in the `[build]` extra, not in `[project.dependencies]`. The deploy artifact is pure static. The `gridflow-serve` runtime stays stdlib-only. PROJECT.md is explicit on this; the roadmap must not collapse build-time and runtime dependencies.

---

## Sources

- Jinja2 PyPI release page — version 3.1.6 (2025-03-05), Python >=3.7 — HIGH (https://pypi.org/project/Jinja2/)
- Jinja2 official docs — current 3.1.x family — HIGH (https://jinja.palletsprojects.com/)
- Eleventy official docs — v3.1.5 stable, Node 18+ — HIGH (https://www.11ty.dev/docs/)
- Eleventy "Pages from Data" docs — canonical pagination-over-JSON pattern — HIGH (https://www.11ty.dev/docs/pages-from-data/)
- Astro getting-started — v6 current, islands + MDX integration — HIGH (https://docs.astro.build/en/getting-started/)
- Hugo GitHub releases — v0.161.1, released 2026-04-29 — HIGH (https://github.com/gohugoio/hugo/releases)
- Repo files: `.planning/PROJECT.md`, `.planning/codebase/STACK.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/CONCERNS.md`, `site/hifi/data/elexon.json`, `site/hifi/data-sources/elexon/fuelhh.html` — HIGH (direct evidence)
- User global preferences (`~/.claude/CLAUDE.md`) — Python + uv + Polars-only + pytest-fail-fast — HIGH

---

*Stack research for: editorial portfolio + data-documentation static site (gridflow-front-end v1 milestone)*
*Researched: 2026-05-17*
