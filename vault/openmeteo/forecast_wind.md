---
source: open_meteo
dataset_key: forecast_wind
vendor: Open-Meteo
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Open-Meteo — Forecast Wind Weather (GB capacity-weighted sites, 1–16 days)

## Overview

Hourly wind-relevant weather forecast for the next 1–16 days at the
**12 capacity-weighted GB wind sites** (8 offshore, 4 onshore). The
forecast endpoint carries the full hub-height set unlike the
[archive counterpart](./historical_wind.md) — `wind_speed_10m`,
`wind_speed_80m`, `wind_speed_100m`, `wind_speed_120m`,
`wind_speed_180m` plus matching directions, gusts, cloud cover, dew
point. Used as the forward-looking wind-generation feed for short-term
generation forecasting and bid optimisation. New at F7.5.

→ This dataset answers: *what is the forecast wind speed/direction at
GB wind sites over the next N hours?* For lookback / backtesting, use
[historical_wind](./historical_wind.md). Source-model hub-height
coverage may differ between calls — fields the underlying NWP model
does not carry are silver-null.

`forecast_wind` is **net-new at F7.5** — no F0-era predecessor.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://api.open-meteo.com/v1` |
| Path             | `/forecast` |
| Method           | GET |
| Auth             | None (public, free tier — no key, no header) |
| Rate limit       | Soft limit ~10 000 requests/day per IP (vendor-published, free tier); ~600/min burst. Project caps at 5 req/s in `config/sources.yaml`. |
| Pagination       | None — chunk via `start_date` / `end_date` (or `forecast_days`) |
| Historical depth | Forward-looking only — supports `past_days` to stitch up to ~92 days of recent past, but the canonical path for past data is the [archive endpoint](./historical_wind.md) |
| Publication lag  | Real-time — current run typically refreshed every ~1 hour by the upstream NWP router |
| Response format  | JSON (columnar — one parallel array per variable) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `53.88` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `1.79` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests **19** forecast fields | `temperature_2m,wind_speed_10m,wind_speed_100m,wind_speed_120m,...` |
| `forecast_days` | int | No | Number of forecast days (default 7, max 16) | `2` |
| `start_date` | date | No | Window start; gridflow uses this | `2026-05-08` |
| `end_date` | date | No | Window end; gridflow uses this | `2026-05-09` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |
| `models` | csv string | No | Pin a specific NWP model — connector does not pin | `ukmo_global` |

Connector requests these `hourly` variables (`endpoints.WIND_FORECAST_VARS`):
the 13-variable `WIND_ARCHIVE_VARS` set **plus** `wind_speed_80m`,
`wind_speed_120m`, `wind_speed_180m`, `wind_direction_80m`,
`wind_direction_120m`, `wind_direction_180m` — 19 variables total.

### Working curl example

```bash
# No auth required — Hornsea offshore, 2 days forecast with hub heights
curl --ssl-no-revoke -fsS \
  "https://api.open-meteo.com/v1/forecast?latitude=53.88&longitude=1.79&hourly=wind_speed_10m,wind_speed_80m,wind_speed_100m,wind_speed_120m,wind_speed_180m,wind_gusts_10m&forecast_days=2&timezone=UTC"
```

The forecast endpoint exposes the wider hub-height set because
underlying NWP models (UKMO UKV / ECMWF IFS / GFS) carry hub-height
output. Open-Meteo nulls fields the selected model does not carry —
`WindWeather` accepts the null-degradation cleanly.

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/forecast_wind__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the twelve `WIND_LOCATIONS` per call and emits one `RawResponse` per
site. The `dataset` field on each `RawResponse` is
`f"forecast_wind__{location.name}"` (**double underscore**), so bronze
partitions live under `bronze/open_meteo/forecast_wind__<site>/...`.
The silver transformer's `BRONZE_DATASET_PREFIX` is `"forecast_wind"`.

### Bronze sample

```json
{
  "latitude": 53.88,
  "longitude": 1.79,
  "generationtime_ms": 0.6,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "elevation": 0.0,
  "hourly_units": {
    "time": "iso8601",
    "wind_speed_10m": "km/h",
    "wind_speed_80m": "km/h",
    "wind_speed_100m": "km/h",
    "wind_speed_120m": "km/h",
    "wind_speed_180m": "km/h",
    "wind_direction_10m": "°",
    "wind_direction_100m": "°",
    "wind_gusts_10m": "km/h",
    "cloud_cover": "%",
    "dew_point_2m": "°C"
  },
  "hourly": {
    "time": ["2026-05-08T00:00", "2026-05-08T01:00"],
    "temperature_2m": [10.5, 10.2],
    "surface_pressure": [1015.0, 1014.8],
    "precipitation": [0.0, 0.0],
    "wind_speed_10m": [18.2, 19.5],
    "wind_speed_80m": [25.1, 26.4],
    "wind_speed_100m": [27.8, 29.0],
    "wind_speed_120m": [30.2, 31.5],
    "wind_speed_180m": [33.6, 34.8],
    "wind_direction_10m": [225.0, 228.0],
    "wind_direction_80m": [230.0, 232.0],
    "wind_direction_100m": [232.0, 234.0],
    "wind_direction_120m": [234.0, 236.0],
    "wind_direction_180m": [236.0, 238.0],
    "wind_gusts_10m": [32.0, 34.0],
    "cloud_cover": [60.0, 65.0],
    "cloud_cover_low": [40.0, 50.0],
    "cloud_cover_mid": [20.0, 15.0],
    "cloud_cover_high": [0.0, 0.0],
    "dew_point_2m": [8.5, 8.2]
  }
}
```

When the underlying model does not carry a hub-height field (e.g. some
GFS configurations omit 80m), the response will simply omit that
parallel array or carry `null` — silver fills `None`.

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/forecast_wind/year=YYYY/month=MM/forecast_wind_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.forecast.ForecastWindWeather`
**Pydantic schema**: `gridflow.schemas.weather.WindWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0). No `forecast_run_at`; older vintages overwritten on re-ingest.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied |
| `location` | `str` | No | derived | Site key from `WIND_LOCATIONS` |
| `latitude` | `float` | No | top-level `latitude` | Float64 |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m` | `float` | Yes | `hourly.temperature_2m[i]` | °C |
| `surface_pressure` | `float` | Yes | `hourly.surface_pressure[i]` | hPa |
| `precipitation` | `float` | Yes | `hourly.precipitation[i]` | mm/hr |
| `wind_speed_10m` | `float` | Yes | `hourly.wind_speed_10m[i]` | km/h at 10m |
| `wind_speed_80m` | `float` | Yes | `hourly.wind_speed_80m[i]` | km/h at 80m — null if NWP model does not carry |
| `wind_speed_100m` | `float` | Yes | `hourly.wind_speed_100m[i]` | km/h at 100m |
| `wind_speed_120m` | `float` | Yes | `hourly.wind_speed_120m[i]` | km/h at 120m — null if NWP model does not carry |
| `wind_speed_180m` | `float` | Yes | `hourly.wind_speed_180m[i]` | km/h at 180m — null if NWP model does not carry |
| `wind_direction_10m` | `float` | Yes | `hourly.wind_direction_10m[i]` | degrees (0=N) |
| `wind_direction_80m` | `float` | Yes | `hourly.wind_direction_80m[i]` | degrees |
| `wind_direction_100m` | `float` | Yes | `hourly.wind_direction_100m[i]` | degrees |
| `wind_direction_120m` | `float` | Yes | `hourly.wind_direction_120m[i]` | degrees |
| `wind_direction_180m` | `float` | Yes | `hourly.wind_direction_180m[i]` | degrees |
| `wind_gusts_10m` | `float` | Yes | `hourly.wind_gusts_10m[i]` | Peak gust 10m, km/h |
| `cloud_cover` | `float` | Yes | `hourly.cloud_cover[i]` | Total cover, % |
| `cloud_cover_low` | `float` | Yes | `hourly.cloud_cover_low[i]` | % |
| `cloud_cover_mid` | `float` | Yes | `hourly.cloud_cover_mid[i]` | % |
| `cloud_cover_high` | `float` | Yes | `hourly.cloud_cover_high[i]` | % |
| `dew_point_2m` | `float` | Yes | `hourly.dew_point_2m[i]` | °C |
| `air_density_kg_m3` | `float` | Yes | derived | `surface_pressure_Pa / (287.05 × T_K)` |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time |

Bitemporal columns (`event_time`, `available_at`, `source_run_id`,
`dataset_version`) are stamped at write time; `DATASET_VERSION = "2.0.0"`.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 8, 0, 0, tzinfo=UTC),
        "location": "hornsea",
        "latitude": 53.88,
        "longitude": 1.79,
        "temperature_2m": 10.5,
        "surface_pressure": 1015.0,
        "precipitation": 0.0,
        "wind_speed_10m": 18.2,
        "wind_speed_80m": 25.1,
        "wind_speed_100m": 27.8,
        "wind_speed_120m": 30.2,
        "wind_speed_180m": 33.6,
        "wind_direction_10m": 225.0,
        "wind_direction_80m": 230.0,
        "wind_direction_100m": 232.0,
        "wind_direction_120m": 234.0,
        "wind_direction_180m": 236.0,
        "wind_gusts_10m": 32.0,
        "cloud_cover": 60.0,
        "cloud_cover_low": 40.0,
        "cloud_cover_mid": 20.0,
        "cloud_cover_high": 0.0,
        "dew_point_2m": 8.5,
        "air_density_kg_m3": 1.249,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2026, 5, 8, 12, 0, tzinfo=UTC),
        "location": "whitelee",
        "latitude": 55.69,
        "longitude": -4.27,
        "temperature_2m": 12.3,
        "surface_pressure": 1010.5,
        "precipitation": 0.2,
        "wind_speed_10m": 14.7,
        "wind_speed_80m": 22.4,
        "wind_speed_100m": 24.1,
        "wind_speed_120m": None,
        "wind_speed_180m": None,
        "wind_direction_10m": 250.0,
        "wind_direction_80m": 255.0,
        "wind_direction_100m": 258.0,
        "wind_direction_120m": None,
        "wind_direction_180m": None,
        "wind_gusts_10m": 26.0,
        "cloud_cover": 75.0,
        "cloud_cover_low": 60.0,
        "cloud_cover_mid": 25.0,
        "cloud_cover_high": 5.0,
        "dew_point_2m": 9.0,
        "air_density_kg_m3": 1.235,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
]
```

The Whitelee row above shows the typical case where the underlying
forecast model carries 80m and 100m hub heights but not 120m / 180m.
Same `WindWeather` schema; nulls flow through silver cleanly.

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Two-host design.** Forecast lives at `api.open-meteo.com`, while
  [historical_wind](./historical_wind.md) lives at
  `archive-api.open-meteo.com`. The connector chooses the correct
  host via the dataset prefix.
- **Unpinned NWP model.** Open-Meteo's forecast endpoint defaults to
  a router that picks UKMO / ECMWF / GFS / ICON / etc. based on
  grid cell and forecast hour. The selection can change silently
  between calls — and so can hub-height field availability. If you
  need a stable hub-height set for backtesting, pin via
  `models=ukmo_global` (UKMO carries the wider set reliably).
- **Hub-height nulls are model-driven, not silver bugs.** When
  `wind_speed_120m` is null, the underlying NWP model did not
  publish it for that grid cell. Silver does not fabricate values.
- **Forecast vintages overwritten.** Each silver build replaces the
  forecast for `(timestamp_utc, location)` with the latest fetch.
  No `forecast_run_at` column.
- **Approximate site centroids.** Same caveat as
  [historical_wind §approximate locations](./historical_wind.md#known-issues-and-gotchas).
  See ADR-020.
- **Wind units.** All wind speeds and gusts are in **km/h**.
- **`past_days` not used.** For past data, use the
  [historical_wind](./historical_wind.md) endpoint.
- **Bronze double-underscore separator.** Bronze paths use
  `forecast_wind__<site>`, **not** `forecast_wind_<site>`.
- **Naming.** Vault folder `open-meteo`, Python package `openmeteo`,
  config key `open_meteo` — see [README §Naming](../README.md#naming).

---

## Implementation delta

- **Wider hub-height set on forecast** vs archive — see
  [historical_wind §Archive 10m+100m limitation](./historical_wind.md#archive-10m100m-limitation).
- **No `forecast_run_at` column.** Connector does not capture the
  forecast issue time. Lead-time / forecast-skill analysis would
  require schema extension.
- **No model pinning.** Connector accepts whatever the router
  selects.
- **`WindWeather` Pydantic schema** present at F7.5 in
  `src/gridflow/schemas/weather.py`. All hub-height fields typed
  `float | None`.
- **Net-new dataset at F7.5.** Bronze backfill needed before query
  use; commands documented in F7.5-RESULTS.md.

---

## Modelling notes

- **Day-ahead wind-generation modelling.** Hub-height inputs at the
  12 sites are the headline features. Use `wind_speed_100m` (or
  higher when available) as the primary; fall back to
  `wind_speed_10m` with a shear correction for null cells.
- **Air-density correction.** `air_density_kg_m3` is derived for use
  with manufacturer power curves at standard 1.225 kg/m³.
- **Forecast-skill backtests.** Cross-vintage analysis is **not
  currently possible** — see Known issues. Pair against
  [historical_wind](./historical_wind.md) at matching lead times for
  bias-correction features after an external `available_at`-aware
  vintage join.
- **Aggregate forecast.** Sites are GW-weighted; for GB-aggregate
  forecast, weight by installed capacity per site.

---

## Links

- [Official API docs (Forecast)](https://open-meteo.com/en/docs)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/forecast.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Historical counterpart](./historical_wind.md)
- [Demand forecast (7 cities)](./forecast_demand.md)
- [Solar forecast (6 sites)](./forecast_solar.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
