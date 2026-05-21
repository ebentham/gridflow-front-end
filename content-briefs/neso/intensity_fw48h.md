---
slug: intensity_fw48h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/fw48h
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_fw48h.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityFw48HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_fw48h"] (lines 97-103, path /intensity/{from_dt}/fw48h)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity, <span class="italic fg-accent">next 48 hours.</span>

**Lede:** GB carbon-intensity forecast for 48 hours ahead — the canonical two-day outlook for ESG reporting, weekend dispatch planning, and longer-horizon load shifting.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/{from}/fw48h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_fw48h` |
| API PATH | `/intensity/{from}/fw48h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~96 rows / call (48h ahead) |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 h | Forecast horizon |
| 3 | ~96 | Rows per call |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_fw24h
- intensity_pt24h
- carbon_intensity
- intensity_at
- regional_intensity_fw48h

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · 48h forward forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · from 6 May 2026 00:00"
- **Seed:** 32
- **Toggles:** `48h` (active) / `24h` / `vs actuals`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month). `actual_gco2_kwh` is **always null** (forecast-only).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 48h-horizon forecast carbon intensity. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null (forecast horizon). | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_fw48h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-07T00:00:00+00:00 | 2026-05-07T00:30:00+00:00 | 215.0 | _null_ | moderate |
| 2026-05-07T12:00:00+00:00 | 2026-05-07T12:30:00+00:00 | 72.0 | _null_ | very low |
| 2026-05-07T18:00:00+00:00 | 2026-05-07T18:30:00+00:00 | 235.0 | _null_ | high |
| 2026-05-08T00:00:00+00:00 | 2026-05-08T00:30:00+00:00 | 198.0 | _null_ | moderate |
| **2026-05-08T12:30:00+00:00** | **2026-05-08T13:00:00+00:00** | **65.0** | **_null_** | **very low** |
| 2026-05-08T15:00:00+00:00 | 2026-05-08T15:30:00+00:00 | 88.0 | _null_ | low |
| 2026-05-08T18:00:00+00:00 | 2026-05-08T18:30:00+00:00 | 245.0 | _null_ | high |
| 2026-05-08T23:30:00+00:00 | 2026-05-09T00:00:00+00:00 | 220.0 | _null_ | moderate |

**Sources:** Eight SPs sampled across the 48h horizon starting 2026-05-07 00:00Z (vault Silver Sample shape, vault/neso/intensity_fw48h.md L83-85). All `actual_gco2_kwh` null by design. Highlighted 2026-05-08 12:30 = the second day's solar trough — the longer horizon lets you compare day 1 vs day 2 clean windows for multi-day flexible load.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/{from}/fw48h` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_fw48h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityFw48HTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/2026-05-07T00:00Z/fw48h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Two-day cleanest 8 SPs — multi-day flexible-load scheduling
SELECT timestamp_utc, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/intensity_fw48h/**/*.parquet')
ORDER BY forecast_gco2_kwh
LIMIT 8;
```

**Tab 3 — Python · polars**
```python
import polars as pl

fw48 = pl.read_parquet("data/silver/neso/intensity_fw48h/**/*.parquet")
# Forecast attenuation: skill at +24h vs +48h horizon
fw48 = fw48.with_columns(
    ((pl.col("timestamp_utc") - pl.col("ingested_at")).dt.total_hours()).alias("horizon_h")
)
print(fw48.group_by(pl.col("horizon_h") // 12 * 12).agg(
    pl.col("forecast_gco2_kwh").std().alias("dispersion")
))
```

# Caveats

## 01 `actual_gco2_kwh` is always null

Forecast-only horizon — no actual is ever returned. Use `carbon_intensity` after the fact for verification. *(Source: `endpoints.py L97-103`.)*

## 02 Skill degrades with horizon

Forecast accuracy at +48h is meaningfully worse than +24h — weather-driven renewable forecasts attenuate. Use horizon-bucketed error metrics, not pooled MAE. *(Source: domain knowledge — meteorology / GB renewable forecast skill.)*

## 03 Path placeholder `{from_dt}` internally

Docs document `/intensity/{from}/fw48h`; connector templates as `{from_dt}` (Python keyword conflict). URL identical. *(Source: vault Implementation Delta L106.)*

## 04 Transformer is dynamically generated

`IntensityFw48HTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_fw24h`** — 24h-ahead forecast · same schema. `30 min`. Compare horizons to measure skill degradation. *neso · national forecast · 30 min*
- **`intensity_pt24h`** — Past-24h actuals · same schema. `30 min`. Mirror window into the past — backtest companion. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range query with actuals. `30 min`. The published actual to test this forecast against. *neso · national intensity · 30 min*
- **`regional_intensity_fw48h`** — Regional version · 48h horizon. `30 min`. Per-DNO-region 48h forecasts — same horizon, finer spatial resolution. *neso · regional forecast · 30 min*
