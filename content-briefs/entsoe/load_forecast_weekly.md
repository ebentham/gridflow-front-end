---
slug: load_forecast_weekly
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A65/A31
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/load_forecast_weekly.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeLoadForecastWeekly (lines 277-292)
  - gridflow/src/gridflow/silver/entsoe/load_forecast_weekly.py::LoadForecastWeeklyTransformer (lines 18-84)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["load_forecast_weekly"] (lines 123-125)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Week-ahead load forecast, <span class="italic fg-accent">A31 horizon.</span>

**Lede:** Week-ahead TSO load forecast in MW per bidding zone — same schema as day-ahead but with `forecast_horizon = "week_ahead"`, used for short-term capacity-adequacy stress tests.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A65/A31](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.load_forecast_weekly` |
| API PATH | `/api?documentType=A65&processType=A31` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | weekly |
| VOLUME | 168 points / zone / week |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A31 | Week-ahead processType |
| 2 | weekly | Publication |
| 3 | `week_ahead` | `forecast_horizon` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- load_forecast
- load_forecast_monthly
- load_forecast_yearly
- actual_load
- forecast_margin

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU week-ahead load forecast · 7 days"
- **Subtitle:** "Line · MW · UTC · w/e 13 May 2026"
- **Seed:** 35
- **Toggles:** `7d` (active) / `30d` / `90d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeLoadForecastWeekly` (lines 277-292). Structurally identical to `EntsoeLoadForecast` except `forecast_horizon` default. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L280, L287-292` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone — `domain_style="out_bidding_zone"`. | `schemas/entsoe.py L281`; `endpoints.py L123-125` |
| `load_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L282` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L283` |
| `forecast_horizon` | `str` | No (default `"week_ahead"`) | _constant_ | Distinguishes this dataset from the day-ahead / monthly / yearly siblings. | `schemas/entsoe.py L284`; `silver/entsoe/load_forecast_weekly.py L73` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L285` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/load_forecast_weekly.py L71` |

**PARQUET PATH:** `data/silver/entsoe/load_forecast_weekly/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/load_forecast_weekly.py L67`)

# Sample data

| timestamp_utc | area_code | load_forecast_mw | resolution | forecast_horizon | data_provider |
|---|---|---|---|---|---|
| 2026-05-11T00:00:00+00:00 | 10Y1001A1001A82H | 41200.0 | PT60M | week_ahead | entsoe |
| 2026-05-11T08:00:00+00:00 | 10Y1001A1001A82H | 56300.0 | PT60M | week_ahead | entsoe |
| 2026-05-11T19:00:00+00:00 | 10Y1001A1001A82H | 61400.0 | PT60M | week_ahead | entsoe |
| **2026-05-13T19:00:00+00:00** | **10Y1001A1001A82H** | **64850.0** | **PT60M** | **week_ahead** | **entsoe** |
| 2026-05-15T19:00:00+00:00 | 10Y1001A1001A82H | 59700.0 | PT60M | week_ahead | entsoe |

**Sources:** Synthesised against a typical mid-May DE-LU week-ahead forecast (Mon-Wed weekday peaks higher than Thu-Fri pre-weekend). The highlighted **2026-05-13T19:00 (64.85 GW)** row is the weekly-peak Wednesday-evening forecast — useful for week-ahead capacity-stress tests that the day-ahead surface (24-hour window) cannot support.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A65&processType=A31&outBiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/load_forecast_weekly/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.load_forecast_weekly.LoadForecastWeeklyTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A65&processType=A31&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605110000&periodEnd=202605180000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Week-ahead vs day-ahead vs actual for the same hours (term-structure test)
SELECT a.timestamp_utc, a.area_code,
       w.load_forecast_mw AS week_ahead,
       d.load_forecast_mw AS day_ahead,
       a.load_mw          AS actual
FROM read_parquet('data/silver/entsoe/actual_load/**/*.parquet') a
LEFT JOIN read_parquet('data/silver/entsoe/load_forecast_weekly/**/*.parquet') w
  ON a.timestamp_utc = w.timestamp_utc AND a.area_code = w.area_code
LEFT JOIN read_parquet('data/silver/entsoe/load_forecast/**/*.parquet') d
  ON a.timestamp_utc = d.timestamp_utc AND a.area_code = d.area_code
WHERE a.timestamp_utc >= current_timestamp - INTERVAL 30 DAY
ORDER BY a.timestamp_utc DESC LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

week = pl.read_parquet("data/silver/entsoe/load_forecast_weekly/**/*.parquet")
day = pl.read_parquet("data/silver/entsoe/load_forecast/**/*.parquet")
# Forecast-revision: how much does the day-ahead update the week-ahead?
diff = week.join(day, on=["timestamp_utc", "area_code"], suffix="_da").with_columns(
    (pl.col("load_forecast_mw_da") - pl.col("load_forecast_mw")).alias("revision_mw")
)
print(diff.group_by("area_code").agg(pl.col("revision_mw").abs().mean()))
```

# Caveats

## 01 `forecast_horizon = "week_ahead"` — not day_ahead

This dataset and `load_forecast` share an identical Pydantic schema except for the `forecast_horizon` default. Always filter on `forecast_horizon` when combining horizons. *(Source: `silver/entsoe/load_forecast_weekly.py L73`.)*

## 02 `outBiddingZone_Domain` (not `in_Domain`)

A65/A31 uses `outBiddingZone_Domain`. *(Source: `endpoints.py L123-125`.)*

## 03 Use a weekly window

Week-ahead forecast — short windows may return EMPTY or partial. Build period bounds at Mon-Mon boundaries. *(Source: vault Known Issues.)*

## 04 Forecast revisions overwrite

Same `(timestamp_utc, area_code)` re-publication overwrites silently on dedup. No `published_at` for PIT — to track week-ahead vs day-ahead deltas, snapshot the silver partition. *(Source: `silver/entsoe/load_forecast_weekly.py L67`.)*

## 05 Not entitlement-blocked

A65/A31 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `load_forecast_weekly-http-401.md`.)*

# Related datasets

- **`load_forecast`** — Day-ahead version of this dataset. `PT60M`. The closer-in revision; pair to measure forecast-update magnitude. `entsoe · load · hourly`
- **`load_forecast_monthly`** — Month-ahead version. `PT60M`. Longer horizon for monthly-balance modelling. `entsoe · load · monthly`
- **`load_forecast_yearly`** — Year-ahead version. `PT60M`. Longest horizon, used in `forecast_margin`. `entsoe · load · annual`
- **`actual_load`** — Realised counterpart. `PT15M-PT60M`. Pair on `(timestamp_utc, area_code)` for week-ahead forecast skill metrics. `entsoe · load · hourly`
