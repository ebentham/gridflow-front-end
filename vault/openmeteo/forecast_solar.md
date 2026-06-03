---
source: open_meteo
dataset_key: forecast_solar
vendor: Open-Meteo
last_verified: 2026-06-03
layer_coverage: bronze, silver
---

# Open-Meteo — Forecast Solar Weather (GB capacity-weighted sites, 1–16 days)

## Overview

Hourly solar-irradiance forecast for the next 1–16 days at the **6
capacity-weighted GB solar sites** (East Anglia (Norfolk),
Wiltshire/Somerset, Kent, Cornwall, Sussex, Oxfordshire). Same
variable set, location list, and tilt geometry as
[historical_solar](./historical_solar.md): full irradiance
decomposition (GHI / DNI / DHI / GTI at `tilt=35°`, `azimuth=180°`),
cloud cover at three heights, and snow variables.

Used as the forward-looking solar-PV forecast feed for short-term
generation forecasting and bid optimisation. New at F7.5.

→ This dataset answers: *what irradiance is forecast at the GB solar
sites over the next N hours, both on horizontal and on a UK fixed tilt
panel?* For lookback / backtesting, use
[historical_solar](./historical_solar.md). For population-centre or
wind-site forecasts, use [forecast_demand](./forecast_demand.md) or
[forecast_wind](./forecast_wind.md).

`forecast_solar` is **net-new at F7.5** — no F0-era predecessor.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://api.open-meteo.com/v1` |
| Path             | `/forecast` |
| Method           | GET |
| Auth             | None (public, free tier — no key, no header) |
| Rate limit       | Soft limit ~10 000 requests/day per IP (vendor-published, free tier); ~600/min burst. Project caps at 5 req/s. |
| Pagination       | None — chunk via `start_date` / `end_date` (or `forecast_days`) |
| Historical depth | Forward-looking only — supports `past_days` to stitch up to ~92 days of recent past, but the canonical path for past data is the [archive endpoint](./historical_solar.md) |
| Publication lag  | Real-time — current run typically refreshed every ~1 hour by the upstream NWP router |
| Response format  | JSON (columnar — one parallel array per variable) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `52.62` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `1.05` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests **12** fields | `temperature_2m,shortwave_radiation,direct_radiation,...` |
| `tilt` | int | Yes (for GTI) | Panel tilt above horizontal, degrees | `35` |
| `azimuth` | int | Yes (for GTI) | Panel azimuth, degrees (0=N, 180=S) | `180` |
| `forecast_days` | int | No | Number of forecast days (default 7, max 16) | `2` |
| `start_date` | date | No | Window start; gridflow uses this | `2026-05-08` |
| `end_date` | date | No | Window end; gridflow uses this | `2026-05-09` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |
| `models` | csv string | No | Pin a specific NWP model — connector does not pin | — |

The connector's `WeatherDatasetSpec.extra_params` for `forecast_solar`
is `(("tilt", "35"), ("azimuth", "180"))` — same UK fixed-tilt
representative geometry as the archive counterpart.

Connector requests these `hourly` variables (`endpoints.SOLAR_HOURLY_VARS`):
`temperature_2m`, `shortwave_radiation`, `direct_radiation`,
`direct_normal_irradiance`, `diffuse_radiation`,
`global_tilted_irradiance`, `cloud_cover`, `cloud_cover_low`,
`cloud_cover_mid`, `cloud_cover_high`, `snowfall`, `snow_depth`.

### Working curl example

```bash
# No auth required — Cornwall, 2 days forecast with full irradiance set
curl --ssl-no-revoke -fsS \
  "https://api.open-meteo.com/v1/forecast?latitude=50.30&longitude=-5.00&hourly=shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance,cloud_cover&tilt=35&azimuth=180&forecast_days=2&timezone=UTC"
```

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/forecast_solar__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the six `SOLAR_LOCATIONS` per call and emits one `RawResponse` per
site. The `dataset` field on each `RawResponse` is
`f"forecast_solar__{location.name}"` (**double underscore**), so
bronze partitions live under `bronze/open_meteo/forecast_solar__<site>/...`.
The silver transformer's `BRONZE_DATASET_PREFIX` is `"forecast_solar"`.

### Bronze sample

```json
{
  "latitude": 50.30,
  "longitude": -5.00,
  "generationtime_ms": 0.65,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "elevation": 35.0,
  "hourly_units": {
    "time": "iso8601",
    "shortwave_radiation": "W/m²",
    "direct_radiation": "W/m²",
    "direct_normal_irradiance": "W/m²",
    "diffuse_radiation": "W/m²",
    "global_tilted_irradiance": "W/m²",
    "cloud_cover": "%",
    "snowfall": "cm",
    "snow_depth": "m"
  },
  "hourly": {
    "time": ["2026-05-08T11:00", "2026-05-08T12:00", "2026-05-08T13:00"],
    "temperature_2m": [14.5, 15.8, 16.6],
    "shortwave_radiation": [580.0, 700.0, 720.0],
    "direct_radiation": [400.0, 500.0, 520.0],
    "direct_normal_irradiance": [750.0, 770.0, 780.0],
    "diffuse_radiation": [180.0, 200.0, 200.0],
    "global_tilted_irradiance": [670.0, 770.0, 790.0],
    "cloud_cover": [30.0, 25.0, 20.0],
    "cloud_cover_low": [15.0, 10.0, 5.0],
    "cloud_cover_mid": [10.0, 10.0, 10.0],
    "cloud_cover_high": [5.0, 5.0, 5.0],
    "snowfall": [0.0, 0.0, 0.0],
    "snow_depth": [0.0, 0.0, 0.0]
  }
}
```

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/forecast_solar/year=YYYY/month=MM/forecast_solar_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.forecast.ForecastSolarWeather`
**Pydantic schema**: `gridflow.schemas.weather.SolarWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0). No `forecast_run_at`; older vintages overwritten on re-ingest.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied |
| `location` | `str` | No | derived | Site key from `SOLAR_LOCATIONS` |
| `latitude` | `float` | No | top-level `latitude` | Float64 |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | °C |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | GHI, W/m² |
| `direct_radiation_wm2` | `float` | Yes | `hourly.direct_radiation[i]` | Beam on horizontal, W/m² |
| `direct_normal_irradiance_wm2` | `float` | Yes | `hourly.direct_normal_irradiance[i]` | DNI, W/m² |
| `diffuse_radiation_wm2` | `float` | Yes | `hourly.diffuse_radiation[i]` | DHI, W/m² |
| `global_tilted_irradiance_wm2` | `float` | Yes | `hourly.global_tilted_irradiance[i]` | GTI on UK fixed tilt (35°/180°), W/m² |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | % |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | % |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | % |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | % |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time |

Bitemporal columns (`event_time`, `available_at`, `source_run_id`,
`dataset_version`) are stamped at write time; `DATASET_VERSION = "2.0.0"`.

**No `air_density_kg_m3` derivation on this dataset** — same rationale
as [historical_solar](./historical_solar.md#silver-schema): the solar
variable list does not request `surface_pressure`. Property test
`tests/unit/test_openmeteo_air_density.py` asserts the solar
transformer does NOT carry air density.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 8, 11, 0, tzinfo=UTC),
        "location": "cornwall",
        "latitude": 50.30,
        "longitude": -5.00,
        "temperature_2m_c": 14.5,
        "shortwave_radiation_wm2": 580.0,
        "direct_radiation_wm2": 400.0,
        "direct_normal_irradiance_wm2": 750.0,
        "diffuse_radiation_wm2": 180.0,
        "global_tilted_irradiance_wm2": 670.0,
        "cloud_cover_pct": 30.0,
        "cloud_cover_low_pct": 15.0,
        "cloud_cover_mid_pct": 10.0,
        "cloud_cover_high_pct": 5.0,
        "snowfall_cm": 0.0,
        "snow_depth_m": 0.0,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2026, 5, 8, 12, 0, tzinfo=UTC),
        "location": "kent",
        "latitude": 51.20,
        "longitude": 0.70,
        "temperature_2m_c": 17.0,
        "shortwave_radiation_wm2": 720.0,
        "direct_radiation_wm2": 510.0,
        "direct_normal_irradiance_wm2": 800.0,
        "diffuse_radiation_wm2": 210.0,
        "global_tilted_irradiance_wm2": 790.0,
        "cloud_cover_pct": 20.0,
        "cloud_cover_low_pct": 5.0,
        "cloud_cover_mid_pct": 10.0,
        "cloud_cover_high_pct": 5.0,
        "snowfall_cm": 0.0,
        "snow_depth_m": 0.0,
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

- **No `air_density_kg_m3` on this dataset** — see
  [historical_solar §Known issues and gotchas](./historical_solar.md#known-issues-and-gotchas).
  Solar variable list does not request `surface_pressure`.
- **GTI requires `tilt` and `azimuth`** — same `tilt=35`, `azimuth=180`
  as historical via `WeatherDatasetSpec.extra_params`.
- **Two-host design.** Forecast lives at `api.open-meteo.com`, while
  [historical_solar](./historical_solar.md) lives at
  `archive-api.open-meteo.com`.
- **Unpinned NWP model.** Open-Meteo's forecast endpoint uses a router;
  irradiance forecast skill varies by model. If reproducibility
  matters, pin via `models=<id>`.
- **Forecast vintages overwritten.** Each silver build replaces the
  forecast for `(timestamp_utc, location)` with the latest fetch. No
  `forecast_run_at` column.
- **Approximate site centroids** — see ADR-020. All 6 sites are below
  53° N (south-east bias).
- **Snow shading.** Same caveat as
  [historical_solar](./historical_solar.md) — snow yield-collapse
  modelling belongs in feature engineering.
- **`past_days` not used.** For past data, use the
  [historical_solar](./historical_solar.md) endpoint.
- **Bronze double-underscore separator.** Bronze paths use
  `forecast_solar__<site>`, **not** `forecast_solar_<site>`.
- **Naming.** Vault folder `open-meteo`, Python package `openmeteo`,
  config key `open_meteo` — see [README §Naming](../README.md#naming).

---

## Implementation delta

- **Net-new dataset at F7.5.** Bronze backfill needed before query
  use; commands documented in F7.5-RESULTS.md.
- **GTI tilt/azimuth via `extra_params`** — same approach as
  `historical_solar`.
- **No air-density derivation** — see Known issues.
- **No `forecast_run_at` column.**
- **No model pinning.**
- **`SolarWeather` Pydantic schema** present at F7.5 in
  `src/gridflow/schemas/weather.py`. Same schema as historical for
  symmetry; `BaseOpenMeteoTransformer` shares the pivot logic.

---

## Modelling notes

- **Day-ahead solar-PV modelling.** `global_tilted_irradiance` is the
  most direct feature for fixed-tilt sites at 35°/180°. For tracker
  installations the GTI underestimates; use `direct_normal_irradiance`
  and a tracker-specific transposition.
- **Cloud-cover dynamics.** Forecast cloud cover at three heights is
  particularly useful for hour-ahead nowcast features.
- **Forecast-skill backtests.** Cross-vintage analysis is **not
  currently possible** without `forecast_run_at` — see Known issues.
  Pair against [historical_solar](./historical_solar.md) at matching
  lead times for bias-correction features.
- **Aggregate forecast.** Sites are GW-capacity-weighted south-east
  hotspots; weight by installed capacity per region for GB-aggregate
  forecast.

---

## Links

- [Official API docs (Forecast)](https://open-meteo.com/en/docs)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/forecast.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Historical counterpart](./historical_solar.md)
- [Demand forecast (7 cities)](./forecast_demand.md)
- [Wind forecast (12 sites)](./forecast_wind.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
