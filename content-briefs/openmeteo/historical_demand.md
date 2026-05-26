---
slug: historical_demand
vendor: openmeteo
vendor_label: Open-Meteo
api_code: archive
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/historical_demand.md
  - gridflow/src/gridflow/schemas/weather.py::DemandWeather (lines 42-63, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalDemandWeather (lines 274-286) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134); registered L335
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (DEMAND_LOCATIONS L54-62, DEMAND_HOURLY_VARS L97-107, DATASET_SPECS["historical_demand"] L164-166, ARCHIVE_BASE_URL L188)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94 — `dataset.startswith("historical")` → ARCHIVE_BASE_URL)
  - https://open-meteo.com/en/docs/historical-weather-api (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (historical_demand.md L142-161) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `wind_speed_10m` (km/h), `surface_pressure`, `hdd`, `cdd`, etc."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names with km/h→m/s conversion: `temperature_2m_c`, `wind_speed_10m_mps` (÷3.6), `surface_pressure_hpa`, `hdd_k`, `cdd_k`, etc."
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

**Tagline:** GB demand-driver weather, <span class="italic fg-accent">ERA5 since 1940.</span>

**Lede:** Hourly ERA5-reanalysis weather at 7 GB population centres — the canonical multi-decade input for demand-model backtests, HDD/CDD calibration, and weather-adjusted load regression.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /archive](https://open-meteo.com/en/docs/historical-weather-api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.historical_demand` |
| API PATH | `/v1/archive` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~5 days (ERA5 reanalysis cadence) |
| VOLUME | 7 sites × 24 rows / day (≈ 60k / year) |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Observation cadence |
| 2 | 1940 | ERA5 depth (start year) |
| 3 | 7 | GB population centres |
| 4 | 18 | Schema columns |

# Sidebar siblings

- forecast_demand
- historical_wind
- historical_solar
- forecast_wind
- forecast_solar

# Sample chart

- **Type:** `heatmap`
- **Title:** "London `hdd_k` · hour-of-day × day-of-year"
- **Subtitle:** "Heatmap · degree-hours · UTC · 2025"
- **Seed:** 23
- **Toggles:** `1y` (active) / `5y` / `10y`

# Schema

Defined in `gridflow/schemas/weather.py` · `DemandWeather` (lines 42-63, subclass of `_BaseWeather` L23). Silver parquet uses **F15-B canonical names** (unit-suffix rename in `BaseOpenMeteoTransformer._UNIT_CONVERSIONS` + `_PURE_RENAMES`, `silver/openmeteo/historical.py L101-134`) — vault tables predate the rename. Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` from `BaseSilverTransformer` (F0); ERA5 archive values are stable once published.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied. Hourly cadence. Validator requires tzinfo. | `schemas/weather.py L26, L34-39` |
| `location` | `str` | No | _derived_ | City key from `DEMAND_LOCATIONS` — one of `london` / `birmingham` / `manchester` / `leeds` / `glasgow` / `cardiff` / `belfast`. | `connectors/openmeteo/endpoints.py L54-62` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees (response value — ERA5 snaps to grid cell). | `schemas/weather.py L29` |
| `longitude` | `float` | No | top-level `longitude` | WGS-84 decimal degrees. | `schemas/weather.py L29` |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Air temperature at 2 m, °C. Drives HDD/CDD derivation. | `schemas/weather.py L50`; rename `silver/openmeteo/historical.py L111` |
| `wind_speed_10m_mps` | `float` | Yes | `hourly.wind_speed_10m[i]` | Wind speed at 10 m, **m/s** (API km/h ÷3.6). | `schemas/weather.py L51`; conversion `silver/openmeteo/historical.py L102` |
| `wind_direction_10m_deg` | `float` | Yes | `hourly.wind_direction_10m[i]` | Wind direction at 10 m, degrees (0=N, 90=E). | `schemas/weather.py L52`; rename L127 |
| `relative_humidity_2m_pct` | `float` | Yes | `hourly.relative_humidity_2m[i]` | Relative humidity at 2 m, %. | `schemas/weather.py L53`; rename L114 |
| `precipitation_mm` | `float` | Yes | `hourly.precipitation[i]` | Hourly precipitation, mm. | `schemas/weather.py L54`; rename L124 |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | GHI, W/m². | `schemas/weather.py L55`; rename L119 |
| `surface_pressure_hpa` | `float` | Yes | `hourly.surface_pressure[i]` | Surface pressure, hPa. Feeds `air_density_kg_m3` derivation. | `schemas/weather.py L56`; rename L113 |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm. | `schemas/weather.py L57`; rename L125 |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m. | `schemas/weather.py L58`; rename L126 |
| `hdd_k` | `float` | Yes | _derived_ | `max(15.5 - temperature_2m_c, 0)` — heating degree-hours, base 15.5°C. Derived **before** rename so `_add_derived` reads pre-rename `temperature_2m`. | `schemas/weather.py L61`; derivation `silver/openmeteo/historical.py L231-239` |
| `cdd_k` | `float` | Yes | _derived_ | `max(temperature_2m_c - 22.0, 0)` — cooling degree-hours, base 22.0°C. | `schemas/weather.py L62`; same derivation block |
| `air_density_kg_m3` | `float` | Yes | _derived_ | `surface_pressure_Pa / (287.05 × T_K)` — ideal gas, dry air. No unit-suffix rename (name already carries units). | `schemas/weather.py L63`; derivation `silver/openmeteo/historical.py L241-252` |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32` |

Plus bitemporal columns from `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"`).

**PARQUET PATH:** `data/silver/open_meteo/historical_demand/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (ERA5 archive values are stable; revisions rare)

# Sample data

| timestamp_utc | location | temperature_2m_c | wind_speed_10m_mps | relative_humidity_2m_pct | surface_pressure_hpa | snowfall_cm | hdd_k | cdd_k | air_density_kg_m3 |
|---|---|---|---|---|---|---|---|---|---|
| **2025-01-15T00:00:00+00:00** | **london** | **-1.2** | **3.47** | **82.0** | **1015.2** | **0.5** | **16.7** | **0.0** | **1.30** |
| 2025-01-15T01:00:00+00:00 | london | -1.6 | 3.28 | 84.0 | 1015.0 | 0.8 | 17.1 | 0.0 | 1.30 |
| 2025-01-15T02:00:00+00:00 | london | -1.9 | 3.67 | 85.0 | 1014.8 | 0.3 | 17.4 | 0.0 | 1.30 |
| 2025-05-01T12:00:00+00:00 | london | 23.4 | 5.00 | 50.0 | 1015.5 | 0.0 | 0.0 | 1.4 | 1.19 |
| 2025-01-15T00:00:00+00:00 | glasgow | -3.5 | 4.72 | 88.0 | 1012.8 | 1.2 | 19.0 | 0.0 | 1.31 |
| 2025-07-15T14:00:00+00:00 | london | 28.6 | 4.17 | 42.0 | 1014.2 | 0.0 | 0.0 | 6.6 | 1.17 |
| 2025-12-25T08:00:00+00:00 | manchester | 2.1 | 6.39 | 90.0 | 1003.5 | 0.0 | 13.4 | 0.0 | 1.27 |
| 2025-08-01T16:00:00+00:00 | belfast | 19.8 | 4.44 | 60.0 | 1019.5 | 0.0 | 0.0 | 0.0 | 1.21 |

**Sources:** First 4 rows (London winter + spring) verbatim from vault Silver Sample (historical_demand.md L171-211, captured 2026-05-09) — wind speeds converted from vault km/h to silver m/s (`12.5 km/h → 3.47 m/s`). Remaining rows synthesised respecting ERA5 grid-realistic GB-climate ranges. The highlighted **London 2025-01-15 midnight** row is the winter-peak demand archetype: `temperature_2m_c = -1.2°C` with light snow → `hdd_k = 16.7` (heating degree-hours = 15.5 - (-1.2)), `air_density_kg_m3 = 1.30` (cold air is denser). The 2025-07-15 14:00 London row shows the inverse summer regime: `cdd_k = 6.6` and density down to 1.17. `surface_pressure_hpa` feeds the `air_density_kg_m3` derivation directly via the ideal-gas law.

# GB demand population centres (location codelist)

The 7 cities are population-weighted hotspots (not equal-weighted), preserved from F0 and used by gridflow's demand model.

| Site key | City | Approx coords | Region |
|---|---|---|---|
| `london` | London | 51.51, -0.13 | South-east (largest demand sink) |
| `birmingham` | Birmingham | 52.49, -1.89 | Midlands |
| `manchester` | Manchester | 53.48, -2.24 | North-west |
| `leeds` | Leeds | 53.80, -1.55 | North-east |
| `glasgow` | Glasgow | 55.86, -4.25 | Scotland |
| `cardiff` | Cardiff | 51.48, -3.18 | Wales |
| `belfast` | Belfast | 54.60, -5.93 | Northern Ireland |

For GB-aggregate demand, weight by population (or by national-demand share per region) rather than equally.

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={YYYY-MM-DD}&end_date={YYYY-MM-DD}&hourly={vars}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/historical_demand__<city>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore** between dataset key and city)
- **TRANSFORMER**: `gridflow.silver.openmeteo.historical.HistoricalDemandWeather` (registered at `silver/openmeteo/historical.py L335`)

**Tab 1 — Example URL:**
```
https://archive-api.open-meteo.com/v1/archive
  ?latitude=51.5074
  &longitude=-0.1278
  &start_date=2025-01-01
  &end_date=2025-01-31
  &hourly=temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m,precipitation,shortwave_radiation,surface_pressure,snowfall,snow_depth
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Multi-year monthly HDD totals per city (multi-decade backtest backbone)
SELECT date_trunc('month', timestamp_utc) AS month,
       location,
       sum(hdd_k) AS hdd_kh,
       sum(cdd_k) AS cdd_kh
FROM read_parquet('data/silver/open_meteo/historical_demand/**/*.parquet')
WHERE timestamp_utc >= TIMESTAMP '2015-01-01'
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/historical_demand/**/*.parquet")
# Population-weighted GB-aggregate daily mean temperature (decade-scale)
gb_temp = (
    df.with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
      .group_by(["day", "location"])
      .agg(pl.col("temperature_2m_c").mean())
      .pivot(index="day", on="location", values="temperature_2m_c")
      .with_columns(
          (pl.col("london")*0.30 + pl.col("birmingham")*0.10
         + pl.col("manchester")*0.12 + pl.col("leeds")*0.08
         + pl.col("glasgow")*0.10 + pl.col("cardiff")*0.05
         + pl.col("belfast")*0.04).alias("gb_pop_temp_c")
      )
      .sort("day")
)
print(gb_temp.tail(7))
```

# Caveats

## 01 ERA5 publication lag is ~5 days

Calls for `end_date` within the last 5 days may return 200 with null trailing values — ERA5 reanalysis cadence is non-real-time by design. Plan backfills accordingly; for recent past use `forecast_demand` with `past_days` (≤92). *(Source: vault `historical_demand.md` Known Issues "ERA5 reanalysis lag".)*

## 02 Silver column names are unit-suffixed (F15-B)

Silver emits `temperature_2m_c`, `wind_speed_10m_mps` (km/h→m/s ÷3.6), `surface_pressure_hpa`, `hdd_k`, `cdd_k`, etc. — vault Silver Schema tables list pre-rename names. *(Source: `silver/openmeteo/historical.py L101-134` + `_output_columns` L255-271.)*

## 03 ERA5 grid-cell snapping

`latitude` / `longitude` echoed in the response can differ slightly from the request — ERA5 snaps to the nearest grid cell (~0.25° resolution). Silver stores the response values, not the request values; don't dedup on lat/lon. *(Source: vault `historical_demand.md` Known Issues "ERA5 grid-cell snapping".)*

## 04 Two-host design — archive lives at `archive-api.open-meteo.com`

The connector routes per `dataset.startswith("historical")` to `ARCHIVE_BASE_URL`, while `forecast_demand` uses `FORECAST_BASE_URL`. The `config/sources.yaml` `base_url` is only valid for forecast; the archive path is selected by the dataset-prefix conditional. *(Source: `connectors/openmeteo/client.py L90-94` + `endpoints.py L188-189`.)*

## 05 Three vendor-name forms coexist by convention

Vault folder is `open-meteo` (kebab); Python package is `openmeteo` (no separator); connector/registry key is `open_meteo` (snake) and is the bronze + silver path prefix. *(Source: vault `historical_demand.md` Known Issues "Naming inconsistency".)*

## 06 Bronze path uses DOUBLE underscore separator

Bronze partitions are `bronze/open_meteo/historical_demand__<city>/<year>/...` — double underscore between dataset key and city. Old F0 single-underscore `historical_<city>` paths are obsolete; existing F0 bronze must be re-keyed before re-ingest. *(Source: `connectors/openmeteo/client.py L112` + `silver/openmeteo/historical.py L142`.)*

# Related datasets

- **`forecast_demand`** (Open-Meteo) — Forecast companion at `api.open-meteo.com/v1/forecast`; chip `hourly` — same 7 cities, same variables, 1-16 day forward horizon. Pair for forecast-skill bias-correction. *open-meteo · weather · hourly*
- **`historical_wind`** (Open-Meteo) — Archive companion at the same host for 12 GB wind sites; chip `hourly` — the renewable-supply counterpart to this demand-driver feed. *open-meteo · weather · hourly*
- **`indo`** (Elexon) — GB initial demand outturn; chip `30 min` — the realised-demand counterpart to validate multi-year HDD/CDD-driven load models. Pair via weighted city-temperature features. *elexon · demand · 30 min*
- **`carbon_intensity`** (NESO) — GB grid carbon intensity; chip `30 min` — temperature explains ~60% of short-run carbon-intensity variation; pair for weather-adjusted carbon backtests. *neso · carbon · 30 min*
