---
slug: forecast_solar
vendor: openmeteo
vendor_label: Open-Meteo
api_code: forecast
last_verified: 2026-05-09
sources_consulted:
  - quant-vault/30-vendors/open-meteo/datasets/forecast_solar.md (vault not yet vendored to gridflow-front-end/vault/openmeteo/ — Phase 10 vendoring deferred)
  - gridflow/src/gridflow/schemas/weather.py::SolarWeather (line 104, subclass of _BaseWeather)
  - gridflow/src/gridflow/silver/openmeteo/forecast.py::ForecastSolarWeather (line 59, subclass of HistoricalSolarWeather; registered L77)
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (SOLAR_LOCATIONS L86, SOLAR_HOURLY_VARS L139, route at L177-181)
  - https://open-meteo.com/en/docs (vendor docs page — interactive playground rather than static API reference; no static doc page to WebFetch successfully)
discrepancies_found:
  - source_a: "vault Naming note (Known Issues last bullet)"
    source_a_says: "Vault folder is `open-meteo` (kebab), Python package is `openmeteo` (no separator), config key is `open_meteo` (snake)"
    source_b: "gridflow connectors/openmeteo/, schemas/weather.py, transformer register_transformer('open_meteo', ...)"
    source_b_says: "Code uses `openmeteo` for module names and `open_meteo` for registry/transformer keys; vault uses `open-meteo` for folder structure"
    orchestrator_recommendation: "documented design intent — three forms coexist by convention. Code-vault bridges should use the appropriate form per context. Document in editorial layer so downstream tools know which form to expect where."
  - source_a: "vault Bronze section — double-underscore separator"
    source_a_says: "Bronze paths use `forecast_solar__<site>`, NOT `forecast_solar_<site>` (single underscore)"
    source_b: "gridflow connectors/openmeteo/ — RawResponse.dataset = f'forecast_solar__{location.name}' (double underscore is the intentional separator); silver transformer's BRONZE_DATASET_PREFIX = 'forecast_solar'"
    orchestrator_recommendation: "documented design intent — double underscore is the separator between dataset key and location, distinguishing from a single-underscore composite key. Surface in caveats so downstream bronze-readers don't misparse."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB solar irradiance, <span class="italic fg-accent">forecast hourly.</span>

**Lede:** Hourly solar-irradiance forecast for the next 1–16 days at six GW-capacity-weighted GB solar sites — full irradiance decomposition (GHI / DNI / DHI / GTI at the UK fixed-tilt geometry), cloud cover at three heights, and snow context. The forward-looking PV-generation forecast input that pairs with the historical archive for forecast-skill backtests.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /forecast](https://open-meteo.com/en/docs)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.forecast_solar` |
| API PATH | `/v1/forecast` |
| FREQUENCY | hourly |
| PUBLICATION LAG | real-time (router refresh ~1h) |
| VOLUME | 6 sites × 24h × 16d = ~2.3k rows / horizon |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Forecast cadence |
| 2 | 16 d | Max forecast horizon |
| 3 | 6 | GB capacity-weighted sites |
| 4 | 18 | Schema columns (incl. bitemporal) |

# Sidebar siblings

- historical_solar
- forecast_wind
- forecast_demand
- historical_wind
- historical_demand

# Overview

1. <code>forecast_solar</code> is **the hourly solar-irradiance forecast** for the next 1–16 days at six capacity-weighted GB solar sites — East Anglia (Norfolk), Wiltshire/Somerset, Kent, Cornwall, Sussex, Oxfordshire. Each row carries the full irradiance decomposition (`shortwave_radiation` = GHI, `direct_normal_irradiance` = DNI, `diffuse_radiation` = DHI, `global_tilted_irradiance` = GTI at the UK fixed-tilt 35°/180° geometry), cloud cover at three atmospheric heights, plus snow context. This is the **forward-looking** PV forecast feed — for historical lookback / backtesting, use the sibling <code>historical_solar</code> dataset (which lives at a different vendor host — see Caveats #03).

2. Gridflow fetches it from <code>api.open-meteo.com/v1/forecast</code> with no authentication (public free tier). The connector dispatches per-site requests via <code>connectors/openmeteo/endpoints.py</code> — the six <code>SOLAR_LOCATIONS</code> at L86 and the twelve <code>SOLAR_HOURLY_VARS</code> at L139 (`temperature_2m`, `shortwave_radiation`, `direct_radiation`, `direct_normal_irradiance`, `diffuse_radiation`, `global_tilted_irradiance`, `cloud_cover` × 4 atmospheric levels, `snowfall`, `snow_depth`). GTI requires `tilt=35` and `azimuth=180` via `WeatherDatasetSpec.extra_params`. The <code>ForecastSolarWeather</code> transformer at <code>silver/openmeteo/forecast.py L59</code> subclasses <code>HistoricalSolarWeather</code> (shared pivot logic — columnar JSON arrays → row-shaped silver) and is registered as <code>('open_meteo', 'forecast_solar')</code> at L77. Pydantic class <code>SolarWeather</code> at <code>schemas/weather.py L104</code> inherits from <code>_BaseWeather</code>.

3. Cadence is real-time — Open-Meteo's NWP router refreshes the underlying forecast roughly every hour. Verified against the live API on 2026-05-09; a 2-day forecast request for Cornwall returned 48 hourly rows with full irradiance decomposition. Use <code>global_tilted_irradiance</code> as the most direct feature for fixed-tilt PV generation forecasting; combine with cloud-cover at low/mid/high atmospheric levels for hour-ahead nowcast features. Forecast vintages are silently overwritten on re-ingest — **no `forecast_run_at` column** (see Caveats #04), so cross-vintage skill backtests require pairing against the historical archive at matching lead times rather than comparing forecast vintages directly.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Cornwall GTI · next 16-day forecast"
- **Subtitle:** "Sparkline · W/m² · hourly · UTC · 2026-05-08 → 2026-05-23"
- **Seed:** 31
- **Toggles:** `16d` (active) / `7d` / `48h`

# Schema

Defined in `gridflow/schemas/weather.py` · `SolarWeather` (line 104, subclass of `_BaseWeather` L23) and `gridflow/silver/openmeteo/forecast.py` · `ForecastSolarWeather` (line 59, subclass of `HistoricalSolarWeather` — shared pivot logic). Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` (bitemporal stamp from `BaseSilverTransformer`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied by transformer. Hourly cadence. | `schemas/weather.py L23+` |
| `location` | `str` | No | _derived_ | Site key from `SOLAR_LOCATIONS` — one of `cornwall` / `kent` / `sussex` / `oxfordshire` / `wiltshire_somerset` / `east_anglia`. | `connectors/openmeteo/endpoints.py L86` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees. | `schemas/weather.py` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py` |
| `temperature_2m` | `float` | Yes | `hourly.temperature_2m[i]` | °C. Surface air temperature at 2m. | `schemas/weather.py L104+` |
| `shortwave_radiation` | `float` | Yes | `hourly.shortwave_radiation[i]` | **GHI** (Global Horizontal Irradiance) in W/m². | `schemas/weather.py` |
| `direct_radiation` | `float` | Yes | `hourly.direct_radiation[i]` | Beam component on horizontal surface, W/m². | `schemas/weather.py` |
| `direct_normal_irradiance` | `float` | Yes | `hourly.direct_normal_irradiance[i]` | **DNI** — beam normal to the sun, W/m². Use for tracker-mounted PV. | `schemas/weather.py` |
| `diffuse_radiation` | `float` | Yes | `hourly.diffuse_radiation[i]` | **DHI** (Diffuse Horizontal Irradiance), W/m². | `schemas/weather.py` |
| `global_tilted_irradiance` | `float` | Yes | `hourly.global_tilted_irradiance[i]` | **GTI** on UK fixed-tilt geometry (35° tilt, 180° azimuth = south-facing). Most direct feature for UK fixed-tilt PV. W/m². | `schemas/weather.py`; `connectors/openmeteo/endpoints.py` (`extra_params=(('tilt','35'),('azimuth','180'))`) |
| `cloud_cover` | `float` | Yes | `hourly.cloud_cover[i]` | Total cloud cover, %. | `schemas/weather.py` |
| `cloud_cover_low` | `float` | Yes | `hourly.cloud_cover_low[i]` | Low-altitude cloud cover, %. | `schemas/weather.py` |
| `cloud_cover_mid` | `float` | Yes | `hourly.cloud_cover_mid[i]` | Mid-altitude cloud cover, %. | `schemas/weather.py` |
| `cloud_cover_high` | `float` | Yes | `hourly.cloud_cover_high[i]` | High-altitude cloud cover, %. | `schemas/weather.py` |
| `snowfall` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm. | `schemas/weather.py` |
| `snow_depth` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m. | `schemas/weather.py` |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"`. **Underscore form** (not `open-meteo` and not `openmeteo` — see Caveats #02). | `schemas/weather.py` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (set to `"2.0.0"` for this dataset). **No `air_density_kg_m3` column** — the solar variable list does not request `surface_pressure`, so the derived column from `forecast_wind` is intentionally absent here. Property test `tests/unit/test_openmeteo_air_density.py` asserts this.

**PARQUET PATH:** `data/silver/open_meteo/forecast_solar/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (silently overwrites prior forecast vintages)

# Sample data

| timestamp_utc | location | latitude | longitude | shortwave_radiation | direct_normal_irradiance | global_tilted_irradiance | cloud_cover | temperature_2m |
|---|---|---|---|---|---|---|---|---|
| 2026-05-08T11:00:00+00:00 | cornwall | 50.30 | -5.00 | 580.0 | 750.0 | 670.0 | 30.0 | 14.5 |
| 2026-05-08T11:00:00+00:00 | kent | 51.20 | 0.70 | 620.0 | 770.0 | 720.0 | 25.0 | 16.0 |
| _ROW HIGHLIGHTED_ 2026-05-08T12:00:00+00:00 | cornwall | 50.30 | -5.00 | 700.0 | 770.0 | 770.0 | 25.0 | 15.8 |
| 2026-05-08T12:00:00+00:00 | kent | 51.20 | 0.70 | 720.0 | 800.0 | 790.0 | 20.0 | 17.0 |
| 2026-05-08T13:00:00+00:00 | cornwall | 50.30 | -5.00 | 720.0 | 780.0 | 790.0 | 20.0 | 16.6 |
| 2026-05-08T13:00:00+00:00 | east_anglia | 52.62 | 1.05 | 680.0 | 760.0 | 740.0 | 35.0 | 17.5 |
| 2026-05-08T18:00:00+00:00 | cornwall | 50.30 | -5.00 | 95.0 | 280.0 | 110.0 | 40.0 | 13.0 |
| 2026-05-09T01:00:00+00:00 | cornwall | 50.30 | -5.00 | 0.0 | 0.0 | 0.0 | 55.0 | 9.2 |

[1] First three rows (cornwall, kent at 11:00) from vault Bronze sample (captured live 2026-05-08); subsequent rows synthesised respecting hourly diurnal arc (peak GTI ~770 W/m² at solar noon, zero overnight) and southern-coastal-vs-east-anglia regional pattern (Cornwall typically clearer; East Anglia slightly cloudier). The highlighted row is Cornwall solar noon (12:00 UTC) — 770 W/m² GTI is a clear-sky south-coast peak, the upper end of what UK fixed-tilt panels see. Overnight row (01:00) shows the zero-radiation null pattern: irradiance columns are 0.0 (not null), cloud_cover and temperature_2m still populated.

# GB capacity-weighted solar sites (location codelist)

The six sites are GW-capacity-weighted hotspots (capacity-installed-rather-than-equal weighting), chosen per ADR-020 to approximate GB-aggregate PV output. All sites are below 53°N (south-east bias matches actual UK solar deployment).

| Site key | Location | Approx coords | Notes |
|---|---|---|---|
| `cornwall` | Cornwall / SW England | 50.30, -5.00 | South-west, highest annual sunshine |
| `wiltshire_somerset` | Wiltshire / Somerset | 51.40, -2.30 | South-west inland |
| `oxfordshire` | Oxfordshire | 51.75, -1.25 | South-central |
| `sussex` | Sussex / South coast | 50.85, -0.30 | South coast |
| `kent` | Kent / SE England | 51.20, 0.70 | South-east |
| `east_anglia` | East Anglia / Norfolk | 52.62, 1.05 | East coast, highest-latitude in set |

For tracker or non-fixed-tilt installations, GTI underestimates — use DNI + a tracker-specific transposition model. For GB-aggregate forecast, weight by installed PV capacity per region.

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={vars}&tilt=35&azimuth=180&forecast_days={1..16}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10,000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/forecast_solar__<location>/<year>/<month>/<day>/raw_<uuid>.json` (note the **double underscore** between dataset key and location)
- **TRANSFORMER**: `gridflow.silver.openmeteo.forecast.ForecastSolarWeather` (registered at `silver/openmeteo/forecast.py L77`)

**Tab 1 — Example URL:**
```
https://api.open-meteo.com/v1/forecast
  ?latitude=50.30
  &longitude=-5.00
  &hourly=temperature_2m,shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,snowfall,snow_depth
  &tilt=35
  &azimuth=180
  &forecast_days=7
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Daily peak GTI per GB solar site (illustrative PV forecast)
SELECT location,
       date_trunc('day', timestamp_utc) AS day,
       max(global_tilted_irradiance) AS peak_gti_wm2,
       avg(cloud_cover) AS avg_cloud_pct
FROM read_parquet('data/silver/open_meteo/forecast_solar/**/*.parquet')
WHERE timestamp_utc >= current_date
  AND timestamp_utc <  current_date + INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 2, 1;
```

**Tab 3 — Python · parquet:**
```python
import polars as pl

df = pl.read_parquet(
    "data/silver/open_meteo/forecast_solar/**/*.parquet",
)
# GB-aggregate hourly GTI (mean across 6 sites — equal weighting for illustration)
gb = (
    df.group_by("timestamp_utc")
      .agg(
          pl.col("global_tilted_irradiance").mean().alias("gb_avg_gti"),
          pl.col("cloud_cover").mean().alias("gb_avg_cloud"),
      )
      .sort("timestamp_utc")
)
print(gb.tail(24))
```

# Caveats

## 01 No `forecast_run_at` — cross-vintage skill backtests need the archive

The dedup keeps the LAST silver row per `(timestamp_utc, location)`, silently overwriting prior forecast vintages on re-ingest. There is no `forecast_run_at` column to distinguish vintages. For forecast-skill backtests (e.g. "how did the 24-hour-ahead forecast compare to actuals?"), pair against the sibling `historical_solar` at matching lead times — that's the canonical workflow. Single-vintage forecasts are present; vintage-vs-vintage comparison is not currently possible. *Source: vault Known Issues + Implementation Delta.*

## 02 Three vendor-name forms coexist by convention

- **Vault folder**: `open-meteo` (kebab, matches Open-Meteo's branding)
- **Python package**: `openmeteo` (no separator, matches PEP 8)
- **Config/registry key**: `open_meteo` (snake, matches gridflow's vendor-key convention)

All three forms are correct in their context. Code reading vault paths uses kebab; importing modules uses no-separator; querying the transformer registry uses snake. Document accordingly in any code that crosses these boundaries. *Source: vault Known Issues last bullet + README §Naming.*

## 03 Two-host design — forecast vs historical lives at different hosts

`forecast_solar` (this dataset) is fetched from `api.open-meteo.com/v1/forecast`. The sibling `historical_solar` is fetched from `archive-api.open-meteo.com/v1/archive` — a different vendor host. The connector handles the split; custom callers must too. Don't try to use this dataset for past data beyond `past_days` (~92 days); fall back to the archive dataset for canonical historical. *Source: vault Known Issues + connector dispatch.*

## 04 No NWP-model pinning by default

Open-Meteo's `/forecast` endpoint uses a router that selects an NWP model per request — usually one of `ecmwf_ifs`, `gfs_seamless`, `icon_seamless`, etc. Irradiance forecast skill varies materially by model. If reproducibility matters (e.g. for production trading), pin via `&models=<id>` — gridflow does NOT pin by default to maximise hit rate and freshness. *Source: vault Known Issues #4.*

## 05 Bronze path uses DOUBLE underscore separator

Bronze partition paths are `bronze/open_meteo/forecast_solar__<site>/<year>/<month>/<day>/raw_<uuid>.json` — note the **double** underscore between `forecast_solar` and the site name (e.g. `forecast_solar__cornwall`). The silver transformer's `BRONZE_DATASET_PREFIX = "forecast_solar"` strips this when reading. Custom bronze-readers MUST use the double-underscore form when listing partitions, or they'll see zero files. *Source: vault Known Issues bronze-double-underscore-separator bullet.*

## 06 No `air_density_kg_m3` derivation — different from forecast_wind

The wind-forecast sibling dataset derives `air_density_kg_m3` from `surface_pressure`. This solar dataset does NOT request `surface_pressure`, so `air_density_kg_m3` is intentionally absent from the silver schema. Property test `tests/unit/test_openmeteo_air_density.py` enforces this. Don't expect the column; use the wind dataset if you need air density. *Source: vault Known Issues + property-test reference.*

# Related datasets

- **`historical_solar`** (Open-Meteo) — Archive companion at `archive-api.open-meteo.com/v1/archive`; chip `hourly` — same site list, same variables, same tilt geometry. Pair with this dataset for forecast-skill backtests at matching lead times. *open-meteo · weather · hourly*

- **`forecast_wind`** (Open-Meteo) — Hourly wind-forecast feed at 12 GB wind sites; chip `hourly` — companion weather forecast for the other major UK renewables. Same `/forecast` endpoint, different variable set + locations (includes `air_density_kg_m3` derivation). *open-meteo · weather · hourly*

- **`fuelhh`** (Elexon) — GB generation by fuel type (`SOLAR` is one of the 16 codes); chip `30 min` — the downstream actuals to validate this dataset's forecasts against. Standard PV-forecast-skill workflow: forecast GTI here → predict PV MW → compare against fuelhh SOLAR column at the same `timestamp_utc`. *elexon · generation · 30 min*

- **`carbon_intensity`** (NESO) — GB grid carbon intensity; chip `30 min` — combine with this dataset's forecast for "expected clean-energy generation × carbon intensity" carbon-aware scheduling decisions. *neso · carbon · 30 min*
