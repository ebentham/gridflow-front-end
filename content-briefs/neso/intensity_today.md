---
slug: intensity_today
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/date
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_today.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityTodayTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_today"] (lines 52-57, path /intensity/date)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Today's GB carbon intensity, <span class="italic fg-accent">all 48 periods.</span>

**Lede:** All 48 half-hour GB carbon-intensity records for the current day — the canonical "today so far" series for live dashboards, day-ahead carbon dispatch, and morning-of reporting.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/date](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_today` |
| API PATH | `/intensity/date` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecasts ahead · actuals post-period |
| VOLUME | ~48 rows / day per call |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 | Rows per call (per day) |
| 3 | 24 h | Coverage horizon |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_current
- carbon_intensity
- intensity_date
- intensity_period
- intensity_fw24h

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · today · 48 periods"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · 6 May 2026"
- **Seed:** 26
- **Toggles:** `today` (active) / `yesterday` / `last 7d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced by `must_be_utc` validator. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity, populated ahead of period. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate; null for future periods within today. | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_today/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 2026-05-06T00:30:00+00:00 | 245.0 | 239.0 | moderate |
| 2026-05-06T03:00:00+00:00 | 2026-05-06T03:30:00+00:00 | 215.0 | 213.0 | moderate |
| 2026-05-06T06:00:00+00:00 | 2026-05-06T06:30:00+00:00 | 165.0 | 161.0 | moderate |
| 2026-05-06T09:00:00+00:00 | 2026-05-06T09:30:00+00:00 | 105.0 | 102.0 | low |
| **2026-05-06T12:00:00+00:00** | **2026-05-06T12:30:00+00:00** | **68.0** | **64.0** | **very low** |
| 2026-05-06T15:00:00+00:00 | 2026-05-06T15:30:00+00:00 | 89.0 | 91.0 | low |
| 2026-05-06T18:00:00+00:00 | 2026-05-06T18:30:00+00:00 | 218.0 | _null_ | moderate |
| 2026-05-06T21:00:00+00:00 | 2026-05-06T21:30:00+00:00 | 245.0 | _null_ | moderate |

**Sources:** Eight representative SPs sampled across a single day (vault Silver Sample shape, vault/neso/intensity_today.md). The highlighted 12:00 row is the day's `very low` solar trough. The last two rows (18:00, 21:00) demonstrate that `actual` becomes null for periods later than the current SP at query time — the call returns the full day's 48 rows whether or not actuals are yet published.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/date` (no path params — returns today's 48 SPs)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_today/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityTodayTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/date
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Today's cleanest 6 SPs — best windows for flexible load
SELECT timestamp_utc, forecast_gco2_kwh, actual_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/intensity_today/**/*.parquet')
WHERE timestamp_utc::date = current_date
ORDER BY coalesce(actual_gco2_kwh, forecast_gco2_kwh)
LIMIT 6;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/intensity_today/**/*.parquet")
# Today's profile — fill missing actuals with forecasts for plotting
today = (
    df.filter(pl.col("timestamp_utc").dt.date() == pl.lit(None))  # bind in app
      .with_columns(
          pl.coalesce(["actual_gco2_kwh", "forecast_gco2_kwh"]).alias("gco2_kwh")
      )
      .sort("timestamp_utc")
)
print(today.tail(10))
```

# Caveats

## 01 Actuals lag — future SPs within today are null

For periods later than the current half-hour, `actual_gco2_kwh` is null. Use `coalesce(actual, forecast)` for "now-and-ahead" display logic. *(Source: vault Known Issues L104.)*

## 02 No path params — always returns today (UTC)

`/intensity/date` is a no-arg route. For a specific date, use `intensity_date` (`/intensity/date/{date}`). The boundary follows UTC, not GB local time. *(Source: `connectors/neso/endpoints.py L52-57`.)*

## 03 DST days carry 46 or 50 SPs

Spring-forward day returns 46 rows, autumn-back returns 50, not the docs' 48. The connector handles this via `timestamp_utc` directly. *(Source: vault Known Issues L106; `connectors/neso/carbon_intensity.py L156-168`.)*

## 04 Transformer is dynamically generated

`IntensityTodayTransformer` is created at import time by `register_neso_transformers()` via `type()`. Static analysers cannot inspect it. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_current`** — Single-row "right now" snapshot. `30 min`. Use for a single-SP read; this dataset for the whole day. *neso · national intensity · 30 min*
- **`intensity_date`** — All SPs for an arbitrary date. `30 min`. Same shape, parameterised by `{date}` instead of "today". *neso · national intensity · 30 min*
- **`intensity_fw24h`** — 24h-ahead forecast from a datetime. `30 min`. Pair with this dataset to compare today-so-far against the next-24h outlook. *neso · national forecast · 30 min*
- **`fuelhh` (Elexon)** — GB generation by fuel. `30 min`. Cross-vendor MEF: join on `timestamp_utc` for per-SP fuel attribution. *elexon · generation · 30 min*
