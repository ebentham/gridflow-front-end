---
slug: intensity_fw24h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/fw24h
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_fw24h.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityFw24HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_fw24h"] (lines 90-96, path /intensity/{from_dt}/fw24h)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity, <span class="italic fg-accent">next 24 hours.</span>

**Lede:** GB carbon-intensity forecast for the 24 hours following a chosen datetime — the canonical day-ahead carbon signal for dispatch scheduling and overnight load shifting.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/{from}/fw24h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_fw24h` |
| API PATH | `/intensity/{from}/fw24h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~48 rows / call (24h ahead) |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Forecast horizon |
| 3 | ~48 | Rows per call |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_fw48h
- intensity_pt24h
- carbon_intensity
- intensity_at
- intensity_current

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · 24h forward forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · from 6 May 2026 00:00"
- **Seed:** 31
- **Toggles:** `24h` (active) / `vs actuals`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month). `actual_gco2_kwh` is **always null** for this dataset (forecast-only horizon).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forward forecast carbon intensity. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null on this endpoint (forecast horizon). | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_fw24h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-07T00:00:00+00:00 | 2026-05-07T00:30:00+00:00 | 215.0 | _null_ | moderate |
| 2026-05-07T03:00:00+00:00 | 2026-05-07T03:30:00+00:00 | 188.0 | _null_ | moderate |
| 2026-05-07T06:00:00+00:00 | 2026-05-07T06:30:00+00:00 | 152.0 | _null_ | moderate |
| 2026-05-07T09:00:00+00:00 | 2026-05-07T09:30:00+00:00 | 98.0 | _null_ | low |
| **2026-05-07T12:00:00+00:00** | **2026-05-07T12:30:00+00:00** | **72.0** | **_null_** | **very low** |
| 2026-05-07T15:00:00+00:00 | 2026-05-07T15:30:00+00:00 | 95.0 | _null_ | low |
| 2026-05-07T18:00:00+00:00 | 2026-05-07T18:30:00+00:00 | 235.0 | _null_ | high |
| 2026-05-07T23:30:00+00:00 | 2026-05-08T00:00:00+00:00 | 218.0 | _null_ | moderate |

**Sources:** Eight SPs sampled across the 24h forecast window starting 2026-05-07 00:00Z (vault Silver Sample shape, vault/neso/intensity_fw24h.md L83-85). Every `actual_gco2_kwh` is null by design — this endpoint returns forecast horizons only. Highlighted 12:00 row is the day-ahead solar trough — flagging the cleanest forecast window for next-day load shifting.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/{from}/fw24h` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_fw24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityFw24HTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/2026-05-07T00:00Z/fw24h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Day-ahead cleanest 4 SPs — best windows for tomorrow's flexible load
SELECT timestamp_utc, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/intensity_fw24h/**/*.parquet')
ORDER BY forecast_gco2_kwh
LIMIT 4;
```

**Tab 3 — Python · polars**
```python
import polars as pl

fw24 = pl.read_parquet("data/silver/neso/intensity_fw24h/**/*.parquet")
actuals = pl.read_parquet("data/silver/neso/carbon_intensity/**/*.parquet")
# Forecast skill at 24h horizon: forecast vs same-SP actual
skill = (
    fw24.select(["timestamp_utc", "forecast_gco2_kwh"])
        .join(actuals.select(["timestamp_utc", "actual_gco2_kwh"]),
              on="timestamp_utc")
        .filter(pl.col("actual_gco2_kwh").is_not_null())
        .with_columns(
            (pl.col("forecast_gco2_kwh") - pl.col("actual_gco2_kwh")).abs().alias("abs_err")
        )
)
print(skill["abs_err"].mean())
```

# Caveats

## 01 `actual_gco2_kwh` is always null

This endpoint returns forecast-horizon rows only — there is no published actual for periods later than the current SP. Pair with `carbon_intensity` for after-the-fact verification. *(Source: `endpoints.py L90-96`; vault Bronze Sample L56.)*

## 02 Path placeholder `{from_dt}` internally

Docs document `/intensity/{from}/fw24h`; the connector templates as `{from_dt}` to avoid Python's `from` keyword conflict. URL is identical. *(Source: vault Implementation Delta L106; `endpoints.py L91`.)*

## 03 `{from}` snaps to half-hour boundary

The vendor anchors the 24h window to the SP enclosing `{from}`. Mid-period datetimes return the same window. *(Source: NESO docs — settlement-period semantics.)*

## 04 Transformer is dynamically generated

`IntensityFw24HTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_fw48h`** — 48h-ahead forecast · same schema. `30 min`. Longer horizon at the same SP cadence. *neso · national forecast · 30 min*
- **`intensity_pt24h`** — Past-24h actuals · same schema. `30 min`. Mirror window into the past — natural backtest companion. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range query with actuals. `30 min`. Pair to compute forecast skill. *neso · national intensity · 30 min*
- **`windfor` (Elexon)** — Wind forecast. `hourly`. Compare GB wind forecast to NESO 24h carbon forecast — high wind days drive low forecast intensity. *elexon · forecast · hourly*
