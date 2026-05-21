---
slug: intensity_stats
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/stats
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_stats.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensityStats (lines 39-45)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityStatsTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=STATS)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_stats"] (lines 119-125, path /intensity/stats/{from_dt}/{to_dt})
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found:
  - source_a: "vault Implementation Delta L109"
    source_a_says: "official docs allow 30 days for statistics; connector chunks with max_query_days=14 (conservative)"
    source_b: "connectors/neso/carbon_intensity.py L21"
    source_b_says: "_MAX_DAYS_PER_REQUEST = 14 applies uniformly; no stats-specific override"
    orchestrator_recommendation: "behaviour-affecting — connector uses the conservative 14-day chunk even though the vendor allows 30 days for stats. Caveats #02 flags this. Could relax in gridflow but no defect."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Carbon intensity, <span class="italic fg-accent">windowed stats.</span>

**Lede:** Aggregated GB carbon-intensity statistics (max / average / min) over a windowed range — the canonical regime feature for rolling carbon labels and per-period QA.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/stats](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_stats` |
| API PATH | `/intensity/stats/{from}/{to}` |
| FREQUENCY | windowed (one row per window) |
| PUBLICATION LAG | derived from observed intensities |
| VOLUME | 1 row / window |
| PRIMARY KEY | `(timestamp_utc, period_end_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | windowed | Aggregation cadence |
| 2 | 30 d vs 14 d | Vendor max vs connector chunk |
| 3 | max / avg / min | Aggregates per window |
| 4 | 8 | Schema columns |

# Sidebar siblings

- intensity_stats_block
- carbon_intensity
- intensity_pt24h
- intensity_factors
- generation

# Sample chart

- **Type:** `barsH`
- **Title:** "GB carbon intensity stats · daily max / avg / min"
- **Subtitle:** "Horizontal bars · gCO2/kWh · last 7 days"
- **Seed:** 34
- **Toggles:** `7d` (active) / `30d` / `90d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensityStats` (lines 39-45, subclass of `_TimestampedNesoBase`). Transformed via the shared `_transform_stats` (`silver/neso/carbon_intensity.py L326-353`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Stats block start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Stats block end. | `schemas/neso.py L21` |
| `max_gco2_kwh` | `float \| None` | Yes | `intensity.max` | Maximum intensity in the window. | `schemas/neso.py L42` |
| `average_gco2_kwh` | `float \| None` | Yes | `intensity.average` | Mean intensity in the window. | `schemas/neso.py L43` |
| `min_gco2_kwh` | `float \| None` | Yes | `intensity.min` | Minimum intensity in the window. | `schemas/neso.py L44` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Window index categorical. | `schemas/neso.py L45` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_stats/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, period_end_utc)` — keep last (`silver/neso/carbon_intensity.py L341`)

# Sample data

| timestamp_utc | period_end_utc | max_gco2_kwh | average_gco2_kwh | min_gco2_kwh | intensity_index |
|---|---|---|---|---|---|
| 2026-05-01T00:00:00+00:00 | 2026-05-02T00:00:00+00:00 | 285.0 | 168.0 | 64.0 | moderate |
| 2026-05-02T00:00:00+00:00 | 2026-05-03T00:00:00+00:00 | 312.0 | 195.0 | 82.0 | moderate |
| 2026-05-03T00:00:00+00:00 | 2026-05-04T00:00:00+00:00 | 295.0 | 178.0 | 72.0 | moderate |
| **2026-05-04T00:00:00+00:00** | **2026-05-05T00:00:00+00:00** | **228.0** | **132.0** | **48.0** | **low** |
| 2026-05-05T00:00:00+00:00 | 2026-05-06T00:00:00+00:00 | 280.0 | 152.0 | 58.0 | moderate |
| 2026-05-06T00:00:00+00:00 | 2026-05-07T00:00:00+00:00 | 293.0 | 161.0 | 64.0 | moderate |
| 2026-05-07T00:00:00+00:00 | 2026-05-08T00:00:00+00:00 | 268.0 | 145.0 | 55.0 | moderate |

**Sources:** Seven daily windows for a 7-day backtest (vault Silver Sample shape, vault/neso/intensity_stats.md L83-87). The single vault sample row (max=250, avg=180, min=120) is consistent with the shape; remaining rows synthesised within plausible daily ranges. Highlighted 2026-05-04 row is the week's cleanest day (`average=132`, `low` index) — windy weekend with strong renewable penetration.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/stats/{from}/{to}` (path segments — vendor allows 30 days; connector chunks at 14)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_stats/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityStatsTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/stats/2026-05-01T00:00Z/2026-05-08T00:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- 30-day rolling regime indicator: average and dispersion
SELECT timestamp_utc, average_gco2_kwh, max_gco2_kwh, min_gco2_kwh,
       max_gco2_kwh - min_gco2_kwh AS spread_g
FROM read_parquet('data/silver/neso/intensity_stats/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 30 DAY
ORDER BY timestamp_utc DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

stats = pl.read_parquet("data/silver/neso/intensity_stats/**/*.parquet")
# Carbon regime label: classify daily windows by average
labelled = stats.with_columns(
    pl.when(pl.col("average_gco2_kwh") < 100).then(pl.lit("clean"))
      .when(pl.col("average_gco2_kwh") < 200).then(pl.lit("moderate"))
      .otherwise(pl.lit("dirty")).alias("regime")
)
print(labelled.group_by("regime").len().sort("len", descending=True))
```

# Caveats

## 01 Aggregates derived from observed intensities, not raw computations

NESO computes max/avg/min from its own published intensity series — these values may not equal a downstream aggregation of `carbon_intensity` rows if revisions occurred between publish times. *(Source: vault Modelling notes L114; NESO methodology.)*

## 02 Vendor allows 30-day window; connector chunks at 14

Vendor max window for stats is 30 days; the connector uses `_MAX_DAYS_PER_REQUEST = 14` uniformly (`connectors/neso/carbon_intensity.py L21`) — conservative, not incomplete. Stats spans larger than 14 days are split into multiple windows. *(Source: vault Implementation Delta L109; `connectors/neso/carbon_intensity.py L21`.)*

## 03 No leakage when joining to per-SP labels

Block stats include the SP they cover. Joining `intensity_stats` aggregates back to per-SP training data without windowing creates lookahead. Use stats only for stable rolling regime features, not labels. *(Source: vault Modelling notes L114.)*

## 04 Transformer is dynamically generated

`IntensityStatsTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_stats_block`** — Same stats, split into hour blocks. `windowed`. Use when you want sub-day blocks (e.g. 6h splits) instead of one row per window. *neso · national intensity stats · windowed*
- **`carbon_intensity`** — Raw per-SP series · 30 min. `30 min`. Source observations underlying these aggregates. *neso · national intensity · 30 min*
- **`intensity_pt24h`** — Past-24h actuals. `30 min`. Rolling-24h equivalent — narrower window, more granular. *neso · national intensity · 30 min*
- **`intensity_factors`** — Per-fuel emissions factors · static. `static`. Pair with stats for fuel-attributed window aggregates. *neso · national intensity · static*
