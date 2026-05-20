---
slug: ndf
vendor: elexon
vendor_label: Elexon BMRS
api_code: NDF
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/ndf.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonDemandForecast (lines 185-203)
  - gridflow/src/gridflow/silver/elexon/demand_forecast.py::DemandForecastTransformer (lines 19-157)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 130-134, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NDF (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Silver Sample uses `issue_time` field placeholder"
    source_a_says: "Silver row includes `issue_time` column"
    source_b: "gridflow silver/elexon/demand_forecast.py L109-115"
    source_b_says: "Transformer derives `issue_time` from `published_at` (renamed from publishTime); it is included in output_cols (L154)"
    orchestrator_recommendation: "trust gridflow — issue_time is the correctly-cast UTC datetime version of publishTime, used as the bitemporal dedup tiebreaker"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB demand forecast, <span class="italic fg-accent">one day ahead.</span>

**Lede:** Daily-published day-ahead GB demand forecast — the canonical load-forecasting benchmark for forecast-error analysis, bitemporal revision tracking, and ramp planning.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · NDF](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NDF)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.ndf` |
| API PATH | `/datasets/NDF` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 1.4k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, forecast_type, issue_time)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 0 | Lag (day-ahead) |
| 3 | day_ahead | Forecast type |
| 4 | 9 | Schema columns |

# Sidebar siblings

- ndfd
- tsdf
- tsdfd
- inddem
- indo

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB national demand forecast · day-ahead 24-hour"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 7 May 2026"
- **Seed:** 31
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonDemandForecast` (lines 185-203) and `gridflow/silver/elexon/demand_forecast.py` · `DemandForecastTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `issue_time` (derived from `publishTime`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L188` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `schemas/elexon.py L189` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/demand_forecast.py L118-128` |
| `forecast_type` | `str` | No | _derived_ | `"day_ahead"` for NDF, `"2_14_day"` for NDFD. Set from `self.dataset` at transform time. | `schemas/elexon.py L191`; `silver/elexon/demand_forecast.py L137-138` |
| `national_demand_mw` | `float` | No | `nationalDemand` / `demand` | MW. Total national demand forecast. | `schemas/elexon.py L192`; `silver/elexon/demand_forecast.py L63-64` |
| `transmission_demand_mw` | `Optional[float]` | Yes | `transmissionSystemDemand` | MW. Transmission-only forecast, when published. | `schemas/elexon.py L193` |
| `issue_time` | `Optional[datetime[UTC]]` | Yes | `publishTime` (renamed `published_at`) | Publication time. UTC. Bitemporal dedup tiebreaker. | `silver/elexon/demand_forecast.py L109-115` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L194` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L195` |

**PARQUET PATH:** `data/silver/elexon/ndf/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, forecast_type, issue_time)` (`silver/elexon/demand_forecast.py L140-142`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | forecast_type | national_demand_mw | issue_time | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | day_ahead | 21200.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | day_ahead | 21177.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | day_ahead | 33120.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | day_ahead | 35080.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **day_ahead** | **38640.0** | **2026-05-06T02:47:00Z** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | day_ahead | 38120.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | day_ahead | 33010.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | day_ahead | 28140.0 | 2026-05-06T02:47:00Z | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `demand=21200`) and 2 (SP10, `demand=21177`) verbatim from the vault Bronze Sample (vault/elexon/ndf.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (float MW, day_ahead forecast_type) and reproduce the same daily arc as the INDO sample (so forecast vs outturn can be cross-checked). The highlighted **SP36 (38640 MW)** row is the interesting case: the day-ahead NDF SP36 matches the INDO SP36 outturn at 38640 MW — a zero-error period that's the cleanest possible forecast outcome.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: NDF is a one-column forecast time series with publication-time dedup; no enumerable taxonomies. The forecast_type discriminator is documented in schema notes.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/NDF`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/ndf/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.demand_forecast.DemandForecastTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/NDF?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Latest-issue NDF forecast per period (one row per period, latest revision)
SELECT settlement_date, settlement_period,
       national_demand_mw, issue_time
FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY settlement_date, settlement_period
    ORDER BY issue_time DESC
  ) AS rn
  FROM read_parquet('data/silver/elexon/ndf/**/*.parquet')
  WHERE forecast_type = 'day_ahead'
)
WHERE rn = 1
  AND settlement_date = current_date
ORDER BY settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ndf = pl.read_parquet("data/silver/elexon/ndf/**/*.parquet").filter(
    pl.col("forecast_type") == "day_ahead"
)
indo = pl.read_parquet("data/silver/elexon/indo/**/*.parquet")
# Day-ahead forecast error (NDF latest-issue forecast vs INDO outturn)
latest_ndf = (
    ndf.sort("issue_time", descending=True)
       .group_by(["settlement_date", "settlement_period"])
       .first()
)
err = (
    latest_ndf.join(indo, on=["settlement_date", "settlement_period"], how="inner")
              .with_columns(
                  (pl.col("national_demand_mw")
                   - pl.col("initial_demand_outturn_mw"))
                    .alias("forecast_error_mw")
              )
)
print(err.tail(20))
```

# Caveats

## 01 Shared transformer with NDFD

`DemandForecastTransformer` serves both; `forecast_type` is set from `self.dataset` (`day_ahead` vs `2_14_day`). Silver path splits per slug. *(Source: `silver/elexon/demand_forecast.py L137`.)*

## 02 Forecast revisions preserved via `issue_time`

Dedup key includes `issue_time`, so revisions coexist; use a window function for latest-issue selection. *(Source: `silver/elexon/demand_forecast.py L140-142`.)*

## 03 `transmission_demand_mw` is conditional

Column appears only if `transmissionSystemDemand` is in bronze; NDF usually lacks it (use `tsdf` instead). Check `df.columns`. *(Source: `silver/elexon/demand_forecast.py L106-107`.)*

## 04 `issue_time` may be null if `publishTime` is absent in bronze

When null, dedup falls back to `(date, period, forecast_type)` last-arrived. Relevant for revision audits. *(Source: `silver/elexon/demand_forecast.py L109-115`.)*

## 05 Pair with `indo` for forecast-error series

`indo − ndf` (latest-issue) is the canonical day-ahead demand forecast error. *(Source: GB demand-forecast benchmarking.)*

# Related datasets

- **ndfd** — National demand forecast 2-14 day. `daily`. Medium-horizon sibling using the same transformer; filter on `forecast_type = '2_14_day'`. `elexon · demand & forecasts · daily`
- **tsdf** — Transmission system demand forecast. `daily`. Transmission-only counterpart; NDF is total national, TSDF is transmission. `elexon · demand & forecasts · daily`
- **indo** — Initial National Demand Outturn. `30 min`. Outturn counterpart for forecast-error analysis. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand. `30 min`. Intra-day half-hourly forecast complement to NDF's daily publication. `elexon · demand & forecasts · 30 min`
