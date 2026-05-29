# Gridflow front-end — project guide

Documentation static site for the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline and gridflow-models projects. Editorial-quiet portfolio aimed at full-stack data-science recruiters in energy trading. **Not a product** — no fake live indicators, no SaaS-style KPIs, no dashboard chrome.

## Planning artifacts

All workflow context lives under `.planning/`:

- **`CONTROL.md` — read this first.** Orchestrator brief: current phase, skill routing guide, open decisions, locked decisions, cold-start reading order. Updated after every significant decision or phase transition.
- `PROJECT.md` — project context, core value, SoT hierarchy, key decisions
- `REQUIREMENTS.md` — REQ-IDs across 11 categories with traceability to phases
- `ROADMAP.md` — v2 phases (7 → 8B → 9 → 10), dependencies, per-phase success criteria
- `STATE.md` — current workflow state, locked decisions, session continuity note
- `config.json` — workflow preferences (interactive, standard granularity, parallel)
- `research/` — STACK / FEATURES / ARCHITECTURE / PITFALLS / SUMMARY (read SUMMARY first)
- `codebase/` — STRUCTURE / ARCHITECTURE / STACK / CONCERNS / CONVENTIONS / INTEGRATIONS / TESTING

**Start here:** read `.planning/CONTROL.md` → `STATE.md` → `ROADMAP.md` before doing anything else. `CONTROL.md` tells you where you are and what to read next.

## Working agreements

- **Never auto-commit** unless the user asks — this overrides the global "commit after each passing test" cadence (a docs site has no test-driven rhythm).
- Never commit to `main` — feature branches only. Conventional commits (`feat:`/`fix:`/`docs:`/`chore:`/`refactor:`/`test:`); one concern per commit.

## Commands

```bash
uv run gridflow-serve              # stdlib-only dev server (no build deps required)
uv run gridflow-build              # render vault .md → site/hifi/data-sources/ (needs [build] extra: Jinja2)
uv run gridflow-build --check      # idempotence / content audit; CI fails on drift
uv run gridflow-drift-check        # verify rendered pages against their vault sources
```

CI (`.github/workflows/deploy.yml`) additionally runs `htmlhint` and `lychee` link-checking before publishing to GitHub Pages.

## Tech stack

- Static HTML5 + CSS3 + vanilla JS (ES2017+, no transpilation, no modules)
- Single shared stylesheet (`site/hifi/assets/theme.css`)
- Runtime chrome injection (`site/hifi/assets/site.js`) via body `data-page` / `data-root` / `data-screen-label` attribute contract
- Deterministic seeded inline-SVG charts (`site/hifi/assets/charts.js`)
- Python 3.11+ stdlib-only dev server (`src/gridflow_front_end/serve.py`, exposed as `gridflow-serve`)
- `gridflow-build` console script (Python + Jinja2 3.1.x) renders vault `.md` files → `site/hifi/data-sources/` (vault → site direction); Jinja2 lives in `[build]` extras only, the runtime dev server stays stdlib-only
- Generated HTML is gitignored; CI runs `gridflow-build --check` before `upload-pages-artifact`
- Deploy: GitHub Pages from `site/hifi/` via `.github/workflows/deploy.yml` on push to `main`

## Source-of-truth hierarchy

Critical — do not invert without explicit discussion:

1. **gridflow code** (`<gridflow>/src/gridflow/schemas/*.py`, `silver/**/*.py`, `connectors/**/*.py`) — canonical
2. **Live API responses** (verified by `verify_curl_and_silver_schema.py` in the vault)
3. **Obsidian Vault** (`<vault>/30-vendors/<vendor>/datasets/*.md`) — authored docs derived from #1+#2; **33 active Elexon datasets**
4. **On-site rendered pages** (`site/hifi/data-sources/<vendor>/<dataset>.html`) — published view generated from #3 via the build script

## Cross-repo paths (Windows local)

- Vault: `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`
- Gridflow main repo: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\`
- This repo: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\`

CI will need both vault and gridflow checkouts available when running `gridflow-build`.

## Key decisions already locked (don't relitigate)

- Editorial / quiet aesthetic (cream + forest-green palette, Fraunces + Inter + JetBrains Mono)
- Recruiter-first audience: full-stack data scientist within energy trading
- Core value: domain depth over polish, gateway, or personal reference
- v1 Elexon scope: **33 datasets** (matches gridflow connector + vault)
- Vault → site direction (vault is the authored content layer)
- Templating: Python + Jinja2 (Option B + CI build)
- ENTSO-E cross-vendor proof: Generation by PSR type
- Kill all 'live' framing; charts are illustrative snapshots
- License: MIT

## Anti-goals

- Looking like a SaaS product or dashboard
- Fake live indicators (timestamps, "X min ago", "Shipping" status badges on unfinished work)
- Performance metrics / KPIs / uptime badges
- Adopting Node/Go SSGs (11ty, Astro, Hugo) — rejected for Python-first portfolio alignment
- Hand-authored dataset pages that bypass the build script entirely (one bounded exception: `authored-pages/<vendor>/<slug>.html` overrides for showcase pages; the long tail stays template-driven)
- Author photos / testimonials / hire-me CTAs

## Conventions

- HTML filenames: kebab-case slugs except Elexon dataset codes (`system_prices.html` keeps underscores from the BMRS API)
- Dataset page anatomy: hero → metadata grid → stats strip → sticky sidebar → overview → snapshot chart → schema → sample → API tabs → caveats → related
- Mobile viewport: every page needs `<meta name="viewport" content="width=device-width, initial-scale=1">`
- A11y minimums: `<main>` landmark, `aria-current="page"` on active nav, distinguishing `aria-label` on dual `<nav>` (top + sidebar), `aria-hidden="true"` on decorative icons

## Slash commands

- `/gsd-plan-phase <n>` — decompose a phase into executable plans
- `/gsd-execute-phase <n>` — execute all plans in a phase
- `/gsd-discuss-phase <n>` — clarify scope before planning (interactive)
- `/gsd-manager` — milestone dashboard: shows D/P/E status per phase, dispatches subagents
- `/gsd-progress` — check progress / advance workflow
- `/grill-with-docs` — Socratic interview to flush out design decisions (use before discuss when scope is unclear)

The full GSD command catalogue is in `~/.claude/get-shit-done/`.

## Agent skills

### Issue tracker

Issues live as markdown files under `.planning/issues/<feature>/` and `.planning/reconciliation/<vendor>/` — same surface as the rest of the GSD planning state. GitHub Issues are not used. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical labels — `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root. Sibling repos (`gridflow`, `gridflow-models`) keep their own domain docs. See `docs/agents/domain.md`.
