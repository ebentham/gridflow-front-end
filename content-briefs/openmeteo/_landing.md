---
slug: _landing
vendor: openmeteo
vendor_label: Open-Meteo
brief_type: landing
vault_dataset_count: 6
last_verified: 2026-05-09
sources_consulted:
  - quant-vault/30-vendors/open-meteo/datasets/ (6 files: forecast_demand.md, forecast_solar.md, forecast_wind.md, historical_demand.md, historical_solar.md, historical_wind.md)
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (ARCHIVE_BASE_URL L188, FORECAST_BASE_URL L189, DATASET_SPECS L163–184, DEMAND_LOCATIONS L54–62, WIND_LOCATIONS L65–83, SOLAR_LOCATIONS L86–93)
  - gridflow/src/gridflow/connectors/openmeteo/client.py (OpenMeteoConnector — no auth, dual base-URL routing at L90–94)
  - gridflow/src/gridflow/schemas/weather.py (4 Pydantic classes: _BaseWeather, DemandWeather, WindWeather, SolarWeather)
  - "gridflow/src/gridflow/silver/openmeteo/ (2 transformers: forecast.py, historical.py — 3 classes each: ForecastDemandWeather, ForecastWindWeather, ForecastSolarWeather; HistoricalDemandWeather, HistoricalWindWeather, HistoricalSolarWeather)"
  - gridflow-front-end/src/gridflow_front_end/build.py COMING_SOON_VENDORS (openmeteo stub — minimal fields, not yet promoted to REAL_VENDORS)
  - https://open-meteo.com/en/docs (fetched 2026-05-20 — interactive playground, primary content rendered via JavaScript; static API facts extracted but full endpoint catalogue not available as flat markdown)
discrepancies_found:
  - source_a: "vault folder naming convention"
    source_a_says: "Vault directory is `open-meteo/` (kebab-case with hyphen)"
    source_b: "gridflow connectors/openmeteo/, schemas/weather.py, build.py COMING_SOON_VENDORS"
    source_b_says: "All code identifiers use `openmeteo` (no separator); config registry key is `open_meteo` (snake_case)"
    orchestrator_recommendation: "documented design intent — three forms coexist by convention (open-meteo for vault folder, openmeteo for module/slug, open_meteo for registry key). Content briefs use `openmeteo` as the canonical vendor key. Document in caveats."
  - source_a: "schemas/weather.py module name"
    source_a_says: "Schema entry-point is `gridflow.schemas.weather` — not `gridflow.schemas.openmeteo`"
    source_b: "All other vendors use `schemas/<vendor>.py` (entsoe.py, entsog.py, gie.py, neso.py)"
    source_b_says: "Open-Meteo schemas live in a shared `weather.py` module alongside potential future non-Open-Meteo weather sources"
    orchestrator_recommendation: "domain knowledge — weather.py is intentionally generic for future multi-source weather data. Surface in source map for Claude Design readers."
  - source_a: "connectors/openmeteo/endpoints.py ARCHIVE_BASE_URL + FORECAST_BASE_URL"
    source_a_says: "Two distinct base hosts: archive-api.open-meteo.com (historical) and api.open-meteo.com (forecast)"
    source_b: "vendor metadata cell BASE URL — only one slot available"
    source_b_says: "The template's 2×3 metadata grid has a single BASE URL cell"
    orchestrator_recommendation: "Surface both hosts in BASE URL cell with a `(archive)` / `(forecast)` qualifier; instruct Claude Design to render with line-break between them. Full disambiguation in Caveats."
  - source_a: "open-meteo.com/en/docs (live vendor docs)"
    source_a_says: "Documentation page is a JavaScript-rendered interactive playground — full endpoint catalogue not available as flat markdown via WebFetch"
    source_b: "vault/open-meteo/datasets/*.md (all 6 files)"
    source_b_says: "All API facts (rate limits, auth, endpoints, variables) are documented in vault with verified curl examples"
    orchestrator_recommendation: "treat vault as canonical fallback per Phase 8D RECIPE §Sources rule; flag vendor_docs_unfetchable: JavaScript-rendered playground"
ready_for_claude_design: true
checked_at: 2026-05-20T12:00:00Z
---

# Editorial layer

**H1 pattern:**

```html
Open-Meteo <span class="italic">Weather.</span>
```

**Eyebrow chip:** `Open-Meteo · GB · Weather`

**Illustrative snapshot chip:** yes (standard)

**Lede paragraph (≤60 words):**

Open-source weather API aggregating ECMWF, GFS, and ERA5 reanalysis into a single columnar JSON interface. No authentication required for non-commercial use. Six datasets covering hourly temperature, wind, and solar irradiance across GB population centres and capacity-weighted generation sites — forward-looking 1–16-day forecasts and ERA5-backed archive to 1940.

**CTA 1:** `Browse 6 datasets ↓` (anchors `#datasets`)
**CTA 2:** `Vendor docs ↗` → `https://open-meteo.com/en/docs`

---

# Vendor metadata

| Cell label | Value |
|---|---|
| BASE URL | `api.open-meteo.com/v1` (forecast)<br/>`archive-api.open-meteo.com/v1` (historical) |
| AUTH | Public · no key required |
| RATE LIMIT | 5 req/s · project default (~10 000 req/day free tier) |
| FORMAT | JSON · ISO-8601 · UTC |
| EARLIEST | 1940-01-01 (ERA5 historical) |
| TIMEZONE | UTC · hourly resolution |

**Render note for BASE URL cell:** Two hosts — instruct Claude Design to render `<br/>` between lines and `font-size: 10px` on the cell value to fit the 80-char cell layout.

---

# Stats strip

| slot | value | label | source |
|---|---|---|---|
| 1 | `6` | `Datasets` | vault: 6 files in `open-meteo/datasets/` |
| 2 | `2` | `Categories` | 2 groups: Forecast + Historical |
| 3 | `1940` | `ERA5 depth` | earliest in vault: historical_demand/wind/solar all 1940-01-01 |
| 4 | `25` | `GB sites` | 7 demand + 12 wind + 6 solar = 25 named geographic locations |

---

# About section

**Paragraph 1 — Who they are:**

`openmeteo` is an open-source weather API operated by a small Swiss team (Open-Meteo, Zürich). The project aggregates multiple global NWP models — ECMWF IFS, GFS, ICON, UKMO, and others — into a unified hourly columnar JSON endpoint, with a separate archive endpoint backed by the ECMWF ERA5 reanalysis dataset. The API is free for non-commercial use with no registration or key.

**Paragraph 2 — What they publish:**

Six gridflow datasets cover three meteorological variable families (demand-weather, wind, solar) across two time horizons (historical archive and forward-looking forecast). Historical datasets expose the ERA5 reanalysis record from 1940-01-01 at 7 GB population centres and 18 capacity-weighted generation sites; forecast datasets project 1–16 days forward from the current NWP model run, updated approximately hourly. Variables include temperature, wind speed and direction at multiple hub heights (10 m, 80 m, 100 m, 120 m, 180 m), shortwave irradiance, direct/diffuse/GTI components, precipitation, snowfall, and snow depth.

**Paragraph 3 — Why it matters for energy trading:**

Open-Meteo is the primary weather-driver input for gridflow's demand and generation-mix models. ERA5 historical data forms the backbone for multi-year backtest calibration of heating-degree-day models and wind/solar capacity-factor regression. The `forecast_wind` and `forecast_solar` datasets, combined with `elexon.fuelhh` outturn, support nowcast skill evaluation; `historical_demand` paired with `elexon.system_prices` enables weather-adjusted price modelling. The dual-host architecture (archive vs forecast) is a deliberate API design — not a versioning split.

---

# Groups

## Group: Forecast

**Blurb:** Hourly NWP model output, 1–16 days ahead, at GB demand centres and generation sites.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `forecast_demand` | Forecast demand weather · population centres | hourly | Real-time (~1 hr refresh) | ~7 × 7 days × 24 hr = 1 176 / run |
| `forecast_solar` | Forecast solar irradiance · capacity-weighted sites | hourly | Real-time (~1 hr refresh) | ~6 × 7 days × 24 hr = 1 008 / run |
| `forecast_wind` | Forecast wind weather · capacity-weighted sites | hourly | Real-time (~1 hr refresh) | ~12 × 7 days × 24 hr = 2 016 / run |

## Group: Historical

**Blurb:** ERA5 reanalysis archive from 1940, ~5 days behind real time, at the same GB sites.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `historical_demand` | Historical demand weather · ERA5 archive | hourly | ~5 days | ~7 × 24 hr / day |
| `historical_solar` | Historical solar irradiance · ERA5 archive | hourly | ~5 days | ~6 × 24 hr / day |
| `historical_wind` | Historical wind weather · ERA5 archive | hourly | ~5 days | ~12 × 24 hr / day |

**Row count invariant:** 6 dataset rows across 2 groups == `vault_dataset_count: 6`. ✓

---

# Source map

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/openmeteo/endpoints.py` | Base URLs (L188–189), DATASET_SPECS (L163–184), all location lists and variable tuples | Two base URLs: `ARCHIVE_BASE_URL` and `FORECAST_BASE_URL` — the connector routes per `dataset.startswith("historical")` |
| `connectors/openmeteo/client.py` | No-auth httpx client, dual-URL routing, semaphore-based rate limiting | `OpenMeteoConnector` at L24; no `base_url` on httpx.AsyncClient (L44) — absolute URLs built per-request (L92–94) |
| `schemas/weather.py` | 4 Pydantic classes: `_BaseWeather`, `DemandWeather`, `WindWeather`, `SolarWeather` | Module named `weather.py` (not `openmeteo.py`) — intentionally generic for future multi-source weather data |
| `silver/openmeteo/forecast.py` | 3 transformer classes: `ForecastDemandWeather`, `ForecastWindWeather`, `ForecastSolarWeather` | All registered via `register_transformer('open_meteo', ...)` |
| `silver/openmeteo/historical.py` | 3 transformer classes: `HistoricalDemandWeather`, `HistoricalWindWeather`, `HistoricalSolarWeather` | ERA5 paths write to `silver/open_meteo/historical_*/year=YYYY/month=MM/` |
| `build.py COMING_SOON_VENDORS` | `openmeteo` stub — minimal `vendor_label` only, not yet promoted to `REAL_VENDORS` | This brief defines the eventual `REAL_VENDORS["openmeteo"]["vendor_meta"]` block for Phase 10 promotion |

---

# Cross-vendor links

- **`elexon` · `fuelhh`** — wind/solar nowcast skill evaluation: `forecast_wind`/`forecast_solar` vs actual generation outturn by fuel type. Core use case for weather-adjusted dispatch modelling.
- **`elexon` · `windfor`** — public wind-forecast benchmarking: Open-Meteo NWP vs Elexon's own D+1 wind forecast. Skill comparison over multi-year backtests.
- **`neso` · `carbon_intensity`** — weather-driven carbon drivers: temperature and cloud cover explain ~60% of short-run carbon-intensity variation in GB. Pair `historical_demand` with NESO national intensity for heating-load attribution.
- **`elexon` · `system_prices`** — weather-adjusted price modelling: temperature HDD/CDD proxies from `historical_demand` combined with system buy/sell prices for weather-normalised regression.
- **`entsoe` · `actual_generation`** — pan-European weather-generation coupling: Open-Meteo wind/solar at EU generation sites vs ENTSO-E actual generation by PSR type for cross-border generation-weather correlation.

---

# Caveats

## 01 Dual base-URL architecture (not a versioning split)

Open-Meteo exposes historical and forecast data on two distinct hosts: `archive-api.open-meteo.com` (ERA5 reanalysis) and `api.open-meteo.com` (NWP forecast). This is an API design choice — not a version difference — and means the `BASE URL` hero cell is inherently ambiguous. The gridflow connector (`client.py L90–94`) routes per `dataset.startswith("historical")`; both paths use the same JSON columnar response shape. Claude Design should render both hosts in the BASE URL cell with a visual separator (e.g., `(archive)` / `(forecast)` qualifier lines).

**Source:** `connectors/openmeteo/endpoints.py ARCHIVE_BASE_URL + FORECAST_BASE_URL`

## 02 Three naming forms coexist by convention

The Open-Meteo vendor uses three distinct naming forms across the stack:
- **`open-meteo`** (kebab) — vault directory, vendor's own branding
- **`openmeteo`** (no separator) — gridflow Python module names, `content-briefs/` slug, build.py vendor key
- **`open_meteo`** (snake\_case) — gridflow connector registry key (`register_connector("open_meteo", ...)`), bronze path prefix (`bronze/open_meteo/`), silver path prefix

These forms are intentional design decisions. Code that bridges vault → connector must select the right form per context. The brief uses `openmeteo` as the canonical slug everywhere outside vault paths.

**Source:** `connectors/openmeteo/client.py L39 source_name = "open_meteo"` vs `build.py COMING_SOON_VENDORS key "openmeteo"` vs vault directory `open-meteo/`

## 03 ERA5 archive lag (~5 days) vs forecast real-time refresh

Historical datasets (`historical_demand`, `historical_wind`, `historical_solar`) use the ERA5 reanalysis, which publishes with approximately 5 days of lag — meaning yesterday's data is not yet available. Forecast datasets refresh approximately every hour as the upstream NWP model completes a new run. This creates a coverage gap: the most recent ~5 days cannot be served from either dataset cleanly (ERA5 not yet available; forecast supports `past_days` ≤ 92 as a bridge but with NWP rather than reanalysis quality). The gridflow connector does not currently implement a `past_days` bridge for this gap — it treats the two dataset families as independent.

**Source:** vault `historical_demand.md` API endpoint table (Publication lag: "~5 days behind real time"); vault `forecast_demand.md` ("Real-time — current run typically refreshed every ~1 hour")

## 04 schema entry-point is `schemas/weather.py`, not `schemas/openmeteo.py`

Unlike every other vendor in gridflow (which uses `schemas/<vendor>.py`), Open-Meteo's Pydantic schema classes live in `schemas/weather.py`. This module is intentionally named for the domain (weather data) rather than the vendor, to accommodate potential future multi-source weather feeds. There are 4 classes: `_BaseWeather` (abstract), `DemandWeather`, `WindWeather`, `SolarWeather`. Downstream tooling that auto-discovers schemas by `schemas/<vendor>.py` pattern will miss Open-Meteo's classes.

**Source:** `schemas/weather.py`; discrepancy surfaced in frontmatter `discrepancies_found` item 2.

## 05 Vendor docs page is a JavaScript-rendered playground

`https://open-meteo.com/en/docs` renders as an interactive variable-selection playground and does not expose a flat, WebFetch-parseable API reference. All API facts in this brief (rate limits, base URLs, variable lists, auth scheme) are sourced from the vault's verified dataset files (`last_verified: 2026-05-09`) and from gridflow's connector code. If vendor-doc discrepancies arise in future, the vault's curl-verified records take precedence.

**Source:** WebFetch of `https://open-meteo.com/en/docs` (2026-05-20) — JavaScript-rendered playground; vault files annotated `vendor_docs_unfetchable: JavaScript-rendered playground`

---

# Per-vendor cheatsheet

## Variable groups

| Variable family | Key fields | Datasets using it |
|---|---|---|
| **Temperature / Demand** | `temperature_2m`, `wind_speed_10m`, `wind_direction_10m`, `relative_humidity_2m`, `precipitation`, `shortwave_radiation`, `surface_pressure`, `snowfall`, `snow_depth` | `forecast_demand`, `historical_demand` |
| **Wind (archive)** | `wind_speed_10m`, `wind_speed_100m`, `wind_direction_10m/100m`, `wind_gusts_10m`, `cloud_cover` (×3 layers), `dew_point_2m`, `precipitation`, `temperature_2m`, `surface_pressure` | `historical_wind` |
| **Wind (forecast)** | Archive vars + `wind_speed_80/120/180m`, `wind_direction_80/120/180m` (hub heights) | `forecast_wind` |
| **Solar** | `shortwave_radiation`, `direct_radiation`, `direct_normal_irradiance`, `diffuse_radiation`, `global_tilted_irradiance` (tilt=35, azimuth=180), `cloud_cover` (×3), `snowfall`, `snow_depth`, `temperature_2m` | `forecast_solar`, `historical_solar` |

## Location sets

| Set | Count | Use |
|---|---|---|
| `DEMAND_LOCATIONS` | 7 | London, Birmingham, Manchester, Leeds, Glasgow, Cardiff, Belfast |
| `WIND_LOCATIONS` | 12 | Offshore (Dogger Bank, Hornsea, East Anglia, Triton Knoll, Walney, Gwynt y Môr, Beatrice, Seagreen) + onshore Scotland + Wales |
| `SOLAR_LOCATIONS` | 6 | East Anglia/Norfolk, Wiltshire/Somerset, Kent, Cornwall, Sussex, Oxfordshire |

## ERA5 archive limitations

- 80 m, 120 m, 180 m wind heights return all-null from ERA5 archive (verified 2026-05-09 at Hornsea and Whitelee); `WIND_ARCHIVE_VARS` deliberately omits these.
- GTI (`global_tilted_irradiance`) uses UK representative geometry: `tilt=35, azimuth=180` (due south, fixed-tilt).

---

# Source-of-truth note

Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.weather` (note: Open-Meteo uses `weather.py` not `openmeteo.py`); values shown in charts are illustrative deterministic snapshots, not live Open-Meteo API responses. The vault's `open-meteo/datasets/` files are the canonical per-dataset reference; this landing brief is the vendor-hub layer above them.
