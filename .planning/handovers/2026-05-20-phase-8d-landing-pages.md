---
handover_from: gridflow-front-end · session ending 2026-05-20 (post-Phase-8C closure)
handover_to: new Claude Code session via /gsd-manager
objective: Plan and execute Phase 8D — produce 5 vendor landing-page content briefs (one per non-Elexon vendor) following the Phase 8C pattern
branch: docs/v2-milestone-start (local-only; ~80 commits ahead of main; do NOT push without explicit user direction)
context_size: large (multiple multi-hour autonomous executions + 80+ commits in this branch's history); handoff exists because re-loading prior session context is wasteful
---

# Handover: Phase 8D — Vendor landing-page content briefs

## TL;DR

You are picking up a recruiter-portfolio documentation site (`gridflow-front-end`) mid-milestone (v2). The previous session closed **Phase 8C** (33 Elexon dataset content briefs, all clean) and **wrote sample briefs for all 5 remaining vendors** at the per-dataset level. Your job is **Phase 8D**: produce 5 *vendor-level landing-page* content briefs (one per non-Elexon vendor), so the user can Claude-Design hand-quality vendor hub HTML pages matching the existing Elexon hub aesthetic.

**Start point:** `/gsd-manager`. The dashboard should show Phase 8D as `Ready to plan`. Phase 8D's scope is fully written in `.planning/phases/08D-vendor-landing-page-briefs/08D-CONTEXT.md` — read that first.

---

## What this project is (in 4 sentences)

`gridflow-front-end` is an editorial-quiet documentation portfolio for the open-source `gridflow` ETL pipeline, which ingests UK / EU power and gas market data from six vendors (Elexon BMRS, ENTSO-E Transparency, ENTSO-G, GIE AGSI+, NESO, Open-Meteo). The site is a recruiter-first portfolio aimed at full-stack data-science recruiters in energy trading — **NOT** a product. The v2 milestone is "complete dataset coverage across all 6 vendors at `fuelhh` fidelity" — 163 total dataset pages plus hub pages, all rendered via a Python+Jinja2 build script reading vendored Obsidian Vault content.

The project sits on the **`docs/v2-milestone-start` feature branch**, ~80 commits ahead of `main`. **Never commit to `main`. Never push without explicit user direction.** Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).

---

## What's been done (so you don't repeat it)

The v1 milestone shipped 33 Elexon templated pages + an ENTSO-E proof. v2 phases since then:

| Phase | Outcome | Where |
|---|---|---|
| **7** — Reconciliation | ✓ Complete | Vault drift surfaces fixed; quant-vault committed to private GitHub repo `EBentham/quant-vault` |
| **8** — CSS bug fix attempt | ✗ Closed/superseded | Two CSS-patch iterations failed visual verification; pivoted scope |
| **8B** — AI-port + build override | ~ Partial | Build-script override path wired (`AUTHORED_DIR` check in `build.py::build_vendor`); 31 AI-ported pages archived to `.planning/archive/08B-ai-ports/` as sub-optimal; 2 reference pages kept at `authored-pages/elexon/{fuelhh,system_prices}.html` |
| **8C** — Elexon dataset content briefs | ✓ Complete | 33 triangulated briefs at `content-briefs/elexon/<slug>.md`; 45 discrepancies surfaced in `.planning/phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md`; gridflow-side bugs handed off via `.planning/handovers/2026-05-20-gridflow-bugs-from-08C.md` (also copied to gridflow main repo at `.planning/handovers/2026-05-20-from-gff-08C.md`) |
| **8D** — Vendor landing-page briefs | — Ready to plan | **YOUR JOB** |

Additionally, 5 sample per-dataset briefs landed today (one per non-Elexon vendor) to prove the brief format extends across vendor surface: `content-briefs/{entsoe/actual_generation,entsog/aggregated_physical_flows,gie/storage,neso/carbon_intensity,openmeteo/forecast_solar}.md`. These are **per-dataset**, NOT landing pages — Phase 8D is the vendor-hub layer.

---

## Your objective: Phase 8D

Produce **5 vendor landing-page content briefs**, one per non-Elexon vendor:

1. `content-briefs/entsoe/_landing.md`
2. `content-briefs/entsog/_landing.md`
3. `content-briefs/gie/_landing.md`
4. `content-briefs/neso/_landing.md`
5. `content-briefs/openmeteo/_landing.md`

Each brief must give Claude Design everything it needs to render a vendor hub HTML page that matches the existing **Elexon landing page** (`site/hifi/data-sources/elexon.html`) in structure and quality.

### The Elexon landing page (your visual model)

Generate it fresh (it's gitignored; the build regenerates it) by running:

```bash
cd /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end
PYTHONPATH=src python -c "from gridflow_front_end.build import main; main()"
```

Then open `site/hifi/data-sources/elexon.html` in a browser at `http://localhost:8001/data-sources/elexon.html` (start dev server with `PYTHONPATH=src python -m gridflow_front_end.serve --port 8001 &`).

The template that produces it is `templates/vendor-hub.html.j2`. It's driven by:
- A `vendor_meta` block in `src/gridflow_front_end/build.py::REAL_VENDORS` (region, domain, heading_prefix, heading_italic, lede, vendor_docs_url, base_url, auth, rate_limit, format, earliest, timezone, stat_three_*, stat_four_*)
- A `manifest` at `site/hifi/data/elexon.json` (groups list, each with name, blurb, datasets[])
- A `manifest_total` count

Anatomy (per `08D-CONTEXT.md` Reference section, abridged):
1. Breadcrumb → 2. Hero (1.4fr 1fr grid; left = identity + lede + CTAs; right = 6-cell metadata) → 3. Stats strip (4 cells) → 4. About section (vendor context) → 5. Datasets section (groups of dataset cards, 2-col grid)

### What each brief must define

For each of the 5 vendors:

- **Editorial layer**: H1 pattern `{heading_prefix} <span class="italic">{heading_italic}.</span>` (e.g. "ENTSO-E *Transparency.*"), lede (2-4 sentences), CTAs
- **Vendor metadata (6 cells)**: BASE URL, AUTH, RATE LIMIT, FORMAT, EARLIEST, TIMEZONE (lift from `gridflow/src/gridflow/connectors/<vendor>/` config + vault API endpoint tables)
- **Stats strip (4 cells)**: `{N} Datasets`, `{N} Categories`, plus 2 vendor-specific notable numbers (e.g. Elexon's are "7 Settlement runs · II → DF" and "11y History")
- **About section**: 2-3 paragraphs of vendor context (who they are, what they publish, why it matters for energy trading)
- **Group definitions**: per the vendor's natural taxonomy (NOT Elexon's). Per `08D-CONTEXT.md` D-05:
  - ENTSO-E: Generation / Load / Transmission / Outages / Capacity / Prices
  - ENTSO-G: Physical Flow / Nominations / Capacities / CMP / Auctions
  - GIE: Storage / LNG / News / Reference (or split AGSI vs ALSI — Q-C open)
  - NESO: Carbon Intensity / Generation Mix / Regional / Statistics
  - Open-Meteo: Historical / Forecast (× Wind / Solar / Demand)
- **Per-dataset listing rows**: every dataset in the vendor's vault gets a row with `id`, `title`, `freq`, `lag`, `rows` (same shape as `elexon.json` entries)

### Triangulation (same discipline as Phase 8C)

For each vendor brief:
1. **Vault**: `~/quant-vault/30-vendors/<vendor>/datasets/*.md` (all datasets — derive group taxonomy + per-dataset listing rows)
2. **Gridflow code**: `~/Python/gridflow/src/gridflow/connectors/<vendor>/` (auth, rate limit, base URL), `~/Python/gridflow/src/gridflow/schemas/<vendor>.py` (Pydantic class coverage), `~/Python/gridflow/src/gridflow_front_end/build.py REAL_VENDORS` and `COMING_SOON_VENDORS` (existing `vendor_meta` values to start from)
3. **Live vendor docs**: WebFetch where possible; ENTSO-E and ENTSO-G are XML/JSON APIs without browsable docs; NESO and Open-Meteo have static docs pages that work

Discrepancies between sources go in frontmatter `discrepancies_found:` (matching Phase 8C convention) — never silently resolved.

### Brief format

Use Phase 8C's per-dataset brief format as the basis (`content-briefs/elexon/system_prices.md` is a clean reference). Adapt to vendor-hub scope:

- Frontmatter: `slug` becomes `_landing` (or the vendor key), `sources_consulted` lists all vendor source files
- Required sections: Editorial layer, Vendor metadata (6 cells), Stats strip (4 cells), About section, Groups (each with name + blurb + dataset list), Source map (which gridflow files define this vendor's surface), Cross-vendor links
- Per-brief structural checks (10-12 of them, adapted from Phase 8C's RECIPE checks)

The new agent's first planning task is to write `08D-LANDING-RECIPE.md` (the per-brief runbook) before producing any briefs.

---

## How to start

```
/gsd-manager
```

You should see Phase 8D as `Ready to plan` on the dashboard. Recommended dispatch:

```
/gsd-plan-phase 8D
```

This produces `.planning/phases/08D-vendor-landing-page-briefs/08D-01-PLAN.md` and a recipe (`08D-LANDING-RECIPE.md`) via the gsd-planner subagent. Plan-checker will validate.

Then either:
- **Foreground** (recommended for tight quality): `/gsd-execute-phase 8D` in this session, producing briefs sequentially with you reviewing each
- **Background autonomous** (matches Phase 8C pattern): spawn an opus-4.7 background agent with the plan as runbook, similar to how Phase 8C executed

The user's preference last session was opus-in-background for batch work, but 5 briefs is small enough for foreground if you prefer.

---

## What's where (path map)

| Thing | Path |
|---|---|
| Phase 8D scope + decisions | `.planning/phases/08D-vendor-landing-page-briefs/08D-CONTEXT.md` |
| This handover | `.planning/handovers/2026-05-20-phase-8d-landing-pages.md` |
| ROADMAP (Phase 8D row at line ~22 in v2 phases list) | `.planning/ROADMAP.md` |
| Phase 8C closure (reference for brief format) | `.planning/phases/08C-elexon-content-briefs/08C-01-SUMMARY.md` |
| Phase 8C brief recipe (model for Phase 8D recipe) | `.planning/phases/08C-elexon-content-briefs/08C-BRIEF-RECIPE.md` |
| Phase 8C discrepancy index | `.planning/phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md` |
| Elexon visual model (vendor hub) | `site/hifi/data-sources/elexon.html` (gitignored; regenerate via `gridflow-build`) |
| Vendor hub template | `templates/vendor-hub.html.j2` |
| Elexon manifest (data shape model) | `site/hifi/data/elexon.json` |
| Per-dataset brief format reference | `content-briefs/elexon/system_prices.md` (or `fuelhh.md`) |
| Sample per-vendor briefs (5, produced today) | `content-briefs/{entsoe,entsog,gie,neso,openmeteo}/<one_slug>.md` |
| Reference Claude-Design hub | None yet — Phase 8D produces the first |
| Reference Claude-Design dataset pages | `authored-pages/elexon/{fuelhh,system_prices}.html` |
| Build-script override path (already wired for datasets) | `src/gridflow_front_end/build.py::build_vendor` (search for `AUTHORED_DIR`) |
| Vendor `vendor_meta` blocks | `src/gridflow_front_end/build.py::REAL_VENDORS` (Elexon + ENTSO-E filled) and `COMING_SOON_VENDORS` (4 stubs at line 118+) |
| Cross-repo: quant-vault upstream | `~/quant-vault/30-vendors/<vendor>/datasets/*.md` |
| Cross-repo: gridflow main | `~/Python/gridflow/src/gridflow/{connectors,schemas,silver}/<vendor>/` |
| Pending gridflow-side bugs (do not fix here) | `.planning/handovers/2026-05-20-gridflow-bugs-from-08C.md` — already handed off to gridflow GSD |

---

## Hard rules / non-negotiables

- **Do NOT push the branch**. ~80 local commits sitting on `docs/v2-milestone-start`. User pushes when ready.
- **Do NOT touch `authored-pages/elexon/fuelhh.html` or `system_prices.html`** — sacred visual references.
- **Do NOT modify the archived AI-ports** under `.planning/archive/08B-ai-ports/`.
- **Do NOT touch `CLAUDE.md` or pre-existing untracked files** (`.agents/`, `skills-lock.json`, `uv.lock`, `.planning/CONTROL.md`, `.planning/research/*.md`).
- **Do NOT use `--no-verify` on commits**. Let pre-commit hooks run.
- **Do NOT auto-commit** unless the workflow you're running expects it (e.g. `gsd-execute-phase` commits atomically per task). Per user CLAUDE.md: "Never auto-commit unless the user asks" — but in-workflow commits inside GSD phases are acceptable.
- **Conventional commits only** (`docs:`, `feat:`, `fix:`, `chore:`, `refactor:`, `test:`).
- **Mobile-safe viewport invariant** (`width=device-width, initial-scale=1` — NOT `width=1280`) carries from Phase 8B D-04 across all authored HTML.
- **No SaaS framing, no fake-live indicators, no emojis in files** (per user CLAUDE.md + PROJECT.md).

---

## What the user is doing while you work

In parallel: the user is **manually Claude-Designing the 33 Elexon dataset HTML pages** using the Phase 8C briefs as input. Their workflow is documented in the previous session: paste brief + `authored-pages/elexon/system_prices.html` (visual reference) into Claude Design → drop returned HTML into `authored-pages/elexon/<slug>.html` → verify at `localhost:8001`. They have a paste-ready Claude Design prompt that was produced in the previous session.

This means:
- They may commit new `authored-pages/elexon/*.html` files while you're working. Your work is in a different directory (`content-briefs/<other_vendors>/`) — no conflict.
- They are NOT available for synchronous feedback while doing this. Treat decisions as autonomous (with sensible defaults per CONTEXT.md decisions D-01 through D-07).

When your Phase 8D briefs land, the user will use the same Claude Design workflow on them to produce 5 vendor hub HTML pages.

---

## Acceptance / done state

Phase 8D is done when:
- [ ] 5 briefs committed at `content-briefs/<vendor>/_landing.md` for entsoe / entsog / gie / neso / openmeteo
- [ ] Each brief passes the structural checks defined in `08D-LANDING-RECIPE.md`
- [ ] `08D-01-SUMMARY.md` written with per-vendor table, source coverage stats, discrepancies summary
- [ ] `08D-LANDING-RECIPE.md` written (the per-brief recipe — model on `08C-BRIEF-RECIPE.md`)
- [ ] Build-script override path extended to serve `authored-pages/<vendor>/_landing.html` if present (the ~5 LoC patch sketched in `08D-CONTEXT.md` § specifics)
- [ ] ROADMAP.md progress table updated for Phase 8D row
- [ ] Discrepancies between sources surfaced in frontmatter (no silent resolution)

After Phase 8D, the user can Claude-Design 5 vendor hub pages and ship them. Phase 9 (ENTSO-E per-dataset briefs) and Phase 10 (4-vendor per-dataset briefs) follow, both building on Phase 8C + 8D as established patterns.

---

## Open questions to resolve in `/gsd-plan-phase 8D` discuss

(Listed in `08D-CONTEXT.md` § "Questions Still Open" — restated here for clarity)

- **Q-A**: Foreground or background-autonomous execution?
- **Q-B**: ENTSO-G one brief or split (33 datasets — maybe transmission family vs capacity-management family)?
- **Q-C**: GIE one brief or split (AGSI vs ALSI — gridflow treats them as sub-products)?
- **Q-D**: What exactly does the per-brief structural checklist look like? (Adapt Phase 8C's 12-check pattern.)
- **Q-E**: How to extend the build-script override for landing pages? (Sketch in CONTEXT § specifics; needs ratification in plan.)

---

**End of handover. Read `08D-CONTEXT.md` next, then `/gsd-manager`.**
