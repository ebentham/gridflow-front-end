---
slug: intensity_at
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/at
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_at.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityAtTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_at"] (lines 83-89, path /intensity/{from_dt})
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Intensity at a datetime, <span class="italic fg-accent">single point.</span>

**Lede:** GB carbon intensity for the half-hour ending at a chosen UTC datetime — the canonical point-in-time lookup for joining timestamped events to grid carbon.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/{from}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_at` |
| API PATH | `/intensity/{from}` |
| FREQUENCY | 30 min (single SP) |
| PUBLICATION LAG | forecast ahead · actual post-period |
| VOLUME | 1 row / call |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 1 | Row per call |
| 3 | ISO-8601 | Datetime format `YYYY-MM-DDThh:mmZ` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_period
- intensity_current
- intensity_date
- carbon_intensity
- intensity_fw24h

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · point-in-time lookups · last 24h"
- **Subtitle:** "Sparkline · gCO2/kWh · UTC · 6 May 2026"
- **Seed:** 29
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate. | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_at/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-06T07:00:00+00:00 | 2026-05-06T07:30:00+00:00 | 148.0 | 145.0 | moderate |
| 2026-05-06T09:00:00+00:00 | 2026-05-06T09:30:00+00:00 | 105.0 | 102.0 | low |
| 2026-05-06T11:00:00+00:00 | 2026-05-06T11:30:00+00:00 | 92.0 | 88.0 | low |
| **2026-05-06T12:00:00+00:00** | **2026-05-06T12:30:00+00:00** | **68.0** | **64.0** | **very low** |
| 2026-05-06T15:00:00+00:00 | 2026-05-06T15:30:00+00:00 | 89.0 | 91.0 | low |
| 2026-05-06T17:00:00+00:00 | 2026-05-06T17:30:00+00:00 | 195.0 | 198.0 | moderate |
| 2026-05-06T19:00:00+00:00 | 2026-05-06T19:30:00+00:00 | 285.0 | 293.0 | high |

**Sources:** Seven point-in-time reads spaced through one day (vault Silver Sample shape, vault/neso/intensity_at.md). Each is a separate API call to `/intensity/{datetime}`. Highlighted 12:00 row = the day's solar trough.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/{from}` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_at/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityAtTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/2026-05-06T12:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Event-keyed carbon lookup: attach intensity to a list of timestamps
WITH events(event_ts) AS (
  SELECT TIMESTAMP '2026-05-06 12:00:00' UNION ALL
  SELECT TIMESTAMP '2026-05-06 18:00:00'
)
SELECT e.event_ts, ci.actual_gco2_kwh, ci.intensity_index
FROM events e
LEFT JOIN read_parquet('data/silver/neso/intensity_at/**/*.parquet') ci
  ON ci.timestamp_utc = date_trunc('hour', e.event_ts)
ORDER BY e.event_ts;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/intensity_at/**/*.parquet")
# Attach intensity to an event log via as_of asof-join
events = pl.DataFrame({"event_ts": [...]}).sort("event_ts")
joined = events.join_asof(
    df.sort("timestamp_utc"),
    left_on="event_ts", right_on="timestamp_utc",
    strategy="backward",
)
print(joined.head())
```

# Caveats

## 01 Single-row endpoint — use for point lookups, not series

Each call returns one record (the half-hour ending at `{from}`). For series, use `carbon_intensity` or `intensity_date`. *(Source: `connectors/neso/endpoints.py L83-89`.)*

## 02 Datetime granularity — half-hour boundary

The API snaps `{from}` to the enclosing settlement-period boundary. Pass `12:00Z`, `12:15Z`, `12:29Z` and you get the same SP (`12:00..12:30`). *(Source: NESO docs — settlement-period semantics.)*

## 03 Future datetimes return forecast only

Calling with a datetime later than the current SP returns `actual_gco2_kwh = null`. *(Source: vault Known Issues L104.)*

## 04 Transformer is dynamically generated

`IntensityAtTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_period`** — Same point lookup keyed by `(date, SP)` instead of datetime. `30 min`. Equivalent — choose by which key your join uses. *neso · national intensity · 30 min*
- **`intensity_current`** — Now-only · same schema. `30 min`. No `{from}` param; returns current SP. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range query · same schema. `30 min`. Cheaper than looping `intensity_at` for windows. *neso · national intensity · 30 min*
- **`intensity_fw24h`** — Same starting datetime extended 24h ahead. `30 min`. Pair with this dataset for "intensity now and next 24h". *neso · national forecast · 30 min*
