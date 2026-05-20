---
slug: tsdfd
vendor: elexon
vendor_label: Elexon BMRS
api_code: TSDFD
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/tsdfd.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonTSDFD class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/tsdfd.py::TSDFDTransformer (lines 18-105)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 222-226, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TSDFD (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonTSDFD class declared"
    source_b: "gridflow silver/elexon/tsdfd.py L18-105"
    source_b_says: "TSDFDTransformer outputs forecast_date, timestamp_utc, forecast_demand_mw, published_at, data_provider, ingested_at — note `forecast_date` not `settlement_date`"
    orchestrator_recommendation: "trust silver transformer; TSDFD is daily horizon, not per-period, so forecast_date (forecast delivery) is the natural key"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Transmission demand, <span class="italic fg-accent">two weeks out.</span>

**Lede:** Daily-published 2-14 day GB transmission demand forecast — the canonical medium-horizon signal for forward margin, transmission planning, and embedded-generation projections.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · TSDFD](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/TSDFD)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.tsdfd` |
| API PATH | `/datasets/TSDFD` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 14k / mo |
| PRIMARY KEY | `(forecast_date)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 12 | Forecast horizon (days) |
| 3 | daily-aggregate | Granularity |
| 4 | 6 | Schema columns |

# Sidebar siblings

- tsdf
- ndfd
- ndf
- fou2t14d
- uou2t14d

# Overview

1. <code>tsdfd</code> is the daily-published 2-to-14-day-ahead GB transmission demand forecast — the medium-horizon companion to <code>tsdf</code> for forward transmission margin, transmission planning, and embedded-generation projections. Daily-aggregate granularity, no settlement-period concept.

2. Gridflow fetches it from <code>/datasets/TSDFD</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>TSDFDTransformer</code> — keyed on <code>forecast_date</code> rather than settlement-date because the horizon is daily, not per-period.

3. Refreshed daily with 12-day horizon and 0 publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Transmission demand forecast · 14-day horizon"
- **Subtitle:** "Sparkline · MW · UTC · forecast delivery dates · published 1 Apr 2026"
- **Shape:** `diurnal-load`
- **Params:** `{"peak": 38500, "trough": 22500, "noise": 0.03, "seed": 30}`
- **Toggles:** `daily forecast` (active) / `vs NDFD spread`

# Schema

Defined in `gridflow/silver/elexon/tsdfd.py` · `TSDFDTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month, derived from `timestamp_utc`/forecast_date). Point-in-time field: `published_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `forecast_date` | `date` | No | `forecastDate` | **Forecast delivery date** (2-14 days ahead of publish). Partition + dedup key. Unlike most siblings, this column is `forecast_date` not `settlement_date`. | `silver/elexon/tsdfd.py L55, L70` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Midnight UTC of `forecast_date`. | `silver/elexon/tsdfd.py L74-79` |
| `forecast_demand_mw` | `Optional[float]` | Yes | `demand` | MW. Daily transmission demand forecast. | `silver/elexon/tsdfd.py L57, L71` |
| `published_at` | `Optional[datetime[UTC]]` | Yes | `publishTime` | Publication timestamp (UTC). Bitemporal context. | `silver/elexon/tsdfd.py L56, L81-87` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/tsdfd.py L93` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/tsdfd.py L94` |

**PARQUET PATH:** `data/silver/elexon/tsdfd/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)` — derived from forecast_date midnight UTC
**DEDUP KEY:** `(forecast_date)` (`silver/elexon/tsdfd.py L89`)

# Sample data

| forecast_date | timestamp_utc | forecast_demand_mw | published_at | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-04-03 | 2026-04-03T00:00:00+00:00 | 28450.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-04 | 2026-04-04T00:00:00+00:00 | 26750.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-05 | 2026-04-05T00:00:00+00:00 | 24910.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-06 | 2026-04-06T00:00:00+00:00 | 23720.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| **2026-04-07** | **2026-04-07T00:00:00+00:00** | **29520.0** | **2026-04-01T13:45:00+00:00** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-04-08 | 2026-04-08T00:00:00+00:00 | 30010.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-12 | 2026-04-12T00:00:00+00:00 | 24610.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-15 | 2026-04-15T00:00:00+00:00 | 28220.0 | 2026-04-01T13:45:00+00:00 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (2026-04-03, `demand=28450`) and 2 (2026-04-04, `demand=26750`) verbatim from the vault Bronze Sample (vault/elexon/tsdfd.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (Optional float MW, forecast_date date) and follow the typical weekday/weekend transmission-demand pattern over a 14-day horizon. The highlighted **2026-04-07 (Monday, 29520 MW)** row is the interesting case: first weekday of the horizon and the Monday re-ramp — the most demand-stressed period in the forecast window.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: TSDFD is a one-column daily forecast time series; no enumerable taxonomies. The forecast_date vs publish_date distinction is captured in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/TSDFD`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/tsdfd/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.tsdfd.TSDFDTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/TSDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- TSDFD vs NDFD spread (implied embedded contribution at the medium horizon)
SELECT t.forecast_date,
       n.national_demand_mw  AS national_forecast_mw,
       t.forecast_demand_mw  AS transmission_forecast_mw,
       (n.national_demand_mw - t.forecast_demand_mw) AS implied_embedded_mw
FROM read_parquet('data/silver/elexon/tsdfd/**/*.parquet') t
JOIN read_parquet('data/silver/elexon/ndfd/**/*.parquet') n
  ON t.forecast_date = n.settlement_date
WHERE t.forecast_date >= current_date
  AND t.forecast_date <= current_date + INTERVAL 14 DAY
ORDER BY t.forecast_date;
```

**Tab 3 — Python · polars**
```python
import polars as pl

tsdfd = pl.read_parquet("data/silver/elexon/tsdfd/**/*.parquet")
# Latest-revision forecast per forecast_date
latest = (
    tsdfd.sort("published_at", descending=True)
         .group_by("forecast_date")
         .first()
         .sort("forecast_date")
)
print(latest.tail(14))
```

# Caveats

## 01 No Pydantic schema; uses `forecast_date` not `settlement_date`

Key column is `forecast_date` (not aliased). Joins to NDFD need explicit `t.forecast_date = n.settlement_date`. *(Source: `silver/elexon/tsdfd.py L55, L70, L89`.)*

## 02 Sparse cadence — use ≥1-day query windows

Sub-day publish windows often return zero rows. Use 1-day minimum. *(Source: vault Implementation Delta.)*

## 03 Forecast_date is delivery date, not publish date

`forecast_date` is 2-14 days ahead. Use `published_at` to filter by publication time. *(Source: `silver/elexon/tsdfd.py L70`.)*

## 04 Forecast revisions collapse on dedup

Dedup `keep="last"` on `forecast_date` collapses revisions. *(Source: `silver/elexon/tsdfd.py L89`.)*

## 05 Daily aggregate — no per-period detail

One row per date; no `settlement_period`. Medium-horizon per-period analysis requires applying a daily profile shape. *(Source: `silver/elexon/tsdfd.py L97-101`.)*

# Related datasets

- **tsdf** — Transmission system demand forecast (day-ahead). `daily`. Day-ahead per-period counterpart; TSDFD extends the same scope to 2-14 days. `elexon · demand & forecasts · daily`
- **ndfd** — National demand forecast 2-14 day. `daily`. National-scope sibling; NDFD − TSDFD = implied embedded-generation forecast. `elexon · demand & forecasts · daily`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Forward availability for the same horizon; combine with TSDFD demand to compute medium-term margin. `elexon · demand & forecasts · daily`
- **uou2t14d** — 2-14 day availability by BM unit. `daily`. Unit-level companion to FOU2T14D; relevant when projecting transmission-side capacity over the TSDFD horizon. `elexon · demand & forecasts · daily`
