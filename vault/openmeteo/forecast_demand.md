---
source: open_meteo
dataset_key: forecast_demand
vendor: Open-Meteo
last_verified: 2026-06-03
layer_coverage: bronze, silver
---

# Open-Meteo — Forecast Demand Weather (population centres, 1–16 days)

## Overview

Hourly weather forecast for the next 1–16 days at 7 GB population
centres (London, Birmingham, Manchester, Leeds, Glasgow, Cardiff,
Belfast). Taken from whichever NWP model the Open-Meteo router
currently selects (typically ECMWF, GFS, or ICON depending on grid cell
and lead time). Used as the forward-looking demand-weather feed —
temperature drives heating/cooling load, snow drives winter-peak load
shocks, derived air density feeds high-load adjustments. Same JSON
columnar response shape as [historical_demand](./historical_demand.md),
so silver shares parsing logic via `BaseOpenMeteoTransformer`.

→ This dataset answers: *what is the forecast temperature / wind /
radiation / snow at the 7 demand centres over the next N hours?* For
lookback / backtesting, use [historical_demand](./historical_demand.md)
(ERA5). For wind-site or solar-site forecasts, use
[forecast_wind](./forecast_wind.md) or
[forecast_solar](./forecast_solar.md).

`forecast_demand` is the F7.5 successor of the F0-era `forecast`
dataset; `DATASET_VERSION` bumped 1.0.0 → 2.0.0.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://api.open-meteo.com/v1` (different host from [historical_demand](./historical_demand.md), which uses `archive-api.open-meteo.com`) |
| Path             | `/forecast` |
| Method           | GET |
| Auth             | None (public, free tier — no key, no header) |
| Rate limit       | Soft limit ~10 000 requests/day per IP (vendor-published, free tier); ~600/min burst. Project caps at 5 req/s in `config/sources.yaml`. |
| Pagination       | None — chunk via `start_date` / `end_date` (or `forecast_days`) |
| Historical depth | Forward-looking only — supports `past_days` to stitch up to ~92 days of recent past, but the canonical path for past data is the [archive endpoint](./historical_demand.md) |
| Publication lag  | Real-time — current run typically refreshed every ~1 hour by the upstream NWP router |
| Response format  | JSON (columnar — one parallel array per variable) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `51.5074` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `-0.1278` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests 9 fields | `temperature_2m,wind_speed_10m,...` |
| `forecast_days` | int | No | Number of forecast days (default 7, max 16) | `2` |
| `past_days` | int | No | Number of past days to include (max ~92) — connector does not use | `0` |
| `start_date` | date | No | Window start; gridflow uses this rather than `forecast_days` | `2026-05-08` |
| `end_date` | date | No | Window end; gridflow uses this | `2026-05-09` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |
| `models` | csv string | No | Pin a specific NWP model — connector does not pin | `ecmwf_ifs025` |

Connector requests these `hourly` variables (`endpoints.DEMAND_HOURLY_VARS`):
`temperature_2m`, `wind_speed_10m`, `wind_direction_10m`,
`relative_humidity_2m`, `precipitation`, `shortwave_radiation`,
`surface_pressure`, `snowfall`, `snow_depth`.

### Working curl example

```bash
# No auth required
curl --ssl-no-revoke -fsS \
  "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&hourly=temperature_2m,wind_speed_10m,shortwave_radiation,snowfall,snow_depth&forecast_days=2"
```

Verified 2026-05-08 (V1 plan F): HTTP 200, 48 hourly time entries
(2 days × 24 hours), London. Variable list matches F7.5 demand set.

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/forecast_demand__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the seven `DEMAND_LOCATIONS` per call and emits one `RawResponse` per
city. The `dataset` field on each `RawResponse` is
`f"forecast_demand__{location.name}"` (**double underscore**), so bronze
partitions live under `bronze/open_meteo/forecast_demand__<city>/...`.
The silver transformer's `BRONZE_DATASET_PREFIX` is `"forecast_demand"`;
its `read_bronze` re-aggregates the per-city sibling directories.

### Bronze sample

```json
{
  "latitude": 51.5,
  "longitude": -0.10000038,
  "generationtime_ms": 0.0717,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 23.0,
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "wind_speed_10m": "km/h",
    "shortwave_radiation": "W/m²",
    "snowfall": "cm",
    "snow_depth": "m"
  },
  "hourly": {
    "time": [
      "2026-05-08T00:00", "2026-05-08T01:00", "2026-05-08T02:00"
    ],
    "temperature_2m": [11.8, 11.1, 10.7],
    "wind_speed_10m": [9.5, 8.2, 7.6],
    "shortwave_radiation": [0.0, 0.0, 0.0],
    "snowfall": [0.0, 0.0, 0.0],
    "snow_depth": [0.0, 0.0, 0.0]
  }
}
```

(Live-shaped response, truncated to selected fields — the full 9-variable
connector request adds `wind_direction_10m`, `relative_humidity_2m`,
`precipitation`, `surface_pressure`.)

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/forecast_demand/year=YYYY/month=MM/forecast_demand_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.forecast.ForecastDemandWeather`
**Pydantic schema**: `gridflow.schemas.weather.DemandWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0). No `forecast_run_at`; older vintages overwritten on re-ingest.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | Parsed from `YYYY-MM-DDTHH:MM` (ISO8601 without tz suffix), UTC tz applied |
| `location` | `str` | No | derived | City name from `DEMAND_LOCATIONS` (london, birmingham, ...) |
| `latitude` | `float` | No | top-level `latitude` | Float64; matches request lat (Open-Meteo may snap to nearest grid cell) |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | Air temperature 2 m above ground, °C |
| `wind_speed_10m_mps` | `float` | Yes | `hourly.wind_speed_10m[i]` | Wind speed 10 m above ground, m/s |
| `wind_direction_10m_deg` | `float` | Yes | `hourly.wind_direction_10m[i]` | Wind direction 10 m, degrees (0=N, 90=E) |
| `relative_humidity_2m_pct` | `float` | Yes | `hourly.relative_humidity_2m[i]` | Relative humidity 2 m, % |
| `precipitation_mm` | `float` | Yes | `hourly.precipitation[i]` | Precipitation total per hour, mm |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | Mean shortwave radiation (GHI), W/m² |
| `surface_pressure_hpa` | `float` | Yes | `hourly.surface_pressure[i]` | Surface pressure, hPa |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m |
| `hdd_k` | `float` | Yes | derived | `max(15.5 - temperature_2m, 0)` — heating degree-hours, base 15.5 °C |
| `cdd_k` | `float` | Yes | derived | `max(temperature_2m - 22.0, 0)` — cooling degree-hours, base 22.0 °C |
| `air_density_kg_m3` | `float` | Yes | derived | `surface_pressure_Pa / (287.05 × T_K)` — ideal gas, dry air |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time |

Bitemporal columns (`event_time`, `available_at`, `source_run_id`,
`dataset_version`) are stamped onto the silver Polars DataFrame at write
time by `BaseSilverTransformer` per the F0 pattern; `DATASET_VERSION` is
`"2.0.0"`.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 8, 0, 0, tzinfo=UTC),
        "location": "london",
        "latitude": 51.5,
        "longitude": -0.1,
        "temperature_2m_c": 11.8,
        "wind_speed_10m_mps": 2.64,
        "wind_direction_10m_deg": 200.0,
        "relative_humidity_2m_pct": 78.0,
        "precipitation_mm": 0.0,
        "shortwave_radiation_wm2": 0.0,
        "surface_pressure_hpa": 1018.4,
        "snowfall_cm": 0.0,
        "snow_depth_m": 0.0,
        "hdd_k": 3.7,
        "cdd_k": 0.0,
        "air_density_kg_m3": 1.245,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2026, 5, 8, 12, 0, tzinfo=UTC),
        "location": "london",
        "latitude": 51.5,
        "longitude": -0.1,
        "temperature_2m_c": 17.2,
        "wind_speed_10m_mps": 4.53,
        "wind_direction_10m_deg": 230.0,
        "relative_humidity_2m_pct": 55.0,
        "precipitation_mm": 0.0,
        "shortwave_radiation_wm2": 540.0,
        "surface_pressure_hpa": 1019.1,
        "snowfall_cm": 0.0,
        "snow_depth_m": 0.0,
        "hdd_k": 0.0,
        "cdd_k": 0.0,
        "air_density_kg_m3": 1.221,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Two-host design.** Forecast lives at `api.open-meteo.com`, while
  the [historical archive](./historical_demand.md) lives at the
  *different* host `archive-api.open-meteo.com`. Don't accidentally
  point the forecast query at the archive host (or vice versa).
- **Unpinned model.** Open-Meteo's forecast endpoint defaults to a
  router that picks ECMWF / GFS / ICON / etc. based on grid cell and
  forecast hour. The selection can change silently between calls. If
  reproducibility matters, pin via `models=<id>`. The gridflow
  connector does **not** pin a model today.
- **Forecast vintages overwritten.** Each silver build replaces the
  forecast for any given `(timestamp_utc, location)` pair with the
  latest fetch. There is no `forecast_run_at` / lead-time column —
  cross-vintage analysis (e.g. "how did the day-ahead forecast at
  lead -24h compare to the realised value?") is **not supported** by
  the current silver layer.
- **No revision history.** Same as above: a `forecast_run_at` is not
  stored. Point-in-time queries against forecast vintages would
  require a schema extension.
- **`past_days` not used.** The forecast endpoint can return up to
  ~92 past days alongside the forecast (`past_days=N`), but the
  gridflow connector does not pass it. For past data, use the
  [historical_demand](./historical_demand.md) endpoint.
- **Columnar response shape.** Identical to historical — parallel
  arrays under `hourly.<variable>`. The silver transformer
  `ForecastDemandWeather` shares `BaseOpenMeteoTransformer` with the
  archive variants, so the pivot logic is unified.
- **Snow units.** `snowfall` is in cm of new snow per hour,
  `snow_depth` is the standing snow column in **metres**.
- **Bronze double-underscore separator.** Bronze paths use
  `forecast_demand__<city>`, **not** `forecast_demand_<city>`.
- **Naming inconsistency.** The vault folder is `open-meteo` (with
  dash), the Python package is `gridflow.connectors.openmeteo` (no
  separator), and the config-source key is `open_meteo` (with
  underscore). All three coexist by design — see
  [README §Naming](../README.md#naming). Do not rename.

---

## Implementation delta

- **Two-host handling factually verified.** The forecast dataset uses
  `FORECAST_BASE_URL = "https://api.open-meteo.com/v1"` from
  `connectors/openmeteo/endpoints.py`, picked up in
  `client.py:_fetch_location` via the dataset-prefix conditional
  (the else branch when prefix ≠ `historical_*`). Matches the
  `base_url` in `config/sources.yaml`. Verified OK 2026-05-09.
- **`DATASET_VERSION = "2.0.0"`**: bumped from `"1.0.0"` at F7.5 to
  reflect the schema-affecting change from the unified
  `WeatherObservation` to the role-split `DemandWeather`.
- **No `forecast_run_at` column.** Connector does not capture the
  forecast issue time. Without it, lead-time analysis is impossible.
  Add to schema if needed for forecast-skill modelling.
- **No model pinning.** Connector accepts whatever model the
  Open-Meteo router selects. Silently shifts upstream — flagged in
  the README too.
- **Pydantic schema present at F7.5.** F0 had no
  `src/gridflow/schemas/openmeteo.py`; F7.5 added
  `src/gridflow/schemas/weather.py` with `DemandWeather`,
  `WindWeather`, `SolarWeather`.
- **Same hard-coded `DEMAND_LOCATIONS`** as historical (7 UK cities,
  in `endpoints.py`).

---

## Modelling notes

- **Day-ahead demand modelling.** `temperature_2m`, derived `hdd` /
  `cdd`, `relative_humidity_2m`, and `air_density_kg_m3` are the
  standard inputs.
- **Day-ahead demand-from-wind/solar modelling.** Use
  `forecast_demand` for population-centre weather but pair with
  [`forecast_wind`](./forecast_wind.md) and
  [`forecast_solar`](./forecast_solar.md) for the renewables side
  rather than retrofitting wind/solar at population centres.
- **Forecast-skill / lead-time studies.** **Not currently possible**
  with the silver schema — see Known issues. Would need
  `forecast_run_at` and a multi-vintage write strategy.
- **Combine with [historical_demand](./historical_demand.md)** for
  residual / bias-correction features by stitching ERA5 archive
  against forecast at matching lead times.

---

## Links

- [Official API docs (Forecast)](https://open-meteo.com/en/docs)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/forecast.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Historical counterpart](./historical_demand.md)
- [Wind forecast (12 sites)](./forecast_wind.md)
- [Solar forecast (6 sites)](./forecast_solar.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
