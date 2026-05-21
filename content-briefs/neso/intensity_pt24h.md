---
slug: intensity_pt24h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/pt24h
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_pt24h.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityPt24HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_pt24h"] (lines 104-110, path /intensity/{from_dt}/pt24h)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity, <span class="italic fg-accent">past 24 hours.</span>

**Lede:** GB carbon intensity for the 24 hours preceding a chosen datetime — the canonical look-back series for forecast-skill scoring, retrospective MEF, and rolling-window features.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/{from}/pt24h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_pt24h` |
| API PATH | `/intensity/{from}/pt24h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | post-period (look-back) |
| VOLUME | ~48 rows / call (24h back) |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Look-back horizon |
| 3 | ~48 | Rows per call |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_fw24h
- intensity_fw48h
- carbon_intensity
- intensity_today
- intensity_at

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · prior 24 hours"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · ending 6 May 2026 00:00"
- **Seed:** 33
- **Toggles:** `24h` (active) / `vs fw24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity (historical). | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate; most rows populated for the past 24h. | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_pt24h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-05T00:00:00+00:00 | 2026-05-05T00:30:00+00:00 | 242.0 | 238.0 | moderate |
| 2026-05-05T06:00:00+00:00 | 2026-05-05T06:30:00+00:00 | 167.0 | 163.0 | moderate |
| 2026-05-05T09:00:00+00:00 | 2026-05-05T09:30:00+00:00 | 108.0 | 104.0 | low |
| **2026-05-05T12:00:00+00:00** | **2026-05-05T12:30:00+00:00** | **70.0** | **66.0** | **very low** |
| 2026-05-05T15:00:00+00:00 | 2026-05-05T15:30:00+00:00 | 91.0 | 88.0 | low |
| 2026-05-05T18:00:00+00:00 | 2026-05-05T18:30:00+00:00 | 222.0 | 228.0 | moderate |
| 2026-05-05T21:00:00+00:00 | 2026-05-05T21:30:00+00:00 | 280.0 | 286.0 | high |
| 2026-05-05T23:30:00+00:00 | 2026-05-06T00:00:00+00:00 | 215.0 | 213.0 | moderate |

**Sources:** Eight SPs across the 24h look-back ending 2026-05-06 00:00Z (vault Silver Sample shape, vault/neso/intensity_pt24h.md L83-85). Most `actual_gco2_kwh` values are populated because the window is in the past. Highlighted 12:00 row = the day's actual solar trough — paired with `intensity_fw24h` for the prior day's forecast, this is the canonical input to a forecast-skill calculation.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/{from}/pt24h` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_pt24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityPt24HTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/2026-05-06T00:00Z/pt24h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Rolling 24h MAE: combine fw24h forecasts vs pt24h actuals
SELECT a.timestamp_utc::date AS day,
       avg(abs(f.forecast_gco2_kwh - a.actual_gco2_kwh)) AS mae_g
FROM read_parquet('data/silver/neso/intensity_pt24h/**/*.parquet') a
JOIN read_parquet('data/silver/neso/intensity_fw24h/**/*.parquet') f
  USING (timestamp_utc)
WHERE a.actual_gco2_kwh IS NOT NULL
GROUP BY 1
ORDER BY 1 DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

pt24 = pl.read_parquet("data/silver/neso/intensity_pt24h/**/*.parquet")
# 24h carbon-aware load shift — find the cleanest 4h window
pt24 = pt24.sort("timestamp_utc")
window = (
    pt24.with_columns(
        pl.col("actual_gco2_kwh").rolling_mean(window_size=8).alias("mean_4h_g")
    )
    .sort("mean_4h_g")
    .head(1)
)
print(window)
```

# Caveats

## 01 Window anchored to the SP enclosing `{from}`

The `pt24h` window ends at the SP containing `{from}` and looks back 24h. Pass mid-period datetimes and they snap to the boundary. *(Source: NESO docs — settlement-period semantics.)*

## 02 Most actuals populated — but tail still null

The most recent 1-2 SPs in the look-back may carry null `actual_gco2_kwh` if the post-period estimate hasn't published yet. Filter `IS NOT NULL` for skill calculations. *(Source: vault Known Issues L99-100.)*

## 03 Path placeholder `{from_dt}` internally

Docs document `/intensity/{from}/pt24h`; connector templates as `{from_dt}`. URL identical. *(Source: vault Implementation Delta L106.)*

## 04 Transformer is dynamically generated

`IntensityPt24HTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_fw24h`** — 24h-ahead forecast · same schema. `30 min`. Mirror-image window — pair for forecast-skill calculation. *neso · national forecast · 30 min*
- **`intensity_today`** — Today's all-SPs · same schema. `30 min`. Use for current-day windows instead of arbitrary 24h tails. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range query · same schema. `30 min`. Cheaper than looping `pt24h` for multi-day windows. *neso · national intensity · 30 min*
- **`generation_pt24h`** — Mirror dataset · generation mix. `30 min`. Same look-back window in fuel-mix shape — multiply by `intensity_factors` for MEF backtest. *neso · national generation mix · 30 min*
