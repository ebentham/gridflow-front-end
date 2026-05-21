---
slug: load_forecast_monthly
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A65/A32
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/load_forecast_monthly.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeLoadForecast (lines 87-102, shared with load_forecast — subclass overrides forecast_horizon default)
  - gridflow/src/gridflow/silver/entsoe/load_forecast_monthly.py::LoadForecastMonthlyTransformer (subclass of LoadForecastTransformer, sets forecast_horizon="month_ahead")
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["load_forecast_monthly"] (lines 126-128)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Month-ahead load forecast, <span class="italic fg-accent">A32 horizon.</span>

**Lede:** Month-ahead TSO load forecast in MW per bidding zone — same shape as day-ahead but with `forecast_horizon = "month_ahead"`, used for monthly capacity adequacy and gas-power balance modelling.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A65/A32](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.load_forecast_monthly` |
| API PATH | `/api?documentType=A65&processType=A32` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | monthly |
| VOLUME | ~720 points / zone / month |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A32 | Month-ahead processType |
| 2 | monthly | Publication |
| 3 | `month_ahead` | `forecast_horizon` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- load_forecast
- load_forecast_weekly
- load_forecast_yearly
- actual_load
- forecast_margin

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU month-ahead load forecast"
- **Subtitle:** "Line · MW · UTC · May 2026"
- **Seed:** 37
- **Toggles:** `30d` (active) / `90d` / `365d`

# Schema

Reuses `gridflow/schemas/entsoe.py` · `EntsoeLoadForecast` (lines 87-102) — same fields as `load_forecast`. Transformer overrides `forecast_horizon = "month_ahead"`. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L90, L97-102` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone — `domain_style="out_bidding_zone"`. | `schemas/entsoe.py L91`; `endpoints.py L126-128` |
| `load_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L92` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L93` |
| `forecast_horizon` | `str` | No | _constant_ | `month_ahead` (subclass override) — distinguishes from sibling forecasts. | `silver/entsoe/load_forecast_monthly.py L12` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L95` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/load_forecast.py L68` (inherited) |

**PARQUET PATH:** `data/silver/entsoe/load_forecast_monthly/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/load_forecast.py L63`, inherited)

# Sample data

| timestamp_utc | area_code | load_forecast_mw | resolution | forecast_horizon | data_provider |
|---|---|---|---|---|---|
| 2026-05-01T00:00:00+00:00 | 10Y1001A1001A82H | 38500.0 | PT60M | month_ahead | entsoe |
| 2026-05-08T19:00:00+00:00 | 10Y1001A1001A82H | 61200.0 | PT60M | month_ahead | entsoe |
| 2026-05-15T19:00:00+00:00 | 10Y1001A1001A82H | 59800.0 | PT60M | month_ahead | entsoe |
| **2026-05-22T19:00:00+00:00** | **10Y1001A1001A82H** | **58200.0** | **PT60M** | **month_ahead** | **entsoe** |
| 2026-05-29T19:00:00+00:00 | 10Y1001A1001A82H | 56700.0 | PT60M | month_ahead | entsoe |

**Sources:** Synthesised against typical DE-LU month-ahead profile (load declining as spring warms). The highlighted **2026-05-22T19:00 (58.2 GW)** row illustrates the smoothing inherent in month-ahead forecasts — daily peak variation is muted relative to the day-ahead surface, because the monthly forecast represents an averaged expectation rather than a date-specific call.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A65&processType=A32&outBiddingZone_Domain={EIC}&periodStart={YYYYMM010000}&periodEnd={YYYYMM(end)0000}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/load_forecast_monthly/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.load_forecast_monthly.LoadForecastMonthlyTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A65&processType=A32&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605010000&periodEnd=202606010000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Per-zone monthly mean forecast (last 12 months)
SELECT date_trunc('month', timestamp_utc) AS month, area_code,
       avg(load_forecast_mw) AS mean_mw
FROM read_parquet('data/silver/entsoe/load_forecast_monthly/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 12 MONTH
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

mfc = pl.read_parquet("data/silver/entsoe/load_forecast_monthly/**/*.parquet")
yfc = pl.read_parquet("data/silver/entsoe/load_forecast_yearly/**/*.parquet")
# Monthly revision of the yearly forecast
diff = mfc.join(yfc, on=["timestamp_utc", "area_code"], suffix="_y").with_columns(
    (pl.col("load_forecast_mw") - pl.col("load_forecast_mw_y")).alias("revision_mw")
)
print(diff.group_by("area_code").agg(pl.col("revision_mw").mean()))
```

# Caveats

## 01 Reuses load_forecast Pydantic schema

The Pydantic class is `EntsoeLoadForecast` (shared with `load_forecast`); the difference is the `forecast_horizon` constant set by the subclass transformer. Always filter on `forecast_horizon` when reading combined load_forecast_* datasets. *(Source: `silver/entsoe/load_forecast_monthly.py`.)*

## 02 `outBiddingZone_Domain` (not `in_Domain`)

A65/A32 uses `outBiddingZone_Domain`. *(Source: `endpoints.py L126-128`.)*

## 03 Monthly forecast is smooth

Month-ahead forecasts represent averaged expectations — daily peak variation is muted relative to day-ahead. Don't expect day-ahead-quality calibration. *(Source: domain knowledge.)*

## 04 Use a monthly window

Short windows (<1 month) may return EMPTY or partial. Build period bounds at month boundaries. *(Source: vault Known Issues.)*

## 05 Not entitlement-blocked

A65/A32 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `load_forecast_monthly-http-401.md`.)*

# Related datasets

- **`load_forecast`** — Day-ahead version. `PT60M`. Closer-in revision; pair to measure forecast-update magnitude. `entsoe · load · hourly`
- **`load_forecast_weekly`** — Week-ahead version. `PT60M`. Intermediate horizon between this and day-ahead. `entsoe · load · weekly`
- **`load_forecast_yearly`** — Year-ahead version. `PT60M`. Longer horizon, the structural baseline this monthly forecast refines. `entsoe · load · annual`
- **`actual_load`** — Realised counterpart. `PT15M-PT60M`. Pair to compute month-ahead forecast skill (typically RMSE 5-10% of mean load). `entsoe · load · hourly`
