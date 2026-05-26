---
source: open_meteo
dataset_key: historical_wind
vendor: Open-Meteo
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Open-Meteo — Historical Wind Weather (ERA5 archive, GB capacity-weighted sites)

## Overview

Hourly historical wind-relevant weather observations from the ECMWF
ERA5 reanalysis at **12 capacity-weighted GB wind sites** — 8 offshore
clusters (Dogger Bank, Hornsea, East Anglia, Triton Knoll, Walney,
Gwynt y Môr, Beatrice, Seagreen) and 4 onshore (Highland Central,
Borders Crystal Rig, Whitelee, Pen y Cymoedd). New at F7.5.

Used as the wind-generation backtest feed — `wind_speed_10m` and
`wind_speed_100m` are the headline features, paired with directions,
gusts, cloud cover, dew point (icing risk), and derived air density
(turbine power-curve density correction).

→ This dataset answers: *what wind speed/direction/gust occurred at
the GB wind sites over hours h0..h1?* For near-real-time use
[forecast_wind](./forecast_wind.md). For population-centre or solar-site
weather, use [historical_demand](./historical_demand.md) or
[historical_solar](./historical_solar.md).

`historical_wind` is **net-new at F7.5** — no F0-era predecessor.
Historical bronze backfill required (~12 sites × 8 yr × 365 d ≈ 35 000
location-days; documented in `F7.5-RESULTS.md` but not run during
phase execution).

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
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `53.88` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `1.79` |
| `start_date` | date | Yes | Inclusive start of the window, `YYYY-MM-DD` | `2025-01-15` |
| `end_date` | date | Yes | Inclusive end of the window, `YYYY-MM-DD` | `2025-01-21` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests **13** archive fields | `temperature_2m,wind_speed_10m,...` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |

Connector requests these `hourly` variables (`endpoints.WIND_ARCHIVE_VARS`):
`temperature_2m`, `surface_pressure`, `wind_speed_10m`,
`wind_speed_100m`, `wind_direction_10m`, `wind_direction_100m`,
`wind_gusts_10m`, `cloud_cover`, `cloud_cover_low`, `cloud_cover_mid`,
`cloud_cover_high`, `dew_point_2m`, `precipitation`.

**`WIND_ARCHIVE_VARS` deliberately excludes `wind_speed_{80,120,180}m`
and the matching directions — see [Archive 10m+100m
limitation](#archive-10m100m-limitation).**

### Working curl example

```bash
# No auth required — Hornsea offshore probe
curl --ssl-no-revoke -fsS \
  "https://archive-api.open-meteo.com/v1/archive?latitude=53.88&longitude=1.79&start_date=2025-01-15&end_date=2025-01-21&hourly=wind_speed_10m,wind_speed_100m,wind_gusts_10m,dew_point_2m,cloud_cover&timezone=UTC"
```

Verified 2026-05-09 (F7.5 hub-height verification): HTTP 200, 168
hourly entries (7 days × 24 hours), 10m and 100m non-null for all hours.

---

## Archive 10m+100m limitation

ERA5 archive reliably exposes only **`wind_speed_10m`** and
**`wind_speed_100m`** for hub-height wind. Heights `80m`, `120m`,
`180m` return `units: "undefined"` and **all-null** values. Verified
2026-05-09 against:

| Probe                          | 10m units | 80m units    | 100m units | 120m units   | 180m units   | Mean 10m | Mean 100m | Corr 10/100m |
|--------------------------------|-----------|--------------|------------|--------------|--------------|---------:|----------:|-------------:|
| Hornsea (53.88, 1.79) offshore | km/h      | undefined ❌ | km/h       | undefined ❌ | undefined ❌ | 23.81    | 27.08     | 0.949        |
| Whitelee (55.69, -4.27) onshore| km/h      | undefined ❌ | km/h       | undefined ❌ | undefined ❌ | 18.58    | 30.87     | 0.977        |

The 10m → 100m ratio differs by regime (offshore mean 1.14, onshore
1.66), which is itself a feature signal (the Hellmann shear exponent).
Both fields therefore carry distinct information despite the high
correlation.

`WIND_ARCHIVE_VARS` deliberately excludes `wind_speed_{80,120,180}m`
and the matching directions to avoid silver carrying empty columns.
The wider hub-height set is available on the **forecast** endpoint —
see [forecast_wind](./forecast_wind.md). `WindWeather` accepts the
null-degradation cleanly (all hub-height fields typed `float | None`),
so silver shape is identical between archive and forecast.

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/historical_wind__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the twelve `WIND_LOCATIONS` per call and emits one `RawResponse` per
site. The `dataset` field on each `RawResponse` is
`f"historical_wind__{location.name}"` (**double underscore**), so bronze
partitions live under
`bronze/open_meteo/historical_wind__<site>/...`. The silver
transformer's `BRONZE_DATASET_PREFIX` is `"historical_wind"`.

### Bronze sample

```json
{
  "latitude": 53.88,
  "longitude": 1.79,
  "generationtime_ms": 0.55,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "elevation": 0.0,
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
    "surface_pressure": "hPa",
    "wind_speed_10m": "km/h",
    "wind_speed_100m": "km/h",
    "wind_direction_10m": "°",
    "wind_direction_100m": "°",
    "wind_gusts_10m": "km/h",
    "cloud_cover": "%",
    "dew_point_2m": "°C",
    "precipitation": "mm"
  },
  "hourly": {
    "time": ["2025-01-15T00:00", "2025-01-15T01:00"],
    "temperature_2m": [4.2, 3.9],
    "surface_pressure": [1010.2, 1009.8],
    "wind_speed_10m": [22.5, 24.1],
    "wind_speed_100m": [25.8, 27.4],
    "wind_direction_10m": [225.0, 228.0],
    "wind_direction_100m": [230.0, 232.0],
    "wind_gusts_10m": [38.0, 41.0],
    "cloud_cover": [85.0, 90.0],
    "cloud_cover_low": [60.0, 75.0],
    "cloud_cover_mid": [25.0, 15.0],
    "cloud_cover_high": [0.0, 0.0],
    "dew_point_2m": [3.0, 2.8],
    "precipitation": [0.0, 0.1]
  }
}
```

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/historical_wind/year=YYYY/month=MM/historical_wind_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.historical.HistoricalWindWeather`
**Pydantic schema**: `gridflow.schemas.weather.WindWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0). ERA5 archive values are stable.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied |
| `location` | `str` | No | derived | Site key from `WIND_LOCATIONS` (hornsea, dogger_bank, walney, ...) |
| `latitude` | `float` | No | top-level `latitude` | Float64 |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m` | `float` | Yes | `hourly.temperature_2m[i]` | °C |
| `surface_pressure` | `float` | Yes | `hourly.surface_pressure[i]` | hPa |
| `precipitation` | `float` | Yes | `hourly.precipitation[i]` | mm/hr |
| `wind_speed_10m` | `float` | Yes | `hourly.wind_speed_10m[i]` | km/h at 10m |
| `wind_speed_80m` | `float` | Yes | not requested on archive | **always null on this dataset** — see [Archive limitation](#archive-10m100m-limitation) |
| `wind_speed_100m` | `float` | Yes | `hourly.wind_speed_100m[i]` | km/h at 100m |
| `wind_speed_120m` | `float` | Yes | not requested on archive | **always null on this dataset** |
| `wind_speed_180m` | `float` | Yes | not requested on archive | **always null on this dataset** |
| `wind_direction_10m` | `float` | Yes | `hourly.wind_direction_10m[i]` | degrees (0=N) |
| `wind_direction_80m` | `float` | Yes | not requested on archive | **always null on this dataset** |
| `wind_direction_100m` | `float` | Yes | `hourly.wind_direction_100m[i]` | degrees |
| `wind_direction_120m` | `float` | Yes | not requested on archive | **always null on this dataset** |
| `wind_direction_180m` | `float` | Yes | not requested on archive | **always null on this dataset** |
| `wind_gusts_10m` | `float` | Yes | `hourly.wind_gusts_10m[i]` | Peak gust 10m, km/h |
| `cloud_cover` | `float` | Yes | `hourly.cloud_cover[i]` | Total cover, % |
| `cloud_cover_low` | `float` | Yes | `hourly.cloud_cover_low[i]` | % |
| `cloud_cover_mid` | `float` | Yes | `hourly.cloud_cover_mid[i]` | % |
| `cloud_cover_high` | `float` | Yes | `hourly.cloud_cover_high[i]` | % |
| `dew_point_2m` | `float` | Yes | `hourly.dew_point_2m[i]` | °C — proxy for icing risk |
| `air_density_kg_m3` | `float` | Yes | derived | `surface_pressure_Pa / (287.05 × T_K)` — turbine power-curve density correction |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time |

The schema declares 80m / 120m / 180m fields for symmetry with
`forecast_wind`; on this dataset they are always null because the
archive endpoint does not expose those heights. Bitemporal columns
(`event_time`, `available_at`, `source_run_id`, `dataset_version`) are
stamped at write time; `DATASET_VERSION = "2.0.0"`.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 1, 15, 0, 0, tzinfo=UTC),
        "location": "hornsea",
        "latitude": 53.88,
        "longitude": 1.79,
        "temperature_2m": 4.2,
        "surface_pressure": 1010.2,
        "precipitation": 0.0,
        "wind_speed_10m": 22.5,
        "wind_speed_80m": None,
        "wind_speed_100m": 25.8,
        "wind_speed_120m": None,
        "wind_speed_180m": None,
        "wind_direction_10m": 225.0,
        "wind_direction_80m": None,
        "wind_direction_100m": 230.0,
        "wind_direction_120m": None,
        "wind_direction_180m": None,
        "wind_gusts_10m": 38.0,
        "cloud_cover": 85.0,
        "cloud_cover_low": 60.0,
        "cloud_cover_mid": 25.0,
        "cloud_cover_high": 0.0,
        "dew_point_2m": 3.0,
        "air_density_kg_m3": 1.273,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2025, 1, 15, 12, 0, tzinfo=UTC),
        "location": "whitelee",
        "latitude": 55.69,
        "longitude": -4.27,
        "temperature_2m": 1.8,
        "surface_pressure": 1004.5,
        "precipitation": 0.4,
        "wind_speed_10m": 17.6,
        "wind_speed_80m": None,
        "wind_speed_100m": 28.3,
        "wind_speed_120m": None,
        "wind_speed_180m": None,
        "wind_direction_10m": 250.0,
        "wind_direction_80m": None,
        "wind_direction_100m": 254.0,
        "wind_direction_120m": None,
        "wind_direction_180m": None,
        "wind_gusts_10m": 30.0,
        "cloud_cover": 95.0,
        "cloud_cover_low": 80.0,
        "cloud_cover_mid": 30.0,
        "cloud_cover_high": 5.0,
        "dew_point_2m": 0.5,
        "air_density_kg_m3": 1.279,
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

- **Archive 10m+100m limitation.** See [§ above](#archive-10m100m-limitation).
  Hub heights {80m, 120m, 180m} are silently null on the archive endpoint;
  the connector deliberately does not request them. The forecast endpoint
  carries the wider set.
- **Approximate site centroids.** The 12 wind locations are
  capacity-weighted approximations, not per-turbine NRO coordinates.
  See `docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md`
  for the rationale (vendor licensing, NRO data ergonomics, modelling
  granularity trade-off).
- **Two-host design.** Wind archive lives at
  `archive-api.open-meteo.com`, while [forecast_wind](./forecast_wind.md)
  lives at `api.open-meteo.com`. The connector chooses the correct host
  via the `historical_*` dataset prefix.
- **ERA5 reanalysis lag.** Roughly 5 days. End_date within the last 5
  days may return null trailing values.
- **ERA5 grid-cell snapping.** `latitude` / `longitude` echoed in the
  response can differ slightly from the request (snapped to the nearest
  ERA5 grid cell). Silver stores the *response* values.
- **Wind units.** All wind speeds and gusts are in **km/h**. Convert to
  m/s for typical power-curve work (`m/s = km/h / 3.6`).
- **`air_density_kg_m3` requires `surface_pressure`.** Both are
  requested on this dataset, so the derivation is always populated when
  the archive returns the underlying fields.
- **Bronze double-underscore separator.** Bronze paths use
  `historical_wind__<site>`, **not** `historical_wind_<site>`.
- **Naming.** Vault folder `open-meteo`, Python package `openmeteo`,
  config key `open_meteo` — see [README §Naming](../README.md#naming).
  Do not rename.

---

## Implementation delta

- **Hub-height archive limitation observed and locked into
  `WIND_ARCHIVE_VARS`** (verified 2026-05-09; documented above).
  `WIND_FORECAST_VARS` includes the wider set as `WIND_ARCHIVE_VARS +
  (wind_speed_80m, wind_speed_120m, wind_speed_180m, wind_direction_80m,
  wind_direction_120m, wind_direction_180m)`.
- **Net-new dataset at F7.5.** No bronze on disk; backfill required
  before this dataset is queryable. Backfill commands are documented
  in `.planning/phases/F7.5-open-meteo-renewable-extension/F7.5-RESULTS.md`
  under "Re-ingest commands".
- **Approximate locations** — see ADR-020. If a future modelling phase
  needs per-turbine resolution, the location list is upgradable in
  `endpoints.py:WIND_LOCATIONS` without schema changes.
- **`WindWeather` Pydantic schema** added at F7.5 in
  `src/gridflow/schemas/weather.py`. All hub-height fields typed
  `float | None` so the same schema validates both archive (sparse) and
  forecast (dense) silver writes.

---

## Modelling notes

- **Wind-generation modelling.** `wind_speed_10m` and
  `wind_speed_100m` are the headline features; the 10m → 100m ratio
  is a useful shear-derived feature. Cube-root or
  power-curve-mapped derivations belong in feature engineering, not
  silver. Convert km/h → m/s before applying turbine power curves.
- **Air-density correction.** `air_density_kg_m3` is the canonical
  correction term applied to manufacturer power curves at standard
  density (1.225 kg/m³). Useful as a multiplicative or residual
  feature.
- **Icing risk.** `dew_point_2m` near or below freezing combined with
  high cloud cover and precipitation flags icing windows; offshore
  blade icing is a documented operational risk.
- **Backtest joins.** Pair against Elexon `windfor` (NESO-published
  wind forecast) for forecast-skill backtests, and against Elexon
  `fuelhh` `WIND` field for actual aggregate output.
- **Spatial aggregation.** Sites are GW-capacity-weighted; for
  GB-aggregate wind output, weight by installed offshore + onshore
  capacity per site rather than equally.

---

## Links

- [Official API docs (Historical Weather)](https://open-meteo.com/en/docs/historical-weather-api)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/historical.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Forecast counterpart](./forecast_wind.md)
- [Demand weather (7 cities)](./historical_demand.md)
- [Solar weather (6 sites)](./historical_solar.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
