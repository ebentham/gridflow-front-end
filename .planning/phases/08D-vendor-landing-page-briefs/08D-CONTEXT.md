# Phase 8D: Vendor landing-page content briefs (5 hubs) - Context

**Gathered:** 2026-05-20
**Status:** Ready to plan
**Related:** Phase 8C (Elexon dataset briefs, complete); Phase 9 (ENTSO-E dataset briefs, depends on 8D); Phase 10 (four-vendor dataset briefs, depends on 8D)
**Handover document:** [`.planning/handovers/2026-05-20-phase-8d-landing-pages.md`](../../handovers/2026-05-20-phase-8d-landing-pages.md) — read first if context is missing

<domain>
## Phase Boundary

Produce content briefs for the **five non-Elexon vendor landing pages** (vendor hubs), emulating the existing Elexon hub at `site/hifi/data-sources/elexon.html`. One brief per vendor:

1. `content-briefs/entsoe/_landing.md`
2. `content-briefs/entsog/_landing.md`
3. `content-briefs/gie/_landing.md`
4. `content-briefs/neso/_landing.md`
5. `content-briefs/openmeteo/_landing.md`

Each brief describes everything Claude Design needs to render a vendor-hub HTML page at `authored-pages/<vendor>/_landing.html` matching the Elexon hub's structure. The build script override path (Phase 8B) already supports `<vendor>.html` outputs — once an authored landing page lands, it ships via `site/hifi/data-sources/<vendor>.html`.

**Decoupled from per-dataset briefs by design.** Phase 8C produced 33 per-dataset briefs for Elexon; Phase 9 will produce 49 per-dataset briefs for ENTSO-E; Phase 10 will produce 81 across four vendors. Phase 8D handles the orthogonal vendor-hub layer for all 5 remaining vendors in one focused pass.

**In scope:**
- 5 vendor landing-page briefs at `content-briefs/<vendor>/_landing.md`
- Per-brief content covers: vendor identity (heading + italic accent + lede), 6-cell access metadata (BASE URL / AUTH / RATE LIMIT / FORMAT / EARLIEST / TIMEZONE), 4-cell stats strip, group definitions with blurbs, per-dataset listing rows
- Triangulation against the same sources used in Phase 8C: upstream `quant-vault`, gridflow main repo (`connectors/<vendor>/`, `schemas/<vendor>.py`), and live vendor docs
- A per-brief recipe document (`08D-LANDING-RECIPE.md`) defining structure + 10-12 structural checks per brief

**Out of scope:**
- Per-dataset briefs for the 5 vendors (Phase 9 + Phase 10 own those)
- Authoring HTML pages in Claude Design (user-side work)
- Updating the build script (Phase 8B's override path already supports `<vendor>.html` outputs — no change needed)
- Designing the main site-wide `/data-sources.html` catalog page (separate work; not in Phase 8D)

## Reference: Elexon landing page anatomy

The Elexon hub (`site/hifi/data-sources/elexon.html`) is the visual model. Section anatomy:

1. **Breadcrumb** — `Gridflow / Data sources / {Vendor Label}` (no slug — vendor is the leaf)
2. **Hero (1.4fr 1fr grid, align-items: end)**:
   - Left: eyebrow (`Vendor · {region} · {domain}`), `Illustrative snapshot` chip, H1 (`{heading_prefix} {italic_accent}`), lede paragraph, two CTAs (`Browse N datasets ↓`, `Vendor docs ↗`)
   - Right: 2×3 metadata card (6 cells): `BASE URL`, `AUTH`, `RATE LIMIT`, `FORMAT`, `EARLIEST`, `TIMEZONE`
3. **Stats strip** (4 cells): `{N} Datasets`, `{N} Categories`, `{vendor-specific stat}`, `{vendor-specific stat}` (e.g. Elexon's "7 Settlement runs · II → DF", "11y History")
4. **About section** (optional but recommended) — 2-3 paragraphs of vendor context
5. **Datasets section** (`#datasets`): grouped by category. Each group has a heading, a short blurb, and a 2-column grid of dataset cards. Each card shows: slug (mono), freq chip, title, frequency/lag/rows row.

The brief drives all of this content.

</domain>

<decisions>
## Implementation Decisions

### Brief location and naming

- **D-01:** **Top-level `content-briefs/<vendor>/_landing.md`**, sibling to per-dataset briefs. Underscore prefix sorts to top of `ls`; clearly distinguishes from per-dataset briefs.
  - **Why:** Parallels Phase 8C's `content-briefs/elexon/<slug>.md` location; tracked in git; not gitignored; sibling to per-dataset briefs for visual co-location.

### Source triangulation (same as Phase 8C)

- **D-02:** **Three sources mandatory.** For each vendor brief:
  1. **Upstream quant-vault** — `~/quant-vault/30-vendors/<vendor>/datasets/*.md` (all datasets for the vendor, to derive group-level stats and per-dataset listing rows)
  2. **Gridflow codebase** — `~/Python/gridflow/src/gridflow/connectors/<vendor>/` (connector config, auth, rate limit, endpoint registry), `~/Python/gridflow/src/gridflow/schemas/<vendor>.py` (schema class coverage), `~/Python/gridflow/REAL_VENDORS` / `COMING_SOON_VENDORS` in `build.py` (existing vendor_meta values to start from)
  3. **Live vendor docs** — vendor's API docs page (WebFetch where possible; may fail same as Phase 8C did for Elexon)
- **D-03:** **Discrepancies surfaced in frontmatter** — never silently resolved, matching Phase 8C's discrepancy-discipline. If vendor docs disagree with gridflow or vault, log it for downstream triage.

### Group categorization

- **D-04:** **Reuse gridflow's `vendor_meta` block where it exists** (already populated for Elexon and ENTSO-E in `src/gridflow_front_end/build.py REAL_VENDORS`; ENTSO-G / GIE / NESO / Open-Meteo have placeholders in `COMING_SOON_VENDORS` at lines 118+). For the four still-stub vendors, the brief drives the eventual `vendor_meta` definitions.
- **D-05:** **Group definitions follow the vendor's natural taxonomy**, not Elexon's. ENTSO-E groups by domain (Generation / Load / Transmission / Outages / Capacity / Prices); ENTSO-G groups by indicator family (Physical Flow / Nominations / Capacities / CMP / Auctions); GIE groups by surface (Storage / LNG / News / Reference); NESO groups by indicator (Carbon Intensity / Generation Mix / Regional / Statistics); Open-Meteo groups by horizon (Historical / Forecast) × variable (Wind / Solar / Demand).

### Editorial voice

- **D-06:** **Brand-aligned per CLAUDE.md** — editorial-quiet, cream + Fraunces, no SaaS framing, no "live" indicators. Same voice as Phase 8C dataset briefs and the existing Elexon hub. Tagline pattern for the H1: `{Vendor name} <span class="italic">{italic accent}.</span>` (e.g., Elexon's is `Elexon BMRS.` with `BMRS.` italic).

### Execution model

- **D-07:** **Foreground production by a single Claude Code session, OR background opus agent.** Defer execution-model choice to the planning step. 5 briefs is a tighter batch than Phase 8C's 33, but each brief covers the full vendor surface (more research breadth, less depth per brief).

</decisions>

<questions_answered>
- **Q-1:** Where do briefs live? → `content-briefs/<vendor>/_landing.md` (D-01)
- **Q-2:** What format? → Markdown with YAML frontmatter, matching Phase 8C dataset briefs
- **Q-3:** Voice? → Brand-aligned per CLAUDE.md, references = Elexon hub + Phase 8C dataset brief voice
- **Q-4:** Scope? → 5 vendors only (entsoe, entsog, gie, neso, openmeteo); Elexon is already shipped
- **Q-5:** What's the visual model? → `site/hifi/data-sources/elexon.html` (templated from `vendor-hub.html.j2` over `elexon.json` + Elexon's `vendor_meta` in `build.py`)
- **Q-6:** Where does Claude-Designed HTML land? → `authored-pages/<vendor>/_landing.html` (the build override at `build_vendor` needs a tiny extension to also check `_landing.html` for the hub, OR the file is named `<vendor>.html` and the override path uses a parallel resolver — defer to planning)

## Questions Still Open (planner decides)

- **Q-A:** Is the brief production autonomous-agent (like Phase 8C) or foreground? 5 briefs is small enough that foreground may produce tighter quality; background is faster but adds variance.
- **Q-B:** Should ENTSO-G be one brief or split (e.g. `transmission` family vs `capacity-management` family)? Vault has 33 ENTSOG datasets across many indicator families — possibly cleaner as two hubs, depending on natural taxonomy.
- **Q-C:** Should GIE be one brief (8 datasets total) or split (AGSI vs ALSI)? Gridflow treats them as sub-products (`gie_agsi` and `gie_alsi` namespaces).
- **Q-D:** What does the per-brief structural checklist look like? Adapt Phase 8C's 12-check pattern: frontmatter completeness, all required sections present, per-dataset row count matches vault, sources cited, etc.
- **Q-E:** How is the build script extended to serve authored landing pages? Currently the override checks `authored-pages/<vendor>/<slug>.html` for dataset pages; the vendor hub itself goes through `render_vendor_hub` in build.py without an override check. Extension is minimal (~5 LoC) but should be specified before execution.

</questions_answered>

<specifics>
## Provisional Implementation Notes

### Existing vendor_meta blocks to lift from build.py

Already populated for Elexon and ENTSO-E in `src/gridflow_front_end/build.py REAL_VENDORS` (lines ~59-117 from earlier inspection). Each carries: `region`, `domain`, `heading_prefix`, `heading_italic`, `lede`, `vendor_docs_url`, `base_url`, `auth`, `rate_limit`, `format`, `earliest`, `timezone`, `stat_three_value`, `stat_three_label`, `stat_four_value`, `stat_four_label`.

For the four still-stub vendors, placeholder stub blocks live in `COMING_SOON_VENDORS` at line 118+ — these have minimal fields (`vendor_label` mostly) and need full vendor_meta values defined by the Phase 8D briefs.

### Per-dataset listing data already in JSON manifests

`site/hifi/data/elexon.json` (the model) groups datasets with: `id` (slug), `title` (display name), `freq`, `lag`, `rows`. Per-vendor manifests for the 5 remaining vendors either don't exist yet (entsog/gie/neso/openmeteo) or are skeletal (entsoe.json has only the 1 v1 dataset). The Phase 8D briefs effectively define what each future `<vendor>.json` will look like — Phase 9 + Phase 10 will populate them as the per-dataset briefs are produced.

### Build-script override extension

`build.py::build_vendor` calls `render_vendor_hub(env, manifest, vendor_id, ...)` and writes to `out_root / "data-sources" / f"{vendor_id}.html"`. To serve an authored landing page, add a check before the render:

```python
authored_hub = AUTHORED_DIR / vendor_id / "_landing.html"
if authored_hub.exists():
    shutil.copy(authored_hub, hub_path)
    print(f"  wrote: data-sources/{vendor_id}.html (authored hub)")
else:
    hub_html = render_vendor_hub(env, manifest, vendor_id, vendor_label, vendor_cfg["vendor_meta"])
    hub_path.write_text(hub_html, encoding="utf-8")
    print(f"  wrote: data-sources/{vendor_id}.html")
```

This mirrors the dataset-page override pattern already in place from Phase 8B. ~5 LoC. Should land as Task 1 of Phase 8D's plan.

</specifics>

<deferred>
## Deferred to later phases

- Per-dataset briefs for ENTSO-E (Phase 9), ENTSO-G/GIE/NESO/Open-Meteo (Phase 10)
- Updating `site/hifi/data/<vendor>.json` manifests with full dataset lists (Phase 9 + Phase 10 work, derived from the per-dataset briefs)
- Site-wide `/data-sources.html` catalog refresh (separate ad-hoc work; not in any phase yet)
- Promoting the 4 COMING_SOON_VENDORS to REAL_VENDORS in build.py (Phase 10)
</deferred>
