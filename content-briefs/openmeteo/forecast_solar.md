---
slug: forecast_solar
vendor: openmeteo
vendor_label: Open-Meteo
api_code: forecast
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/forecast_solar.md
  - gridflow/src/gridflow/schemas/weather.py::SolarWeather (lines 104-126, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/forecast.py::ForecastSolarWeather (lines 59-66, subclass of HistoricalSolarWeather; registered L77)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalSolarWeather (lines 310-325) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134)
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (SOLAR_LOCATIONS L86-93, SOLAR_HOURLY_VARS L139-152, _SOLAR_GTI_PARAMS L157-160, DATASET_SPECS["forecast_solar"] L180-183, FORECAST_BASE_URL L189)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94)
  - gridflow/tests/unit/test_openmeteo_air_density.py (asserts solar transformer omits air_density_kg_m3)
  - https://open-meteo.com/en/docs (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (forecast_solar.md L146-165) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `shortwave_radiation`, `direct_radiation`, `direct_normal_irradiance`, `diffuse_radiation`, `global_tilted_irradiance`, `cloud_cover`, `snowfall`, `snow_depth`."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names: `temperature_2m_c`, `shortwave_radiation_wm2`, `direct_radiation_wm2`, `direct_normal_irradiance_wm2`, `diffuse_radiation_wm2`, `global_tilted_irradiance_wm2`, `cloud_cover_pct`, `snowfall_cm`, `snow_depth_m`."
    orchestrator_recommendation: "trust gridflow — F15-B canonical-schema rename is the SoT; vault tables predate it. This brief uses suffixed names."
  - source_a: "vault folder naming convention"
    source_a_says: "Vault directory is `open-meteo/` (kebab); README documents three coexisting forms"
    source_b: "gridflow: Python package `openmeteo` (no separator); connector/transformer registry key `open_meteo` (snake); bronze + silver path prefix `open_meteo/`"
    orchestrator_recommendation: "documented design intent — three forms coexist by convention. Brief uses `openmeteo` as the canonical slug."
  - source_a: "module location `schemas/weather.py`"
    source_a_says: "Pydantic classes live in `schemas/weather.py` (DemandWeather, WindWeather, SolarWeather, _BaseWeather)"
    source_b: "every other vendor uses `schemas/<vendor>.py` (entsoe.py, entsog.py, gie.py, neso.py, elexon.py)"
    orchestrator_recommendation: "domain knowledge — `weather.py` is intentionally generic for future multi-source weather feeds."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB solar irradiance, <span class="italic fg-accent">forecast hourly.</span>

**Lede:** Hourly GHI/DNI/DHI/GTI forecast at 6 GB capacity-weighted solar sites — the canonical PV-generation-forecast input for day-ahead bid optimisation and forecast-skill backtests.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /forecast](https://open-meteo.com/en/docs)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.forecast_solar` |
| API PATH | `/v1/forecast` |
| FREQUENCY | hourly |
| PUBLICATION LAG | real-time (NWP router refresh ~1h) |
| VOLUME | 6 sites × 24h × 16d ≈ 2.3k rows / horizon |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Forecast cadence |
| 2 | 16 d | Max forecast horizon |
| 3 | 6 | GB capacity-weighted sites |
| 4 | 16 | Schema columns |

# Sidebar siblings

- historical_solar
- forecast_wind
- forecast_demand
- historical_wind
- historical_demand

# Sample chart

- **Type:** `sparkline`
- **Title:** "Cornwall `global_tilted_irradiance_wm2` · next 16-day forecast"
- **Subtitle:** "Sparkline · W/m² · hourly · UTC · 2026-05-08 → 2026-05-23"
- **Seed:** 31
- **Toggles:** `16d` (active) / `7d` / `48h`

# Schema

Defined in `gridflow/schemas/weather.py` · `SolarWeather` (lines 104-126, subclass of `_BaseWeather` L23). Silver parquet uses **F15-B canonical names** (unit-suffix rename in `BaseOpenMeteoTransformer._PURE_RENAMES`, `silver/openmeteo/historical.py L101-134`) — vault tables predate the rename. Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` (bitemporal stamp from `BaseSilverTransformer`); no `forecast_run_at`. **No `air_density_kg_m3`** — solar variable list omits `surface_pressure`; property test `tests/unit/test_openmeteo_air_density.py` locks this contract.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied. Hourly cadence. Validator requires tzinfo. | `schemas/weather.py L26, L34-39` |
| `location` | `str` | No | _derived_ | Site key from `SOLAR_LOCATIONS` — one of `east_anglia_norfolk` / `wiltshire_somerset` / `kent` / `cornwall` / `sussex` / `oxfordshire`. | `connectors/openmeteo/endpoints.py L86-93` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Surface air temperature at 2 m, °C. Drives Sandia-style module-temperature derate. | `schemas/weather.py L112`; rename `silver/openmeteo/historical.py L111` |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | **GHI** (Global Horizontal Irradiance), W/m². | `schemas/weather.py L114`; rename L119 |
| `direct_radiation_wm2` | `float` | Yes | `hourly.direct_radiation[i]` | Beam component on horizontal surface, W/m². | `schemas/weather.py L115`; rename L120 |
| `direct_normal_irradiance_wm2` | `float` | Yes | `hourly.direct_normal_irradiance[i]` | **DNI** — beam normal to the sun, W/m². Use for tracker-mounted PV. | `schemas/weather.py L116`; rename L121 |
| `diffuse_radiation_wm2` | `float` | Yes | `hourly.diffuse_radiation[i]` | **DHI** (Diffuse Horizontal Irradiance), W/m². | `schemas/weather.py L117`; rename L122 |
| `global_tilted_irradiance_wm2` | `float` | Yes | `hourly.global_tilted_irradiance[i]` | **GTI** on UK fixed-tilt geometry (`tilt=35°`, `azimuth=180°`). Most direct feature for UK fixed-tilt PV. W/m². | `schemas/weather.py L118`; rename L123; `endpoints.py L157-160` (extra_params) |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | Total cloud cover, %. | `schemas/weather.py L120`; rename L115 |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | Low-altitude cloud cover, %. | `schemas/weather.py L121`; rename L116 |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | Mid-altitude cloud cover, %. | `schemas/weather.py L122`; rename L117 |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | High-altitude cloud cover, %. | `schemas/weather.py L123`; rename L118 |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm. | `schemas/weather.py L125`; rename L125 |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m. | `schemas/weather.py L126`; rename L126 |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"`).

**PARQUET PATH:** `data/silver/open_meteo/forecast_solar/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (silently overwrites prior forecast vintages)

# Sample data

| timestamp_utc | location | shortwave_radiation_wm2 | direct_normal_irradiance_wm2 | diffuse_radiation_wm2 | global_tilted_irradiance_wm2 | cloud_cover_pct | temperature_2m_c |
|---|---|---|---|---|---|---|---|
| 2026-05-08T11:00:00+00:00 | cornwall | 580.0 | 750.0 | 180.0 | 670.0 | 30.0 | 14.5 |
| 2026-05-08T11:00:00+00:00 | kent | 620.0 | 770.0 | 195.0 | 720.0 | 25.0 | 16.0 |
| **2026-05-08T12:00:00+00:00** | **cornwall** | **700.0** | **770.0** | **200.0** | **770.0** | **25.0** | **15.8** |
| 2026-05-08T12:00:00+00:00 | kent | 720.0 | 800.0 | 210.0 | 790.0 | 20.0 | 17.0 |
| 2026-05-08T13:00:00+00:00 | cornwall | 720.0 | 780.0 | 200.0 | 790.0 | 20.0 | 16.6 |
| 2026-05-08T13:00:00+00:00 | east_anglia_norfolk | 680.0 | 760.0 | 215.0 | 740.0 | 35.0 | 17.5 |
| 2026-05-08T18:00:00+00:00 | cornwall | 95.0 | 280.0 | 60.0 | 110.0 | 40.0 | 13.0 |
| 2026-05-09T01:00:00+00:00 | cornwall | 0.0 | 0.0 | 0.0 | 0.0 | 55.0 | 9.2 |

**Sources:** First two rows from vault Bronze sample (cornwall + kent, captured 2026-05-08); remaining 6 rows synthesised respecting hourly diurnal arc (peak GTI ~770 W/m² at solar noon, zero overnight). The highlighted **Cornwall solar-noon row** (12:00 UTC) is a clear-sky south-coast peak — `global_tilted_irradiance_wm2 = 770` is the upper end of what UK fixed-tilt panels see. Overnight row (01:00) shows the zero-radiation pattern: all irradiance columns 0.0 (not null), cloud cover and temperature still populated. `cloud_cover_pct` is the renamed-with-`_pct` form (vault still says `cloud_cover`).

# GB capacity-weighted solar sites (location codelist)

The 6 sites are GW-capacity-weighted hotspots, chosen per ADR-020 to approximate GB-aggregate PV output. All sites are below 53° N (south-east bias matches actual UK solar deployment).

| Site key | Location | Approx coords | Notes |
|---|---|---|---|
| `cornwall` | Cornwall / SW England | 50.30, -5.00 | South-west, highest annual sunshine |
| `wiltshire_somerset` | Wiltshire / Somerset | 51.20, -2.50 | South-west inland |
| `oxfordshire` | Oxfordshire | 51.75, -1.25 | South-central |
| `sussex` | Sussex / South coast | 50.95, -0.10 | South coast |
| `kent` | Kent / SE England | 51.20, 0.70 | South-east |
| `east_anglia_norfolk` | East Anglia / Norfolk | 52.62, 1.05 | East coast, highest-latitude in set |

For tracker installations, GTI underestimates — use DNI plus a tracker-specific transposition. For GB-aggregate forecast, weight by installed PV capacity per region.

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={vars}&tilt=35&azimuth=180&forecast_days={1..16}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/forecast_solar__<location>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore**)
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
       max(global_tilted_irradiance_wm2) AS peak_gti_wm2,
       avg(cloud_cover_pct)              AS avg_cloud_pct
FROM read_parquet('data/silver/open_meteo/forecast_solar/**/*.parquet')
WHERE timestamp_utc >= current_date
  AND timestamp_utc <  current_date + INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 2, 1;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/forecast_solar/**/*.parquet")
# GB-aggregate hourly GTI (equal-weight mean across 6 sites for illustration)
gb = (
    df.group_by("timestamp_utc")
      .agg(
          pl.col("global_tilted_irradiance_wm2").mean().alias("gb_avg_gti_wm2"),
          pl.col("cloud_cover_pct").mean().alias("gb_avg_cloud_pct"),
      )
      .sort("timestamp_utc")
)
print(gb.tail(24))
```

# Caveats

## 01 No `forecast_run_at` — cross-vintage backtests need the archive

Dedup keeps the last silver row per `(timestamp_utc, location)`, overwriting prior forecast vintages on re-ingest. Vintage-vs-vintage forecast-skill analysis is not possible; pair against `historical_solar` at matching lead times. *(Source: vault Known Issues + `silver/openmeteo/historical.py L217`.)*

## 02 Silver column names are unit-suffixed (F15-B)

Silver emits `shortwave_radiation_wm2`, `direct_normal_irradiance_wm2`, `global_tilted_irradiance_wm2`, `temperature_2m_c`, `cloud_cover_pct`, etc. — vault Silver Schema lists pre-rename names. *(Source: `silver/openmeteo/historical.py L101-134` + `_output_columns` L255-271.)*

## 03 GTI requires `tilt` and `azimuth` (UK fixed-tilt 35°/180°)

The connector injects `tilt=35&azimuth=180` via `WeatherDatasetSpec.extra_params` for the UK representative geometry (latitude ~−15°, due south). Tracker installations need DNI plus a tracker-specific transposition model. *(Source: `connectors/openmeteo/endpoints.py L157-160`.)*

## 04 No `air_density_kg_m3` on this dataset (unlike forecast_wind)

The solar variable list omits `surface_pressure`, so `BaseOpenMeteoTransformer.DERIVE_AIR_DENSITY` cannot run; the column is absent. Property test `tests/unit/test_openmeteo_air_density.py` locks the contract. *(Source: `silver/openmeteo/historical.py L241-252` + test file.)*

## 05 No NWP-model pinning — irradiance skill varies by model

Open-Meteo's `/forecast` router selects an NWP model per request; irradiance forecast skill differs materially between ECMWF / GFS / ICON. Pin via `&models=<id>` for reproducibility. *(Source: vault `forecast_solar.md` Known Issues "Unpinned NWP model".)*

## 06 Bronze path uses DOUBLE underscore separator

Bronze partitions are `bronze/open_meteo/forecast_solar__<site>/<year>/...` — double underscore between dataset key and site name. Silver `BRONZE_DATASET_PREFIX = "forecast_solar"` strips it on read. *(Source: `connectors/openmeteo/client.py L112` + `silver/openmeteo/historical.py L142`.)*

# Related datasets

- **`historical_solar`** (Open-Meteo) — Archive companion at `archive-api.open-meteo.com/v1/archive`; chip `hourly` — same site list, same variables, same tilt geometry. Pair with this dataset for forecast-skill backtests at matching lead times. *open-meteo · weather · hourly*
- **`forecast_wind`** (Open-Meteo) — Hourly wind-forecast feed at 12 GB wind sites; chip `hourly` — companion renewable forecast on the same `/forecast` host; includes `air_density_kg_m3` derivation absent here. *open-meteo · weather · hourly*
- **`fuelhh`** (Elexon) — GB generation by fuel type (`SOLAR` is one of 16 codes); chip `30 min` — downstream actuals to validate forecasts against. Standard PV-skill workflow: forecast GTI → predict PV MW → compare against `fuelhh` `SOLAR` outturn. *elexon · generation · 30 min*
- **`carbon_intensity`** (NESO) — GB grid carbon intensity; chip `30 min` — combine with forecast for "expected clean generation × carbon intensity" carbon-aware scheduling. *neso · carbon · 30 min*
