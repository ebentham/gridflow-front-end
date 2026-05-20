---
slug: _landing
vendor: entsoe
vendor_label: ENTSO-E Transparency
brief_type: landing
vault_dataset_count: 49
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/entsoe/datasets/ (49 files — all dataset .md files)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py (DOC_TYPES L~1–end, 47 entries; BIDDING_ZONES L12 entries; DEFAULT_ZONES; DEFAULT_CONTROL_AREAS)
  - gridflow/src/gridflow/connectors/entsoe/client.py (EntsoeConnector — securityToken query param auth, retry policy, XML/zip handling)
  - gridflow/src/gridflow/connectors/entsoe/parsers.py (XML GL_MarketDocument parsers)
  - gridflow/src/gridflow/schemas/entsoe.py (32 Pydantic classes)
  - "gridflow/src/gridflow/silver/entsoe/ (26 non-init files: actual_generation.py, day_ahead_prices.py, actual_load.py, cross_border_flows.py, wind_solar_forecast.py, load_forecast.py, outages_generation.py, installed_capacity.py, water_reservoirs.py, etc. — ~26 transformer files)"
  - gridflow-front-end/src/gridflow_front_end/build.py REAL_VENDORS['entsoe'] (L88–114 — fully populated vendor_meta block)
  - https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html (vendor API docs — attempted WebFetch; surfaced in discrepancies_found)
discrepancies_found:
  - source_a: "build.py REAL_VENDORS['entsoe'].vendor_meta.lede"
    source_a_says: "Lede is 'The pan-European transmission system operators Transparency Platform. Day-ahead prices, actual generation per production type, cross-border flows, forecasts, and outages across EU bidding zones — cross-vendor proof for the documentation template.'"
    source_b: "Phase 8D RECIPE editorial guidance"
    source_b_says: "Lift existing lede verbatim from REAL_VENDORS for ENTSO-E"
    orchestrator_recommendation: "Lift verbatim — the lede is already polished. Note the trailing phrase ('cross-vendor proof for the documentation template') is a Phase 7 artefact and should be removed by Claude Design when rendering."
  - source_a: "connectors/entsoe/endpoints.py DOC_TYPES count"
    source_a_says: "DOC_TYPES dict has 47 entries — more than the 49 vault datasets"
    source_b: "vault/entsoe/datasets/ — 49 dataset .md files"
    source_b_says: "49 vault files correspond to 49 gridflow datasets; some vault datasets map to multiple DOC_TYPES entries or use combined endpoint calls"
    orchestrator_recommendation: "Surface as note in Source map. The 47 DOC_TYPES vs 49 datasets gap is normal — some datasets (e.g. commercial_schedules_net_positions, offered_transfer_capacity variants) share underlying API doc_type codes."
  - source_a: "https://transparency.entsoe.eu/...Guide.html (live vendor API docs)"
    source_a_says: "Static HTML API guide — WebFetch attempted; result unclear (may be JavaScript-gated)"
    source_b: "vault/entsoe/datasets/*.md and connector code"
    source_b_says: "All API facts verified in vault from live curl tests; connector is the canonical implementation reference"
    orchestrator_recommendation: "vendor_docs_unfetchable: attempted; vault canonical fallback applied"
ready_for_claude_design: true
checked_at: 2026-05-20T12:00:00Z
---

# Editorial layer

**H1 pattern (lift from REAL_VENDORS verbatim):**

```html
ENTSO-E <span class="italic">Transparency.</span>
```

**Eyebrow chip:** `ENTSO-E · European Union · Electricity`

**Illustrative snapshot chip:** yes (standard)

**Lede paragraph (lifted from `build.py REAL_VENDORS["entsoe"].vendor_meta.lede`):**

The pan-European transmission system operators' Transparency Platform. Day-ahead prices, actual generation per production type, cross-border flows, forecasts, and outages across EU bidding zones — cross-vendor proof for the documentation template.

**Note for Claude Design:** Remove the trailing phrase "— cross-vendor proof for the documentation template" when rendering. Revised lede: "The pan-European transmission system operators' Transparency Platform. Day-ahead prices, actual generation per production type, cross-border flows, forecasts, and outages across EU bidding zones."

**CTA 1:** `Browse 49 datasets ↓` (anchors `#datasets`)
**CTA 2:** `Vendor docs ↗` → `https://transparency.entsoe.eu/`

---

# Vendor metadata

All values lifted from `build.py REAL_VENDORS["entsoe"]["vendor_meta"]` (lines 91–113).

| Cell label | Value |
|---|---|
| BASE URL | `web-api.tp.entsoe.eu` |
| AUTH | API key · query param `securityToken` |
| RATE LIMIT | ~1 req/s · polite default |
| FORMAT | XML · GL_MarketDocument |
| EARLIEST | 2014-12-05 |
| TIMEZONE | UTC · PT15M / PT30M / PT60M |

---

# Stats strip

All values lifted from `build.py REAL_VENDORS["entsoe"]["vendor_meta"]` (slots 3 + 4) or derived.

| slot | value | label | source |
|---|---|---|---|
| 1 | `49` | `Datasets` | vault: 49 files in `entsoe/datasets/` |
| 2 | `6` | `Categories` | 6 groups in this brief |
| 3 | `B25` | `PSR types · production codes` | `stat_three_value` / `stat_three_label` from REAL_VENDORS |
| 4 | `EU` | `Bidding zones` | `stat_four_value` / `stat_four_label` from REAL_VENDORS |

---

# About section

**Paragraph 1 — Who they are:**

`entsoe` is the ENTSO-E Transparency Platform, operated by the European Network of Transmission System Operators for Electricity. It is the pan-EU mandatory transparency publication under Regulation (EU) 543/2013, collecting and publishing power system data from all EU-27 TSOs plus Norway, Switzerland, and the UK (UK data available pre-Brexit; GB continues to publish post-Brexit via NESO / Elexon channels). API access requires a free registration and an API key passed as `securityToken` query parameter.

**Paragraph 2 — What they publish:**

49 endpoint surfaces across six domains: generation (actual outturn by PSR type, unit-level, capacity, forecasts, water reservoirs), load (actual outturn, day-ahead/weekly/monthly/yearly forecasts, forecast margin), transmission and cross-border (physical flows, NTC, commercial schedules, offered/allocated/used transfer capacity, net positions, redispatching), outages (generation unit, production unit, consumption, transmission, offshore grid), and prices and balancing (day-ahead prices, imbalance prices and volumes, activated/contracted/procured reserves, balancing bids, cross-zonal balancing capacity, balancing financial data, current balancing state). Data is published in XML using the `GL_MarketDocument` schema family.

**Paragraph 3 — Why it matters for energy trading:**

ENTSO-E `actual_generation` is the ground truth for pan-European generation dispatch by fuel type — the EU-level counterpart to Elexon `fuelhh`. Pairing `day_ahead_prices` across bidding zones (GB, FR, NL, BE, DE-LU, IE-SEM) enables cross-border price spread modelling and interconnector arbitrage identification. `cross_border_flows` combined with ENTSO-G `aggregated_physical_flows` closes the pan-European power-and-gas joint dispatch chain. `wind_solar_forecast` combined with Open-Meteo ERA5 data supports forecast skill assessment for GB renewable generation.

---

# Groups

## Group: Generation

**Blurb:** Actual and forecast generation by PSR type, unit-level outturn, installed capacity, and water storage.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `actual_generation` | Actual generation by PSR type · bidding zone | PT15M/PT30M/PT60M | T+1 hr | varies by zone |
| `actual_generation_units` | Actual generation per unit · GB | PT30M | T+1 hr | varies |
| `generation_forecast` | Day-ahead generation forecast aggregated | PT60M | D-1 | varies by zone |
| `generation_units_master_data` | Production and generation unit master data | static | on change | varies |
| `installed_capacity` | Installed generation capacity aggregated | yearly | annual | varies by zone |
| `installed_capacity_units` | Installed capacity per production unit | yearly | annual | varies |
| `water_reservoirs` | Water reservoirs and hydro storage | weekly | weekly | varies |
| `wind_solar_forecast` | Day-ahead wind and solar forecast | PT60M | D-1 | varies by zone |

## Group: Load

**Blurb:** Actual total load and day-ahead through yearly forecasts across EU bidding zones.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `actual_load` | Actual total load · bidding zone | PT15M/PT30M/PT60M | T+1 hr | varies by zone |
| `load_forecast` | Day-ahead load forecast | PT60M | D-1 | varies by zone |
| `load_forecast_weekly` | Week-ahead load forecast | PT60M | weekly | varies |
| `load_forecast_monthly` | Month-ahead load forecast | PT60M | monthly | varies |
| `load_forecast_yearly` | Year-ahead load forecast | PT60M | annual | varies |
| `forecast_margin` | Year-ahead forecast margin | PT60M | annual | varies |

## Group: Transmission & Cross-Border

**Blurb:** Physical cross-border flows, NTC, commercial schedules, offered/allocated capacity, and redispatching.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `cross_border_flows` | Physical cross-border flows (A11) | PT60M | T+1 hr | varies by border |
| `net_transfer_capacity` | Forecasted net transfer capacity (A61) | PT60M | D-1 | varies by border |
| `commercial_schedules` | Commercial schedules (A09) | PT60M | D-1 | varies |
| `commercial_schedules_net_positions` | Commercial schedules net positions | PT60M | D-1 | varies |
| `offered_transfer_capacity_continuous` | Offered transfer capacity continuous (A31) | PT60M | D-1 | varies |
| `offered_transfer_capacity_explicit` | Offered transfer capacity explicit (A31) | PT60M | D-1 | varies |
| `offered_transfer_capacity_implicit` | Offered transfer capacity implicit (A31) | PT60M | D-1 | varies |
| `total_capacity_allocated` | Total capacity already allocated (A26) | PT60M | D-1 | varies |
| `total_nominated_capacity` | Total nominated capacity (A26) | PT60M | D-1 | varies |
| `transfer_capacity_use` | Use of transfer capacity (A25) | PT60M | T+1 hr | varies |
| `redispatching_cross_border` | Redispatching cross-border (A63) | PT60M | as published | varies |
| `redispatching_internal` | Redispatching internal (A63) | PT60M | as published | varies |

## Group: Outages & Unavailabilities

**Blurb:** Planned and unplanned unavailabilities for generation units, production units, transmission, and offshore grid.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `outages_generation` | Unavailability of generation units (A80) | as published | real-time | varies |
| `outages_production` | Unavailability of production units (A77) | as published | real-time | varies |
| `outages_consumption` | Unavailability of consumption units (A76) | as published | real-time | varies |
| `outages_transmission` | Unavailability of transmission infrastructure (A78) | as published | real-time | varies |
| `outages_offshore_grid` | Unavailability of offshore grid infrastructure (A79) | as published | real-time | varies |

## Group: Prices & Balancing

**Blurb:** Day-ahead and imbalance prices, activated/contracted reserves, balancing bids, and financial settlement.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `day_ahead_prices` | Day-ahead prices (A44) | PT60M | D-1 | varies by zone |
| `imbalance_prices` | Imbalance prices (A85) | PT30M | T+1 hr | varies |
| `imbalance_volume` | Imbalance volumes (A86) | PT30M | T+1 hr | varies |
| `activated_balancing_prices` | Activated balancing energy prices (A84/A16) | PT60M | as published | varies |
| `activated_balancing_qty` | Activated balancing energy quantity | PT60M | as published | varies |
| `balancing_energy_bids` | Balancing energy bids (A37/A47/B74) | PT60M | as published | varies |
| `aggregated_balancing_energy_bids` | Aggregated balancing energy bids (A24/A51) | PT60M | as published | varies |
| `procured_balancing_capacity` | Procured balancing capacity (A15/A51) | PT60M | as published | varies |
| `contracted_reserves` | Contracted reserves (A81/A52) | PT60M | as published | varies |
| `cross_zonal_balancing_capacity` | Allocation and use of cross-zonal balancing capacity (A38/A51) | PT60M | as published | varies |
| `current_balancing_state` | Current balancing state (A86/B33) | PT30M | T+1 hr | varies |
| `balancing_financial_expenses_income` | Financial expenses and income for balancing (A87) | PT60M | as published | varies |

## Group: Capacity & Auctions

**Blurb:** Net positions, congestion income and costs, auction revenue, countertrading, and DC link limits.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `net_positions` | Implicit auction net positions (A25/B09) | PT60M | D-1 | varies |
| `congestion_income` | Congestion income (A25/B10) | PT60M | as published | varies |
| `congestion_management_costs` | Costs of congestion management (A92) | PT60M | as published | varies |
| `auction_revenue` | Auction revenue (A25/B07) | PT60M | as published | varies |
| `countertrading` | Countertrading (A91) | PT60M | as published | varies |
| `dc_link_intraday_transfer_limits` | DC link intraday transfer limits (A93) | PT60M | as published | varies |

**Row count:** 8 + 6 + 12 + 5 + 12 + 6 = 49 dataset rows across 6 groups == `vault_dataset_count: 49`. ✓

---

# Source map

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/entsoe/endpoints.py` | DOC_TYPES dict (47 entries — API doc_type → dataset mapping); BIDDING_ZONES (12 zones: GB, DE-LU, FR, NL, BE, ES, IT, DK-1, DK-2, NO-1, SE-1, IE-SEM); DEFAULT_ZONES (6); DEFAULT_CONTROL_AREAS (GB) | 47 DOC_TYPES vs 49 datasets: some vault datasets share API doc_types or use combined calls |
| `connectors/entsoe/client.py` | Auth: `securityToken` query param from `ENTSOE_API_KEY` env var; XML + ZIP response handling; retry policy | `EntsoeConnector` — XML responses sometimes zip-encoded; connector auto-decompresses |
| `connectors/entsoe/parsers.py` | XML GL_MarketDocument family parsers | Separate parser module (unlike most vendors) due to ENTSO-E's complex XML schema |
| `schemas/entsoe.py` | 32 Pydantic classes covering the typed silver surface | Classes: `EntsoeDayAheadPrice`, `EntsoeActualLoad`, `EntsoeActualGeneration`, `EntsoeCrossborderFlow`, `EntsoeLoadForecast`, `EntsoeWindSolarForecast`, `EntsoeOutagesGeneration`, `EntsoeInstalledCapacity`, `EntsoeInstalledCapacityUnits`, `EntsoeGenerationForecast`, `EntsoeActualGenerationUnits`, `EntsoeWaterReservoirs`, `EntsoeGenerationUnitsMasterData`, `EntsoeLoadForecastWeekly`, `EntsoeForecastMargin`, `EntsoeNetTransferCapacity`, `EntsoeImbalancePrices`, `EntsoeImbalanceVolume`, `EntsoeActivatedBalancingQty`, `EntsoeActivatedBalancingPrices`, `EntsoeContractedReserves`, `EntsoeOutagesConsumption`, `EntsoeOutagesTransmission`, `EntsoeOutagesOffshoreGrid`, `EntsoeOutagesProduction`, `EntsoeTransmissionMarketQuantity`, `EntsoeTransmissionMarketAmount`, `EntsoeBalancingState`, `EntsoeBalancingEnergyBid`, `EntsoeBalancingCapacity`, `EntsoeCrossZonalBalancingCapacity`, `EntsoeBalancingFinancial` |
| `silver/entsoe/` | ~26 transformer files; key: `actual_generation.py`, `day_ahead_prices.py`, `actual_load.py`, `cross_border_flows.py`, `wind_solar_forecast.py`, `load_forecast.py`, `outages_generation.py`, `installed_capacity.py`, `water_reservoirs.py`, `h6_market.py`, `h8_balancing.py` | Some transformer files cover multiple datasets (e.g. `h6_market.py` covers market/auction surfaces; `h8_balancing.py` covers balancing datasets) |
| `build.py REAL_VENDORS["entsoe"]` | Fully populated `vendor_meta` block at L88–114 | Already promoted to `REAL_VENDORS` — no Phase 10 work needed for ENTSO-E |

---

# Cross-vendor links

- **`elexon` · `fuelhh`** — GB vs EU generation by fuel: ENTSO-E `actual_generation` at GB bidding zone vs Elexon `fuelhh` at half-hourly grain. Core generation reconciliation; ENTSO-E is hourly, Elexon is 30-minute.
- **`entsog` · `aggregated_physical_flows`** — power-and-gas joint dispatch: ENTSO-E cross-border electricity flows combined with ENTSO-G gas interconnection flows for the EU supply side of the gas-to-power conversion chain.
- **`openmeteo` · `historical_wind`** — renewable generation attribution: ENTSO-E `actual_generation` by wind PSR type paired with Open-Meteo ERA5 wind at capacity-weighted sites for pan-EU wind-to-generation regression.
- **`neso` · `carbon_intensity`** — EU carbon context: ENTSO-E `actual_generation` EU-wide carbon signal compared with NESO GB carbon intensity — cross-border carbon import/export attribution.
- **`gie` · `storage`** — gas storage → CCGT: ENTSO-E gas-fired generation (PSR B04/B05) vs GIE AGSI storage withdrawal — correlates gas storage drawdown with CCGT dispatch decisions.

---

# Caveats

## 01 API key required — free registration at ENTSO-E portal

ENTSO-E is the only vendor in this set that requires a non-trivial registration step. Users must register at `https://transparency.entsoe.eu/` and request an API key, which is then passed as `securityToken` query parameter. The free tier is sufficient for all gridflow datasets. Many endpoints return HTTP 401 for unregistered keys or for endpoints gated to registered TSO users.

**Source:** vault `actual_generation.md` Auth row; `connectors/entsoe/client.py` auth implementation.

## 02 XML format with GL_MarketDocument schema — not JSON

All ENTSO-E responses are XML using the ENTSO-E `GL_MarketDocument` family (IEC CIM-based schema). Some responses are ZIP-compressed. The gridflow connector (`client.py`) auto-decompresses ZIP responses; `parsers.py` contains the XML family parsers. This contrasts with every other vendor in gridflow (all JSON). Downstream consumers building their own tooling must implement both the XML parser and the ZIP decompression.

**Source:** `connectors/entsoe/client.py` ZIP handling; `connectors/entsoe/parsers.py`.

## 03 Time resolution varies by surface (PT15M / PT30M / PT60M)

ENTSO-E data uses three time resolutions depending on the dataset and bidding zone. Some zones publish at 15-minute intervals (PT15M, common in continental Europe), some at 30 minutes (PT30M, common in GB), and some at hourly (PT60M). When joining ENTSO-E data with half-hourly Elexon data (30-minute periods), users must account for the resolution mismatch and aggregate PT60M to PT30M with appropriate averaging or allocation logic.

**Source:** vault `actual_generation.md` and `actual_load.md` time resolution notes; `build.py REAL_VENDORS["entsoe"].timezone = "UTC · PT15M / PT30M / PT60M"`.

## 04 Historical depth varies by area and surface (earliest ~2014-12-05)

The official API earliest date is 2014-12-05 for most surfaces, but actual coverage varies by bidding zone and dataset. Some capacity and balancing surfaces have shallower history (2015–2016). Some zones have data gaps for specific periods. The 2014-12-05 figure is the connector's `earliest` canonical claim; users should treat it as the earliest for GB and the main continental zones on the primary surfaces (actual generation, actual load, day-ahead prices).

**Source:** `build.py REAL_VENDORS["entsoe"].earliest = "2014-12-05"`; vault `actual_generation.md` Historical depth.

## 05 47 DOC_TYPES vs 49 vault datasets — shared codes

The connector's `DOC_TYPES` dict has 47 entries, yet 49 vault datasets are defined. This is because some vault datasets share the same underlying ENTSO-E API document type code with different query parameters (e.g. the three `offered_transfer_capacity_*` variants, `commercial_schedules_net_positions` vs `commercial_schedules`, and several balancing surfaces that use A25 with different `businessType` values). This is not a bug — it is the API's design.

**Source:** `connectors/entsoe/endpoints.py DOC_TYPES` (47 entries); vault (49 files).

---

# Per-vendor cheatsheet

## PSR production type codes (B-series)

`B01` Biomass · `B02` Fossil brown coal / lignite · `B03` Fossil coal-derived gas · `B04` Fossil gas · `B05` Fossil hard coal · `B06` Fossil oil · `B07` Fossil oil shale · `B08` Fossil peat · `B09` Geothermal · `B10` Hydro pumped storage · `B11` Hydro run-of-river and poundage · `B12` Hydro water reservoir · `B13` Marine · `B14` Nuclear · `B15` Other renewable · `B16` Solar · `B17` Waste · `B18` Wind offshore · `B19` Wind onshore · `B20` Other · `B25` Not specified (catch-all)

## Gridflow DEFAULT_ZONES (6 bidding zones)

`GB` · `FR` · `NL` · `BE` · `DE-LU` · `IE-SEM`

## All BIDDING_ZONES (12)

`GB` · `DE-LU` · `FR` · `NL` · `BE` · `ES` · `IT` · `DK-1` · `DK-2` · `NO-1` · `SE-1` · `IE-SEM`

## Time resolutions

`PT15M` (15 min — common in continental zones) · `PT30M` (30 min — GB, Nordic) · `PT60M` (hourly — most continental long-run series)

---

# Source-of-truth note

Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.entsoe` (32 Pydantic classes covering the typed silver surface); values shown in charts are illustrative deterministic snapshots, not live ENTSO-E Transparency Platform responses. The vault's `entsoe/datasets/` files are the canonical per-dataset reference; this landing brief is the vendor-hub layer above them.
