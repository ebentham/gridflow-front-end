# Official vendor docs vs Vault coverage

Date: 2026-05-19

Scope: step-one research only. No files under `vault/` were changed.

## Executive summary

The current in-repo vault snapshot is not yet complete against the v2 "all vendors at depth" goal.

Current local vault snapshot:

| Vendor | Local vault files | Active-looking local files | v2 target in planning | Immediate gap |
|---|---:|---:|---:|---:|
| Elexon BMRS | 33 | 33 | 33 in v2, but official BMRS has more | Complete for current GridFlow scope; incomplete if "all BMRS dataset endpoints" means vendor-complete |
| ENTSO-E | 25 | 25 | 49 | 24 local files missing from the v2 target |
| ENTSO-G | 5 | 1 active + 4 `removed` | 33 | 28 local files missing from the v2 target; 4 existing docs describe removed endpoints |
| GIE AGSI/ALSI | 0 | 0 | 8 | 8 missing |
| NESO Carbon Intensity | 0 | 0 | 34 | 34 missing |
| Open-Meteo | 0 | 0 | 6 | 6 missing |

The bigger product decision is whether "all datasets" means:

1. **All GridFlow-supported datasets**: keep Elexon at 33, then fill ENTSO-E 49, ENTSO-G 33, GIE 8, NESO 34, Open-Meteo 6 as planned.
2. **All official vendor-published datasets/endpoints**: Elexon alone expands from 33 current vault docs to at least 82 raw `/datasets/{code}` BMRS endpoints, plus non-dataset semantic/reference endpoints. Open-Meteo and NESO also become much broader than the current v2 target counts.

Recommendation: lock the boundary as "all GridFlow-supported datasets" for v2, and open a separate vendor-complete backlog for Elexon BMRS and NESO/Open-Meteo expansion.

## Sources checked

Official or vendor-owned sources used:

- Elexon BMRS/Insights OpenAPI: <https://data.elexon.co.uk/swagger/v1/swagger.json>
- Elexon developer portal: <https://developer.data.elexon.co.uk/apis>
- Elexon BMRS API docs UI: <https://bmrs.elexon.co.uk/api-documentation>
- ENTSO-E Transparency Platform REST API guide: <https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide_prod_backup_06_11_2024.html>
- ENTSO-E API endpoint: <https://web-api.tp.entsoe.eu/api>
- ENTSO-G TP API user manual v3.0: <https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/ENTSOG_TP_API_UserManual_v3.0.pdf>
- ENTSO-G API base: <https://transparency.entsog.eu/api/v1>
- GIE AGSI/ALSI API manual v005: <https://www.gie.eu/transparency-platform/GIE_API_documentation_v005.pdf>
- GIE AGSI/ALSI platform overview: <https://www.gie.eu/agsi-and-alsi-transparency-platforms/>
- Open-Meteo docs index: <https://open-meteo.com/en/docs>
- Open-Meteo historical weather API: <https://open-meteo.com/en/docs/historical-weather-api>
- Open-Meteo air quality API: <https://open-meteo.com/en/docs/air-quality-api>
- Open-Meteo marine API: <https://open-meteo.com/en/docs/marine-weather-api>
- Open-Meteo climate API: <https://open-meteo.com/en/docs/climate-api>
- NESO Carbon Intensity API: <https://api.carbonintensity.org.uk/>
- NESO Carbon Intensity API definitions: <https://carbon-intensity.github.io/api-definitions/>
- NESO applications and APIs index: <https://www.neso.energy/applications-portals-and-apis>
- NESO Data Portal CKAN API: <https://api.neso.energy/api/3/action/package_search?rows=0>

Local sources checked:

- `vault/`
- `site/hifi/data/*.json`
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/reconciliation/**`

## Elexon BMRS

Official evidence: Elexon's OpenAPI spec exposes 306 total paths under the BMRS API server and 82 raw dataset endpoints matching `/datasets/{CODE}`. The current vault documents 33 Elexon files. Of those, 30 map to raw `/datasets/{CODE}` endpoints and 3 map to semantic/reference endpoints:

- `bmunits_reference`: `/reference/bmunits/all`
- `market_depth`: `/balancing/settlement/market-depth/{settlementDate}`
- `system_prices`: `/balancing/settlement/system-prices/{settlementDate}`

Current GridFlow-scoped Elexon coverage is complete: 33 vault files exist and match the v1/v2 Elexon target. Vendor-complete Elexon coverage is not complete: 52 official raw `/datasets/{CODE}` endpoints are not represented in the vault.

Missing official Elexon raw dataset endpoints:

| Code | Official summary |
|---|---|
| ABUC | Amount Of Balancing Reserves Under Contract (ABUC / B1720) |
| AOBE | Accepted Offered Balancing Energy (AOBE) |
| B1610 | Actual Generation Output Per Generation Unit (B1610) |
| BEB | Balancing Energy Bids (BEB) |
| BOD | Bid Offer Data (BOD) |
| CBS | Current Balancing State (CBS) |
| CCM | Cost of Congestion Management (CCM / B1330) |
| CDN | Credit default notices (CDN) |
| DAG | Day-Ahead Aggregated Generation (DAG / B1430) |
| DATL | Day-Ahead Total Load Forecast Per Bidding Zone (DATL / B0620) |
| DCI | Demand control instructions (DCI) |
| DGWS | Day-Ahead Generation For Wind And Solar (DGWS / B1440) |
| FEIB | Financial Expenses and Income for Balancing (FEIB / B1790) |
| FOU2T3YW | 2 to 156 weeks ahead generation availability aggregated by fuel type (FOU2T3YW) |
| IGCA | Installed Generation Capacity Aggregated (IGCA / B1410) |
| IGCPU | Installed Generation Capacity per Unit (IGCPU / B1420) |
| MATL | Month-Ahead Total Load Forecast Per Bidding Zone (MATL / B0640) |
| MDP | Maximum Delivery Period (MDP) |
| MDV | Maximum Delivery Volume (MDV) |
| MELS | Maximum Export Limit (MELS) |
| MILS | Maximum Import Limit (MILS) |
| MNZT | Minimum Non-Zero Time (MNZT) |
| MZT | Minimum Zero Time (MZT) |
| NDFW | 2-52 weeks ahead National Demand and surplus forecast (NDFW) |
| NDZ | Notice to Deviate from Zero (NDZ) |
| NOU2T14D | 2 to 14 days ahead generation availability aggregated data (NOU2T14D) |
| NOU2T3YW | 2 to 156 weeks ahead generation availability aggregated data (NOU2T3YW) |
| NTB | Notice to Deliver Bids (NTB) |
| NTO | Notice to Deliver Offers (NTO) |
| OCNMF3Y | 2-156 weeks ahead demand surplus forecast (OCNMF3Y) |
| OCNMF3Y2 | 2-156 weeks ahead demand margin forecast (OCNMF3Y2) |
| OCNMFD | 2-14 days ahead demand surplus forecast (OCNMFD) |
| OCNMFD2 | 2-14 days ahead demand margin forecast (OCNMFD2) |
| PBC | Procured Balancing Capacity (PBC) |
| PPBR | Prices Of Procured Balancing Reserves (PPBR / B1730) |
| QAS | Balancing Services Volume (QAS) |
| QPN | Quiescent Physical Notifications (QPN) |
| RDRE | Run Down Rate Export (RDRE) |
| RDRI | Run Down Rate Import (RDRI) |
| RURE | Run Up Rate Export (RURE) |
| RURI | Run Up Rate Import (RURI) |
| RZDF | Restoration Region Demand Forecast (RZDF) |
| RZDR | Restoration Region Demand Restored (RZDR) |
| SEL | Stable Export Limit (SEL) |
| SIL | Stable Import Limit (SIL) |
| SYSWARN | System warnings (SYSWARN) |
| TSDFW | 2-52 weeks ahead Transmission System Demand and surplus forecast (TSDFW) |
| TUDM | Trading unit data (S0491_TUDM) |
| UOU2T3YW | 2 to 156 weeks ahead generation availability aggregated by Balancing Mechanism Units (UOU2T3YW) |
| WATL | Week-Ahead Total Load Forecast Per Bidding Zone (WATL / B0630) |
| YAFM | Year Ahead Forecast Margin (YAFM / B0810) |
| YATL | Year-Ahead Total Load Forecast Per Bidding Zone (YATL / B0650) |

Elexon frontend/data note: `site/hifi/data/vendors.json` still says Elexon has `28` datasets, while the visible site/vault reality is 33 and the official raw dataset endpoint count is 82. This is not a vault problem, but it is a frontend metadata drift surface.

## ENTSO-E

Official evidence: the ENTSO-E REST guide organizes the API into these data domains:

- Load
- Transmission
- Congestion
- Generation
- Master Data
- Balancing
- Outages

The official guide examples include, among others, actual total load, day/week/month/year-ahead load forecast, expansion/dismantling projects, flow-based parameters, intraday transfer limits, redispatching, countertrading, installed generation capacity, generation forecasts, actual generation per unit, aggregated generation per type, water reservoirs, production/generation master data, balancing energy/capacity/price/financial datasets, and outage datasets.

Local vault state: 25 ENTSO-E files are present. The v2 planning target is 49 files. Therefore the local snapshot is 24 files short of the target.

Current local ENTSO-E files:

- `actual_generation`
- `actual_generation_units`
- `aggregated_balancing_energy_bids`
- `auction_revenue`
- `balancing_energy_bids`
- `balancing_financial_expenses_income`
- `congestion_income`
- `congestion_management_costs`
- `cross_border_flows`
- `cross_zonal_balancing_capacity`
- `current_balancing_state`
- `dc_link_intraday_transfer_limits`
- `generation_forecast`
- `generation_units_master_data`
- `installed_capacity`
- `installed_capacity_units`
- `net_transfer_capacity`
- `outages_consumption`
- `outages_generation`
- `outages_offshore_grid`
- `outages_production`
- `outages_transmission`
- `procured_balancing_capacity`
- `water_reservoirs`
- `wind_solar_forecast`

Important existing finding: `.planning/reconciliation/entsoe/` already records ENTSO-E entitlement drift. The notes say many ENTSO-E datasets returned HTTP 401 with the current token and are deferred to Phase 9 for the decision between extending access or shipping `skip-with-warn` caveats.

ENTSO-E frontend/data note: `site/hifi/data/entsoe.json` exposes only `actual_generation`, while `site/hifi/data/vendors.json` advertises 14 datasets and v2 planning targets 49. That is a site manifest gap, not a vault edit request.

## ENTSO-G

Official evidence: the ENTSO-G TP API manual v3.0 lists these endpoint families under `https://transparency.entsog.eu/api/v1`:

| Category | Official endpoint family | Coverage implication |
|---|---|---|
| Point Data | `/operationalDatas` | Nominations, renominations, allocations, physical flows, GCV, Wobbe Index, capacities, interruptions, CMP/CMA, gas quality |
| Point Data | `/cmpUnsuccessfulRequests` | CMP unsuccessful requests |
| Point Data | `/cmpUnavailables` | CMP unavailable firm capacity |
| Point Data | `/cmpAuctions` | CMP auction premiums |
| Point Data | `/interruptions` | Planned/unplanned interruptions |
| Zone Data | `/aggregatedData` | Aggregated nominations, allocations, physical flows |
| Tariff Data | `/tariffsSimulations.xml` | Tariff simulations |
| Tariff Data | `/tariffsFulls.xml` | Tariff components |
| UMM Data | `/urgentMarketMessages` | Urgent market messages |
| Referential Data | `/connectionPoints` | Connection points |
| Referential Data | `/operators` | Operators |
| Referential Data | `/balancingZones` | Balancing zones |
| Referential Data | `/operatorPointDirections` | Operator-point-direction flow keys |
| Referential Data | `/interconnections` | Interconnections |
| Referential Data | `/aggregateInterconnections` | Aggregate interconnections |

Local vault state: only 5 ENTSO-G files are present:

- `physical_flows`
- `hydrogen_content` (`removed: 2026-05-19`)
- `interruptions` (`removed: 2026-05-19`)
- `methane_content` (`removed: 2026-05-19`)
- `oxygen_content` (`removed: 2026-05-19`)

This means the active local ENTSO-G surface is effectively one dataset page candidate (`physical_flows`). The v2 target is 33, so the local snapshot is 28 files short of the planned target.

Existing reconciliation findings already enumerate the intended ENTSO-G target names: allocations, nominations, renominations, GCV, Wobbe Index, capacity variants, CMP datasets, tariff datasets, UMMs, and reference datasets. Those map cleanly to the official ENTSO-G API manual families above.

## GIE AGSI/ALSI

Official evidence: GIE's API manual says AGSI+ and ALSI provide API access to daily storage and LNG reporting. It identifies:

- `/api/about?show=listing` for EIC/listing metadata
- `/api` with query parameters such as `country`, `company`, `facility`, `from`, `to`, `date`, `page`, and `size`
- AGSI+ historical data since 2011 where available
- ALSI historical data since 2012 where available
- Aggregated datasets by company and country level

The manual also explicitly says unavailability reporting is currently not part of the API coverage in v005. Any GIE `unavailability` vault target needs a source check against a newer GIE endpoint or a non-API source before it is rendered as current API coverage.

Local vault state: no `vault/gie/`, `vault/gie_agsi/`, or `vault/gie_alsi/` files are present. The v2 target is 8 files, so all 8 are missing locally.

Existing reconciliation findings under `.planning/reconciliation/gie/` mention these target concepts:

- `about_listing`
- `about_summary`
- `lng`
- `news`
- `news_item`
- `unavailability`

That is 6 finding slugs, while the v2 target is 8. The missing two target names should be recovered from the upstream `quant-vault` or GridFlow connector before authoring manifests.

## NESO Carbon Intensity

Official evidence: the official Carbon Intensity API exposes JSON endpoint groups for:

- National carbon intensity: current, by date, by date/settlement period, factors, by datetime, forward 24h, forward 48h, previous 24h, from/to
- National statistics: from/to and block aggregation
- National generation mix: current, previous 24h, from/to
- Regional carbon intensity: all regions, England, Scotland, Wales, postcode, region id, forward 24h, forward 48h, previous 24h, from/to, with postcode and region variants

The official docs also expose XML mirrors for at least the national intensity/statistics endpoints.

Local vault state: no `vault/neso/` files are present. The v2 target is 34 files, so all 34 are missing locally.

Boundary warning: NESO is larger than the Carbon Intensity API. The NESO applications/API page links both Carbon Intensity and the NESO Data Portal API. A live CKAN query on the NESO Data Portal reports 128 datasets. If "all NESO datasets" means the full data portal, then the v2 target of 34 Carbon Intensity pages is not vendor-complete. If the vendor scope is explicitly "NESO Carbon Intensity", the 34 target can be treated as complete after the vault files are vendored.

## Open-Meteo

Official evidence: Open-Meteo's official docs list more API families than the v2 target count of 6. Confirmed official families include:

| Family | Official endpoint example |
|---|---|
| Weather Forecast | `https://api.open-meteo.com/v1/forecast` |
| Historical Weather | `https://archive-api.open-meteo.com/v1/archive` |
| Historical Forecast | `https://historical-forecast-api.open-meteo.com/v1/forecast` |
| Previous Model Runs | `https://previous-runs-api.open-meteo.com/v1/forecast` |
| Ensemble | `https://ensemble-api.open-meteo.com/v1/ensemble` |
| Seasonal Forecast | `https://seasonal-api.open-meteo.com/v1/seasonal` |
| Climate Change | `https://climate-api.open-meteo.com/v1/climate` |
| Marine Weather | `https://marine-api.open-meteo.com/v1/marine` |
| Air Quality | `https://air-quality-api.open-meteo.com/v1/air-quality` |
| Satellite Radiation | `https://satellite-api.open-meteo.com/v1/archive` |
| Geocoding | `https://geocoding-api.open-meteo.com/v1/search` |
| Elevation | `https://api.open-meteo.com/v1/elevation` |
| Flood | `https://flood-api.open-meteo.com/v1/flood` |

The docs also provide provider/model-specific APIs or model selectors for DWD, NOAA/GFS/HRRR, Meteo-France, ECMWF, UK Met Office, JMA, KMA, MeteoSwiss, MET Norway, GEM Canada, BOM Australia, CMA China, KNMI, DMI, ItaliaMeteo, and GeoSphere Austria.

Local vault state: no `vault/openmeteo/` files are present. The v2 target is 6 files, so all 6 are missing locally.

Boundary warning: a 6-file Open-Meteo target is reasonable for GridFlow weather features, but it is not "all official Open-Meteo APIs." The likely v2 subset should be named explicitly, for example: forecast, historical weather, historical forecast/previous runs, ensemble, air quality, marine or satellite radiation.

## Cross-cutting frontend gaps

These are not vault edits, but they matter when the vault is expanded:

- `site/hifi/data/vendors.json` is stale for Elexon (`28`) and ENTSO-E (`14`) relative to the current/v2 story.
- `site/hifi/data/entsoe.json` contains 1 dataset, but v2 needs 49.
- No manifest exists yet for `entsog`, `gie`, `neso`, or `openmeteo`.
- The current local vault has `vault/entsog/`, but the v1/v2 narrative in `.planning/PROJECT.md` still says the in-repo snapshot holds only Elexon 33 + ENTSO-E 1. That planning text is stale relative to the present checkout.

## Recommended next actions

1. **Define "all datasets" precisely before authoring more files.** Use "all GridFlow-supported datasets" for v2 unless the intent is to grow GridFlow itself to every official endpoint.
2. **Do not expand Elexon inside v2 unless GridFlow code already supports those 52 extra BMRS dataset endpoints.** Treat the 52-code table above as a future Elexon vendor-complete backlog.
3. **Reconcile ENTSO-E local snapshot vs target 49.** The local repo has 25 files, while v2 expects 49. Recover the missing 24 from upstream `quant-vault` or from GridFlow endpoint definitions.
4. **Keep ENTSO-E entitlement as a Phase 9 decision.** The existing 401 findings are real and should determine whether pages ship with live verification or `requires additional entitlement` caveats.
5. **For ENTSO-G, decide whether removed docs stay as archived/removed pages or are deleted from the publishable target.** Four of five local files are already marked removed.
6. **For GIE, source-check `unavailability` before publishing.** The official v005 manual says unavailability is not currently part of API coverage.
7. **For NESO, decide Carbon Intensity only vs full NESO Data Portal.** The latter is 128 datasets and outside the current v2 target.
8. **For Open-Meteo, name the six selected API families.** The official docs expose more than six families, so the manifest should make the subset deliberate.

