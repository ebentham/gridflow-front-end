---
slug: generation_current
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: generation
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/generation_current.md
  - gridflow/src/gridflow/schemas/neso.py::GenerationMix (lines 55-59)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::GenerationCurrentTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=GENERATION)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["generation_current"] (lines 135-140, path /generation)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Generation Mix - National **beta**)
discrepancies_found:
  - source_a: "vault Implementation Delta L109"
    source_a_says: "live /generation returns {data: {...}} (single object); fixtures and silver tests expected {data: [{...}]} (list)"
    source_b: "silver/neso/carbon_intensity.py L153-161 _data_entries"
    source_b_says: "Helper accepts both shapes — dict wrapped into single-item list, list passed through unchanged"
    orchestrator_recommendation: "trust gridflow — the parser handles both envelopes correctly. Caveats #02 flags the dual envelope for downstream callers reading bronze directly."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB generation mix, <span class="italic fg-accent">right now.</span>

**Lede:** Current GB generation mix percentage by fuel for the live half-hour — the canonical "what's powering the grid right now" snapshot for live dashboards and carbon-aware UI.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /generation](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.generation_current` |
| API PATH | `/generation` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | current-period estimate |
| VOLUME | ~10 rows / call (one per fuel) |
| PRIMARY KEY | `(timestamp_utc, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | ~10 | Fuel categories per call |
| 3 | beta | NESO API status |
| 4 | 6 | Schema columns |

# Sidebar siblings

- generation
- generation_pt24h
- intensity_current
- intensity_factors
- regional_current

# Sample chart

- **Type:** `donut`
- **Title:** "GB generation mix · live"
- **Subtitle:** "Donut · percent share · 30 min SP · UTC · 6 May 2026 12:00"
- **Seed:** 37
- **Toggles:** `now` (active) / `24h ago` / `7d avg`

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

**PARQUET PATH:** `data/silver/neso/generation_current/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, fuel)` — keep last (`silver/neso/carbon_intensity.py L387`)

# Sample data

| timestamp_utc | period_end_utc | fuel | generation_percentage | data_provider |
|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | biomass | 8.3 | neso |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | coal | 0.4 | neso |
| **2026-05-08T17:30:00+00:00** | **2026-05-08T18:00:00+00:00** | **gas** | **42.4** | **neso** |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | hydro | 1.6 | neso |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | nuclear | 11.4 | neso |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | solar | 6.1 | neso |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | wind | 13.7 | neso |
| 2026-05-08T17:30:00+00:00 | 2026-05-08T18:00:00+00:00 | imports | 16.1 | neso |

**Sources:** Single live snapshot for SP at 17:30 UTC (vault Bronze sample at L60, verified 2026-05-08); each call produces a multi-row "long" silver table (one row per fuel). Highlighted `gas` row at 42.4% — evening peak, gas dominates as solar fades. Together with `intensity_factors`, gas at 42.4% × ~394 gCO2/kWh = ~167 gCO2/kWh contribution — drives the moderate evening intensity.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/generation` (no path params — returns current half-hour mix)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/generation_current/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.GenerationCurrentTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/generation
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Latest fuel mix as a stacked bar
SELECT fuel, generation_percentage
FROM read_parquet('data/silver/neso/generation_current/**/*.parquet')
WHERE timestamp_utc = (
  SELECT max(timestamp_utc) FROM read_parquet('data/silver/neso/generation_current/**/*.parquet')
)
ORDER BY generation_percentage DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

mix = pl.read_parquet("data/silver/neso/generation_current/**/*.parquet")
factors = pl.read_parquet(
    "data/silver/neso/intensity_factors/intensity_factors.parquet"
)
# Live carbon attribution: combine current mix with emission factors
attribution = (
    mix.sort("timestamp_utc", descending=True)
       .group_by("fuel").first()
       .join(factors, on="fuel", how="left")
       .with_columns(
           (pl.col("generation_percentage") * pl.col("factor_gco2_kwh") / 100).alias("contrib_g")
       )
)
print(attribution.sort("contrib_g", descending=True))
```

# Caveats

## 01 NESO API status: beta

`Generation Mix - National` carries the beta qualifier (`endpoints.py L137`). NESO may modify or deprecate without the versioning notice applied to main intensity routes. *(Source: `endpoints.py L137`.)*

## 02 Dual response envelope

Live `/generation` returns `{"data": {...}}` (single object); the connector helper `_data_entries` (`silver/neso/carbon_intensity.py L153-161`) lifts the dict into a single-item list. Downstream readers of raw bronze must handle both shapes. *(Source: vault Implementation Delta L109; `silver/neso/carbon_intensity.py L153-161`.)*

## 03 One row per fuel — long shape, not wide

Each call produces `N` silver rows (one per fuel in `generationmix`). Pivot to wide via `polars.pivot` or DuckDB's `PIVOT` clause for visualisation. *(Source: `silver/neso/carbon_intensity.py L387`.)*

## 04 Transformer is dynamically generated

`GenerationCurrentTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`generation`** — Range query · same schema. `30 min`. Use for historical / multi-period; this dataset for "right now". *neso · national generation mix · 30 min*
- **`generation_pt24h`** — Past-24h mix · same schema. `30 min`. Look-back companion to this snapshot. *neso · national generation mix · 30 min*
- **`intensity_current`** — Current intensity gCO2/kWh. `30 min`. Paired display: mix vs resulting intensity, same SP. *neso · national intensity · 30 min*
- **`intensity_factors`** — Per-fuel emissions factors · static. `static`. Multiply by this dataset for live MEF attribution. *neso · national intensity · static*
