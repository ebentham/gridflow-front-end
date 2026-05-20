# Phase 9 — ENTSO-E content briefs

## Scope

Produce 49 ENTSO-E content briefs at `content-briefs/entsoe/<slug>.md`, one per ENTSO-E dataset, feeding Claude Design's renderer (target: `authored-pages/entsoe/<slug>.html`).

## Inherited decisions

- **D-20 (2026-05-20) — tightened brief recipe.** Lede 1 sentence ≤25 words (hard cap 30). No `# Overview` section. Caveats 3–6 items, each 1 short sentence + citation. Inherited from Phase 8C / Phase 8D (closed). Canonical reference: `content-briefs/elexon/fuelhh.md` + `content-briefs/elexon/system_prices.md`. Full recipe in `.planning/phases/08C-elexon-content-briefs/08C-BRIEF-RECIPE.md`.

- **D-06 (Phase 7) — entitlement handling.** 35 of 49 ENTSO-E datasets return HTTP 401 with the unregistered default API key (catalogued in `.planning/reconciliation/entsoe/01..35-*-http-401.md`). Per "commence now" directive: produce a FULL brief for ALL 49 datasets regardless of entitlement status, sourcing from vault + gridflow source code (both accessible without an API key). For the 35 entitlement-blocked datasets, frontmatter carries:

  ```yaml
  entitlement_required: true
  entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/NN-<slug>-http-401.md)"
  ```

  Verified line for entitlement-blocked datasets reads "Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · vendor-doc fetch deferred — platform is PDF-heavy."

- **Vendor docs unfetchable.** ENTSO-E Transparency Platform docs are PDF-heavy. Per Phase 7, all API facts are verified from vault (live curl tests on the 14 unblocked endpoints) and connector code is the canonical implementation reference. `vendor_docs_unfetchable: PDF-based platform — see vault references` appears in frontmatter where relevant.

- **Vendoring complete.** All 49 vault files vendored from `quant-vault/30-vendors/entsoe/datasets/` to `gridflow-front-end/vault/entsoe/` in commit `05f42e2` (prior phase).

## Cross-cutting anomalies (flagged by advisor before brief production)

1. **`commercial_schedules_net_positions`** — REMOVED from gridflow in V2 (ADR-019). The vault file still exists. No DOC_TYPES entry, no Pydantic class, no transformer. Brief carries `schema_class: (absent — removed in V2 ADR-019, registry-duplicate of commercial_schedules)`. Also has reconciliation finding `44-commercial-schedules-net-positions-no-silver-section.md` (`wontfix`, v3-candidate).

2. **`activated_balancing_qty`** — has a `EntsoeActivatedBalancingQty` Pydantic class and a transformer, but NO DOC_TYPES entry in `endpoints.py`. Reconciliation finding `36-activated-balancing-qty-manual-transformer-schema.md` (`wontfix`, v3-candidate) marks this. The class IS present in `schemas/entsoe.py` L384–407 — the verifier finding's "no importable Pydantic class declared" is now stale (closed by a later schema addition). Treat as manual transformer for the endpoint dispatch — flag in Caveats.

3. **H6 family shares Pydantic classes.** 12 zone-pair quantity datasets share `EntsoeTransmissionMarketQuantity`: `commercial_schedules`, `redispatching_cross_border`, `redispatching_internal`, `countertrading`, `offered_transfer_capacity_continuous`, `offered_transfer_capacity_implicit`, `offered_transfer_capacity_explicit`, `transfer_capacity_use`, `total_nominated_capacity`, `total_capacity_allocated`, `net_positions`, `dc_link_intraday_transfer_limits`. 3 share `EntsoeTransmissionMarketAmount`: `congestion_management_costs`, `auction_revenue`, `congestion_income`. All cite the shared class honestly (file:line); differentiate via Lede + Caveats + sample chart + API-doc-type code.

4. **H7 outages family shares transformer pattern.** `outages_consumption`, `outages_transmission`, `outages_offshore_grid`, `outages_production` all live in `silver/entsoe/outages_h7.py` (single base class `_H7OutageTransformer`). `outages_generation` has its own file `outages_generation.py` (older, A80-specific).

5. **H8 balancing family shares transformer pattern.** `current_balancing_state`, `balancing_energy_bids`, `aggregated_balancing_energy_bids`, `procured_balancing_capacity`, `cross_zonal_balancing_capacity`, `balancing_financial_expenses_income` all live in `silver/entsoe/h8_balancing.py`.

6. **Reconciliation findings 36–73** carry real schema/nullability/table-presence content (not just 401 status). Scan all 73 files per slug, not just 401 list.

## Commit batches (by ENTSO-E category)

1. **Setup** — `09-CONTEXT.md` + `BRIEF-LOG.md` (this commit).
2. **Generation** (9 datasets) — actual_generation, actual_generation_units, generation_forecast, installed_capacity, installed_capacity_units, generation_units_master_data, water_reservoirs, wind_solar_forecast, forecast_margin.
3. **Load** (4 datasets) — actual_load, load_forecast, load_forecast_weekly, load_forecast_monthly, load_forecast_yearly (5 — `forecast_margin` is borderline; see category 2).

   Final allocation: forecast_margin is generation-side (forecasts net generation availability), placed in Generation. Load = 5 datasets.

4. **Transmission & cross-border** (~12 datasets) — cross_border_flows, net_transfer_capacity, offered_transfer_capacity_{continuous,explicit,implicit}, commercial_schedules, commercial_schedules_net_positions, dc_link_intraday_transfer_limits, total_capacity_allocated, total_nominated_capacity, transfer_capacity_use, redispatching_cross_border, redispatching_internal, countertrading, net_positions.

5. **Outages** (5 datasets) — outages_consumption, outages_generation, outages_offshore_grid, outages_production, outages_transmission.

6. **Balancing** (~10 datasets) — current_balancing_state, aggregated_balancing_energy_bids, balancing_energy_bids, balancing_financial_expenses_income, contracted_reserves, procured_balancing_capacity, activated_balancing_prices, activated_balancing_qty, cross_zonal_balancing_capacity.

7. **Prices & capacity** (~9 datasets) — auction_revenue, day_ahead_prices, imbalance_prices, imbalance_volume, congestion_income, congestion_management_costs.

   Total 49. Group boundaries align with `_landing.md` taxonomy (Generation 9, Load 5, Transmission 14, Outages 5, Balancing 9, Capacity & Auctions / Prices 7).

## Structural checks (per brief, pre-commit)

Inherited from `08C-BRIEF-RECIPE.md` ¶225, omitting `# Overview` from required sections. See `BRIEF-LOG.md` for failures.
