---
slug: forecast_wind
vendor: openmeteo
vendor_label: Open-Meteo
api_code: forecast
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/forecast_wind.md
  - gridflow/src/gridflow/schemas/weather.py::WindWeather (lines 66-101, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/forecast.py::ForecastWindWeather (lines 43-56, subclass of HistoricalWindWeather with WIND_FORECAST_VARS override; registered L76)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalWindWeather (lines 289-307) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134)
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (WIND_LOCATIONS L65-83, WIND_FORECAST_VARS L129-136, DATASET_SPECS["forecast_wind"] L173-175, FORECAST_BASE_URL L189)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94)
  - https://open-meteo.com/en/docs (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (forecast_wind.md L154-182) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `wind_speed_10m` (km/h), `wind_speed_80m`...`180m`, `wind_direction_*`, `wind_gusts_10m`, `cloud_cover[_low/mid/high]`, `dew_point_2m`, `precipitation`, `surface_pressure`."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names with km/h→m/s conversion: `temperature_2m_c`, `wind_speed_10m_mps` (÷3.6), `wind_speed_80m_mps`...`180m_mps`, `wind_direction_*_deg`, `wind_gusts_10m_mps`, `cloud_cover[_low/mid/high]_pct`, `dew_point_2m_c`, `precipitation_mm`, `surface_pressure_hpa`."
    orchestrator_recommendation: "trust gridflow — F15-B canonical-schema rename is the SoT; vault tables predate it. Brief uses suffixed names."
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

**Tagline:** GB hub-height wind, <span class="italic fg-accent">forecast hourly.</span>

**Lede:** Hourly wind-weather forecast at 12 GB capacity-weighted sites with full hub-height coverage (10/80/100/120/180 m) — the canonical wind-generation forecast input.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /forecast](https://open-meteo.com/en/docs)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.forecast_wind` |
| API PATH | `/v1/forecast` |
| FREQUENCY | hourly |
| PUBLICATION LAG | real-time (NWP router refresh ~1h) |
| VOLUME | 12 sites × 24h × 16d ≈ 4.6k rows / horizon |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Forecast cadence |
| 2 | 16 d | Max forecast horizon |
| 3 | 12 | GB wind sites (8 offshore + 4 onshore) |
| 4 | 26 | Schema columns |

# Sidebar siblings

- historical_wind
- forecast_solar
- forecast_demand
- historical_solar
- historical_demand

# Sample chart

- **Type:** `sparkline`
- **Title:** "Hornsea `wind_speed_100m_mps` · next 7-day forecast"
- **Subtitle:** "Sparkline · m/s · hourly · UTC · 2026-05-08 → 2026-05-15"
- **Seed:** 19
- **Toggles:** `7d` (active) / `16d` / `48h`

# Schema

Defined in `gridflow/schemas/weather.py` · `WindWeather` (lines 66-101, subclass of `_BaseWeather` L23). Forecast variant uses the wider `WIND_FORECAST_VARS` set (19 vars: archive 13 + hub heights 80m/120m/180m × speed+direction). Silver parquet uses **F15-B canonical names** (unit-suffix rename, `silver/openmeteo/historical.py L101-134`). Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` (bitemporal from `BaseSilverTransformer`); no `forecast_run_at`. **Includes `air_density_kg_m3`** derivation (turbine power-curve density correction).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied. Validator requires tzinfo. | `schemas/weather.py L26, L34-39` |
| `location` | `str` | No | _derived_ | Site key from `WIND_LOCATIONS` — one of 12 (e.g. `hornsea`, `dogger_bank`, `whitelee`, `pen_y_cymoedd`). | `connectors/openmeteo/endpoints.py L65-83` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees (response value — may snap to grid cell). | `schemas/weather.py L29` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Air temperature at 2 m, °C. | `schemas/weather.py L76`; rename `silver/openmeteo/historical.py L111` |
| `surface_pressure_hpa` | `float` | Yes | `hourly.surface_pressure[i]` | Surface pressure, hPa. Feeds `air_density_kg_m3` derivation. | `schemas/weather.py L77`; rename L113 |
| `wind_speed_10m_mps` | `float` | Yes | `hourly.wind_speed_10m[i]` | Wind speed at 10 m, **m/s** (API km/h ÷3.6). | `schemas/weather.py L80`; conversion `silver/openmeteo/historical.py L102` |
| `wind_speed_80m_mps` | `float` | Yes | `hourly.wind_speed_80m[i]` | 80 m wind speed, m/s. Null when underlying NWP model omits this height. | `schemas/weather.py L81`; conversion L104 |
| `wind_speed_100m_mps` | `float` | Yes | `hourly.wind_speed_100m[i]` | 100 m wind speed, m/s. Headline hub-height feature. | `schemas/weather.py L82`; conversion L103 |
| `wind_speed_120m_mps` | `float` | Yes | `hourly.wind_speed_120m[i]` | 120 m wind speed, m/s. Null when NWP model omits this height. | `schemas/weather.py L83`; conversion L105 |
| `wind_speed_180m_mps` | `float` | Yes | `hourly.wind_speed_180m[i]` | 180 m wind speed, m/s. Null when NWP model omits this height. | `schemas/weather.py L84`; conversion L106 |
| `wind_direction_10m_deg` | `float` | Yes | `hourly.wind_direction_10m[i]` | 10 m direction, degrees (0=N, 90=E). | `schemas/weather.py L86`; rename L127 |
| `wind_direction_80m_deg` | `float` | Yes | `hourly.wind_direction_80m[i]` | 80 m direction, degrees. Null if model omits. | `schemas/weather.py L87`; rename L129 |
| `wind_direction_100m_deg` | `float` | Yes | `hourly.wind_direction_100m[i]` | 100 m direction, degrees. | `schemas/weather.py L88`; rename L128 |
| `wind_direction_120m_deg` | `float` | Yes | `hourly.wind_direction_120m[i]` | 120 m direction, degrees. Null if model omits. | `schemas/weather.py L89`; rename L130 |
| `wind_direction_180m_deg` | `float` | Yes | `hourly.wind_direction_180m[i]` | 180 m direction, degrees. Null if model omits. | `schemas/weather.py L90`; rename L131 |
| `wind_gusts_10m_mps` | `float` | Yes | `hourly.wind_gusts_10m[i]` | Peak gust at 10 m, m/s (km/h ÷3.6). | `schemas/weather.py L92`; conversion L107 |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | Total cloud cover, %. | `schemas/weather.py L94`; rename L115 |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | Low-altitude cloud cover, %. | `schemas/weather.py L95`; rename L116 |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | Mid-altitude cloud cover, %. | `schemas/weather.py L96`; rename L117 |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | High-altitude cloud cover, %. | `schemas/weather.py L97`; rename L118 |
| `dew_point_2m_c` | `float` | Yes | `hourly.dew_point_2m[i]` | Dew point at 2 m, °C — proxy for icing risk on offshore blades. | `schemas/weather.py L99`; rename L112 |
| `precipitation_mm` | `float` | Yes | `hourly.precipitation[i]` | Hourly precipitation, mm. | `schemas/weather.py L78`; rename L124 |
| `air_density_kg_m3` | `float` | Yes | _derived_ | `surface_pressure_Pa / (287.05 × T_K)`. Turbine power-curve density correction (standard 1.225 kg/m³). No unit-suffix rename. | `schemas/weather.py L101`; derivation `silver/openmeteo/historical.py L241-252` |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"`).

**PARQUET PATH:** `data/silver/open_meteo/forecast_wind/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (silently overwrites prior forecast vintages)

# Sample data

| timestamp_utc | location | wind_speed_10m_mps | wind_speed_100m_mps | wind_speed_180m_mps | wind_gusts_10m_mps | cloud_cover_pct | dew_point_2m_c | air_density_kg_m3 |
|---|---|---|---|---|---|---|---|---|
| 2026-05-08T00:00:00+00:00 | hornsea | 5.06 | 7.72 | 9.33 | 8.89 | 60.0 | 8.5 | 1.249 |
| 2026-05-08T01:00:00+00:00 | hornsea | 5.42 | 8.06 | 9.67 | 9.44 | 65.0 | 8.2 | 1.248 |
| **2026-05-08T12:00:00+00:00** | **hornsea** | **8.33** | **11.94** | **13.89** | **13.33** | **45.0** | **7.5** | **1.241** |
| 2026-05-08T12:00:00+00:00 | dogger_bank | 7.78 | 11.39 | 13.33 | 12.78 | 50.0 | 7.8 | 1.243 |
| 2026-05-08T12:00:00+00:00 | whitelee | 4.08 | 6.69 | null | 7.22 | 75.0 | 9.0 | 1.235 |
| 2026-05-08T12:00:00+00:00 | beatrice | 6.94 | 10.28 | 12.22 | 11.11 | 55.0 | 6.5 | 1.246 |
| 2026-05-08T12:00:00+00:00 | pen_y_cymoedd | 3.61 | 6.11 | null | 6.39 | 80.0 | 9.5 | 1.230 |
| 2026-05-08T12:00:00+00:00 | east_anglia | 7.50 | 11.11 | 13.06 | 12.50 | 55.0 | 7.2 | 1.242 |

**Sources:** Hornsea rows derived from vault Bronze sample (forecast_wind.md L91-135, captured 2026-05-08) — wind speeds converted from vault km/h to silver m/s (e.g. `18.2 km/h → 5.06 m/s`, `25.1 km/h → 6.97 m/s` rounded — corrected to current 100m measurement). The highlighted **Hornsea solar-noon row** is offshore peak: `wind_speed_100m_mps ≈ 11.94 m/s` sits comfortably above turbine cut-in (~3 m/s) and below rated (~12-14 m/s). Whitelee + Pen y Cymoedd rows show **180 m null** — the underlying NWP model (typically ECMWF / GFS for inland Scotland and Wales) does not carry that hub height; `WindWeather` accepts the null cleanly. `air_density_kg_m3` is the lone non-suffixed-renamed column (its name already carries units).

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
- **ENDPOINT**: `api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={vars}&forecast_days={1..16}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/forecast_wind__<site>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore**)
- **TRANSFORMER**: `gridflow.silver.openmeteo.forecast.ForecastWindWeather` (registered at `silver/openmeteo/forecast.py L76`)

**Tab 1 — Example URL:**
```
https://api.open-meteo.com/v1/forecast
  ?latitude=53.88
  &longitude=1.79
  &hourly=temperature_2m,surface_pressure,precipitation,wind_speed_10m,wind_speed_80m,wind_speed_100m,wind_speed_120m,wind_speed_180m,wind_direction_10m,wind_direction_80m,wind_direction_100m,wind_direction_120m,wind_direction_180m,wind_gusts_10m,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,dew_point_2m
  &forecast_days=7
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Day-ahead GB offshore mean 100m wind speed (capacity-weighted illustration)
SELECT date_trunc('hour', timestamp_utc) AS hour,
       avg(wind_speed_100m_mps) FILTER (WHERE location IN
         ('dogger_bank','hornsea','east_anglia','triton_knoll',
          'walney','gwynt_y_mor','beatrice','seagreen'))
         AS offshore_avg_100m_mps,
       avg(wind_speed_100m_mps) FILTER (WHERE location IN
         ('highland_central','borders_crystalrig','whitelee','pen_y_cymoedd'))
         AS onshore_avg_100m_mps
FROM read_parquet('data/silver/open_meteo/forecast_wind/**/*.parquet')
WHERE timestamp_utc >= current_date
GROUP BY 1 ORDER BY 1;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/forecast_wind/**/*.parquet")
# Power-curve-ready hub-height feature: prefer 100m, fall back to 10m × shear
power_input = (
    df.with_columns(
        pl.coalesce([
            pl.col("wind_speed_100m_mps"),
            pl.col("wind_speed_10m_mps") * 1.4,  # rough shear bump
        ]).alias("hub_height_mps"),
        # Density-corrected effective wind speed (Betz / power-curve work)
        (pl.col("hub_height_mps") * (pl.col("air_density_kg_m3") / 1.225) ** (1/3))
        .alias("rho_corrected_mps"),
    )
    .select(["timestamp_utc","location","hub_height_mps","rho_corrected_mps"])
)
print(power_input.tail(24))
```

# Caveats

## 01 No `forecast_run_at` — vintages overwrite silently

Dedup keeps the last silver row per `(timestamp_utc, location)`, overwriting prior forecast vintages on re-ingest. Lead-time backtests must pair against `historical_wind` at matching lead times. *(Source: vault Known Issues + `silver/openmeteo/historical.py L217`.)*

## 02 Silver column names are unit-suffixed (F15-B), wind in m/s

Silver emits `wind_speed_10m_mps`, `wind_speed_100m_mps`...`180m_mps`, `wind_direction_*_deg`, `wind_gusts_10m_mps` with **km/h→m/s ÷3.6 conversion**. Vault Silver Schema lists pre-rename km/h names. *(Source: `silver/openmeteo/historical.py L101-108` + `_output_columns` L255-271.)*

## 03 Hub-height nulls are model-driven, not silver bugs

`wind_speed_80/120/180m_mps` and matching directions go null when the underlying NWP router selects a model that doesn't carry those heights (e.g. some GFS configurations). Silver fabricates no values; `WindWeather` is permissive. Pin `models=ukmo_global` for stable hub-height coverage. *(Source: vault `forecast_wind.md` Known Issues "Hub-height nulls".)*

## 04 No NWP-model pinning by default

Open-Meteo's `/forecast` router selects an NWP model per request (UKMO / ECMWF / GFS / ICON). Hub-height availability shifts with model selection; pin via `&models=<id>` if reproducibility matters. *(Source: vault `forecast_wind.md` Known Issues "Unpinned NWP model".)*

## 05 Approximate site centroids (capacity-weighted, not NRO)

The 12 wind locations are capacity-weighted approximations per ADR-020, not per-turbine NRO coordinates. Sub-cluster resolution requires reading ADR-020 trade-offs (vendor licensing + ergonomics). *(Source: `docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md`.)*

## 06 Bronze path uses DOUBLE underscore separator

Bronze partitions are `bronze/open_meteo/forecast_wind__<site>/<year>/...` — double underscore between dataset key and site name. Silver `BRONZE_DATASET_PREFIX = "forecast_wind"` strips it on read. *(Source: `connectors/openmeteo/client.py L112` + `silver/openmeteo/historical.py L142`.)*

# Related datasets

- **`historical_wind`** (Open-Meteo) — Archive companion at `archive-api.open-meteo.com/v1/archive`; chip `hourly` — same 12 sites, ERA5 reanalysis from 1940. **Archive omits 80/120/180 m heights** (verified all-null vs ERA5); forecast carries them. Pair for forecast-skill backtests. *open-meteo · weather · hourly*
- **`forecast_solar`** (Open-Meteo) — Hourly solar-forecast feed at 6 GB solar sites; chip `hourly` — companion renewable forecast on the same `/forecast` host; **no `air_density_kg_m3`** (solar request omits `surface_pressure`). *open-meteo · weather · hourly*
- **`windfor`** (Elexon) — NESO-published GB wind-generation forecast; chip `hourly` — compare against this dataset for public-vs-NWP wind-forecast skill benchmarks over multi-year backtests. *elexon · generation · hourly*
- **`fuelhh`** (Elexon) — GB generation by fuel type (`WIND` field — onshore+offshore combined); chip `30 min` — downstream actuals to validate wind-power-curve mappings from this dataset. *elexon · generation · 30 min*
