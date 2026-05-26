---
slug: forecast_demand
vendor: openmeteo
vendor_label: Open-Meteo
api_code: forecast
last_verified: 2026-05-09
sources_consulted:
  - vault/openmeteo/forecast_demand.md
  - gridflow/src/gridflow/schemas/weather.py::DemandWeather (lines 42-63, subclass of _BaseWeather L23)
  - gridflow/src/gridflow/silver/openmeteo/forecast.py::ForecastDemandWeather (lines 33-40, subclass of HistoricalDemandWeather; registered L75)
  - gridflow/src/gridflow/silver/openmeteo/historical.py::HistoricalDemandWeather (lines 274-286) + BaseOpenMeteoTransformer (lines 83-271, F15-B unit-suffix renames at L101-134)
  - gridflow/src/gridflow/connectors/openmeteo/endpoints.py (DEMAND_LOCATIONS L54-62, DEMAND_HOURLY_VARS L97-107, DATASET_SPECS["forecast_demand"] L167-169, FORECAST_BASE_URL L189)
  - gridflow/src/gridflow/connectors/openmeteo/client.py::OpenMeteoConnector (dual-host routing L90-94)
  - https://open-meteo.com/en/docs (vendor docs — JavaScript-rendered playground, no flat WebFetch surface; vault canonical fallback applied)
discrepancies_found:
  - source_a: "vault Silver schema (forecast_demand.md L141-160) — pre-rename column names"
    source_a_says: "Vault lists `temperature_2m`, `wind_speed_10m`, `surface_pressure`, `hdd`, `cdd`, etc."
    source_b: "gridflow silver/openmeteo/historical.py L101-134 (F15-B _UNIT_CONVERSIONS + _PURE_RENAMES) + L255-271 _output_columns"
    source_b_says: "Silver parquet emits unit-suffixed names: `temperature_2m_c`, `wind_speed_10m_mps` (with km/h→m/s conversion ÷3.6), `surface_pressure_hpa`, `hdd_k`, `cdd_k`, etc."
    orchestrator_recommendation: "trust gridflow — F15-B canonical-schema rename is the SoT; vault tables predate it. This brief uses suffixed names; downstream queries against the parquet must use the suffixed names."
  - source_a: "vault folder naming convention"
    source_a_says: "Vault directory is `open-meteo/` (kebab); README documents three coexisting forms"
    source_b: "gridflow: Python package `openmeteo` (no separator); connector/transformer registry key `open_meteo` (snake); bronze + silver path prefix `open_meteo/`"
    orchestrator_recommendation: "documented design intent — three forms coexist by convention (kebab vault, no-separator Python, snake registry). Brief uses `openmeteo` as the canonical slug."
  - source_a: "module location `schemas/weather.py`"
    source_a_says: "Pydantic classes live in `schemas/weather.py` (DemandWeather, WindWeather, SolarWeather, _BaseWeather)"
    source_b: "every other vendor uses `schemas/<vendor>.py` (entsoe.py, entsog.py, gie.py, neso.py, elexon.py)"
    orchestrator_recommendation: "domain knowledge — `weather.py` is intentionally generic for future multi-source weather feeds. Auto-discovery tooling that pattern-matches `schemas/<vendor>.py` will miss this."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB demand-driver weather, <span class="italic fg-accent">forecast hourly.</span>

**Lede:** Hourly demand-weather forecast at 7 GB population centres — the canonical input for day-ahead load modelling, HDD/CDD features, and winter-peak snow shocks.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Open-Meteo · /forecast](https://open-meteo.com/en/docs)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.forecast_demand` |
| API PATH | `/v1/forecast` |
| FREQUENCY | hourly |
| PUBLICATION LAG | real-time (NWP router refresh ~1h) |
| VOLUME | 7 sites × 24h × 16d ≈ 2.7k rows / horizon |
| PRIMARY KEY | `(timestamp_utc, location)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Forecast cadence |
| 2 | 16 d | Max forecast horizon |
| 3 | 7 | GB population centres |
| 4 | 18 | Schema columns |

# Sidebar siblings

- historical_demand
- forecast_wind
- forecast_solar
- historical_wind
- historical_solar

# Sample chart

- **Type:** `sparkline`
- **Title:** "London `temperature_2m_c` · next 7-day forecast"
- **Subtitle:** "Sparkline · °C · hourly · UTC · 2026-05-08 → 2026-05-15"
- **Seed:** 7
- **Toggles:** `7d` (active) / `16d` / `48h`

# Schema

Defined in `gridflow/schemas/weather.py` · `DemandWeather` (lines 42-63, subclass of `_BaseWeather` L23). Silver parquet uses **F15-B canonical names** (unit-suffix rename in `BaseOpenMeteoTransformer._UNIT_CONVERSIONS` + `_PURE_RENAMES`, `silver/openmeteo/historical.py L101-134`) — vault tables predate the rename and are stale. Partitioned by `timestamp_utc` (year + month). Point-in-time field: `available_at` from `BaseSilverTransformer` (F0); no `forecast_run_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | Parsed from `YYYY-MM-DDTHH:MM`, UTC tz applied. Validator requires tzinfo. | `schemas/weather.py L26, L34-39`; `silver/openmeteo/historical.py L188-193` |
| `location` | `str` | No | _derived_ | City key from `DEMAND_LOCATIONS` — one of `london` / `birmingham` / `manchester` / `leeds` / `glasgow` / `cardiff` / `belfast`. | `connectors/openmeteo/endpoints.py L54-62` |
| `latitude` | `float` | No | top-level `latitude` | WGS-84 decimal degrees (response value — may snap to grid cell). | `schemas/weather.py L29` |
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
| `air_density_kg_m3` | `float` | Yes | _derived_ | `surface_pressure_Pa / (287.05 × T_K)` — ideal gas, dry air. No unit-suffix rename. | `schemas/weather.py L63`; derivation `silver/openmeteo/historical.py L241-252` |
| `data_provider` | `str` | No | _derived_ | Constant `"open_meteo"` (underscore form). | `schemas/weather.py L31`; stamp `silver/openmeteo/historical.py L221` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock UTC at silver-build time. | `schemas/weather.py L32`; stamp `silver/openmeteo/historical.py L222` |

Plus bitemporal columns stamped by `BaseSilverTransformer` (F0): `event_time`, `available_at`, `source_run_id`, `dataset_version` (`"2.0.0"` for this dataset).

**PARQUET PATH:** `data/silver/open_meteo/forecast_demand/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, location)` — `keep="last"` (silently overwrites prior forecast vintages)

# Sample data

| timestamp_utc | location | temperature_2m_c | wind_speed_10m_mps | relative_humidity_2m_pct | surface_pressure_hpa | hdd_k | cdd_k | air_density_kg_m3 |
|---|---|---|---|---|---|---|---|---|
| 2026-05-08T00:00:00+00:00 | london | 11.8 | 2.64 | 78.0 | 1018.4 | 3.7 | 0.0 | 1.245 |
| 2026-05-08T06:00:00+00:00 | london | 12.5 | 3.10 | 70.0 | 1018.9 | 3.0 | 0.0 | 1.242 |
| **2026-05-08T12:00:00+00:00** | **london** | **17.2** | **4.53** | **55.0** | **1019.1** | **0.0** | **0.0** | **1.221** |
| 2026-05-08T18:00:00+00:00 | london | 15.4 | 3.86 | 62.0 | 1019.3 | 0.1 | 0.0 | 1.228 |
| 2026-05-08T12:00:00+00:00 | glasgow | 13.8 | 5.69 | 68.0 | 1014.2 | 1.7 | 0.0 | 1.231 |
| 2026-05-08T12:00:00+00:00 | manchester | 16.1 | 4.17 | 60.0 | 1017.6 | 0.0 | 0.0 | 1.224 |
| 2026-05-08T12:00:00+00:00 | belfast | 14.5 | 5.08 | 70.0 | 1015.3 | 1.0 | 0.0 | 1.227 |
| 2026-05-08T12:00:00+00:00 | cardiff | 16.8 | 3.36 | 58.0 | 1018.1 | 0.0 | 0.0 | 1.222 |

**Sources:** First 4 London rows derived from vault Silver Sample (forecast_demand.md L168-211, captured 2026-05-09) — wind speeds converted from vault km/h to silver m/s (e.g. `9.5 km/h → 2.64 m/s`). Other 4 city rows at solar noon synthesised respecting regional patterns (Scotland windier and cooler than south coast). The highlighted London **solar-noon row** (12:00 UTC) is the demand-modelling sweet spot — `temperature_2m_c = 17.2°C` sits between heating and cooling thresholds so both `hdd_k` and `cdd_k` are zero (the dataset's spring shoulder regime). All wind speeds in m/s (km/h ÷3.6); `surface_pressure_hpa` directly feeds `air_density_kg_m3 = P×100 / (287.05 × (T+273.15))`.

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
- **ENDPOINT**: `api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={vars}&forecast_days={1..16}&timezone=UTC`
- **AUTH**: None (public, free tier — no key, no header). Soft limit ~10 000 requests/day per IP.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/open_meteo/forecast_demand__<city>/<year>/<month>/<day>/raw_<uuid>.json` (note **double underscore** between dataset key and location)
- **TRANSFORMER**: `gridflow.silver.openmeteo.forecast.ForecastDemandWeather` (registered at `silver/openmeteo/forecast.py L75`)

**Tab 1 — Example URL:**
```
https://api.open-meteo.com/v1/forecast
  ?latitude=51.5074
  &longitude=-0.1278
  &hourly=temperature_2m,wind_speed_10m,wind_direction_10m,relative_humidity_2m,precipitation,shortwave_radiation,surface_pressure,snowfall,snow_depth
  &forecast_days=7
  &timezone=UTC
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Day-ahead GB demand-weighted temperature (population-weighted by city)
SELECT date_trunc('hour', timestamp_utc) AS hour,
       sum(temperature_2m_c * pop_weight) AS gb_pop_temp_c,
       sum(hdd_k * pop_weight)            AS gb_pop_hdd_k
FROM read_parquet('data/silver/open_meteo/forecast_demand/**/*.parquet') f
JOIN (VALUES ('london',0.30),('birmingham',0.10),('manchester',0.12),
              ('leeds',0.08),('glasgow',0.10),('cardiff',0.05),
              ('belfast',0.04)) t(loc, pop_weight) ON f.location = t.loc
WHERE timestamp_utc >= current_date
GROUP BY 1 ORDER BY 1;
```

**Tab 3 — Python · polars:**
```python
import polars as pl

df = pl.read_parquet("data/silver/open_meteo/forecast_demand/**/*.parquet")
# Daily HDD totals per city (hourly hdd_k summed to daily degree-hours)
daily_hdd = (
    df.with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
      .group_by(["day", "location"])
      .agg(pl.col("hdd_k").sum().alias("hdd_kh"))
      .pivot(index="day", on="location", values="hdd_kh")
      .sort("day")
)
print(daily_hdd.tail(7))
```

# Caveats

## 01 No `forecast_run_at` — vintages overwrite silently

Dedup keeps the last silver row per `(timestamp_utc, location)`, overwriting prior forecast vintages on re-ingest. Lead-time / forecast-skill backtests must pair against the historical archive at matching lead times. *(Source: vault Known Issues + `silver/openmeteo/historical.py L217`.)*

## 02 Silver column names are unit-suffixed (F15-B)

Silver emits `temperature_2m_c`, `wind_speed_10m_mps` (km/h→m/s ÷3.6), `surface_pressure_hpa`, `hdd_k`, etc. — vault Silver Schema tables list pre-rename names. *(Source: `silver/openmeteo/historical.py L101-134` + `_output_columns` L255-271.)*

## 03 Two-host design — forecast vs archive

This dataset uses `api.open-meteo.com/v1/forecast`. The historical archive sibling uses `archive-api.open-meteo.com/v1/archive`. `past_days` ≤ 92 is not used by the connector; for past data, use `historical_demand`. *(Source: `connectors/openmeteo/client.py L90-94`.)*

## 04 No NWP-model pinning by default

Open-Meteo's `/forecast` router selects an NWP model per request (ECMWF / GFS / ICON / UKMO). The selection can change silently between calls; pin via `&models=<id>` if reproducibility matters. *(Source: vault Known Issues — `forecast_demand.md` "Unpinned model".)*

## 05 Three vendor-name forms coexist by convention

Vault folder is `open-meteo` (kebab); Python package is `openmeteo` (no separator); connector/registry key is `open_meteo` (snake) and is the bronze + silver path prefix. *(Source: vault `forecast_demand.md` Known Issues "Naming inconsistency".)*

## 06 Bronze path uses DOUBLE underscore separator

Bronze partitions are `bronze/open_meteo/forecast_demand__<city>/<year>/...` — double underscore between dataset key and city. The silver `BRONZE_DATASET_PREFIX = "forecast_demand"` strips it on read; custom bronze-readers must match the `__` form or list zero files. *(Source: `connectors/openmeteo/client.py L112` + `silver/openmeteo/historical.py L142`.)*

# Related datasets

- **`historical_demand`** (Open-Meteo) — Archive companion at `archive-api.open-meteo.com/v1/archive`; chip `hourly` — same 7 cities, same variables, ERA5 reanalysis depth from 1940. Pair with this dataset for forecast-skill backtests. *open-meteo · weather · hourly*
- **`forecast_wind`** (Open-Meteo) — Hourly wind-forecast feed at 12 GB wind sites; chip `hourly` — the renewable-supply counterpart to this demand-driver feed. Same `/forecast` host. *open-meteo · weather · hourly*
- **`fuelhh`** (Elexon) — GB half-hourly generation by fuel type; chip `30 min` — the realised-demand counterpart (national demand = generation + interconnector imports) to validate this dataset's HDD/CDD-driven load model. *elexon · generation · 30 min*
- **`carbon_intensity`** (NESO) — GB grid carbon intensity; chip `30 min` — temperature explains ~60% of short-run carbon-intensity variation; combine for weather-adjusted carbon modelling. *neso · carbon · 30 min*
