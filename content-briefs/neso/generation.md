---
slug: generation
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: generation
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/generation.md
  - gridflow/src/gridflow/schemas/neso.py::GenerationMix (lines 55-59)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::GenerationTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=GENERATION)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["generation"] (lines 148-154, path /generation/{from_dt}/{to_dt})
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Generation Mix - National **beta**)
discrepancies_found:
  - source_a: "vault Implementation Delta L106"
    source_a_says: "official docs and config/sources.yaml use {from} / {to}; endpoints.py uses {from_dt} / {to_dt} internally"
    source_b: "endpoints.py L149"
    source_b_says: "path_template uses {from_dt} / {to_dt} (Python keyword conflict)"
    orchestrator_recommendation: "cosmetic — same URL emitted; no fix needed."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB generation mix, <span class="italic fg-accent">half-hourly.</span>

**Lede:** GB generation mix percentage by fuel per half-hour over a datetime range — the canonical explanatory feature for carbon intensity, renewable penetration, and price regimes.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /generation](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.generation` |
| API PATH | `/generation/{from}/{to}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | per generation-mix endpoint |
| VOLUME | ~48 × N fuels / day |
| PRIMARY KEY | `(timestamp_utc, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | ~10 | Fuel categories per period |
| 3 | beta | NESO API status |
| 4 | 6 | Schema columns |

# Sidebar siblings

- generation_current
- generation_pt24h
- carbon_intensity
- intensity_factors
- regional_intensity

# Sample chart

- **Type:** `stackedArea`
- **Title:** "GB generation mix · 24h snapshot"
- **Subtitle:** "Stacked area · percent share · 30 min SP · UTC · 6 May 2026"
- **Seed:** 36
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `GenerationMix` (lines 55-59, subclass of `_TimestampedNesoBase`). Transformed via the shared `_transform_generation` (`silver/neso/carbon_intensity.py L374-397`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `fuel` | `str` | No | `generationmix.fuel` | Fuel type code (e.g. `gas`, `wind`, `solar`, `nuclear`, `imports`). | `schemas/neso.py L58` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Share of generation mix in percent (0..100). | `schemas/neso.py L59` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/generation/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, fuel)` — keep last (`silver/neso/carbon_intensity.py L387`)

# Sample data

| timestamp_utc | period_end_utc | fuel | generation_percentage | data_provider |
|---|---|---|---|---|
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | biomass | 8.7 | neso |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | gas | 11.2 | neso |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | nuclear | 11.5 | neso |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | hydro | 1.9 | neso |
| **2026-04-21T23:30:00+00:00** | **2026-04-22T00:00:00+00:00** | **wind** | **46.1** | **neso** |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | solar | 0.0 | neso |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | imports | 18.6 | neso |
| 2026-04-21T23:30:00+00:00 | 2026-04-22T00:00:00+00:00 | coal | 2.0 | neso |

**Sources:** Bronze sample (vault/neso/generation.md L57, live 2026-04-21) provides `biomass`, `gas`, `wind`; remaining rows synthesised to fill a complete 8-fuel mix on a windy overnight SP (sums to 100%). Highlighted `wind` row at 46.1% illustrates a high-wind night — the canonical low-carbon period; pairs with `intensity_factors` to derive `wind=0 gCO2/kWh × 46.1% = 0 gCO2/kWh contribution`, dominating the period's low intensity.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/generation/{from}/{to}` (path segments; max 14-day range)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/generation/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.GenerationTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/generation/2026-04-21T00:00Z/2026-04-22T00:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Daily mean wind share — renewable-penetration trend
SELECT timestamp_utc::date AS day,
       avg(generation_percentage) AS mean_wind_pct
FROM read_parquet('data/silver/neso/generation/**/*.parquet')
WHERE fuel = 'wind'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 30;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/generation/**/*.parquet")
# Wide pivot: one column per fuel for residual-load modelling
wide = df.pivot(
    index=["timestamp_utc", "period_end_utc"],
    on="fuel", values="generation_percentage",
    aggregate_function="sum",
).with_columns(
    (pl.col("wind") + pl.col("solar") + pl.col("hydro") + pl.col("biomass") + pl.col("nuclear"))
    .alias("clean_share_pct")
)
print(wide.head())
```

# Caveats

## 01 NESO API status: beta

The `Generation Mix - National` category carries a beta qualifier (`endpoints.py L150` `category="Generation Mix - National beta"`) — NESO may modify the surface without the versioning notice applied to the main intensity routes. *(Source: `endpoints.py L150`.)*

## 02 14-day max window per request

Vendor max window is 14 days. The connector chunks longer spans (`_MAX_DAYS_PER_REQUEST=14`, `connectors/neso/carbon_intensity.py L21`). *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 03 Fuel codes are vendor-managed and unstable

NESO's fuel category list (`gas`, `wind`, `solar`, `nuclear`, `imports`, `biomass`, `hydro`, `coal`, `other`) is not formally codified. New categories can appear; some are aggregates (`imports` collapses all interconnectors). *(Source: vault Modelling notes L110.)*

## 04 Path placeholder `{from_dt}` internally

Docs document `/generation/{from}/{to}`; connector templates as `{from_dt}` / `{to_dt}`. URL identical. *(Source: vault Implementation Delta L106.)*

## 05 Transformer is dynamically generated

`GenerationTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`generation_current`** — Single SP snapshot · same schema. `30 min`. Live current-mix view; this dataset for historical / range. *neso · national generation mix · 30 min*
- **`generation_pt24h`** — Past-24h mix · same schema. `30 min`. Rolling 24h window — natural look-back companion. *neso · national generation mix · 30 min*
- **`carbon_intensity`** — Resulting intensity · 30 min. `30 min`. Same time index; multiply this dataset by `intensity_factors` to derive carbon_intensity values. *neso · national intensity · 30 min*
- **`fuelhh` (Elexon)** — GB generation MW by fuel. `30 min`. Sibling: absolute MW (Elexon) vs percentage share (NESO). Combine for absolute carbon attribution. *elexon · generation · 30 min*
