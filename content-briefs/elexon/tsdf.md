---
slug: tsdf
vendor: elexon
vendor_label: Elexon BMRS
api_code: TSDF
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/tsdf.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonTSDF class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/tsdf.py::TSDFTransformer (lines 19-108)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 217-221, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TSDF (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonTSDF class declared"
    source_b: "gridflow silver/elexon/tsdf.py L19-108"
    source_b_says: "TSDFTransformer outputs settlement_date, settlement_period, timestamp_utc, forecast_demand_mw, boundary, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same shape gap as other indicated/transmission datasets"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Transmission demand forecast, <span class="italic fg-accent">day-ahead.</span>

**Lede:** Half-hourly GB transmission-only demand forecast — the canonical day-ahead signal for transmission scheduling, ITSDO forecast error, and embedded-generation derivation.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · TSDF](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TSDF)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.tsdf` |
| API PATH | `/datasets/TSDF` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, boundary)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Per-period cadence |
| 2 | 0 | Lag (day-ahead) |
| 3 | transmission-only | Scope |
| 4 | 7 | Schema columns |

# Sidebar siblings

- tsdfd
- itsdo
- ndf
- ndfd
- inddem

# Overview

1. <code>tsdf</code> is the half-hourly day-ahead GB transmission-only demand forecast — the transmission-system counterpart to <code>ndf</code>, used for transmission scheduling, ITSDO forecast-error analysis, and embedded-generation derivation.

2. Gridflow fetches it from <code>/datasets/TSDF</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>TSDFTransformer</code> — no Pydantic class; <code>boundary</code> column carries zonal attribution.

3. Refreshed daily with 0 publication lag (forward-looking, per-period). Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Transmission demand forecast · 24-hour day-ahead"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Shape:** `diurnal-load`
- **Params:** `{"peak": 38000, "trough": 22000, "noise": 0.03, "seed": 29}`
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/tsdf.py` · `TSDFTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/tsdf.py L73` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/tsdf.py L74` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/tsdf.py L78-87` |
| `forecast_demand_mw` | `Optional[float]` | Yes | `demand` | MW. Transmission-only national or zonal demand forecast. | `silver/elexon/tsdf.py L59, L75` |
| `boundary` | `Optional[str]` | Yes | `boundary` | `N` (national), `Z` (zonal aggregate), or specific zone (`B1`, ...). | `silver/elexon/tsdf.py L60, L100` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/tsdf.py L96` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/tsdf.py L97` |

**PARQUET PATH:** `data/silver/elexon/tsdf/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, boundary)` (`silver/elexon/tsdf.py L89-92`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | forecast_demand_mw | boundary | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 195.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | 195.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 28940.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 31810.0 | N | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **35820.0** | **N** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 35540.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 30580.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 26410.0 | N | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `demand=195`, `boundary=B1`) and 2 (SP10, `demand=195`, `boundary=B1`) verbatim from the vault Bronze Sample (vault/elexon/tsdf.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (Optional float MW, boundary string) and represent typical `boundary='N'` transmission-only forecasts that pair with the ITSDO outturn in this brief set. The highlighted **SP36 (35820 MW national)** row is the interesting case: matches the ITSDO SP36 outturn (35820 MW) — a zero-error period for the transmission-only forecast.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: TSDF emits one scalar per (period, boundary); no enumerable taxonomies. Boundary code semantics are inline in schema notes.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/TSDF`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/tsdf/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.tsdf.TSDFTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/TSDF?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- TSDF national-boundary forecast vs ITSDO outturn (transmission-only forecast error)
WITH f AS (
  SELECT settlement_date, settlement_period, forecast_demand_mw
  FROM read_parquet('data/silver/elexon/tsdf/**/*.parquet')
  WHERE boundary = 'N'
), o AS (
  SELECT settlement_date, settlement_period,
         initial_transmission_system_demand_outturn_mw AS outturn_mw
  FROM read_parquet('data/silver/elexon/itsdo/**/*.parquet')
)
SELECT f.settlement_date, f.settlement_period,
       f.forecast_demand_mw, o.outturn_mw,
       (f.forecast_demand_mw - o.outturn_mw) AS error_mw
FROM f JOIN o USING (settlement_date, settlement_period)
WHERE f.settlement_date = current_date - INTERVAL 1 DAY
ORDER BY f.settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

tsdf = pl.read_parquet("data/silver/elexon/tsdf/**/*.parquet").filter(
    pl.col("boundary") == "N"
)
itsdo = pl.read_parquet("data/silver/elexon/itsdo/**/*.parquet")
err = (
    tsdf.join(itsdo, on=["settlement_date", "settlement_period"], how="inner")
        .with_columns(
            (pl.col("forecast_demand_mw")
             - pl.col("initial_transmission_system_demand_outturn_mw"))
              .alias("forecast_error_mw")
        )
        .group_by(pl.col("timestamp_utc").dt.hour().alias("hour"))
        .agg(pl.col("forecast_error_mw").mean().alias("bias_mw"))
        .sort("hour")
)
print(err)
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonTSDF` class; shape lives in `TSDFTransformer.output_cols`. *(Source: `silver/elexon/tsdf.py`.)*

## 02 Boundary semantics — small values are zonal deltas

Zonal boundaries emit small attributed deltas; filter `boundary='N'` for national totals. *(Source: vault Bronze Sample.)*

## 03 Transmission-only — excludes embedded

Forecasts only transmission-visible demand. `ndf − tsdf` (at `boundary='N'`) = expected embedded contribution. *(Source: vault Overview.)*

## 04 Forecast revisions collapse on dedup

Dedup `keep="last"` on `(date, period, boundary)` collapses intra-day revisions. *(Source: `silver/elexon/tsdf.py L89-92`.)*

## 05 Pair with `itsdo` for forecast-error analysis

`tsdf − itsdo` per period (boundary='N') gives transmission-side forecast error. *(Source: GB demand-forecast benchmarking.)*

# Related datasets

- **tsdfd** — 2-14 day transmission demand forecast. `daily`. Medium-horizon companion; TSDF is day-ahead, TSDFD extends 2-14 days. `elexon · demand & forecasts · daily`
- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. The realised demand counterpart for forecast-error analysis. `elexon · demand & forecasts · 30 min`
- **ndf** — National demand forecast (day-ahead). `daily`. National-scope counterpart; NDF − TSDF (at boundary='N') = expected embedded generation contribution. `elexon · demand & forecasts · daily`
- **inddem** — Indicated demand (day & day-ahead). `30 min`. Same publish cadence and key as TSDF but national scope; combine for full forecast picture. `elexon · demand & forecasts · 30 min`
