---
slug: historical_wind
vendor: openmeteo
vendor_label: Open-Meteo
api_code: archive
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/historical_wind.md
  - gridflow/src/gridflow/schemas/weather.py::WindWeather (lines 66-101, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalWindWeather (lines 289-307) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134); registered L336
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (WIND_LOCATIONS L65-83, WIND_ARCHIVE_VARS L111-125, DATASET_SPECS["historical_wind"] L170-172, ARCHIVE_BASE_URL L188)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94)
  - https://open-meteo.com/en/docs/historical-weather-api (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (historical_wind.md L177-204) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `wind_speed_10m` (km/h), `wind_speed_100m`, `wind_direction_*`, `wind_gusts_10m`, `cloud_cover[_low/mid/high]`, `dew_point_2m`, `precipitation`, `surface_pressure`."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names with km/h→m/s conversion: `temperature_2m_c`, `wind_speed_10m_mps`, `wind_speed_100m_mps`, `wind_direction_*_deg`, `wind_gusts_10m_mps`, `cloud_cover[_low/mid/high]_pct`, `dew_point_2m_c`, `precipitation_mm`, `surface_pressure_hpa`."
    orchestrator_recommendation: "trust gridflow — F15-B canonical-schema rename is the SoT. Brief uses suffixed names. NOTE: archive omits hub heights 80/120/180m (verified all-null vs ERA5), so those columns are NOT in silver output for this dataset."
  - source_a: "vault folder naming convention"
    source_a_says: "Vault directory is `open-meteo/` (kebab); README documents three coexisting forms"
    source_b: "gridflow: Python package `openmeteo` (no separator); connector/transformer registry key `open_meteo` (snake); bronze + silver path prefix `open_meteo/`"
    orchestrator_recommendation: "documented design intent — three forms coexist by convention."
  - source_a: "module location `schemas/weather.py`"
    source_a_says: "Pydantic classes live in `schemas/weather.py` (DemandWeather, WindWeather, SolarWeather, _BaseWeather)"
    source_b: "every other vendor uses `schemas/<vendor>.py` (entsoe.py, entsog.py, gie.py, neso.py, elexon.py)"
    orchestrator_recommendation: "domain knowledge — `weather.py` is intentionally generic for future multi-source weather feeds."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB wind sites, <span class="italic fg-accent">ERA5 since 1940.</span>

**Lede:** Hourly ERA5-reanalysis wind weather at 12 GB capacity-weighted sites (10 m + 100 m only) — the canonical multi-decade backtest input for wind-generation modelling and shear-feature engineering.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /archive](https://open-meteo.com/en/docs/historical-weather-api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.historical_wind` |
| API PATH | `/v1/archive` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~5 days (ERA5 reanalysis cadence) |
| VOLUME | 12 sites × 24 rows / day (≈ 105k / year) |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Observation cadence |
| 2 | 1940 | ERA5 depth (start year) |
| 3 | 12 | GB wind sites (8 offshore + 4 onshore) |
| 4 | 20 | Schema columns (archive subset) |

# Sidebar siblings

- forecast_wind
- historical_solar
- historical_demand
- forecast_solar
- forecast_demand

# Sample chart

- **Type:** `sparkline`
- **Title:** "Hornsea `wind_speed_100m_mps` · annual cycle"
- **Subtitle:** "Sparkline · m/s · daily mean · UTC · 2025"
- **Seed:** 41
- **Toggles:** `1y` (active) / `5y` / `10y`

# Schema

Defined in `gridflow/schemas/weather.py` · `WindWeather` (lines 66-101, subclass of `_BaseWeather` L23). **Archive variant uses the narrower `WIND_ARCHIVE_VARS` set (13 vars)** — 80/120/180 m hub heights are excluded because ERA5 returns `units: "undefined"` and all-null at those heights (verified 2026-05-09 against Hornsea and Whitelee). The schema declares hub-height fields for symmetry with `forecast_wind`; on this dataset they are absent from silver output. Silver parquet uses **F15-B canonical names** (`silver/openmeteo/historical.py L101-134`). Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` from `BaseSilverTransformer` (F0); ERA5 values are stable. **Includes `air_density_kg_m3`** (turbine power-curve density correction).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied. Validator requires tzinfo. | `schemas/weather.py L26, L34-39` |
| `location` | `str` | No | _derived_ | Site key from `WIND_LOCATIONS` — one of 12 (e.g. `hornsea`, `dogger_bank`, `whitelee`, `pen_y_cymoedd`). | `connectors/openmeteo/endpoints.py L65-83` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees (ERA5 snaps to grid cell). | `schemas/weather.py L29` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Air temperature at 2 m, °C. | `schemas/weather.py L76`; rename `silver/openmeteo/historical.py L111` |
| `surface_pressure_hpa` | `float` | Yes | `hourly.surface_pressure[i]` | Surface pressure, hPa. Feeds `air_density_kg_m3` derivation. | `schemas/weather.py L77`; rename L113 |
| `precipitation_mm` | `float` | Yes | `hourly.precipitation[i]` | Hourly precipitation, mm. | `schemas/weather.py L78`; rename L124 |
| `wind_speed_10m_mps` | `float` | Yes | `hourly.wind_speed_10m[i]` | Wind speed at 10 m, **m/s** (API km/h ÷3.6). | `schemas/weather.py L80`; conversion `silver/openmeteo/historical.py L102` |
| `wind_speed_100m_mps` | `float` | Yes | `hourly.wind_speed_100m[i]` | 100 m wind speed, m/s. Headline hub-height feature. | `schemas/weather.py L82`; conversion L103 |
| `wind_direction_10m_deg` | `float` | Yes | `hourly.wind_direction_10m[i]` | 10 m direction, degrees (0=N). | `schemas/weather.py L86`; rename L127 |
| `wind_direction_100m_deg` | `float` | Yes | `hourly.wind_direction_100m[i]` | 100 m direction, degrees. | `schemas/weather.py L88`; rename L128 |
| `wind_gusts_10m_mps` | `float` | Yes | `hourly.wind_gusts_10m[i]` | Peak gust at 10 m, m/s (km/h ÷3.6). | `schemas/weather.py L92`; conversion L107 |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | Total cloud cover, %. | `schemas/weather.py L94`; rename L115 |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | Low-altitude cloud cover, %. | `schemas/weather.py L95`; rename L116 |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | Mid-altitude cloud cover, %. | `schemas/weather.py L96`; rename L117 |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | High-altitude cloud cover, %. | `schemas/weather.py L97`; rename L118 |
| `dew_point_2m_c` | `float` | Yes | `hourly.dew_point_2m[i]` | Dew point at 2 m, °C — proxy for offshore-blade icing risk. | `schemas/weather.py L99`; rename L112 |
| `air_density_kg_m3` | `float` | Yes | _derived_ | `surface_pressure_Pa / (287.05 × T_K)`. Turbine power-curve density correction (standard 1.225 kg/m³). | `schemas/weather.py L101`; derivation `silver/openmeteo/historical.py L241-252` |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"`).

**PARQUET PATH:** `data/silver/open_meteo/historical_wind/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (ERA5 values are stable; revisions rare)

# Sample data

| timestamp_utc | location | wind_speed_10m_mps | wind_speed_100m_mps | wind_gusts_10m_mps | wind_direction_100m_deg | cloud_cover_pct | dew_point_2m_c | air_density_kg_m3 |
|---|---|---|---|---|---|---|---|---|
| 2025-01-15T00:00:00+00:00 | hornsea | 6.25 | 7.17 | 10.56 | 230.0 | 85.0 | 3.0 | 1.273 |
| 2025-01-15T01:00:00+00:00 | hornsea | 6.69 | 7.61 | 11.39 | 232.0 | 90.0 | 2.8 | 1.272 |
| **2025-01-15T12:00:00+00:00** | **whitelee** | **4.89** | **7.86** | **8.33** | **254.0** | **95.0** | **0.5** | **1.279** |
| 2025-02-08T18:00:00+00:00 | dogger_bank | 11.39 | 13.61 | 18.06 | 245.0 | 70.0 | 2.5 | 1.265 |
| 2025-07-15T12:00:00+00:00 | hornsea | 4.17 | 5.28 | 6.94 | 200.0 | 40.0 | 14.0 | 1.215 |
| 2025-11-20T06:00:00+00:00 | beatrice | 8.89 | 11.11 | 14.44 | 215.0 | 75.0 | 4.0 | 1.255 |
| 2025-03-12T15:00:00+00:00 | pen_y_cymoedd | 3.06 | 5.06 | 5.83 | 220.0 | 65.0 | 6.0 | 1.230 |
| 2025-12-25T08:00:00+00:00 | east_anglia | 7.78 | 9.17 | 12.50 | 260.0 | 90.0 | 1.0 | 1.270 |

**Sources:** First three rows (Hornsea winter midnight + Whitelee winter noon) derived from vault Silver Sample (historical_wind.md L215-272, captured 2026-05-09) — wind speeds converted from vault km/h to silver m/s (`22.5 km/h → 6.25 m/s`, `25.8 km/h → 7.17 m/s`). The highlighted **Whitelee 2025-01-15 noon** row illustrates the 10 m → 100 m shear regime onshore: ratio 7.86/4.89 ≈ 1.6 (the Hellmann exponent signal). Remaining rows synthesised across seasons and sites — offshore winter (Dogger Bank Feb storm) shows the high-wind regime; summer Hornsea shows the low-density (warm-air) regime where turbines benefit from density correction. **No 80/120/180 m columns** — archive omits them; the schema declares them for forecast-symmetry but ERA5 returns null.

# GB capacity-weighted wind sites (location codelist)

12 sites: 8 offshore clusters + 4 onshore (Scotland + Wales). Capacity-weighted approximations per ADR-020, not per-turbine NRO coordinates.

| Site key | Region | Lat / Lon | Type |
|---|---|---|---|
| `dogger_bank` | Southern North Sea | 54.95, 1.95 | Offshore |
| `hornsea` | Southern North Sea | 53.88, 1.79 | Offshore |
| `east_anglia` | Southern North Sea | 52.50, 2.50 | Offshore |
| `triton_knoll` | Southern North Sea | 53.45, 0.42 | Offshore |
| `walney` | Irish Sea | 54.04, -3.52 | Offshore |
| `gwynt_y_mor` | Irish Sea | 53.46, -3.59 | Offshore |
| `beatrice` | Moray / Forth | 58.26, -2.89 | Offshore |
| `seagreen` | Moray / Forth | 56.59, -1.93 | Offshore |
| `highland_central` | Scotland | 57.20, -4.40 | Onshore |
| `borders_crystalrig` | Scottish Borders | 55.85, -2.50 | Onshore |
| `whitelee` | Scotland | 55.69, -4.27 | Onshore (UK's largest) |
| `pen_y_cymoedd` | Wales | 51.69, -3.61 | Onshore |

For GB-aggregate wind output, weight by installed offshore + onshore capacity per site.

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&hourly={vars}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/historical_wind__<site>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore**)
- **TRANSFORMER**: `gridflow.silver.openmeteo.historical.HistoricalWindWeather` (registered at `silver/openmeteo/historical.py L336`)

**Tab 1 — Example URL:**
```
https://archive-api.open-meteo.com/v1/archive
  ?latitude=53.88
  &longitude=1.79
  &start_date=2025-01-15
  &end_date=2025-01-21
  &hourly=temperature_2m,surface_pressure,wind_speed_10m,wind_speed_100m,wind_direction_10m,wind_direction_100m,wind_gusts_10m,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,dew_point_2m,precipitation
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Monthly capacity-factor-style 100m wind statistic per site (multi-year backtest)
SELECT date_trunc('month', timestamp_utc) AS month,
       location,
       avg(wind_speed_100m_mps)                       AS mean_100m_mps,
       quantile_cont(wind_speed_100m_mps, 0.50)       AS p50_100m_mps,
       avg(wind_speed_100m_mps / wind_speed_10m_mps)  AS shear_ratio
FROM read_parquet('data/silver/open_meteo/historical_wind/**/*.parquet')
WHERE timestamp_utc >= TIMESTAMP '2020-01-01'
  AND wind_speed_10m_mps > 0.5
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/historical_wind/**/*.parquet")
# Hellmann shear exponent: ln(v100/v10) / ln(100/10) — feature for hub-height extrapolation
shear = (
    df.filter((pl.col("wind_speed_10m_mps") > 0.5)
            & (pl.col("wind_speed_100m_mps") > 0.5))
      .with_columns(
          (pl.col("wind_speed_100m_mps") / pl.col("wind_speed_10m_mps")).log()
          .truediv(pl.lit(10.0).log())
          .alias("alpha_hellmann")
      )
      .group_by("location")
      .agg(pl.col("alpha_hellmann").mean().alias("mean_alpha"))
)
print(shear.sort("mean_alpha"))
```

# Caveats

## 01 ERA5 archive omits hub heights 80/120/180 m

The connector excludes those heights from `WIND_ARCHIVE_VARS` — verified 2026-05-09 against Hornsea and Whitelee: ERA5 returns `units: "undefined"` and all-null. The `WindWeather` schema declares them for forecast-symmetry; silver output does not carry them on this dataset. Use `forecast_wind` for the wider hub-height set. *(Source: vault `historical_wind.md` §Archive 10m+100m limitation; `connectors/openmeteo/endpoints.py L109-125`.)*

## 02 Silver column names are unit-suffixed (F15-B), wind in m/s

Silver emits `wind_speed_10m_mps`, `wind_speed_100m_mps`, `wind_direction_*_deg`, `wind_gusts_10m_mps` with **km/h→m/s ÷3.6 conversion**. Vault Silver Schema lists pre-rename km/h names. *(Source: `silver/openmeteo/historical.py L101-108` + `_output_columns` L255-271.)*

## 03 ERA5 publication lag is ~5 days

Calls for `end_date` within the last 5 days may return 200 with null trailing values. For very recent past use `forecast_wind` with `past_days`. *(Source: vault `historical_wind.md` Known Issues "ERA5 reanalysis lag".)*

## 04 Approximate site centroids (capacity-weighted, not NRO)

The 12 wind locations are capacity-weighted approximations per ADR-020, not per-turbine NRO coordinates. Sub-cluster resolution requires reading ADR-020 trade-offs (vendor licensing + ergonomics + modelling granularity). *(Source: `docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md`.)*

## 05 ERA5 grid-cell snapping

`latitude` / `longitude` echoed in the response can differ slightly from the request — ERA5 snaps to the nearest grid cell (~0.25° resolution). Silver stores the response values, not the request values. *(Source: vault `historical_wind.md` Known Issues "ERA5 grid-cell snapping".)*

## 06 Bronze path uses DOUBLE underscore separator

Bronze partitions are `bronze/open_meteo/historical_wind__<site>/<year>/...` — double underscore between dataset key and site name. Silver `BRONZE_DATASET_PREFIX = "historical_wind"` strips it on read. *(Source: `connectors/openmeteo/client.py L112` + `silver/openmeteo/historical.py L142`.)*

# Related datasets

- **`forecast_wind`** (Open-Meteo) — Forecast companion at `api.open-meteo.com/v1/forecast`; chip `hourly` — same 12 sites, **wider hub-height set (10/80/100/120/180 m)** — UKMO/ECMWF/GFS forecast models carry the deeper heights ERA5 omits. *open-meteo · weather · hourly*
- **`historical_solar`** (Open-Meteo) — Archive companion at the same host for 6 GB solar sites; chip `hourly` — the other renewables-side ERA5 feed. *open-meteo · weather · hourly*
- **`fuelhh`** (Elexon) — GB generation by fuel type (`WIND` field — onshore+offshore combined); chip `30 min` — downstream actuals for multi-year wind-power-curve calibration and capacity-factor regression. *elexon · generation · 30 min*
- **`windfor`** (Elexon) — NESO-published GB wind-generation forecast; chip `hourly` — pair with this dataset for multi-year public-vs-NWP forecast-skill backtests. *elexon · generation · hourly*
