---
slug: intensity_current
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_current.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityCurrentTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_current"] (lines 46-51, path /intensity)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector, lines 25-90)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Current GB carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current half-hour GB grid carbon intensity in gCO2/kWh — the canonical no-arg snapshot for live dashboards, carbon-aware scheduling, and "is it a clean hour" decisions.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_current` |
| API PATH | `/intensity` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual post-period |
| VOLUME | 1 snapshot / call |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | ~0 | Publication lag |
| 3 | 1 | Row per call (current SP) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- carbon_intensity
- intensity_today
- intensity_at
- intensity_fw24h
- intensity_factors

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · current half-hour"
- **Subtitle:** "Sparkline · gCO2/kWh · UTC · 6 May 2026"
- **Seed:** 24
- **Toggles:** `now` (active) / `24h` / `7d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36, subclass of `_TimestampedNesoBase`). Transformed by the shared `GenericNesoJsonTransformer` with `parser_family=INTENSITY` (`silver/neso/carbon_intensity.py` `_transform_intensity` L298-323). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced by `_TimestampedNesoBase.must_be_utc` validator. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end (`timestamp_utc + 30 min`). | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity. Populated ahead of the period. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate; null until published. Treat null as "not yet available". | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` / `low` / `moderate` / `high` / `very high`. Vendor-managed list. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_current/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T11:30:00+00:00 | 2026-05-06T12:00:00+00:00 | 78.0 | _null_ | low | neso |
| 2026-05-06T12:00:00+00:00 | 2026-05-06T12:30:00+00:00 | 68.0 | _null_ | very low | neso |
| **2026-05-06T12:30:00+00:00** | **2026-05-06T13:00:00+00:00** | **64.0** | **_null_** | **very low** | **neso** |
| 2026-05-06T13:00:00+00:00 | 2026-05-06T13:30:00+00:00 | 71.0 | _null_ | very low | neso |

**Sources:** Single-row snapshots from consecutive `/intensity` polls (shape from vault Silver Sample, vault/neso/intensity_current.md L83-85). Each call returns exactly one row — these four entries illustrate four sequential polls over two hours. The highlighted 12:30 row is the day's solar peak — `forecast=64 gCO2/kWh`, `actual` still null because the period has not closed yet (publication lag pattern — see Caveat #01).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity` (no path params, no query string)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s (project default; vendor rate limit undocumented).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_current/<year>/<month>/<day>/raw_<timestamp>_<hash>.json` (+ `.meta.json` sidecar)
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityCurrentTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Live snapshot history (poll log): forecast skill rolling 24h
SELECT timestamp_utc,
       forecast_gco2_kwh,
       actual_gco2_kwh,
       intensity_index
FROM read_parquet('data/silver/neso/intensity_current/**/*.parquet')
ORDER BY timestamp_utc DESC
LIMIT 48;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/intensity_current/**/*.parquet")
# Latest cleanest-hour view — most recent low / very low periods
clean = (
    df.filter(pl.col("intensity_index").is_in(["very low", "low"]))
      .sort("timestamp_utc", descending=True)
      .head(5)
)
print(clean)
```

# Caveats

## 01 Actuals lag — null is "not yet published"

`actual_gco2_kwh` is null for the current and most-recent periods until NESO publishes the post-period estimate. Treat null as "not yet available", not "zero carbon". *(Source: vault Known Issues L99-100.)*

## 02 No-arg route — `/intensity` returns one row

Unlike `carbon_intensity` (range) and `intensity_today` (all-day), this endpoint returns exactly one record for the current half-hour. Use range siblings for time-series queries. *(Source: `connectors/neso/endpoints.py` L46-51.)*

## 03 Transformer is dynamically generated

`IntensityCurrentTransformer` is not source-defined — it is created at import time by `register_neso_transformers()` (`silver/neso/carbon_intensity.py` L110-118) via `type()`. Static analysers (mypy, IDE) cannot inspect it without running registration. *(Source: `silver/neso/carbon_intensity.py L121-136`.)*

## 04 Index thresholds drift as the grid decarbonises

`intensity_index` buckets (`very low` … `very high`) are vendor-managed and shift over time as the GB grid decarbonises. Use raw `gCO2/kWh` for back-fitted analytics; use the index only for stable user-facing displays. *(Source: domain knowledge — NESO methodology.)*

# Related datasets

- **`carbon_intensity`** — Range query · same schema. `30 min`. Use for historical / back-fill / multi-period; this dataset for "right now". *neso · national intensity · 30 min*
- **`intensity_today`** — Today's 48 periods · same schema. `30 min`. Use for "today so far" rather than the single current snapshot. *neso · national intensity · 30 min*
- **`intensity_fw24h`** — 24h-ahead forecast · same schema. `30 min`. Pair with this dataset for nowcast-vs-forecast skill measurement. *neso · national forecast · 30 min*
- **`fuelhh` (Elexon)** — Per-fuel GB generation. `30 min`. Cross-vendor MEF derivation — weight `fuelhh` mix by `intensity_factors` to attribute current intensity to fuels. *elexon · generation · 30 min*
