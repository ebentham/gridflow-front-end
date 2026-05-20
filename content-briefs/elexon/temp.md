---
slug: temp
vendor: elexon
vendor_label: Elexon BMRS
api_code: TEMP
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/temp.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonTEMP class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/temp.py::TempTransformer (lines 18-104)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 161-165, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TEMP (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Implementation Delta"
    source_a_says: "API field `measurementDate` is not currently mapped to a silver field — temp.py mapping renames publishDateTime → timestamp_utc"
    source_b: "gridflow silver/elexon/temp.py L55-62"
    source_b_says: "Column mapping includes `measurementDate → measurement_date` (L57) but output_cols (L95-99) does NOT include measurement_date"
    orchestrator_recommendation: "trust gridflow — measurement_date is renamed internally but dropped from silver output; only timestamp_utc (derived from publishTime preferentially) is kept. If measurement-date attribution matters, extend output_cols."
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonTEMP class declared"
    source_b: "gridflow silver/elexon/temp.py L18-104"
    source_b_says: "TempTransformer outputs 7 columns including temperature plus seasonal reference values"
    orchestrator_recommendation: "trust silver transformer"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB ambient temperature, <span class="italic fg-accent">daily reference.</span>

**Lede:** Daily GB ambient temperature with seasonal climatology — the canonical reference for demand-vs-weather regression, forecast calibration, and deviation-from-normal framing.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · TEMP](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TEMP)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.temp` |
| API PATH | `/datasets/TEMP` |
| FREQUENCY | daily |
| PUBLICATION LAG | 1 day |
| VOLUME | 30 / mo |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 1 day | Publication lag |
| 3 | 30 | Rows / month |
| 4 | 7 | Schema columns |

# Sidebar siblings

- ndf
- ndfd
- indo
- inddem
- bmunits_reference

# Overview

1. <code>temp</code> is the daily GB ambient temperature alongside seasonal climatology references — published daily by Elexon. It is the canonical input for demand-vs-weather regression, forecast calibration, and deviation-from-normal framing of load.

2. Gridflow fetches it from <code>/datasets/TEMP</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>TempTransformer</code> — no Pydantic class; the API's <code>measurementDate</code> is internally renamed but not surfaced in silver output (<code>timestamp_utc</code> is the canonical time key).

3. Refreshed daily with 1 day publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB ambient temperature · last 90 days"
- **Subtitle:** "Sparkline · degrees C · UTC · April–May 2026"
- **Shape:** `diurnal-temp`
- **Params:** `{"peak": 18, "trough": 6, "noise": 0.5, "seed": 15}`
- **Toggles:** `30d` / `90d` (active) / `12mo`

# Schema

Defined in `gridflow/silver/elexon/temp.py` · `TempTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month, derived from `timestamp_utc`). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `publishDateTime` / `publishTime` (renamed to `timestamp_utc`) | Publication time. ISO-8601 UTC. Derived from `publishTime` preferentially; falls back to `measurement_date + T00:00:00Z` if only the date is present. | `silver/elexon/temp.py L55-56, L77-81` |
| `temperature` | `Optional[float]` | Yes | `temperature` | Celsius — daily measured ambient temperature. | `silver/elexon/temp.py L58, L83-85` |
| `normal_temperature` | `Optional[float]` | Yes | `normal` | Celsius — seasonal-normal reference. Not always populated. | `silver/elexon/temp.py L59` |
| `low_temperature` | `Optional[float]` | Yes | `low` | Celsius — seasonal-low reference. Not always populated. | `silver/elexon/temp.py L60` |
| `high_temperature` | `Optional[float]` | Yes | `high` | Celsius — seasonal-high reference. Not always populated. | `silver/elexon/temp.py L61` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/temp.py L91` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/temp.py L92` |

**PARQUET PATH:** `data/silver/elexon/temp/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)` — derived from `timestamp_utc`
**DEDUP KEY:** `(timestamp_utc)` (`silver/elexon/temp.py L87`)

# Sample data

| timestamp_utc | temperature | normal_temperature | low_temperature | high_temperature | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| **2026-04-01T15:45:00+00:00** | **10.6** | _null_ | _null_ | _null_ | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-04-02T15:45:00+00:00 | 11.4 | 10.2 | 8.6 | 12.8 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-03T15:45:00+00:00 | 9.8 | 10.4 | 8.8 | 13.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-04T15:45:00+00:00 | 12.1 | 10.5 | 9.0 | 13.2 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-05T15:45:00+00:00 | 13.6 | 10.7 | 9.2 | 13.4 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-15T15:45:00+00:00 | 14.2 | 11.8 | 10.2 | 14.6 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-01T15:45:00+00:00 | 16.4 | 13.8 | 12.2 | 16.8 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T15:45:00+00:00 | 18.2 | 14.5 | 12.8 | 17.4 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Row 1 (2026-04-01, `temperature=10.6`, no climatology values populated) verbatim from the vault Bronze Sample (vault/elexon/temp.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (Optional float Celsius, climatology references) and follow typical UK April-May temperature rise. The highlighted **2026-04-01** row is the interesting case: vendor-verified shape with `normal`/`low`/`high` all absent — these climatology fields are not always populated in fresh bronze, so consumers should defensively `COALESCE` or filter.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: TEMP is a short scalar series; no enumerable taxonomies. The four temperature columns are documented inline in schema rows.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/TEMP`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/temp/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.temp.TempTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/TEMP?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Deviation from seasonal normal over the last 90 days
SELECT date_trunc('day', timestamp_utc) AS day,
       temperature,
       normal_temperature,
       (temperature - normal_temperature) AS deviation_c
FROM read_parquet('data/silver/elexon/temp/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 90 DAY
  AND normal_temperature IS NOT NULL
ORDER BY day;
```

**Tab 3 — Python · polars**
```python
import polars as pl

t = pl.read_parquet("data/silver/elexon/temp/**/*.parquet")
indo = pl.read_parquet("data/silver/elexon/indo/**/*.parquet")
# Daily peak demand vs temperature
daily = (
    indo.with_columns(pl.col("settlement_date").alias("day"))
        .group_by("day")
        .agg(pl.col("initial_demand_outturn_mw").max().alias("peak_mw"))
        .join(
            t.with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
             .select(["day", "temperature"]),
            on="day", how="inner",
        )
)
print(daily.tail(20))
```

# Caveats

## 01 Sparse cadence — use ≥1-day query windows

Sub-day publish windows often return zero rows. Use 1-day minimum. *(Source: vault Implementation Delta.)*

## 02 No Pydantic schema in `schemas/elexon.py`

No `ElexonTEMP` class; shape lives in `TempTransformer.output_cols`. *(Source: `silver/elexon/temp.py`.)*

## 03 `measurement_date` dropped from silver

Transformer renames `measurementDate` internally but excludes it from `output_cols`. Read bronze for measurement date. *(Source: `silver/elexon/temp.py L57 vs L95-99`.)*

## 04 Climatology references are not forecasts

`normal`/`low`/`high` are seasonal averages by day-of-year, not predictions. Use for deviation framing only. *(Source: vault Known Issues.)*

## 05 Climatology fields may be null

Fresh API returns `temperature` without climatology fields. Filter `WHERE normal_temperature IS NOT NULL` before joining. *(Source: vault Bronze Sample.)*

# Related datasets

- **ndf** — National demand forecast (day-ahead). `daily`. Temperature is the primary driver of demand forecast accuracy — join on date for forecast-error-vs-temperature regression. `elexon · demand & forecasts · daily`
- **ndfd** — National demand forecast 2-14 day. `daily`. Medium-horizon companion; temperature errors compound over the forecast horizon. `elexon · demand & forecasts · daily`
- **indo** — Initial National Demand Outturn. `30 min`. The actual demand; combine with TEMP for daily peak-demand-vs-temperature scatter and elasticity estimation. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand (day-ahead). `30 min`. Day-ahead indicated demand; cross-reference TEMP to validate temperature inputs in the forecast pipeline. `elexon · demand & forecasts · 30 min`
