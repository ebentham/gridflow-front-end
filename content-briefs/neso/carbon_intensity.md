---
slug: carbon_intensity
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/carbon_intensity.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::CarbonIntensityTransformer (lines 103-107; the only source-defined NESO transformer — parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["carbon_intensity"] (lines 111-117, path /intensity/{from_dt}/{to_dt})
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py (CarbonIntensityConnector + _request_specs, lines 25-153)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found:
  - source_a: "vault Implementation Delta L111"
    source_a_says: "official docs and config/sources.yaml use {from} / {to}; endpoints.py uses {from_dt} / {to_dt} internally"
    source_b: "connectors/neso/endpoints.py L112"
    source_b_says: "path_template uses {from_dt} / {to_dt} (Python `from` keyword conflict avoidance)"
    orchestrator_recommendation: "cosmetic — final URL is identical to the documented form. No fix needed."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB carbon intensity, <span class="italic fg-accent">range query.</span>

**Lede:** GB grid carbon intensity per half-hour over a datetime range — the canonical historical series for back-fitted carbon labels, MEF modelling, and reporting baselines.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.carbon_intensity` |
| API PATH | `/intensity/{from}/{to}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual post-period |
| VOLUME | 48 / day · ~1.4k / mo |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 14 d | Max range per request |
| 3 | 48 | Rows / day |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_current
- intensity_factors
- intensity_at
- intensity_date
- intensity_fw24h

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · forecast vs actual · 24h snapshot"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · 6 May 2026"
- **Seed:** 23
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36, subclass of `_TimestampedNesoBase`). Transformed by `CarbonIntensityTransformer` (`silver/neso/carbon_intensity.py L103-107`) using `_transform_intensity` (L298-323). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced by `_TimestampedNesoBase.must_be_utc` validator. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end (`timestamp_utc + 30 min`). | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity. Populated ahead of the period. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate; null until published. Treat null as "not yet available". | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` / `low` / `moderate` / `high` / `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/carbon_intensity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`; forecast → actual replaces forecast row in place)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 2026-05-06T00:30:00+00:00 | 245.0 | 239.0 | moderate | neso |
| 2026-05-06T00:30:00+00:00 | 2026-05-06T01:00:00+00:00 | 250.0 | 248.0 | moderate | neso |
| 2026-05-06T11:00:00+00:00 | 2026-05-06T11:30:00+00:00 | 92.0 | 88.0 | low | neso |
| **2026-05-06T12:00:00+00:00** | **2026-05-06T12:30:00+00:00** | **68.0** | **64.0** | **very low** | **neso** |
| 2026-05-06T13:00:00+00:00 | 2026-05-06T13:30:00+00:00 | 71.0 | 70.0 | very low | neso |
| 2026-05-06T18:00:00+00:00 | 2026-05-06T18:30:00+00:00 | 218.0 | 224.0 | moderate | neso |
| 2026-05-06T19:00:00+00:00 | 2026-05-06T19:30:00+00:00 | 285.0 | 293.0 | high | neso |
| 2026-05-06T23:30:00+00:00 | 2026-05-07T00:00:00+00:00 | 198.0 | _null_ | moderate | neso |

**Sources:** First two rows from vault Silver Sample (vault/neso/carbon_intensity.md L83-85, live 2026-05-08); remaining six rows synthesised to illustrate a 24h arc on a sunny May day. The highlighted 12:00 row is the day's solar trough (lowest emissions, `very low`, 64 gCO2/kWh actual). The final row (23:30) demonstrates the publication-lag pattern: `forecast` present, `actual` still null because the post-period estimate has not been published at query time.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/{from}/{to}` (path segments — not query params; max 14-day range per request)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s (project default; vendor rate limit undocumented).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/carbon_intensity/<year>/<month>/<day>/raw_<timestamp>_<hash>.json` (+ `.meta.json` sidecar)
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.CarbonIntensityTransformer` (the one source-defined NESO transformer; siblings are dynamically generated)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/2026-05-06T00:00Z/2026-05-07T00:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Cleanest hour per day over the last 30 days
SELECT date_trunc('day', timestamp_utc) AS day,
       min(actual_gco2_kwh) AS min_actual,
       arg_min(timestamp_utc, actual_gco2_kwh) AS cleanest_sp
FROM read_parquet('data/silver/neso/carbon_intensity/**/*.parquet')
WHERE actual_gco2_kwh IS NOT NULL
  AND timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1 DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/carbon_intensity/**/*.parquet")
# Forecast skill: mean absolute error between forecast and actual per day
skill = (
    df.filter(pl.col("actual_gco2_kwh").is_not_null())
      .with_columns(
          (pl.col("forecast_gco2_kwh") - pl.col("actual_gco2_kwh")).abs().alias("abs_err")
      )
      .group_by(pl.col("timestamp_utc").dt.date().alias("day"))
      .agg(pl.col("abs_err").mean().alias("mae_gco2_kwh"))
      .sort("day")
)
print(skill.tail(7))
```

# Caveats

## 01 Actuals lag — null is "not yet published"

`actual_gco2_kwh` is null for periods whose post-period estimate hasn't been computed (typically the most recent 1-2 hours plus backfill gaps). Filter `IS NOT NULL` for back-fitted models; do not treat null as zero. *(Source: vault Known Issues L104.)*

## 02 Distinct from `intensity_current` despite shared `/intensity` prefix

`carbon_intensity` is a range route (`/intensity/{from}/{to}`, max 14 days); `intensity_current` is the no-arg `/intensity` returning one row. Same schema, different query semantics. *(Source: vault Implementation Delta L113.)*

## 03 14-day max window per request

Single requests cannot span more than 14 days. The connector auto-chunks longer windows into 14-day sub-requests (`connectors/neso/carbon_intensity.py L21, L146-150`). Raw HTTP callers must respect this. *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 04 Path placeholders use `{from_dt}` / `{to_dt}` internally

Official docs document `/intensity/{from}/{to}`; the connector templates as `{from_dt}` / `{to_dt}` to avoid Python's `from` keyword conflict. Final URL is identical. *(Source: vault Implementation Delta L111; `endpoints.py L112`.)*

## 05 DST days carry 46 or 50 settlement periods

Despite docs describing 1-48 per day, GB clock-change days have 46 (spring) or 50 (autumn) SPs. The connector handles this via `timestamp_utc`; raw period-number callers must too. *(Source: vault Known Issues L105.)*

# Related datasets

- **`intensity_current`** — Live single-record snapshot · same schema. `30 min`. Companion for "right now"; this dataset for historical / range. *neso · national intensity · 30 min*
- **`intensity_factors`** — Per-fuel emission factors · static. `static`. The reference table behind this dataset's values — weight by `fuelhh` mix for MEF derivation. *neso · national intensity · static*
- **`fuelhh` (Elexon)** — GB generation by fuel · 30 min. `30 min`. Cross-vendor MEF: pair to attribute each `gCO2/kWh` reading to fuel categories. *elexon · generation · 30 min*
- **`system_prices` (Elexon)** — GB cash-out per SP. `30 min`. Most-load-bearing downstream — `gold_uk_imbalance_context` joins these two on `timestamp_utc`. *elexon · prices · 30 min*
