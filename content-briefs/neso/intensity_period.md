---
slug: intensity_period
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: intensity/date/period
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/intensity_period.md
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (lines 31-36)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::IntensityPeriodTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=INTENSITY)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["intensity_period"] (lines 66-75; settlement_period_iteration=True)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py::_settlement_period_count (lines 156-168; DST-aware GB SP count)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs)
discrepancies_found:
  - source_a: "vault API endpoint table L36"
    source_a_says: "Half-hour settlement period between 1 and 48 in official docs"
    source_b: "connectors/neso/carbon_intensity.py L156-168 _settlement_period_count"
    source_b_says: "Connector iterates GB SP count via Europe/London tz arithmetic — yields 46 (spring) or 50 (autumn) on DST days"
    orchestrator_recommendation: "trust gridflow — DST behavior matches GB settlement reality; docs are nominal. Caveats #01 flags this."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Single settlement period intensity, <span class="italic fg-accent">date and SP.</span>

**Lede:** GB carbon intensity for one settlement period on one date — the narrow point lookup for SP-keyed joins, period-aligned backtests, and BSC-style settlement accounting.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /intensity/date/{date}/{period}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.intensity_period` |
| API PATH | `/intensity/date/{date}/{period}` |
| FREQUENCY | 30 min (single SP) |
| PUBLICATION LAG | forecast ahead · actual post-period |
| VOLUME | 1 row / call |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Single SP cadence |
| 2 | 1..50 | Settlement period range (DST-aware) |
| 3 | 46/48/50 | SPs per day (DST-dependent) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_date
- intensity_today
- intensity_current
- carbon_intensity
- intensity_at

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · single SP across dates"
- **Subtitle:** "Sparkline · gCO2/kWh · SP 24 (peak) · UTC · last 30 days"
- **Seed:** 28
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (lines 31-36). Transformed via the shared `_transform_intensity` (`silver/neso/carbon_intensity.py L298-323`). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Forecast carbon intensity. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Post-period estimate. | `schemas/neso.py L35` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L12, L36` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/intensity_period/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (`silver/neso/carbon_intensity.py L312`)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-04-15T11:30:00+00:00 | 2026-04-15T12:00:00+00:00 | 245.0 | 239.0 | moderate |
| 2026-04-16T11:30:00+00:00 | 2026-04-16T12:00:00+00:00 | 168.0 | 165.0 | moderate |
| 2026-04-17T11:30:00+00:00 | 2026-04-17T12:00:00+00:00 | 94.0 | 89.0 | low |
| **2026-04-18T11:30:00+00:00** | **2026-04-18T12:00:00+00:00** | **62.0** | **58.0** | **very low** |
| 2026-04-19T11:30:00+00:00 | 2026-04-19T12:00:00+00:00 | 78.0 | 80.0 | low |
| 2026-04-20T11:30:00+00:00 | 2026-04-20T12:00:00+00:00 | 145.0 | 148.0 | moderate |
| 2026-04-21T11:30:00+00:00 | 2026-04-21T12:00:00+00:00 | 188.0 | 184.0 | moderate |

**Sources:** Seven consecutive days at the same settlement period (SP 24, mid-day), illustrating same-SP-different-date analysis (vault Silver Sample shape, vault/neso/intensity_period.md L83-85). Highlighted 2026-04-18 row shows the lowest mid-day intensity in the week (`very low`, 58 gCO2/kWh actual) — likely a sunny weekend.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/intensity/date/{date}/{period}` (`{date}` = `YYYY-MM-DD`, `{period}` = 1..50)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/intensity_period/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.IntensityPeriodTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/intensity/date/2026-04-15/24
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Same-SP year-over-year comparison: noon-ish (SP 24) intensity
SELECT timestamp_utc::date AS day,
       actual_gco2_kwh,
       intensity_index
FROM read_parquet('data/silver/neso/intensity_period/**/*.parquet')
WHERE extract('hour' FROM timestamp_utc) = 11
  AND extract('minute' FROM timestamp_utc) = 30
ORDER BY day DESC
LIMIT 30;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/intensity_period/**/*.parquet")
# Daily noon-SP series — a proxy for "best clean window" tracking
noon = (
    df.filter(
        (pl.col("timestamp_utc").dt.hour() == 11)
        & (pl.col("timestamp_utc").dt.minute() == 30)
    )
    .sort("timestamp_utc")
    .tail(30)
)
print(noon)
```

# Caveats

## 01 SP range is 1..50 (DST-aware)

Docs describe 1..48; the connector iterates GB-local SP counts via Europe/London tz arithmetic (`_settlement_period_count` L156-168), yielding 46 (spring) or 50 (autumn) on DST days. Raw HTTP callers should cap at 50 not 48. *(Source: `connectors/neso/carbon_intensity.py L156-168`; vault Implementation Delta L107.)*

## 02 One row per call — high call volume for backtests

A single API request returns one record. The connector's `settlement_period_iteration=True` loops over all SPs of each day in a range, multiplying call counts (range_days × ~48 calls). Use `intensity_date` for whole-day windows. *(Source: `connectors/neso/endpoints.py L72`.)*

## 03 Future SPs return forecast only

Calls for SPs after the current half-hour return `actual_gco2_kwh = null`. *(Source: vault Known Issues L104.)*

## 04 Transformer is dynamically generated

`IntensityPeriodTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`intensity_date`** — Whole-day all-SPs · same schema. `30 min`. Use when you want all 48 SPs of a date, not one. *neso · national intensity · 30 min*
- **`intensity_at`** — Single record by datetime not SP-number · same schema. `30 min`. Equivalent point-in-time read, keyed on UTC datetime. *neso · national intensity · 30 min*
- **`carbon_intensity`** — Range over many SPs · same schema. `30 min`. Cheaper than looping `intensity_period` for backtests. *neso · national intensity · 30 min*
- **`system_prices` (Elexon)** — GB cash-out keyed by `(settlement_date, settlement_period)`. `30 min`. Natural SP-keyed join. *elexon · prices · 30 min*
