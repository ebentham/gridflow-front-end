---
slug: intensity_stats_block
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/stats/block
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_stats_block.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensityStats (lines 39-45)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityStatsBlockTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=STATS)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_stats_block"] (lines 126-133, path /intensity/stats/{from_dt}/{to_dt}/{block}, default block=24)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity, <span class="italic fg-accent">hour-block stats.</span>

**Lede:** GB carbon-intensity statistics split into configurable hour blocks — the canonical sub-day regime view for diurnal-pattern analysis and intra-day flexible-load planning.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/stats/{from}/{to}/{block}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_stats_block` |
| API PATH | `/intensity/stats/{from}/{to}/{block}` |
| FREQUENCY | block-windowed (one row per block) |
| PUBLICATION LAG | derived from observed intensities |
| VOLUME | varies by block size |
| PRIMARY KEY | `(timestamp_utc, period_end_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | block | Aggregation cadence |
| 2 | 24 h | Default block size |
| 3 | max / avg / min | Aggregates per block |
| 4 | 8 | Schema columns |

# Sidebar siblings

- intensity_stats
- carbon_intensity
- intensity_pt24h
- intensity_factors
- generation

# Sample chart

- **Type:** `heatmap`
- **Title:** "GB carbon intensity · 6h block stats · hour-of-day"
- **Subtitle:** "Heatmap · gCO2/kWh · 4 blocks × 30 days"
- **Seed:** 35
- **Toggles:** `6h` (active) / `12h` / `24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensityStats` (lines 39-45, subclass of `_TimestampedNesoBase`). Transformed via the shared `_transform_stats` (`silver/neso/carbon_intensity.py L326-353`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Block start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Block end. | `schemas/neso.py L21` |
| `max_gco2_kwh` | `float \| None` | Yes | `intensity.max` | Maximum intensity in block. | `schemas/neso.py L42` |
| `average_gco2_kwh` | `float \| None` | Yes | `intensity.average` | Mean intensity in block. | `schemas/neso.py L43` |
| `min_gco2_kwh` | `float \| None` | Yes | `intensity.min` | Minimum intensity in block. | `schemas/neso.py L44` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Block index categorical. | `schemas/neso.py L45` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_stats_block/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, period_end_utc)` — keep last (`silver/neso/carbon_intensity.py L341`)

# Sample data

| timestamp_utc | period_end_utc | max_gco2_kwh | average_gco2_kwh | min_gco2_kwh | intensity_index |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 2026-05-06T06:00:00+00:00 | 245.0 | 212.0 | 168.0 | moderate |
| 2026-05-06T06:00:00+00:00 | 2026-05-06T12:00:00+00:00 | 168.0 | 110.0 | 68.0 | low |
| **2026-05-06T12:00:00+00:00** | **2026-05-06T18:00:00+00:00** | **125.0** | **78.0** | **64.0** | **very low** |
| 2026-05-06T18:00:00+00:00 | 2026-05-07T00:00:00+00:00 | 293.0 | 225.0 | 178.0 | moderate |

**Sources:** Four 6-hour blocks across 2026-05-06 (block=6 request; vault Silver Sample shape, vault/neso/intensity_stats_block.md L83). Highlighted 12:00-18:00 block is the cleanest of the day (`average=78`, `very low`) — the canonical diurnal pattern, solar peaks mid-afternoon. Compare to evening block (18:00-24:00, `average=225`) for the diurnal swing magnitude.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/stats/{from}/{to}/{block}` (path segments; `{block}` is hours per block, default 24)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_stats_block/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityStatsBlockTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/stats/2026-05-06T00:00Z/2026-05-07T00:00Z/6
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Diurnal pattern: average intensity by 6h block-of-day over 30 days
SELECT extract('hour' FROM timestamp_utc) AS block_start_h,
       avg(average_gco2_kwh) AS mean_g,
       count(*) AS n
FROM read_parquet('data/silver/neso/intensity_stats_block/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

blocks = pl.read_parquet("data/silver/neso/intensity_stats_block/**/*.parquet")
# Diurnal regime: assign block-of-day, then median per block
hourly = blocks.with_columns(
    pl.col("timestamp_utc").dt.hour().alias("block_h")
)
print(hourly.group_by("block_h").agg(
    pl.col("average_gco2_kwh").median().alias("median_g")
).sort("block_h"))
```

# Caveats

## 01 `{block}` defaults to 24 in the connector

`endpoints.py L132` sets `default_values={"block": 24}` — calling with no override yields one row per day. Pass `block=6` for the diurnal split. *(Source: `endpoints.py L132`; `endpoints.py L16 DEFAULT_STATS_BLOCK_HOURS=24`.)*

## 02 Block boundaries are clock-aligned, not solar-aligned

Blocks start at UTC midnight; sunrise/sunset bias falls inside blocks. For solar-aligned analysis, either request hour-of-day stats over `intensity_period` rows or compute aggregates client-side. *(Source: NESO docs — block windowing semantics.)*

## 03 14-day connector chunking applies

`_MAX_DAYS_PER_REQUEST=14` (`connectors/neso/carbon_intensity.py L21`) applies to stats_block as well as raw stats. Multi-week pulls split into multiple windowed requests. *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 04 Transformer is dynamically generated

`IntensityStatsBlockTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_stats`** — Single-window stats (no block split). `windowed`. Use when you want one row per range; this dataset for sub-day splits. *neso · national intensity stats · windowed*
- **`carbon_intensity`** — Raw per-SP series · 30 min. `30 min`. Underlying observations behind these aggregates. *neso · national intensity · 30 min*
- **`generation`** — Per-fuel mix · 30 min. `30 min`. Pair with block stats to explain block-level intensity via dominant fuels. *neso · national generation mix · 30 min*
- **`intensity_pt24h`** — Past-24h actuals. `30 min`. Rolling equivalent — finer-grained than 6h blocks. *neso · national intensity · 30 min*
