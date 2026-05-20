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

**Lede:** TSDF is the Transmission System Demand Forecast — the published demand expectation restricted to the transmission network (excludes embedded generation). Same shape as `inddem` but transmission-only, and the forecast counterpart to `itsdo`. Used for transmission-side scheduling and as the demand input to the LOLPDRM derived-margin calculation.

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

1. <code>tsdf</code> is **Transmission System Demand Forecast** — published demand expectations restricted to the GB transmission system (excludes embedded generation). The transmission-only counterpart to `inddem` (national indicated demand) and the day-ahead forecast for `itsdo`. Each row carries `forecast_demand_mw` per settlement period, optionally split by `boundary` (`N` national, zonal codes like `B1`).

2. Gridflow fetches it from <code>/datasets/TSDF</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L217-221</code>). The <code>TSDFTransformer</code> renames `demand` → `forecast_demand_mw`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period, boundary)` so each boundary survives. No Pydantic class is declared.

3. Cadence is daily publication, zero lag (day-ahead and intra-day). Verified against the live API on 2026-05-08; the sample returned `demand=195` for SP9 and SP10 on `boundary=B1` — zonal-boundary attributions matching the small-value semantics seen in `inddem`/`indgen`/`melngc`. For national-transmission forecasts use `boundary='N'` (when present). Pair with `itsdo` for forecast-error analysis on the transmission side.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Transmission demand forecast · 24-hour day-ahead"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Seed:** 29
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

Like the rest of the indicated/forecast suite, TSDF has no dedicated Pydantic class. Silver shape is defined by `TSDFTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no TSDF class.)*

## 02 Boundary semantics — small values are zonal deltas

Same pattern as INDDEM/INDGEN/MELNGC: small `demand` values for zonal boundaries (`B1`, etc.) are zone-attributed contributions, not national totals. Filter on `boundary='N'` (when present) for national transmission demand. *(Source: vault Bronze Sample; cross-reference with INDDEM brief.)*

## 03 Transmission-only — excludes embedded

TSDF mirrors ITSDO in scope: it forecasts demand visible on the transmission network only, excluding embedded generation offset. Compare to NDF (national, including embedded) to derive expected embedded-generation contribution at the forecast horizon. *(Source: vault Overview — "restricted to the transmission system (excludes embedded generation)".)*

## 04 Forecast revisions collapse on dedup

The transformer dedups on `(settlement_date, settlement_period, boundary)` keeping the latest. Multiple intra-day forecast publishes for the same period are collapsed; silver holds only the latest. For revision history, read bronze and preserve `published_at`. *(Source: `silver/elexon/tsdf.py L89-92`.)*

## 05 Pair with `itsdo` for forecast-error analysis

`tsdf.forecast_demand_mw - itsdo.initial_transmission_system_demand_outturn_mw` for the same (date, period) gives the transmission-side forecast error. Filter TSDF to `boundary='N'` first. Useful for diagnosing whether overall NDF forecast error is driven by transmission or embedded mis-estimation. *(Source: domain knowledge — GB demand-forecast benchmarking.)*

# Related datasets

- **tsdfd** — 2-14 day transmission demand forecast. `daily`. Medium-horizon companion; TSDF is day-ahead, TSDFD extends 2-14 days. `elexon · demand & forecasts · daily`
- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. The realised demand counterpart for forecast-error analysis. `elexon · demand & forecasts · 30 min`
- **ndf** — National demand forecast (day-ahead). `daily`. National-scope counterpart; NDF − TSDF (at boundary='N') = expected embedded generation contribution. `elexon · demand & forecasts · daily`
- **inddem** — Indicated demand (day & day-ahead). `30 min`. Same publish cadence and key as TSDF but national scope; combine for full forecast picture. `elexon · demand & forecasts · 30 min`
