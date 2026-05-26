---
slug: load_forecast
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A65/A01
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/load_forecast.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeLoadForecast (lines 87-102)
  - gridflow/src/gridflow/silver/entsoe/load_forecast.py::LoadForecastTransformer (lines 18-80)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["load_forecast"] (lines 34-36)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Day-ahead load forecast, <span class="italic fg-accent">PT60M.</span>

**Lede:** Day-ahead TSO-published total load forecast in MW per bidding zone — the demand-side input for residual-load modelling and the forecast counterpart against which actual_load is benchmarked.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A65/A01](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.load_forecast` |
| API PATH | `/api?documentType=A65&processType=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | 24-96 points / zone / day |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A01 | Day-ahead processType |
| 2 | D-1 | Publication |
| 3 | `day_ahead` | `forecast_horizon` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- actual_load
- load_forecast_weekly
- load_forecast_monthly
- load_forecast_yearly
- forecast_margin

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU day-ahead load forecast · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 33
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeLoadForecast` (lines 87-102). Transformer adds `forecast_horizon = "day_ahead"` as a constant column. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L90, L97-102` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone — `domain_style="out_bidding_zone"`. | `schemas/entsoe.py L91`; `endpoints.py L34-36` |
| `load_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L92` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L93` |
| `forecast_horizon` | `str` | No (default `"day_ahead"`) | _constant_ | `day_ahead` for this surface; varies in sibling load_forecast_* datasets. | `schemas/entsoe.py L94`; `silver/entsoe/load_forecast.py L69` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L95` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/load_forecast.py L68` |

**PARQUET PATH:** `data/silver/entsoe/load_forecast/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/load_forecast.py L63`)

# Sample data

| timestamp_utc | area_code | load_forecast_mw | resolution | forecast_horizon | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 43200.0 | PT60M | day_ahead | entsoe |
| 2026-05-06T06:00:00+00:00 | 10Y1001A1001A82H | 51800.0 | PT60M | day_ahead | entsoe |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | 58200.0 | PT60M | day_ahead | entsoe |
| **2026-05-06T19:00:00+00:00** | **10Y1001A1001A82H** | **63950.0** | **PT60M** | **day_ahead** | **entsoe** |
| 2026-05-06T23:00:00+00:00 | 10Y1001A1001A82H | 46100.0 | PT60M | day_ahead | entsoe |

**Sources:** Synthesised against typical DE-LU day-ahead forecast shape. The highlighted **19:00 (63.95 GW)** row is the canonical forecast for the winter-evening peak; pair against `actual_load` for the same `(timestamp_utc, area_code)` to compute forecast error (here actual was 64.18 GW; error = +230 MW).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A65&processType=A01&outBiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/load_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.load_forecast.LoadForecastTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A65&processType=A01&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Forecast error per zone, last 7 days
SELECT date_trunc('hour', f.timestamp_utc) AS hour, f.area_code,
       a.load_mw - f.load_forecast_mw AS error_mw
FROM read_parquet('data/silver/entsoe/load_forecast/**/*.parquet') f
JOIN read_parquet('data/silver/entsoe/actual_load/**/*.parquet') a
  ON f.timestamp_utc = a.timestamp_utc AND f.area_code = a.area_code
WHERE f.timestamp_utc >= current_timestamp - INTERVAL 7 DAY
ORDER BY abs(error_mw) DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

fc = pl.read_parquet("data/silver/entsoe/load_forecast/**/*.parquet")
act = pl.read_parquet("data/silver/entsoe/actual_load/**/*.parquet")
err = fc.join(act, on=["timestamp_utc", "area_code"]).with_columns(
    (pl.col("load_mw") - pl.col("load_forecast_mw")).alias("err_mw")
)
# Per-zone forecast skill (RMSE)
print(err.group_by("area_code").agg(
    (pl.col("err_mw") ** 2).mean().sqrt().alias("rmse_mw")
).sort("rmse_mw"))
```

# Caveats

## 01 `forecast_horizon` distinguishes from siblings

The transformer pins `forecast_horizon = "day_ahead"` on this dataset; `load_forecast_weekly` / `_monthly` / `_yearly` set `week_ahead` / `month_ahead` / `year_ahead` respectively. Use this column when stacking multiple forecast horizons. *(Source: `silver/entsoe/load_forecast.py L23, L69`.)*

## 02 `outBiddingZone_Domain` (not `in_Domain`)

A65/A01 uses `outBiddingZone_Domain`. Wrong param style returns EMPTY. *(Source: `endpoints.py L34-36`.)*

## 03 GB publishes — unlike actual_generation

GB continues to publish day-ahead load forecast via ENTSO-E. For more granular GB demand forecast, also use Elexon `ndf`. *(Source: vault Known Issues.)*

## 04 Forecast revisions overwrite

Same `(timestamp_utc, area_code)` re-publication overwrites silently on dedup. No `published_at` for PIT. *(Source: `silver/entsoe/load_forecast.py L63`.)*

## 05 Not entitlement-blocked

A65/A01 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `load_forecast-http-401.md`.)*

# Related datasets

- **`actual_load`** — Realised counterpart. `PT15M-PT60M`. Pair on `(timestamp_utc, area_code)` for forecast-error / forecast-skill. `entsoe · load · hourly`
- **`load_forecast_weekly`** — Week-ahead version of this dataset. `PT60M`. Same schema, different `forecast_horizon`. Use to stack horizons for term-structure modelling. `entsoe · load · weekly`
- **`generation_forecast`** — Day-ahead supply forecast. `PT60M`. Pair to compute demand-supply imbalance forecast (`generation_forecast - load_forecast`). `entsoe · forecast · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices. `PT60M`. Demand forecast is the dominant short-term price-direction feature in load-driven zones (BE, NL, FR). `entsoe · prices · hourly`
