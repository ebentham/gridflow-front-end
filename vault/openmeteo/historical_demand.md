---
source: open_meteo
dataset_key: historical_demand
vendor: Open-Meteo
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Open-Meteo — Historical Demand Weather (ERA5 archive, population centres)

## Overview

Hourly historical weather observations derived from the ECMWF ERA5
reanalysis at 7 GB population centres (London, Birmingham, Manchester,
Leeds, Glasgow, Cardiff, Belfast). This is the demand-modelling feed —
temperature drives heating and cooling load, snow and humidity feed
winter-peak load surprises, and air density (derived in silver) is a
secondary input for high-load adjustments. ERA5 has multi-decade depth,
is gridded globally, and is the de facto standard for climate-derived
features, so demand backtests over multi-year windows can use this
feed without the station-coverage gaps you'd hit with raw observations.

→ This dataset answers: *what was the temperature / wind / radiation /
snow at the 7 demand centres over hours h0..h1?* For near-real-time use
the [forecast_demand](./forecast_demand.md) dataset. For wind-site or
solar-site weather, use [historical_wind](./historical_wind.md) or
[historical_solar](./historical_solar.md).

`historical_demand` is the F7.5 successor of the F0-era `historical`
dataset; `DATASET_VERSION` bumped 1.0.0 → 2.0.0.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://archive-api.open-meteo.com/v1` |
| Path             | `/archive` |
| Method           | GET |
| Auth             | None (public, free tier — no key, no header) |
| Rate limit       | Soft limit ~10 000 requests/day per IP (vendor-published, free tier); ~600/min burst. Project caps at 5 req/s in `config/sources.yaml`. |
| Pagination       | None — chunk via `start_date` / `end_date` window |
| Historical depth | 1940-01-01 (ERA5 reanalysis depth — vendor states "since 1940") |
| Publication lag  | ~5 days behind real time (ERA5 reanalysis cadence) |
| Response format  | JSON (columnar — one parallel array per variable) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `51.5074` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `-0.1278` |
| `start_date` | date | Yes | Inclusive start of the window, `YYYY-MM-DD` | `2025-05-01` |
| `end_date` | date | Yes | Inclusive end of the window, `YYYY-MM-DD` | `2025-05-07` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests 9 fields | `temperature_2m,wind_speed_10m,...` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |
| `daily` | csv string | No | Daily-aggregated variables — not used by gridflow | — |
| `models` | csv string | No | ERA5 model variant override — not used | — |

Connector requests these `hourly` variables (`endpoints.DEMAND_HOURLY_VARS`):
`temperature_2m`, `wind_speed_10m`, `wind_direction_10m`,
`relative_humidity_2m`, `precipitation`, `shortwave_radiation`,
`surface_pressure`, `snowfall`, `snow_depth`.

### Working curl example

```bash
# No auth required
curl --ssl-no-revoke -fsS \
  "https://archive-api.open-meteo.com/v1/archive?latitude=51.5074&longitude=-0.1278&start_date=2025-05-01&end_date=2025-05-07&hourly=temperature_2m,wind_speed_10m,shortwave_radiation,snowfall,snow_depth"
```

Verified 2026-05-09 against London, Hornsea, and Whitelee probe coordinates
during F7.5 hub-height verification.

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/historical_demand__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the seven `DEMAND_LOCATIONS` per call and emits one `RawResponse` per
city. The `dataset` field on each `RawResponse` is
`f"historical_demand__{location.name}"` (**double underscore**),
so bronze partitions live under
`bronze/open_meteo/historical_demand__<city>/...`. The silver
transformer's `BRONZE_DATASET_PREFIX` is `"historical_demand"`; its
`read_bronze` re-aggregates the per-city sibling directories.

### Bronze sample

```json
{
  "latitude": 51.5074,
  "longitude": -0.1278,
  "generationtime_ms": 0.42,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "timezone_abbreviation": "GMT",
  "elevation": 25.0,
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "wind_speed_10m": "km/h",
    "wind_direction_10m": "°",
    "relative_humidity_2m": "%",
    "precipitation": "mm",
    "shortwave_radiation": "W/m²",
    "surface_pressure": "hPa",
    "snowfall": "cm",
    "snow_depth": "m"
  },
  "hourly": {
    "time": ["2024-01-15T00:00", "2024-01-15T01:00", "2024-01-15T02:00"],
    "temperature_2m": [-1.2, -1.6, -1.9],
    "wind_speed_10m": [12.5, 11.8, 13.2],
    "wind_direction_10m": [225.0, 230.0, 220.0],
    "relative_humidity_2m": [82.0, 84.0, 85.0],
    "precipitation": [0.0, 0.1, 0.0],
    "shortwave_radiation": [0.0, 0.0, 0.0],
    "surface_pressure": [1015.2, 1015.0, 1014.8],
    "snowfall": [0.5, 0.8, 0.3],
    "snow_depth": [0.04, 0.05, 0.05]
  }
}
```

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/historical_demand/year=YYYY/month=MM/historical_demand_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.historical.HistoricalDemandWeather`
**Pydantic schema**: `gridflow.schemas.weather.DemandWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0). ERA5 archive values are stable once published.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | Parsed from `YYYY-MM-DDTHH:MM` (ISO8601 without tz suffix), UTC tz applied |
| `location` | `str` | No | derived | City name from `DEMAND_LOCATIONS` (london, birmingham, ...) |
| `latitude` | `float` | No | top-level `latitude` | Float64; matches request lat (Open-Meteo may snap to nearest grid cell) |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m` | `float` | Yes | `hourly.temperature_2m[i]` | Air temperature 2 m above ground, °C |
| `wind_speed_10m` | `float` | Yes | `hourly.wind_speed_10m[i]` | Wind speed 10 m above ground, km/h |
| `wind_direction_10m` | `float` | Yes | `hourly.wind_direction_10m[i]` | Wind direction 10 m, degrees (0=N, 90=E) |
| `relative_humidity_2m` | `float` | Yes | `hourly.relative_humidity_2m[i]` | Relative humidity 2 m, % |
| `precipitation` | `float` | Yes | `hourly.precipitation[i]` | Precipitation total per hour, mm |
| `shortwave_radiation` | `float` | Yes | `hourly.shortwave_radiation[i]` | Mean shortwave radiation (GHI), W/m² |
| `surface_pressure` | `float` | Yes | `hourly.surface_pressure[i]` | Surface pressure, hPa |
| `snowfall` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm |
| `snow_depth` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m |
| `hdd` | `float` | Yes | derived | `max(15.5 - temperature_2m, 0)` — heating degree-hours, base 15.5 °C |
| `cdd` | `float` | Yes | derived | `max(temperature_2m - 22.0, 0)` — cooling degree-hours, base 22.0 °C |
| `air_density_kg_m3` | `float` | Yes | derived | `surface_pressure_Pa / (287.05 × T_K)` — ideal gas, dry air |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time (F0 retains for backward compat; bitemporal `available_at` is authoritative) |

Bitemporal columns (`event_time`, `available_at`, `source_run_id`,
`dataset_version`) are stamped onto the silver Polars DataFrame at write
time by `BaseSilverTransformer` per the F0 pattern; `DATASET_VERSION` is
`"2.0.0"`.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 1, 15, 0, 0, tzinfo=UTC),
        "location": "london",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "temperature_2m": -1.2,
        "wind_speed_10m": 12.5,
        "wind_direction_10m": 225.0,
        "relative_humidity_2m": 82.0,
        "precipitation": 0.0,
        "shortwave_radiation": 0.0,
        "surface_pressure": 1015.2,
        "snowfall": 0.5,
        "snow_depth": 0.04,
        "hdd": 16.7,
        "cdd": 0.0,
        "air_density_kg_m3": 1.30,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2025, 5, 1, 12, 0, tzinfo=UTC),
        "location": "london",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "temperature_2m": 23.4,
        "wind_speed_10m": 18.0,
        "wind_direction_10m": 230.0,
        "relative_humidity_2m": 50.0,
        "precipitation": 0.0,
        "shortwave_radiation": 720.0,
        "surface_pressure": 1015.5,
        "snowfall": 0.0,
        "snow_depth": 0.0,
        "hdd": 0.0,
        "cdd": 1.4,
        "air_density_kg_m3": 1.19,
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

- **Two-host design.** Demand archive lives at
  `archive-api.open-meteo.com`, while [forecast_demand](./forecast_demand.md)
  lives at `api.open-meteo.com`. The `config/sources.yaml` `base_url` for
  `open_meteo` is `https://api.open-meteo.com/v1` and is **only** valid
  for forecast endpoints. The connector chooses the correct host for
  archive datasets via the `historical_*` dataset prefix; see
  [Implementation delta](#implementation-delta).
- **ERA5 reanalysis lag.** Roughly 5 days. Calls for `end_date` within
  the last 5 days may return 200 with truncated arrays or null trailing
  values. Plan backfills with this lag in mind.
- **ERA5 grid-cell snapping.** The `latitude` / `longitude` echoed in
  the response can differ slightly from the request (snapped to the
  nearest grid cell). Silver stores the *response* values, not the
  request values. Don't dedup on lat/lon.
- **Columnar response, not row-oriented.** Hourly data is delivered as
  parallel arrays under `hourly.<variable>`; the silver transformer
  pivots `hourly.time[i]` together with each variable's `[i]` index.
  If a variable is missing from the response (e.g. you request a
  variable that doesn't exist for that grid cell), the parallel array
  is shorter or absent — the silver transformer fills `None`.
- **Snow units.** `snowfall` is in cm of new snow per hour, `snow_depth`
  is the standing snow column in **metres**. Don't conflate.
- **Naming inconsistency.** The vault folder is `open-meteo` (with
  dash), the Python package is `gridflow.connectors.openmeteo` (no
  separator), and the config-source key is `open_meteo` (with
  underscore). All three coexist by design — see
  [README §Naming](../README.md#naming). Do not rename.
- **Bronze double-underscore separator.** Bronze paths use
  `historical_demand__<city>`, **not** `historical_demand_<city>` — the
  `__` separator disambiguates the multi-word dataset prefix from
  multi-word location names. Old single-underscore `historical_<city>`
  paths from F0 are obsolete; existing F0 bronze must be re-keyed before
  re-ingest.
- **DST is not a concern.** ERA5 timestamps are always UTC and we
  always pass `timezone=UTC`. Unlike Elexon settlement-period feeds,
  there are no 46- / 50-period days here.

---

## Implementation delta

- **Two-host override**: `config/sources.yaml` declares only
  `base_url: https://api.open-meteo.com/v1` and the dataset path
  `archive`. The connector ignores this `base_url` for `historical_*`
  datasets — `connectors/openmeteo/client.py:_fetch_location` builds
  the URL from a dataset-prefix conditional that selects
  `ARCHIVE_BASE_URL` when the dataset starts with `historical_`,
  else `FORECAST_BASE_URL`. Constants in
  `connectors/openmeteo/endpoints.py`. Verified OK 2026-05-09.
- **`DATASET_VERSION = "2.0.0"`**: bumped from `"1.0.0"` at F7.5 to
  reflect the schema-affecting change from the unified
  `WeatherObservation` to the role-split `DemandWeather`.
- **Connector dataset name vs silver dataset name.** Bronze
  `RawResponse.dataset` values are `historical_demand__<city>` (per
  location); the silver transformer's `dataset` is the unqualified
  `historical_demand`. Bronze partitions therefore live under per-city
  subdirectories (`bronze/open_meteo/historical_demand__london/...`),
  not `historical_demand/`. The silver `BRONZE_DATASET_PREFIX`
  mechanism re-aggregates them. Not a bug — design choice — but worth
  knowing when probing bronze paths.
- **Hard-coded `DEMAND_LOCATIONS` (7 UK cities).** The location list
  lives in `connectors/openmeteo/endpoints.py`, not in
  `config/sources.yaml`. Adding a city today requires a code change.
- **Pydantic schema present at F7.5.** F0 had no
  `src/gridflow/schemas/openmeteo.py`; F7.5 added
  `src/gridflow/schemas/weather.py` with `DemandWeather`,
  `WindWeather`, `SolarWeather`.

---

## Modelling notes

- **Demand modelling.** `temperature_2m` is the primary feature for
  HDD / CDD-driven demand models; the derived `hdd` and `cdd` columns
  are ready-to-use. `relative_humidity_2m` and `wind_speed_10m`
  (cooling effect / wind-chill) are useful secondary features.
- **Winter-peak load.** `snowfall` and `snow_depth` are added at F7.5
  specifically for winter peak surprise modelling — heating load
  during prolonged snow cover behaves non-linearly versus dry cold.
- **Air density.** `air_density_kg_m3` is derived from `surface_pressure`
  and `temperature_2m` via the ideal gas law (R_specific dry air =
  287.05 J/(kg·K)). High-altitude or low-pressure days lower density;
  useful as a residual feature in some demand models.
- **Backtest joins.** Pair against Elexon `indo` / `indod` / `tsdf`
  (national demand) for load models, weighted by population per city.
- **Spatial aggregation.** The seven demand cities are population-
  weighted hotspots, not a uniform grid. For GB-wide aggregates, weight
  by demand or installed capacity rather than equally.

---

## Links

- [Official API docs (Historical Weather)](https://open-meteo.com/en/docs/historical-weather-api)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/historical.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Forecast counterpart](./forecast_demand.md)
- [Wind weather (12 sites)](./historical_wind.md)
- [Solar weather (6 sites)](./historical_solar.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
