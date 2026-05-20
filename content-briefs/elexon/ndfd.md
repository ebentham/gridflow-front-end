---
slug: ndfd
vendor: elexon
vendor_label: Elexon BMRS
api_code: NDFD
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/ndfd.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonDemandForecast (lines 185-203, shared with NDF)
  - gridflow/src/gridflow/silver/elexon/demand_forecast.py::NDFDTransformer (lines 160-167, extends DemandForecastTransformer)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 135-139, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NDFD (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Known Issues"
    source_a_says: "NDFD has no settlementPeriod in API — silver fills with placeholder 1"
    source_b: "gridflow silver/elexon/demand_forecast.py L83-89"
    source_b_says: "When settlement_date/settlement_period absent from bronze, transformer sets settlement_date=forecast_date and settlement_period=lit(1)"
    orchestrator_recommendation: "documented behaviour; placeholder period=1 is a workaround — joins on settlement_period will silently match only the SP1 of the day. Recommend filtering on settlement_date only when working with NDFD."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB demand forecast, <span class="italic fg-accent">two weeks out.</span>

**Lede:** Daily-published 2-14 day GB demand forecast — the canonical medium-horizon signal for forward margin, spark-spread analytics, and capacity-adequacy planning.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · NDFD](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NDFD)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.ndfd` |
| API PATH | `/datasets/NDFD` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 20k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period=1, forecast_type, issue_time)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 12 | Forecast horizon (days) |
| 3 | 2_14_day | Forecast type |
| 4 | 9 | Schema columns |

# Sidebar siblings

- ndf
- tsdf
- tsdfd
- fou2t14d
- uou2t14d

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB demand forecast · 14-day horizon"
- **Subtitle:** "Sparkline · MW · UTC · forecast delivery dates · published 1 Apr 2026"
- **Seed:** 32
- **Toggles:** `daily peak` (active) / `daily mean`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonDemandForecast` (lines 185-203, shared with NDF) and `gridflow/silver/elexon/demand_forecast.py` · `DemandForecastTransformer.output_cols`. Partitioned by `settlement_date` (year + month, forecast delivery date). Point-in-time field: `issue_time`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` / `forecastDate` | **The forecast delivery date** (2-14 days ahead), not the publish date. Partition key. | `schemas/elexon.py L188`; `silver/elexon/demand_forecast.py L83-86` |
| `settlement_period` | `int` | No | `settlementPeriod` (when present) / **placeholder `1`** for NDFD | NDFD rows have `settlement_period=1` as a placeholder — the dataset is daily aggregate, not per-period. See caveat 02. | `silver/elexon/demand_forecast.py L88` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | When period is placeholder 1: midnight UTC of forecast_date. | `silver/elexon/demand_forecast.py L118-128` |
| `forecast_type` | `str` | No | _derived_ | Always `"2_14_day"` for this slug (set from `self.dataset="ndfd"` via the NDFDTransformer subclass). | `silver/elexon/demand_forecast.py L137-138, L160-163` |
| `national_demand_mw` | `float` | No | `nationalDemand` / `demand` | MW. Daily-aggregate forecast value. | `schemas/elexon.py L192` |
| `transmission_demand_mw` | `Optional[float]` | Yes | `transmissionSystemDemand` | MW. Rarely populated for NDFD; use `tsdfd` for transmission-only forecasts. | `schemas/elexon.py L193` |
| `issue_time` | `Optional[datetime[UTC]]` | Yes | `publishTime` | Publication time. Bitemporal dedup tiebreaker. | `silver/elexon/demand_forecast.py L109-115` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L194` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L195` |

**PARQUET PATH:** `data/silver/elexon/ndfd/year=YYYY/month=MM/` (partitioned by forecast delivery date)
**PARTITION BY:** `settlement_date (year + month)` (forecast delivery date)
**DEDUP KEY:** `(settlement_date, settlement_period=1, forecast_type, issue_time)` (`silver/elexon/demand_forecast.py L140-142`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | forecast_type | national_demand_mw | issue_time | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-04-03 | 1 | 2026-04-03T00:00:00+00:00 | 2_14_day | 27850.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-04-04 | 1 | 2026-04-04T00:00:00+00:00 | 2_14_day | 26150.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-04-05 | 1 | 2026-04-05T00:00:00+00:00 | 2_14_day | 24380.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-04-06 | 1 | 2026-04-06T00:00:00+00:00 | 2_14_day | 23210.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| **2026-04-07** | **1** | **2026-04-07T00:00:00+00:00** | **2_14_day** | **28920.0** | **2026-04-01T13:45:00Z** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-04-08 | 1 | 2026-04-08T00:00:00+00:00 | 2_14_day | 29410.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-04-12 | 1 | 2026-04-12T00:00:00+00:00 | 2_14_day | 24010.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |
| 2026-04-15 | 1 | 2026-04-15T00:00:00+00:00 | 2_14_day | 27620.0 | 2026-04-01T13:45:00Z | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (2026-04-03, `demand=27850`) and 2 (2026-04-04, `demand=26150`) verbatim from the vault Bronze Sample (vault/elexon/ndfd.md, live 2026-05-08; both with publishTime 2026-04-01T13:45:00Z). Remaining rows synthesised — respect transformer constraints (placeholder period=1, forecast_type=2_14_day, float MW) and follow a typical 14-day demand outlook with weekend trough at SP5-SP6 and Monday rise at SP7. The highlighted **2026-04-07 (Monday, 28920 MW)** row is the interesting case: first weekday of the forecast horizon and the typical Monday demand re-ramp that medium-term planning analytics need to capture.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: NDFD shares the schema and forecast_type discriminator with NDF; relevant caveats are in caveats. No additional enumerable taxonomies.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/NDFD`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/ndfd/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.demand_forecast.NDFDTransformer` (subclass of `DemandForecastTransformer`)

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/NDFD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Latest-issue 14-day NDFD forecast
SELECT settlement_date, national_demand_mw, issue_time
FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY settlement_date
    ORDER BY issue_time DESC
  ) AS rn
  FROM read_parquet('data/silver/elexon/ndfd/**/*.parquet')
  WHERE forecast_type = '2_14_day'
)
WHERE rn = 1
  AND settlement_date BETWEEN current_date + INTERVAL 2 DAY
                          AND current_date + INTERVAL 14 DAY
ORDER BY settlement_date;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ndfd = pl.read_parquet("data/silver/elexon/ndfd/**/*.parquet").filter(
    pl.col("forecast_type") == "2_14_day"
)
# Forecast horizon coverage — how many distinct delivery dates does the latest publish cover?
latest_issue = ndfd.select("issue_time").max().item()
coverage = (
    ndfd.filter(pl.col("issue_time") == latest_issue)
        .select("settlement_date")
        .n_unique()
)
print(f"Latest NDFD issue ({latest_issue}) covers {coverage} delivery dates")
```

# Caveats

## 01 Settlement date is forecast delivery, not publish

`settlement_date` is the 2-14 day-ahead delivery date. Filter on `issue_time` for recent publishes. *(Source: vault Known Issues.)*

## 02 `settlement_period=1` is a placeholder, not a real period

NDFD has no `settlementPeriod`; transformer sets `lit(1)`. Joins on `(date, period)` to HH data match only SP1; join on `settlement_date` alone. *(Source: `silver/elexon/demand_forecast.py L88`.)*

## 03 Shared transformer / Pydantic with NDF

`NDFDTransformer` is a thin subclass; rows share `ElexonDemandForecast`. Silver paths are separate. *(Source: `silver/elexon/demand_forecast.py L160-167`.)*

## 04 Forecast revisions preserved via `issue_time`

Dedup includes `issue_time`, so revisions coexist; use window function for latest-issue. *(Source: `silver/elexon/demand_forecast.py L140-142`.)*

## 05 Lower row volume than NDF

NDFD covers 14 future dates per publish; row count (~20k/mo) exceeds NDF (~1.4k/mo) despite less frequent publishes. *(Source: manifest comparison.)*

# Related datasets

- **ndf** — National demand forecast (day-ahead). `daily`. Shorter-horizon sibling using the same transformer; filter on `forecast_type = 'day_ahead'`. `elexon · demand & forecasts · daily`
- **tsdfd** — 2-14 day transmission demand forecast. `daily`. Transmission-only counterpart; pair with NDFD to derive embedded-generation projections (NDFD − TSDFD). `elexon · demand & forecasts · daily`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Forward availability for the same horizon; compute forward margin = FOU2T14D total − NDFD demand. `elexon · demand & forecasts · daily`
- **uou2t14d** — 2-14 day availability by BM unit. `daily`. Unit-level companion to FOU2T14D; useful for per-BMU forward forecasting. `elexon · demand & forecasts · daily`
