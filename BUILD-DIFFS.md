# BUILD-DIFFS.md

**Created:** 2026-05-18 (Phase 3, v1 milestone)
**Scope:** Intentional diffs between the 6 originally-complete Elexon dataset pages and their `gridflow-build` regenerated form.

ROADMAP §3 success criterion #5 reads: *"The 6 originally-complete pages (`fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`) regenerate byte-equivalently from the new template + vault content vs the pre-Phase-3 committed files (or with documented intentional diffs)."*

Byte equivalence is **not achievable** because the canonical source-of-truth direction has changed: vault content (`vault/elexon/<slug>.md`, structured frontmatter + sections) now drives the rendered HTML, replacing the hand-curated prose that lived in the HTML itself. That is the Phase 3 architectural pivot — accepting the resulting diffs is the point of the pivot. The categories of intentional diff are catalogued below so the audit trail is explicit.

## Categories of intentional diff

### 1. Hero metadata cells: `LAST FETCH` → `PRIMARY KEY` (honesty pre-emption)

The original 6-cell metadata card shipped a `LAST FETCH` cell with a fake `N min ago` value. Phase 5 owns the site-wide `chip live` / `LAST FETCH` sweep (HON-01), but baking it into the template now avoids a 33× regen later. Every regenerated page shows `PRIMARY KEY` derived from the vault `Dedup key:` field instead.

### 2. "Live" chips on hero and related-card → "Illustrative snapshot" framing

Same rationale as (1). The template never emits `<span class="chip live">`, `chip live · 30 min`, or the `24h / 7d / 30d` time-window pill row on the chart. The chart container instead carries an explicit `<span class="chip">Illustrative snapshot</span>` chip and the in-section eyebrow "Illustrative snapshot · shape only, not real values." Phase 5 grep checklist returns zero hits as a side-effect.

### 3. Hand-curated chart with snapshot-window callouts → deterministic seeded SVG only

The originals had a dedicated `#live-chart` section per-page with hand-tuned callouts (e.g. fuelhh's "Demand range / Wind share / Fuel types observed" sidecar). The vault has no equivalent structured content for those numerics, and they were never measured — they were illustrative. The regenerated pages carry a single `#snapshot-chart` section with a `data-chart="stackedArea"` placeholder and no fabricated callouts (Pitfall 7 — made-up precision — eliminated).

### 4. "Related datasets" cards: vault-derived list + manifest blurbs (no hand-curated "pair with X to do Y")

The original `fuelhh.html` and friends had hand-written "Join on (settlement_date, settlement_period) to add price context to the dispatch stack" blurbs. The vault doesn't declare per-pair editorial copy. The regenerated related-card grid shows the four sibling datasets from the same manifest category, each with its title + freq/lag/rows triple. Restoring "Why X with Y" callouts is a v2 candidate (would live as a `related_blurbs:` field in vault frontmatter).

### 5. Schema-table notes use vault prose, not the original hand-tuned cell text

The vault schema tables (`### Silver schema`) carry the column / type / nullable / source-field / notes structure verbatim. The regenerated schema tables now show whatever the vault says — which is usually richer and more accurate than the originals (the vault was audited against the live API on 2026-05-08), but stylistically different (e.g. vault uses `(BST/GMT calendar)` parentheticals where the original prose said `Partition key`).

### 6. Sample table: vault-sourced (often 1-3 rows of typed JSON) instead of hand-typed 8-12 rows

The vault's `### Silver sample` typically captures a Python `[{...}]` literal extracted from a live API response on the `last_verified` date. The original pages had longer hand-typed sample tables with carefully-chosen settlement periods. The regenerated sample tables show the vault rows — fewer, but provenance-traceable. Each cell value is now defensible against `gridflow.silver.elexon.<slug>` output, where the originals were illustrative.

### 7. fuelhh-specific `.fuel-grid` / `.fuel-pill` block — page-specific CSS no longer rendered

The original `fuelhh.html` rendered a 16-pill fuel-type grid (CCGT / coal / wind / etc.) with colour swatches. That block had no equivalent vault content and existed as a domain-knowledge differentiator in the original page. The Phase 2 refactor preserved the page-specific `.fuel-grid` / `.fuel-pill` CSS in fuelhh's inline `<style>` block. **The Phase 3 regenerated fuelhh.html does NOT render the fuel-type grid**, because the template is shared and adding fuelhh-specific markup is out of scope (it would re-introduce the per-page-edit anti-pattern Phase 3 is retiring).

Restoring the fuel-type grid as a v2 enhancement could go through a vault frontmatter field (`fuel_types: [...]`) that the template renders conditionally — see "Future v2 candidates" below.

### 8. Per-dataset `verified-against-vendor-docs: YYYY-MM-DD` micro-line (new)

Not a removal — an addition. Every regenerated page carries a tiny "Verified against vendor docs: 2026-05-08 · Elexon BMRS · FUELHH" line under the hero lede, linking to the canonical Elexon endpoint reference (`https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/<CODE>`). ELX-07 / Pitfall 3 (vendor-doc drift) machinery; was not present on the originals.

### 9. Inline Pydantic schema class name (`gridflow.schemas.elexon.ElexonFuelHH`) under the Schema heading (new)

Also additive. ELX-08. Where a class exists in `gridflow/src/gridflow/schemas/elexon.py`, the regenerated page cites it. Where the class is not yet declared (the vault's "Implementation delta" notes), the page emits a *"Schema enforced by transformer; no dedicated Pydantic class declared in `gridflow.schemas.elexon` yet — drift-surface flagged"* line. Both branches satisfy ELX-08's text *"matching Pydantic schema class name as an inline `<code>` reference"* while honestly surfacing the drift gap.

## Pydantic-schema class drift surface

The 12 classes that exist in `gridflow.schemas.elexon` at HEAD (last verified 2026-05-18):

`ElexonSystemPrice`, `ElexonGenerationByFuel`, `ElexonFuelHH`, `ElexonBOAL`, `ElexonBOD`, `ElexonMID`, `ElexonFrequency`, `ElexonDemandForecast`, `ElexonWindForecast`, `ElexonPN`, `ElexonDISBSAD`, `ElexonBMUnit`

The remaining 21 datasets (`agpt`, `agws`, `nonbm`, `windfor`, `netbsad`, `pn` — wait, those *are* mapped — and `indod`, `itsdo`, `ndf`, `ndfd`, `tsdf`, `fou2t14d`, `uou2t14d`, `freq`, `temp`, `remit`, `bmunits_reference`, `soso`, `atl`, `imbalngc`, `inddem`, `indgen`, `lolpdrm`, `market_depth`, `melngc`, `tsdfd`, and any others without a matching `Elexon<Name>` class) render with the "drift-surface flagged" line. This is intentional — the site honestly surfaces where the gridflow code lags the vault's enumerated datasets. Future v2 work in the `gridflow` repo to declare the missing classes will flip these pages to the "Defined in …" form on the next regen.

## What is NOT a diff (regeneration must preserve)

- The 7-section anatomy (hero → metadata grid → stats strip → sidebar → overview → snapshot chart → schema → sample → api → caveats → related). The Phase 3 template captures all of it.
- The CSS class taxonomy used (`.schema-table`, `.data-table`, `.page-layout`, `.sidebar`, `.caveat-item`, `.related-grid` — all of which now live in `theme.css` under `body[data-page="dataset"]` after Phase 2).
- The body data-attribute contract (`data-page="dataset"`, `data-root="../../"`).
- The 6 sidebar anchors (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) — every one resolves to a real `<section id>` on every regenerated page (Pitfall 2 prevention, ROADMAP §3 SC#2).
- The chrome-injection contract via `site.js` (top-nav + footer; mobile menu; scroll-spy gated by `.sidebar a[href^="#"]`).

## Future v2 candidates

- Restore per-pair "Why X with Y" callouts via a `related_blurbs:` field in vault frontmatter.
- Restore fuelhh's fuel-type grid via a `fuel_types: [{code, label, color, desc}]` field in vault frontmatter; render conditionally in the template under a new `#fuel-types` section.
- Wire each dataset's Pydantic schema class reference to a deep-link into `gridflow` source on GitHub (currently the class name is shown as plain code).
- Add a `last_synced_from_vault: YYYY-MM-DD @ <commit-hash>` footer line (the vendored `vault/` snapshot in this repo can drift from the upstream `quant-vault` between syncs; the snapshot date should be visible).
