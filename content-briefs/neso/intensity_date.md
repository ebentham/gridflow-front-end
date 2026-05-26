---
slug: intensity_date
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/date
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_date.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityDateTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_date"] (lines 58-65; daily_iteration=True)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector + daily_iteration in _request_specs, L122-136)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity for any date, <span class="italic fg-accent">whole day.</span>

**Lede:** All half-hour GB carbon-intensity records for a chosen date — the canonical single-day pull for backtests, weekday/weekend patterning, and per-day reporting.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/date/{date}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_date` |
| API PATH | `/intensity/date/{date}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecasts ahead · actuals post-period |
| VOLUME | 48 / call (46 or 50 on DST days) |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 | Rows per call (standard day) |
| 3 | 1 / call | Daily iteration |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_today
- intensity_period
- carbon_intensity
- intensity_current
- intensity_at

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · single date · 48 periods"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · 6 May 2026"
- **Seed:** 27
- **Toggles:** `24h` (active) / `weekday avg` / `weekend avg`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate; null until publication. | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_date/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-04-15T00:00:00+00:00 | 2026-04-15T00:30:00+00:00 | 232.0 | 228.0 | moderate |
| 2026-04-15T03:00:00+00:00 | 2026-04-15T03:30:00+00:00 | 198.0 | 195.0 | moderate |
| 2026-04-15T06:00:00+00:00 | 2026-04-15T06:30:00+00:00 | 152.0 | 150.0 | moderate |
| 2026-04-15T09:00:00+00:00 | 2026-04-15T09:30:00+00:00 | 110.0 | 108.0 | low |
| **2026-04-15T12:30:00+00:00** | **2026-04-15T13:00:00+00:00** | **74.0** | **71.0** | **very low** |
| 2026-04-15T15:00:00+00:00 | 2026-04-15T15:30:00+00:00 | 95.0 | 99.0 | low |
| 2026-04-15T18:00:00+00:00 | 2026-04-15T18:30:00+00:00 | 224.0 | 230.0 | moderate |
| 2026-04-15T21:00:00+00:00 | 2026-04-15T21:30:00+00:00 | 263.0 | 269.0 | high |

**Sources:** Eight representative SPs from a single backtest date (vault Silver Sample shape, vault/neso/intensity_date.md). The highlighted 12:30 row is the day's solar trough (`very low`, 71 gCO2/kWh actual). Unlike `intensity_today`, every row's `actual` is populated because the date is in the past.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/date/{date}` (path param `{date}` in `YYYY-MM-DD` form)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_date/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityDateTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/date/2026-04-15
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Day-of-week mean intensity over the last 90 days
SELECT extract('dow' FROM timestamp_utc) AS dow,
       avg(actual_gco2_kwh) AS mean_gco2_kwh,
       count(*) AS n_periods
FROM read_parquet('data/silver/neso/intensity_date/**/*.parquet')
WHERE actual_gco2_kwh IS NOT NULL
  AND timestamp_utc >= current_date - INTERVAL 90 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/intensity_date/**/*.parquet")
# Per-date min/median/max — daily-intensity profile feature
daily = (
    df.with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
      .group_by("day")
      .agg([
          pl.col("actual_gco2_kwh").min().alias("min_g"),
          pl.col("actual_gco2_kwh").median().alias("p50_g"),
          pl.col("actual_gco2_kwh").max().alias("max_g"),
      ])
      .sort("day")
)
print(daily.tail(7))
```

# Caveats

## 01 Connector daily-iterates over the requested window

The endpoint accepts only a single `{date}`. For a range, the connector iterates day-by-day (`endpoints.py L64 daily_iteration=True`; `carbon_intensity.py L122-136`) — N calls for N days. *(Source: `connectors/neso/carbon_intensity.py L122-136`.)*

## 02 DST days return 46 or 50 rows

Spring-forward returns 46, autumn-back returns 50, not the docs' 48. The shared transformer handles this via `timestamp_utc` directly. *(Source: vault Known Issues L106.)*

## 03 Future-date calls return forecasts only

Calling `intensity_date` for a future date returns rows with populated `forecast_gco2_kwh` and null `actual_gco2_kwh`. *(Source: vault Known Issues L104.)*

## 04 Transformer is dynamically generated

`IntensityDateTransformer` is created at import time by `register_neso_transformers()` via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_today`** — Today's 48 SPs · same schema. `30 min`. Same shape, today only. *neso · national intensity · 30 min*
- **`intensity_period`** — Single SP on a date · same schema. `30 min`. Narrow `intensity_date` to one of the 48 periods. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range query · same schema. `30 min`. Use for spans longer than a day. *neso · national intensity · 30 min*
- **`fuelhh` (Elexon)** — GB generation by fuel. `30 min`. Cross-vendor MEF backtest: join on `timestamp_utc` for per-SP fuel attribution. *elexon · generation · 30 min*
