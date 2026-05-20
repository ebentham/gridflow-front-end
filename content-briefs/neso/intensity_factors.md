---
slug: intensity_factors
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/factors
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_factors.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensityFactor (lines 48-52)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityFactorsTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=FACTORS, reference_dataset=True)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_factors"] (lines 76-82, path /intensity/factors, reference=True)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Per-fuel emissions factors, <span class="italic fg-accent">reference table.</span>

**Lede:** NESO's published gCO2/kWh emissions factor per generation fuel — the static reference table behind the entire NESO intensity series and the canonical MEF lookup.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/factors](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_factors` |
| API PATH | `/intensity/factors` |
| FREQUENCY | static (reference) |
| PUBLICATION LAG | on change |
| VOLUME | ~20 rows (one per fuel) |
| PRIMARY KEY | `(fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | static | Reference cadence |
| 2 | ~20 | Fuel types in factor table |
| 3 | gCO2/kWh | Reporting unit |
| 4 | 4 | Schema columns |

# Sidebar siblings

- carbon_intensity
- intensity_current
- generation
- intensity_stats
- intensity_today

# Sample chart

- **Type:** `barsH`
- **Title:** "NESO emissions factors · per generation fuel"
- **Subtitle:** "Horizontal bars · gCO2/kWh · static reference"
- **Seed:** 30
- **Toggles:** `all` (active) / `fossil` / `clean`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensityFactor` (lines 48-52, subclass of `_NesoBase` — **no `timestamp_utc`**). Transformed via the shared `_transform_factors` (`silver/neso/carbon_intensity.py L356-371`). Reference dataset — written as a single `intensity_factors.parquet` (not date-partitioned; see `silver/neso/carbon_intensity.py L87-100`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `fuel` | `str` | No | _raw object key_ | Normalised to lowercase snake_case (e.g. `"Gas (Combined Cycle)"` → `gas_combined_cycle`). | `schemas/neso.py L51`; `silver/neso/carbon_intensity.py L362-363` |
| `factor_gco2_kwh` | `float \| None` | Yes | _raw object value_ | Fuel carbon factor in gCO2/kWh. | `schemas/neso.py L52` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_factors/intensity_factors.parquet` (single file — not partitioned)
**PARTITION BY:** _none — reference dataset_ (`silver/neso/carbon_intensity.py L87-100`)
**DEDUP KEY:** `(fuel)` — keep last (`silver/neso/carbon_intensity.py L368`)

# Sample data

| fuel | factor_gco2_kwh | data_provider | ingested_at |
|---|---|---|---|
| `biomass` | 120.0 | neso | 2026-05-04T00:00:00+00:00 |
| `coal` | 937.0 | neso | 2026-05-04T00:00:00+00:00 |
| `gas_combined_cycle` | 394.0 | neso | 2026-05-04T00:00:00+00:00 |
| `gas_open_cycle` | 651.0 | neso | 2026-05-04T00:00:00+00:00 |
| `nuclear` | 0.0 | neso | 2026-05-04T00:00:00+00:00 |
| `oil` | 935.0 | neso | 2026-05-04T00:00:00+00:00 |
| **`solar`** | **0.0** | **neso** | **2026-05-04T00:00:00+00:00** |
| `wind` | 0.0 | neso | 2026-05-04T00:00:00+00:00 |

**Sources:** `gas_combined_cycle` (`394`) and zero-factor renewables (`wind`, `solar`, `nuclear`) verbatim from vault Bronze Sample (vault/neso/intensity_factors.md L57). Remaining rows synthesised from canonical NESO methodology values (`coal=937`, `oil=935`, `biomass=120`, `gas_open_cycle=651`). The highlighted `solar` row carries `factor_gco2_kwh=0` — renewables and nuclear are treated as zero-carbon under NESO methodology; lifecycle factors are out of scope. Note the snake_case fuel keys — joining to `fuelhh` (uppercase codes) requires case mapping.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/factors` (no path params; static reference)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_factors/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityFactorsTransformer` (dynamically generated; `reference_dataset=True` — written single-file, not partitioned)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/factors
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- MEF lookup: rank fuels by emissions factor
SELECT fuel, factor_gco2_kwh
FROM read_parquet('data/silver/neso/intensity_factors/intensity_factors.parquet')
ORDER BY factor_gco2_kwh DESC NULLS LAST;
```

**Tab 3 — Python · polars**
```python
import polars as pl

factors = pl.read_parquet(
    "data/silver/neso/intensity_factors/intensity_factors.parquet"
)
# Approximate national intensity from a fuel-mix forecast (% per fuel)
mix = pl.DataFrame({"fuel": [...], "perc": [...]})  # bind in app
nat_intensity = (
    mix.join(factors, on="fuel")
       .with_columns((pl.col("perc") * pl.col("factor_gco2_kwh") / 100).alias("contrib"))
       .select(pl.col("contrib").sum().alias("approx_gco2_kwh"))
)
print(nat_intensity)
```

# Caveats

## 01 No `timestamp_utc` — reference schema

`CarbonIntensityFactor` inherits `_NesoBase`, not `_TimestampedNesoBase` — there is no `timestamp_utc` column. The dataset is a static lookup. *(Source: `schemas/neso.py L48-52`.)*

## 02 Written as a single file, not partitioned

`reference_dataset=True` (`endpoints.py L81`) routes through `_write_silver` L87-100 — emits one `intensity_factors.parquet` at the silver root, overwriting on each ingest. No `year=YYYY/month=MM/` partition tree. *(Source: `silver/neso/carbon_intensity.py L87-100`.)*

## 03 Fuel keys are normalised to snake_case

Raw API keys like `"Gas (Combined Cycle)"` become `gas_combined_cycle` (`silver/neso/carbon_intensity.py L362-363`). Joins to `fuelhh` codes (uppercase) require explicit case mapping. *(Source: `silver/neso/carbon_intensity.py L362-363`.)*

## 04 Renewables and nuclear are zero-carbon by methodology

NESO assigns `factor_gco2_kwh = 0` to wind, solar, hydro, nuclear. Lifecycle emissions (manufacturing, fuel cycle) are out of scope — see Caveats #04 if you need full LCA factors. *(Source: NESO methodology; vault Modelling notes L109.)*

## 05 Factor revisions silently update the file

The single-file write means a factor revision overwrites prior values with no version history in silver. Snapshot bronze for time-travel; do not assume factors are immutable. *(Source: `silver/neso/carbon_intensity.py L87-100`; vault Modelling notes L109.)*

# Related datasets

- **`generation`** — Per-fuel mix percentages · 30 min. `30 min`. Multiply by these factors for an approximate per-SP grid carbon intensity. *neso · national generation mix · 30 min*
- **`carbon_intensity`** — Published intensity series · 30 min. `30 min`. NESO's authoritative output combining this table with the fuel mix. *neso · national intensity · 30 min*
- **`fuelhh` (Elexon)** — GB generation by fuel · MW. `30 min`. Multiply MW × factor to get gCO2 emissions per SP per fuel — MEF derivation. *elexon · generation · 30 min*
- **`intensity_stats`** — Aggregated intensity over windows. `30 min`. Use factors to sanity-check published averages. *neso · national intensity · 30 min*
