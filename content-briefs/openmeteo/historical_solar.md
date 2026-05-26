---
slug: historical_solar
vendor: openmeteo
vendor_label: Open-Meteo
api_code: archive
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/historical_solar.md
  - gridflow/src/gridflow/schemas/weather.py::SolarWeather (lines 104-126, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalSolarWeather (lines 310-325) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134); registered L337
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (SOLAR_LOCATIONS L86-93, SOLAR_HOURLY_VARS L139-152, _SOLAR_GTI_PARAMS L157-160, DATASET_SPECS["historical_solar"] L176-179, ARCHIVE_BASE_URL L188)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94)
  - gridflow/tests/unit/test_openmeteo_air_density.py (asserts solar transformer omits air_density_kg_m3)
  - gridflow/tests/unit/test_openmeteo_irradiance_components.py (asserts direct_radiation + diffuse_radiation ≈ shortwave_radiation within 5% for daylight rows)
  - https://open-meteo.com/en/docs/historical-weather-api (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (historical_solar.md L163-182) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `shortwave_radiation`, `direct_radiation`, `direct_normal_irradiance`, `diffuse_radiation`, `global_tilted_irradiance`, `cloud_cover[_low/mid/high]`, `snowfall`, `snow_depth`."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names: `temperature_2m_c`, `shortwave_radiation_wm2`, `direct_radiation_wm2`, `direct_normal_irradiance_wm2`, `diffuse_radiation_wm2`, `global_tilted_irradiance_wm2`, `cloud_cover[_low/mid/high]_pct`, `snowfall_cm`, `snow_depth_m`."
    orchestrator_recommendation: "trust gridflow — F15-B canonical-schema rename is the SoT. Brief uses suffixed names."
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

**Tagline:** GB solar archive, <span class="italic fg-accent">ERA5 since 1940.</span>

**Lede:** Hourly ERA5-reanalysis irradiance (GHI/DNI/DHI/GTI) at 6 GB capacity-weighted solar sites — the canonical multi-decade backtest input for PV-generation calibration and clear-sky regime studies.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /archive](https://open-meteo.com/en/docs/historical-weather-api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.historical_solar` |
| API PATH | `/v1/archive` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~5 days (ERA5 reanalysis cadence) |
| VOLUME | 6 sites × 24 rows / day (≈ 53k / year) |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Observation cadence |
| 2 | 1940 | ERA5 depth (start year) |
| 3 | 6 | GB capacity-weighted sites |
| 4 | 16 | Schema columns |

# Sidebar siblings

- forecast_solar
- historical_wind
- historical_demand
- forecast_wind
- forecast_demand

# Sample chart

- **Type:** `sparkline`
- **Title:** "Cornwall `global_tilted_irradiance_wm2` · annual cycle"
- **Subtitle:** "Sparkline · W/m² · daily mean · UTC · 2025"
- **Seed:** 53
- **Toggles:** `1y` (active) / `5y` / `10y`

# Schema

Defined in `gridflow/schemas/weather.py` · `SolarWeather` (lines 104-126, subclass of `_BaseWeather` L23). Silver parquet uses **F15-B canonical names** (unit-suffix rename in `BaseOpenMeteoTransformer._PURE_RENAMES`, `silver/openmeteo/historical.py L101-134`) — vault tables predate the rename. Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` from `BaseSilverTransformer` (F0); ERA5 values are stable. **No `air_density_kg_m3`** — solar variable list omits `surface_pressure`; property test `tests/unit/test_openmeteo_air_density.py` locks the contract.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied. Hourly cadence. Validator requires tzinfo. | `schemas/weather.py L26, L34-39` |
| `location` | `str` | No | _derived_ | Site key from `SOLAR_LOCATIONS` — one of `east_anglia_norfolk` / `wiltshire_somerset` / `kent` / `cornwall` / `sussex` / `oxfordshire`. | `connectors/openmeteo/endpoints.py L86-93` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees (ERA5 snaps to grid cell). | `schemas/weather.py L29` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Surface air temperature at 2 m, °C — drives module-temperature derate. | `schemas/weather.py L112`; rename `silver/openmeteo/historical.py L111` |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | **GHI** (Global Horizontal Irradiance), W/m². | `schemas/weather.py L114`; rename L119 |
| `direct_radiation_wm2` | `float` | Yes | `hourly.direct_radiation[i]` | Beam component on horizontal surface, W/m². Sums with diffuse ≈ GHI (property test). | `schemas/weather.py L115`; rename L120 |
| `direct_normal_irradiance_wm2` | `float` | Yes | `hourly.direct_normal_irradiance[i]` | **DNI** — beam normal to the sun, W/m². Use for tracker-mounted PV. | `schemas/weather.py L116`; rename L121 |
| `diffuse_radiation_wm2` | `float` | Yes | `hourly.diffuse_radiation[i]` | **DHI** (Diffuse Horizontal Irradiance), W/m². | `schemas/weather.py L117`; rename L122 |
| `global_tilted_irradiance_wm2` | `float` | Yes | `hourly.global_tilted_irradiance[i]` | **GTI** on UK fixed-tilt geometry (`tilt=35°`, `azimuth=180°`). Most direct feature for UK fixed-tilt PV. W/m². | `schemas/weather.py L118`; rename L123; `endpoints.py L157-160` (extra_params) |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | Total cloud cover, %. | `schemas/weather.py L120`; rename L115 |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | Low-altitude cloud cover, %. | `schemas/weather.py L121`; rename L116 |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | Mid-altitude cloud cover, %. | `schemas/weather.py L122`; rename L117 |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | High-altitude cloud cover, %. | `schemas/weather.py L123`; rename L118 |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm. | `schemas/weather.py L125`; rename L125 |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m. Flags PV yield-collapse windows. | `schemas/weather.py L126`; rename L126 |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"`).

**PARQUET PATH:** `data/silver/open_meteo/historical_solar/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (ERA5 values are stable)

# Sample data

| timestamp_utc | location | shortwave_radiation_wm2 | direct_normal_irradiance_wm2 | diffuse_radiation_wm2 | global_tilted_irradiance_wm2 | cloud_cover_pct | temperature_2m_c | snow_depth_m |
|---|---|---|---|---|---|---|---|---|
| 2025-06-01T11:00:00+00:00 | cornwall | 620.0 | 780.0 | 190.0 | 710.0 | 25.0 | 16.3 | 0.0 |
| **2025-06-01T12:00:00+00:00** | **cornwall** | **750.0** | **800.0** | **210.0** | **820.0** | **20.0** | **17.8** | **0.0** |
| 2025-06-01T13:00:00+00:00 | cornwall | 780.0 | 810.0 | 215.0 | 845.0 | 15.0 | 18.6 | 0.0 |
| 2025-12-15T12:00:00+00:00 | east_anglia_norfolk | 95.0 | 60.0 | 83.0 | 175.0 | 90.0 | 4.5 | 0.01 |
| 2025-06-21T12:00:00+00:00 | kent | 810.0 | 830.0 | 220.0 | 880.0 | 10.0 | 22.0 | 0.0 |
| 2025-01-15T12:00:00+00:00 | wiltshire_somerset | 120.0 | 100.0 | 80.0 | 220.0 | 75.0 | 3.0 | 0.0 |
| 2025-08-15T15:00:00+00:00 | sussex | 540.0 | 700.0 | 175.0 | 590.0 | 35.0 | 23.0 | 0.0 |
| 2025-03-12T18:00:00+00:00 | oxfordshire | 80.0 | 250.0 | 50.0 | 95.0 | 50.0 | 9.5 | 0.0 |

**Sources:** First three Cornwall rows verbatim from vault Bronze sample (historical_solar.md L134-148, captured 2025-06-01 live snapshot). Norfolk winter row verbatim from vault Silver Sample (December noon under cloud — the mostly-diffuse regime). Remaining rows synthesised respecting Open-Meteo's separation model where `direct_radiation_wm2 + diffuse_radiation_wm2 ≈ shortwave_radiation_wm2` (property test `tests/unit/test_openmeteo_irradiance_components.py` enforces within 5%). The highlighted **Cornwall 2025-06-01 noon** row is the clear-sky south-west peak archetype: `global_tilted_irradiance_wm2 = 820` exceeds GHI = 750 because the 35° tilt captures more midday flux than horizontal. **Norfolk December noon (90 % cloud)** illustrates the inverse: DNI collapses to 60 W/m², DHI dominates GHI, GTI > GHI for the same tilt-vs-horizontal geometry reason. No `air_density_kg_m3` column — solar request omits `surface_pressure`.

# GB capacity-weighted solar sites (location codelist)

The 6 sites are GW-capacity-weighted hotspots, chosen per ADR-020 to approximate GB-aggregate PV output. All sites are below 53° N (south-east bias matches actual UK solar deployment — Glasgow at 55.9° N receives ~60 % of Cornwall's annual irradiance).

| Site key | Location | Approx coords | Notes |
|---|---|---|---|
| `cornwall` | Cornwall / SW England | 50.30, -5.00 | South-west, highest annual sunshine |
| `wiltshire_somerset` | Wiltshire / Somerset | 51.20, -2.50 | South-west inland |
| `oxfordshire` | Oxfordshire | 51.75, -1.25 | South-central |
| `sussex` | Sussex / South coast | 50.95, -0.10 | South coast |
| `kent` | Kent / SE England | 51.20, 0.70 | South-east |
| `east_anglia_norfolk` | East Anglia / Norfolk | 52.62, 1.05 | East coast, highest-latitude in set |

For GB-aggregate PV output, weight by installed solar MW per region rather than equally. ENTSO-E `actual_generation` `B16` is the EU-grid equivalent.

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&hourly={vars}&tilt=35&azimuth=180&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/historical_solar__<location>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore**)
- **TRANSFORMER**: `gridflow.silver.openmeteo.historical.HistoricalSolarWeather` (registered at `silver/openmeteo/historical.py L337`)

**Tab 1 — Example URL:**
```
https://archive-api.open-meteo.com/v1/archive
  ?latitude=50.30
  &longitude=-5.00
  &start_date=2025-06-01
  &end_date=2025-06-07
  &hourly=temperature_2m,shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance,cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,snowfall,snow_depth
  &tilt=35
  &azimuth=180
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Multi-year monthly GTI integral per site (PV-yield backtest backbone)
SELECT date_trunc('month', timestamp_utc) AS month,
       location,
       sum(global_tilted_irradiance_wm2) / 1000.0 AS gti_kwh_per_m2_per_month
FROM read_parquet('data/silver/open_meteo/historical_solar/**/*.parquet')
WHERE timestamp_utc >= TIMESTAMP '2020-01-01'
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/historical_solar/**/*.parquet")
# Clear-sky-index regression feature: GTI / (GTI on clear-sky equivalent)
# Approximate clear-sky GTI via the daylight max-quantile per (location, month, hour)
df2 = df.with_columns([
    pl.col("timestamp_utc").dt.month().alias("month"),
    pl.col("timestamp_utc").dt.hour().alias("hour_utc"),
])
clear_sky = (
    df2.group_by(["location", "month", "hour_utc"])
       .agg(pl.col("global_tilted_irradiance_wm2").quantile(0.95).alias("gti_clear"))
)
joined = df2.join(clear_sky, on=["location","month","hour_utc"]).with_columns(
    (pl.col("global_tilted_irradiance_wm2") / pl.col("gti_clear"))
      .clip(0.0, 1.5).alias("clear_sky_index")
)
print(joined.select(["timestamp_utc","location","clear_sky_index"]).tail(24))
```

# Caveats

## 01 ERA5 publication lag is ~5 days

Calls for `end_date` within the last 5 days may return 200 with null trailing values. For very recent past use `forecast_solar` with `past_days`. *(Source: vault `historical_solar.md` Known Issues "ERA5 reanalysis lag".)*

## 02 Silver column names are unit-suffixed (F15-B)

Silver emits `shortwave_radiation_wm2`, `direct_normal_irradiance_wm2`, `global_tilted_irradiance_wm2`, `temperature_2m_c`, `cloud_cover_pct`, etc. — vault Silver Schema lists pre-rename names. *(Source: `silver/openmeteo/historical.py L101-134` + `_output_columns` L255-271.)*

## 03 GTI requires `tilt` and `azimuth` (UK fixed-tilt 35°/180°)

The connector injects `tilt=35&azimuth=180` via `WeatherDatasetSpec.extra_params` for the UK representative geometry. Tracker installations underestimate at this fixed tilt — use DNI plus a tracker-specific transposition model. *(Source: `connectors/openmeteo/endpoints.py L157-160`.)*

## 04 No `air_density_kg_m3` on this dataset (unlike historical_wind/demand)

The solar variable list omits `surface_pressure`, so `BaseOpenMeteoTransformer.DERIVE_AIR_DENSITY` cannot run; the column is absent from silver output. Property test `tests/unit/test_openmeteo_air_density.py` locks the contract. *(Source: `silver/openmeteo/historical.py L241-252` + test file.)*

## 05 GHI ≈ DNI·cos(z) + DHI invariant (separation-model passthrough)

Open-Meteo's separation model is upstream; silver does not re-derive components. Property test `tests/unit/test_openmeteo_irradiance_components.py` asserts `direct_radiation_wm2 + diffuse_radiation_wm2` is within 5 % of `shortwave_radiation_wm2` for daylight rows. *(Source: vault Working curl example verification + test file.)*

## 06 Latitude bias — all 6 sites below 53° N

The location set is deliberately south-eastern (matching actual UK PV deployment); averaging against northern demand locations like Glasgow gives biased aggregate irradiance. Weight by installed MW per region for GB aggregates. *(Source: vault `historical_solar.md` Known Issues "Latitude bias".)*

# Related datasets

- **`forecast_solar`** (Open-Meteo) — Forecast companion at `api.open-meteo.com/v1/forecast`; chip `hourly` — same 6 sites, same variables, same tilt geometry, 1-16 day forward horizon. Pair for forecast-skill bias-correction. *open-meteo · weather · hourly*
- **`historical_wind`** (Open-Meteo) — Archive companion at the same host for 12 GB wind sites; chip `hourly` — the other renewables-side ERA5 feed; includes `air_density_kg_m3` absent here. *open-meteo · weather · hourly*
- **`fuelhh`** (Elexon) — GB generation by fuel type (`SOLAR` field — embedded estimate); chip `30 min` — downstream actuals for multi-year PV capacity-factor calibration. *elexon · generation · 30 min*
- **`actual_generation`** (ENTSO-E) — European generation by PSR type (`B16` = Solar); chip `15-60 min` — the EU-grid equivalent of GB `fuelhh.SOLAR`; cross-vendor solar-weather coupling at EU scale. *entsoe · generation · 15-60 min*
