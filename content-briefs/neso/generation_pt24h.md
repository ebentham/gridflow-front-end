---
slug: generation_pt24h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: generation/pt24h
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/generation_pt24h.md
  - gridflow/src/gridflow/schemas/neso.py::GenerationMix (lines 55-59)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::GenerationPt24HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=GENERATION)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["generation_pt24h"] (lines 141-147, path /generation/{from_dt}/pt24h)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Generation Mix - National **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB generation mix, <span class="italic fg-accent">past 24 hours.</span>

**Lede:** GB generation mix percentage by fuel for the 24 hours preceding a chosen datetime — the canonical rolling-window mix view for diurnal-pattern analysis and recent-history backtests.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /generation/{from}/pt24h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.generation_pt24h` |
| API PATH | `/generation/{from}/pt24h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | post-period (look-back) |
| VOLUME | ~48 × N fuels (24h × ~10) |
| PRIMARY KEY | `(timestamp_utc, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Look-back horizon |
| 3 | ~480 | Rows per call (48 × 10) |
| 4 | 6 | Schema columns |

# Sidebar siblings

- generation
- generation_current
- intensity_pt24h
- intensity_factors
- carbon_intensity

# Sample chart

- **Type:** `stackedArea`
- **Title:** "GB generation mix · prior 24h"
- **Subtitle:** "Stacked area · percent share · 30 min SP · UTC · to 6 May 2026 00:00"
- **Seed:** 38
- **Toggles:** `24h` (active) / `clean share` / `fossil share`

# Schema

Defined in `gridflow/schemas/neso.py` · `GenerationMix` (lines 55-59). Transformed via the shared `_transform_generation` (`silver/neso/carbon_intensity.py L374-397`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `fuel` | `str` | No | `generationmix.fuel` | Fuel type code. | `schemas/neso.py L58` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Share of generation mix in percent. | `schemas/neso.py L59` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/generation_pt24h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, fuel)` — keep last (`silver/neso/carbon_intensity.py L387`)

# Sample data

| timestamp_utc | period_end_utc | fuel | generation_percentage | data_provider |
|---|---|---|---|---|
| 2026-05-05T00:00:00+00:00 | 2026-05-05T00:30:00+00:00 | wind | 42.8 | neso |
| 2026-05-05T00:00:00+00:00 | 2026-05-05T00:30:00+00:00 | gas | 22.4 | neso |
| 2026-05-05T06:00:00+00:00 | 2026-05-05T06:30:00+00:00 | wind | 38.1 | neso |
| 2026-05-05T06:00:00+00:00 | 2026-05-05T06:30:00+00:00 | gas | 31.5 | neso |
| **2026-05-05T12:00:00+00:00** | **2026-05-05T12:30:00+00:00** | **solar** | **22.3** | **neso** |
| 2026-05-05T12:00:00+00:00 | 2026-05-05T12:30:00+00:00 | wind | 28.5 | neso |
| 2026-05-05T18:00:00+00:00 | 2026-05-05T18:30:00+00:00 | gas | 48.2 | neso |
| 2026-05-05T18:00:00+00:00 | 2026-05-05T18:30:00+00:00 | wind | 18.3 | neso |

**Sources:** Pairs of dominant-fuel rows sampled across the 24h look-back ending 2026-05-06 00:00Z (long-form, vault Silver Sample shape, vault/neso/generation_pt24h.md). The full silver output has one row per (SP × fuel) — ~480 rows per call. Highlighted 12:00 `solar` row at 22.3% is the day's solar peak — pairs with `intensity_pt24h` to show the same SP's `very low` intensity.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/generation/{from}/pt24h` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/generation_pt24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.GenerationPt24HTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/generation/2026-05-06T00:00Z/pt24h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Hour-of-day fuel share over the prior 24h
SELECT extract('hour' FROM timestamp_utc) AS hod, fuel,
       avg(generation_percentage) AS mean_share
FROM read_parquet('data/silver/neso/generation_pt24h/**/*.parquet')
WHERE fuel IN ('wind', 'solar', 'gas', 'nuclear')
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/generation_pt24h/**/*.parquet")
# Derived clean / fossil share — residual-load feature engineering
wide = df.pivot(
    index="timestamp_utc", on="fuel",
    values="generation_percentage", aggregate_function="sum",
).with_columns([
    (pl.sum_horizontal(["wind", "solar", "hydro", "biomass", "nuclear"])).alias("clean_pct"),
    (pl.sum_horizontal(["gas", "coal"])).alias("fossil_pct"),
])
print(wide.tail())
```

# Caveats

## 01 NESO API status: beta

`Generation Mix - National` is beta (`endpoints.py L143`); subject to vendor changes without notice. *(Source: `endpoints.py L143`.)*

## 02 Window anchored to SP enclosing `{from}`

The 24h look-back ends at the SP containing `{from}`. Mid-period datetimes snap to the boundary. *(Source: NESO docs — settlement-period semantics.)*

## 03 One row per (SP × fuel) — ~480 rows per call

Each call yields `~48 SPs × ~10 fuels = ~480 rows`. Plan storage / pagination accordingly. *(Source: `silver/neso/carbon_intensity.py L387`.)*

## 04 Path placeholder `{from_dt}` internally

Docs document `/generation/{from}/pt24h`; connector templates as `{from_dt}`. *(Source: vault Implementation Delta L106.)*

## 05 Transformer is dynamically generated

`GenerationPt24HTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`generation`** — Range query · same schema. `30 min`. Use for arbitrary windows; this dataset for a fixed-24h look-back. *neso · national generation mix · 30 min*
- **`generation_current`** — Live snapshot · same schema. `30 min`. The "now" companion to this dataset's "past 24h". *neso · national generation mix · 30 min*
- **`intensity_pt24h`** — Past-24h intensity · 30 min. `30 min`. Mirror dataset: same look-back, intensity form. *neso · national intensity · 30 min*
- **`intensity_factors`** — Per-fuel emission factors · static. `static`. Multiply by this dataset for MEF backtest over the 24h window. *neso · national intensity · static*
