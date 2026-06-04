---
source: open_meteo
dataset_key: historical_solar
vendor: Open-Meteo
last_verified: 2026-06-04
layer_coverage: bronze, silver
---

# Open-Meteo — Historical Solar Weather (ERA5 archive, GB capacity-weighted sites)

## Overview

Hourly historical solar-irradiance observations from the ECMWF ERA5
reanalysis at **6 capacity-weighted GB solar sites** — East Anglia
(Norfolk), Wiltshire/Somerset, Kent, Cornwall, Sussex, Oxfordshire.
All sites are below the Bristol-Norwich line (53° N); GB installed
solar capacity is heavily south-east biased, and Glasgow at 55.9° N
receives ~60% of the annual irradiance of Cornwall at 50.3° N. New at
F7.5.

Used as the solar-PV-generation backtest feed. The dataset adds the
full irradiance decomposition over the F0-era `historical` set:
**GHI** (`shortwave_radiation`), **DNI** (`direct_normal_irradiance`),
**DHI** (`diffuse_radiation`), and **GTI** (`global_tilted_irradiance`)
at a UK fixed-tilt representative geometry (`tilt=35°`, `azimuth=0°`
— latitude minus ~15°, due south; Open-Meteo PV convention 0=S, ±180=N). Also carries cloud cover at three
heights and snow variables (snowfall, snow_depth) for snow-shading
events.

→ This dataset answers: *what irradiance components arrived at the GB
solar sites over hours h0..h1, both on horizontal and on a UK fixed
tilt panel?* For near-real-time use [forecast_solar](./forecast_solar.md).
For population-centre or wind-site weather, use
[historical_demand](./historical_demand.md) or
[historical_wind](./historical_wind.md).

`historical_solar` is **net-new at F7.5** — no F0-era predecessor.
Historical bronze backfill required (~6 sites × 8 yr × 365 d ≈ 17 500
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
| Rate limit       | Soft limit ~10 000 requests/day per IP (vendor-published, free tier); ~600/min burst. Project caps at 5 req/s. |
| Pagination       | None — chunk via `start_date` / `end_date` window |
| Historical depth | 1940-01-01 (ERA5 reanalysis depth — vendor states "since 1940") |
| Publication lag  | ~5 days behind real time (ERA5 reanalysis cadence) |
| Response format  | JSON (columnar — one parallel array per variable) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | WGS-84 latitude in decimal degrees | `52.62` |
| `longitude` | float | Yes | WGS-84 longitude in decimal degrees | `1.05` |
| `start_date` | date | Yes | Inclusive start of the window, `YYYY-MM-DD` | `2025-06-01` |
| `end_date` | date | Yes | Inclusive end of the window, `YYYY-MM-DD` | `2025-06-07` |
| `hourly` | csv string | Yes | Comma-separated variable names — connector requests **12** fields | `temperature_2m,shortwave_radiation,direct_radiation,...` |
| `tilt` | int | Yes (for GTI) | Panel tilt above horizontal, degrees | `35` |
| `azimuth` | int | Yes (for GTI) | Panel azimuth, degrees — Open-Meteo PV convention `0=S, ±180=N` (NOT compass) | `0` |
| `timezone` | string | No (default `GMT`) | Connector always passes `UTC` | `UTC` |

The connector's `WeatherDatasetSpec.extra_params` for `historical_solar`
is `(("tilt", "35"), ("azimuth", "0"))` — the UK fixed-tilt
representative geometry (35° tilt, due south). Both params are **required** when
`global_tilted_irradiance` is in the `hourly` list.

Connector requests these `hourly` variables (`endpoints.SOLAR_HOURLY_VARS`):
`temperature_2m`, `shortwave_radiation`, `direct_radiation`,
`direct_normal_irradiance`, `diffuse_radiation`,
`global_tilted_irradiance`, `cloud_cover`, `cloud_cover_low`,
`cloud_cover_mid`, `cloud_cover_high`, `snowfall`, `snow_depth`.

### Working curl example

```bash
# No auth required — Cornwall solar probe with full irradiance set
curl --ssl-no-revoke -fsS \
  "https://archive-api.open-meteo.com/v1/archive?latitude=50.30&longitude=-5.00&start_date=2025-06-01&end_date=2025-06-07&hourly=shortwave_radiation,direct_radiation,direct_normal_irradiance,diffuse_radiation,global_tilted_irradiance,cloud_cover&tilt=35&azimuth=0&timezone=UTC"
```

Verified 2026-05-09 (F7.5): GHI = `shortwave_radiation` and the
separation `GHI ≈ DNI × cos(zenith) + DHI` is a useful invariant —
silver passes through the API's separation-model output and a property
test (`tests/unit/test_openmeteo_irradiance_components.py`) asserts
`direct_radiation + diffuse_radiation` is within 5% of
`shortwave_radiation` for daylight rows.

---

## Bronze layer

**Path pattern**: `data/bronze/open_meteo/historical_solar__<location>/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per (location, fetch). The connector iterates
the six `SOLAR_LOCATIONS` per call and emits one `RawResponse` per
site. The `dataset` field on each `RawResponse` is
`f"historical_solar__{location.name}"` (**double underscore**), so
bronze partitions live under
`bronze/open_meteo/historical_solar__<site>/...`. The silver
transformer's `BRONZE_DATASET_PREFIX` is `"historical_solar"`.

### Bronze sample

```json
{
  "latitude": 50.30,
  "longitude": -5.00,
  "generationtime_ms": 0.7,
  "utc_offset_seconds": 0,
  "timezone": "GMT",
  "elevation": 35.0,
  "hourly_units": {
    "time": "iso8601",
    "temperature_2m": "°C",
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
    "time": ["2025-06-01T11:00", "2025-06-01T12:00", "2025-06-01T13:00"],
    "temperature_2m": [16.3, 17.8, 18.6],
    "shortwave_radiation": [620.0, 750.0, 780.0],
    "direct_radiation": [430.0, 540.0, 565.0],
    "direct_normal_irradiance": [780.0, 800.0, 810.0],
    "diffuse_radiation": [190.0, 210.0, 215.0],
    "global_tilted_irradiance": [710.0, 820.0, 845.0],
    "cloud_cover": [25.0, 20.0, 15.0],
    "cloud_cover_low": [10.0, 5.0, 5.0],
    "cloud_cover_mid": [10.0, 10.0, 5.0],
    "cloud_cover_high": [5.0, 5.0, 5.0],
    "snowfall": [0.0, 0.0, 0.0],
    "snow_depth": [0.0, 0.0, 0.0]
  }
}
```

---

## Silver layer

**Path pattern**: `data/silver/open_meteo/historical_solar/year=YYYY/month=MM/historical_solar_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.openmeteo.historical.HistoricalSolarWeather`
**Pydantic schema**: `gridflow.schemas.weather.SolarWeather`
**Dedup key**: `(timestamp_utc, location)` — `df.unique(subset=["timestamp_utc", "location"], keep="last")`
**Point-in-time field**: `available_at` — bitemporal stamp from `BaseSilverTransformer` (F0).

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | `hourly.time[i]` | UTC tz applied |
| `location` | `str` | No | derived | Site key from `SOLAR_LOCATIONS` (cornwall, kent, ...) |
| `latitude` | `float` | No | top-level `latitude` | Float64 |
| `longitude` | `float` | No | top-level `longitude` | Float64 |
| `temperature_2m_c` | `float` | Yes | `hourly.temperature_2m[i]` | °C — drives module-temperature derate |
| `shortwave_radiation_wm2` | `float` | Yes | `hourly.shortwave_radiation[i]` | GHI — global horizontal irradiance, W/m² |
| `direct_radiation_wm2` | `float` | Yes | `hourly.direct_radiation[i]` | Beam component on horizontal, W/m² |
| `direct_normal_irradiance_wm2` | `float` | Yes | `hourly.direct_normal_irradiance[i]` | DNI — beam normal to sun, W/m² |
| `diffuse_radiation_wm2` | `float` | Yes | `hourly.diffuse_radiation[i]` | DHI — diffuse on horizontal, W/m² |
| `global_tilted_irradiance_wm2` | `float` | Yes | `hourly.global_tilted_irradiance[i]` | GTI on UK fixed tilt (35°, due south = azimuth 0), W/m² |
| `cloud_cover_pct` | `float` | Yes | `hourly.cloud_cover[i]` | Total cover, % |
| `cloud_cover_low_pct` | `float` | Yes | `hourly.cloud_cover_low[i]` | % |
| `cloud_cover_mid_pct` | `float` | Yes | `hourly.cloud_cover_mid[i]` | % |
| `cloud_cover_high_pct` | `float` | Yes | `hourly.cloud_cover_high[i]` | % |
| `snowfall_cm` | `float` | Yes | `hourly.snowfall[i]` | New-snow water equivalent per hour, cm |
| `snow_depth_m` | `float` | Yes | `hourly.snow_depth[i]` | Standing snow depth, m |
| `data_provider` | `str` | No | derived | Constant `"open_meteo"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | Wall-clock UTC at silver-build time |

Bitemporal columns (`event_time`, `available_at`, `source_run_id`,
`dataset_version`) are stamped at write time; `DATASET_VERSION = "2.0.0"`.

**No `air_density_kg_m3` derivation on this dataset.** The solar
variable list does not request `surface_pressure`, so air density
cannot be computed and the column is omitted from `SolarWeather`. (The
demand and wind schemas do carry it; see those pages.) Property test
`tests/unit/test_openmeteo_air_density.py` asserts the solar
transformer does NOT carry air density, locking this contract in.

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 6, 1, 11, 0, tzinfo=UTC),
        "location": "cornwall",
        "latitude": 50.30,
        "longitude": -5.00,
        "temperature_2m_c": 16.3,
        "shortwave_radiation_wm2": 620.0,
        "direct_radiation_wm2": 430.0,
        "direct_normal_irradiance_wm2": 780.0,
        "diffuse_radiation_wm2": 190.0,
        "global_tilted_irradiance_wm2": 710.0,
        "cloud_cover_pct": 25.0,
        "cloud_cover_low_pct": 10.0,
        "cloud_cover_mid_pct": 10.0,
        "cloud_cover_high_pct": 5.0,
        "snowfall_cm": 0.0,
        "snow_depth_m": 0.0,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2025, 12, 15, 12, 0, tzinfo=UTC),
        "location": "east_anglia_norfolk",
        "latitude": 52.62,
        "longitude": 1.05,
        "temperature_2m_c": 4.5,
        "shortwave_radiation_wm2": 95.0,
        "direct_radiation_wm2": 12.0,
        "direct_normal_irradiance_wm2": 60.0,
        "diffuse_radiation_wm2": 83.0,
        "global_tilted_irradiance_wm2": 175.0,
        "cloud_cover_pct": 90.0,
        "cloud_cover_low_pct": 75.0,
        "cloud_cover_mid_pct": 30.0,
        "cloud_cover_high_pct": 5.0,
        "snowfall_cm": 0.2,
        "snow_depth_m": 0.01,
        "data_provider": "open_meteo",
        "ingested_at": datetime(2026, 5, 9, 9, 12, 5, tzinfo=UTC),
    },
]
```

The winter row above (Norfolk, December noon) shows the mostly-diffuse
regime under heavy cloud — DNI collapses, DHI dominates GHI, GTI on a
35° tilted panel exceeds GHI on horizontal because the steeper sun
angle is partially compensated by the panel orientation (and a touch of
ground reflection).

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **No `air_density_kg_m3` on this dataset.** Solar variable list does
  not request `surface_pressure`, so the derivation cannot run.
  Contract enforced by `test_openmeteo_air_density.py`. If a future
  modelling phase needs solar-site density, add `surface_pressure` to
  `SOLAR_HOURLY_VARS` and the derivation will activate via
  `BaseOpenMeteoTransformer.DERIVE_AIR_DENSITY`.
- **GTI requires `tilt` and `azimuth` query params.** The connector
  injects `tilt=35&azimuth=0` via `WeatherDatasetSpec.extra_params`
  (azimuth 0 = due south under Open-Meteo's PV convention 0=S / ±180=N).
  Modifying the tilt geometry requires a code change in
  `_SOLAR_GTI_PARAMS` and a downstream re-ingest; document any change
  here. UK fixed-tilt sites typically use latitude minus ~15°, due
  south.
- **GHI ≈ DNI·cos(z) + DHI invariant.** Property test asserts
  `direct_radiation + diffuse_radiation ≈ shortwave_radiation` within
  5% for daylight rows. Open-Meteo's separation model is the upstream
  source; silver does not re-derive components.
- **Approximate site centroids.** The 6 solar locations are
  capacity-weighted approximations; see ADR-020.
- **Snow shading.** `snowfall` and `snow_depth` are kept as features;
  panel snow cover is a documented operational risk for solar yield.
  Snow-cover modelling belongs in feature engineering, not silver.
- **Two-host design.** Solar archive lives at
  `archive-api.open-meteo.com`, while [forecast_solar](./forecast_solar.md)
  lives at `api.open-meteo.com`.
- **ERA5 reanalysis lag.** Roughly 5 days. End_date within the last 5
  days may return null trailing values.
- **Latitude bias.** All 6 sites are below 53° N. Aggregate solar
  yield modelling for GB should not be derived by averaging these
  sites with northerly load — they are deliberately south-eastern.
- **Bronze double-underscore separator.** Bronze paths use
  `historical_solar__<site>`, **not** `historical_solar_<site>`.
- **Naming.** Vault folder `open-meteo`, Python package `openmeteo`,
  config key `open_meteo` — see [README §Naming](../README.md#naming).

---

## Implementation delta

- **Net-new dataset at F7.5.** No bronze on disk; backfill required.
- **GTI tilt/azimuth via `extra_params` on `WeatherDatasetSpec`.**
  The frozen dataclass uses a tuple of `(key, value)` pairs because it
  needs to stay `frozen=True`; the connector materialises it back to a
  dict at request time. If the dataset is duplicated for a different
  tilt geometry (e.g. UK two-axis tracker representative), create a
  new `WeatherDatasetSpec` rather than mutating the existing one.
- **No air-density derivation** — see Known issues.
- **Approximate locations** — see ADR-020.
- **`SolarWeather` Pydantic schema** added at F7.5 in
  `src/gridflow/schemas/weather.py`. All irradiance fields typed
  `float | None`.

---

## Modelling notes

- **Day-ahead solar-PV modelling.** `global_tilted_irradiance` is the
  most direct feature — it represents the irradiance arriving on the
  representative panel geometry — but watch out: the tilt is fixed at
  35° due south (azimuth 0), so for sites with tracker installations the GTI will
  systematically underestimate. `shortwave_radiation` is GHI; combine
  with cloud cover for cloud-shading proxy features.
- **DNI / DHI separation.** Useful for tracker-vs-fixed comparisons
  and for clear-sky / overcast regime classification (high DNI/GHI =
  clear; low DNI/GHI = overcast).
- **Module temperature.** `temperature_2m` plus a Sandia /
  King-style temperature model belongs in feature engineering; silver
  carries the raw input.
- **Snow shading.** `snowfall` + `snow_depth` flag yield-collapse
  windows; modelling should derate during snow-cover hours.
- **Backtest joins.** Pair against Elexon `fuelhh` (national `SOLAR`
  field) for actual aggregate solar output, weighted by installed
  capacity per site. ENTSOE `actual_generation` (B16) is the EU-grid
  equivalent.
- **Spatial aggregation.** All 6 sites are south-eastern hotspots;
  for GB aggregate, weight by installed solar MW per region.

---

## Links

- [Official API docs (Historical Weather)](https://open-meteo.com/en/docs/historical-weather-api)
- [Connector source](../../../../Python/gridflow/src/gridflow/connectors/openmeteo/client.py)
- [Silver transformer](../../../../Python/gridflow/src/gridflow/silver/openmeteo/historical.py)
- [Pydantic schema](../../../../Python/gridflow/src/gridflow/schemas/weather.py)
- [Gold view/builder](#) — none
- [Forecast counterpart](./forecast_solar.md)
- [Demand weather (7 cities)](./historical_demand.md)
- [Wind weather (12 sites)](./historical_wind.md)
- [ADR-020 — location approximation](../../../../Python/gridflow/docs/DECISION_LOG/ADR-020-openmeteo-location-approximation.md)
