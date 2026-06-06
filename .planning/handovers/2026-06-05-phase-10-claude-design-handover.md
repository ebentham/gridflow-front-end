# Phase 10 — Four-vendor pages via Claude Design (master handover)

**Date:** 2026-06-05
**Phase:** 10 — Four-vendor batch (ENTSO-G 33 · GIE 8 · NESO 33 · Open-Meteo 6 = 80 datasets)
**Authoring path:** Claude Design (external) draws the HTML; main Claude drops it into `authored-pages/<vendor>/<slug>.html`, runs `gridflow-build`, verifies, and the user commits.

This is the master pack for the v2 close-out. It mirrors the Phase 9 ENTSO-E handover (`2026-05-27-phase-9-claude-design-handover.md`) but covers four vendors at once. It contains the shared workflow, the shared acceptance checklist, the per-vendor batch order, and the close-out. **The paste-ready Claude Design prompt is a separate file per vendor** (the four vendors diverge enough — JSON vs the ENTSO-E XML model, schema-absence, auth — that one prompt cannot serve all four):

| Vendor | Prompt file | Datasets | Groups | POC already on disk |
|---|---|---|---|---|
| ENTSO-G | `phase-10/entsog-prompt.md` | 33 | 5 | `aggregated_physical_flows.html` |
| GIE | `phase-10/gie-prompt.md` | 8 | 2 (AGSI + ALSI) | `storage.html` |
| NESO | `phase-10/neso-prompt.md` | 33 | 4 | `carbon_intensity.html` |
| Open-Meteo | `phase-10/openmeteo-prompt.md` | 6 | 2 (Forecast + Historical) | `forecast_solar.html` |

> **Read `10-01-PLAN.md` Task 00 first.** Four decisions (D-1 Overview fidelity · D-2 site count · D-3 GIE hub shape · D-4 reference strategy) gate everything. This pack assumes the **recommended** answers: **D-22 synthesis** (so scope = 80 pages incl. re-rendering the 4 POCs), **162** total, **unified `gie`**, **`actual_generation.html` as the shared reference**. If D-1 is decided as D-20 (lean), drop the "Overview synthesis" + "Caveats section" instructions from each prompt (a one-line note marks where) and scope = 76.

---

## Workflow

```
You (human)                                    Claude Design                 Main Claude (here)
───────────                                    ─────────────                 ──────────────────
1. Open fresh Claude Design conversation
2. Paste phase-10/<vendor>-prompt.md       ─►  [seeded]
3. Attach reference + POC + brief files    ─►  [reads context]
4. Ask: "Produce <slug>.html" (a batch)    ─►  [renders HTML]   ─────►     5. Paste HTML back
                                                                            6. main Claude saves to
                                                                               authored-pages/<vendor>/<slug>.html
                                                                            7. main Claude runs gridflow-build
                                                                            8. main Claude spot-checks + reports
9. Approve next batch                                                       10. User commits on feature branch
```

**Branch:** `feat/phase-10-four-vendor` off `main` (main Claude creates it on first landing; the user pushes/commits).
**One vendor per Claude Design conversation** — don't mix vendors in a session (the prompt is vendor-specific). Within a vendor, 3–6 thematically related briefs per batch works well (sidebar siblings cross-reference cleanly).

---

## Companion files to attach (every Claude Design session)

1. **`authored-pages/entsoe/actual_generation.html`** — the **primary** gold-standard reference (D-22: `#overview` synthesised + `#caveats` rendered). Claude Design mimics its **structure, class names, inline `<style>` block, and layout** — **not** its content.
2. **The vendor's own POC page** (`authored-pages/<vendor>/<the-poc>.html`, listed in the table above) — the **secondary** vendor-specific layout example. It shows how this vendor's quirks render: the dual-host BASE URL cell (gie/openmeteo), the JSON/no-Pydantic schema table (entsog), the gCO₂/kWh stats (neso). Note it is **D-20** (no `#overview`/`#caveats`) — take **layout** from it, take the **Overview/Caveats treatment** from `actual_generation.html`.
3. **`content-briefs/<vendor>/<slug>.md`** — one brief per dataset you want produced (attach the batch together).
4. `site/hifi/assets/theme.css` — only if Claude Design asks for the token list (usually unnecessary; the references use the tokens already).

Do **not** attach: another vendor's pages, the build script, STATE.md / CONTROL.md, or any `*-v2`/rejected layout.

---

## Per-vendor batch order

### ENTSO-G (33 → 5 batches)
1. **Zone + core Operational** — `aggregated_physical_flows` (re-render POC), `physical_flows`, `nominations`, `renominations`, `allocations`
2. **Capacities** — `firm_available`, `firm_booked`, `firm_technical`, `interruptible_available`, `interruptible_booked`, `interruptible_total`, `available_through_oversubscription`, `available_through_surrender`, `available_through_uioli_long_term`, `available_through_uioli_short_term`
3. **Gas quality** — `gcv`, `wobbe_index`, `methane_content`, `hydrogen_content`, `oxygen_content`
4. **CMP + Tariff** — `cmp_unsuccessful_requests`, `cmp_unavailable_firm_capacity`, `cmp_auction_premiums`, `tariffs`, `tariff_simulations`
5. **Reference + UMM** — `connection_points`, `operators`, `balancing_zones`, `operator_point_directions`, `interconnections`, `aggregate_interconnections`, `interruptions`, `urgent_market_messages`

### GIE (8 → 2 batches)
1. **Storage core (AGSI) + LNG** — `storage` (re-render POC), `storage_reports`, `unavailability`, `lng`
2. **Reference + news** — `about_listing`, `about_summary`, `news`, `news_item`

### NESO (33 → 4 batches)
1. **Carbon Intensity · National** — `carbon_intensity` (re-render POC), `intensity_current`, `intensity_today`, `intensity_date`, `intensity_period`, `intensity_at`, `intensity_fw24h`, `intensity_fw48h`, `intensity_pt24h`, `intensity_factors`
2. **Statistics + Generation Mix** — `intensity_stats`, `intensity_stats_block`, `generation`, `generation_current`, `generation_pt24h`
3. **Regional A** — `regional_current`, `regional_england`, `regional_scotland`, `regional_wales`, `regional_postcode`, `regional_regionid`, `regional_intensity`, `regional_intensity_fw24h`, `regional_intensity_fw24h_postcode`
4. **Regional B** — `regional_intensity_fw24h_regionid`, `regional_intensity_fw48h`, `regional_intensity_fw48h_postcode`, `regional_intensity_fw48h_regionid`, `regional_intensity_pt24h`, `regional_intensity_pt24h_postcode`, `regional_intensity_pt24h_regionid`, `regional_intensity_postcode`, `regional_intensity_regionid`

### Open-Meteo (6 → 2 batches)
1. **Forecast** — `forecast_demand`, `forecast_solar` (re-render POC), `forecast_wind`
2. **Historical** — `historical_demand`, `historical_solar`, `historical_wind`

---

## Acceptance criteria (run on every returned HTML before main Claude lands it)

Shared across all four vendors. If anything fails, push back in the Claude Design conversation rather than letting main Claude paper over it.

- [ ] **Body attribute contract:** `<body data-page="dataset" data-root="../../" data-screen-label="<VENDOR> · <slug>">` (dataset pages are depth-2 → `../../` is **correct** here; do not "fix" it).
- [ ] **Asset paths:** `../../assets/theme.css`, `../../assets/charts.js`, `../../assets/site.js`.
- [ ] **Breadcrumb:** Gridflow / Data sources / `<Vendor label>` / `<slug>` — four crumbs, last is plain text. (Vendor label: "ENTSO-G Transparency" / "GIE Storage" / "NESO Carbon Intensity" / "Open-Meteo".)
- [ ] **Hero metadata grid:** 6 cells in 3×2 from the brief's "Hero metadata" table. Dual-host cells (gie/openmeteo BASE URL) render with `<br/>` + `font-size:10px`.
- [ ] **Stats strip:** 4 cells from the brief's "Stats strip" table.
- [ ] **Sidebar siblings:** `← All datasets` → `../<vendor>.html`; current slug active; brief's "Sidebar siblings" list as faint `style="color:var(--ink-faint);"` links.
- [ ] **Chart:** `data-chart` ∈ `{stackedArea, sparkline, barsH, priceLadder}`; type + seed match the brief's "Sample chart". Anything else = invented chart kind → push back.
- [ ] **Schema table:** every column from the brief is present; **every row cites a gridflow source** in `<span class="cite">`. For schema-absent datasets (most of entsog, gie reference/news) the citation is a `silver/<vendor>/...py L<n>` path, **not** a Pydantic class — the page must NOT invent a schema class.
- [ ] **Sample data:** rows **verbatim from the brief** — no invented numbers, no reordered columns. The bolded brief row gets `outline: 1px solid #3b6b4b; outline-offset: -1px;`.
- [ ] **Overview (D-22 only):** 3 paragraphs synthesised from brief content (slug + endpoint + transformer + verified line); no invented figures; first paragraph opens with `<code>{slug}</code>`. (Skip if D-1 = D-20.)
- [ ] **API & ingestion:** 2-card grid (Endpoint+Auth · Bronze+Transformer) + tabs (Example URL / DuckDB·SQL / Python·polars) with the brief's verbatim code.
- [ ] **Caveats (D-22 only):** numbered `01..NN` in brief order; each ends in a source attribution; discrepancy-class caveats get `class="caveat-item discrepancy"`. (Skip if D-1 = D-20.)
- [ ] **Related grid:** 3–4 cards; cross-vendor card (e.g. Elexon `fuelhh` from a gas page) gets `border:1px solid var(--ink)` + a `cross-vendor` accent chip.
- [ ] **Scripts:** both inline scripts (IntersectionObserver + `setTab`) present at end of `<body>`.
- [ ] **No anti-goals:** no `<meta name="viewport" content="width=device-width">` (desktop-first `width=1280`); no emojis; no fake-live indicators / SaaS chrome / hire-me CTAs; no invented codelists.

---

## After Claude Design returns HTML

Paste the HTML block(s) to main Claude: *"Here is the produced HTML for `<slug>` (and any others). Land it."* Main Claude will:
1. Save each to `authored-pages/<vendor>/<slug>.html`.
2. Run `gridflow-build` (while the vendor is still `COMING_SOON`, the authored page is copied to `data-sources/<vendor>/<slug>.html` automatically).
3. Spot-check against the acceptance checklist.
4. Report status, then **stage + ask before the user commits** (never auto-commit).

If anything fails, main Claude tells you what to push back on in the Claude Design conversation rather than auto-fixing — the source of truth stays the brief + reference.

---

## Close-out (when all four vendors are fully landed)

Per `10-01-PLAN.md` Tasks 05–09 — main Claude (not Claude Design):
1. Author `site/hifi/data/{entsog,gie,neso,openmeteo}.json` manifests (group structure from the `_landing` briefs).
2. Migrate the four vendors `COMING_SOON_VENDORS` → `REAL_VENDORS` in `build.py` (GIE: merge `gie_agsi` + `gie_alsi` → unified `gie`) — **per vendor, only after that vendor's pages are 100% landed** (templated fallback is unproven on non-Elexon vendors).
3. Verify the six authored hubs are `data-root="../"` (already correct).
4. Reconcile site-wide counts to **162** (`index.html`, `data-sources.html`, `site.js`) + every vendor row → real hub.
5. Cold-rebuild CI: `gridflow-build` + `--check`, `htmlhint`, `lychee` — all 0.
6. Reconcile REQUIREMENTS/ROADMAP/STATE to disk truth; write `10-01-SUMMARY.md`; open PR `feat/phase-10-four-vendor` → `main`.
7. After merge + green Pages deploy → `/gsd-complete-milestone` to archive v2.

---

*Created 2026-06-05 at the start of Phase 10 execution. Mirrors the pattern that produced the 49 ENTSO-E authored pages in Phase 9. Per-vendor prompts: `phase-10/{entsog,gie,neso,openmeteo}-prompt.md`.*
