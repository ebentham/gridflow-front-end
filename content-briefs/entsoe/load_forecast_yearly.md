---
slug: load_forecast_yearly
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A65/A33
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/load_forecast_yearly.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeLoadForecast (lines 87-102, shared — subclass overrides forecast_horizon default)
  - gridflow/src/gridflow/silver/entsoe/load_forecast_yearly.py::LoadForecastYearlyTransformer (subclass of LoadForecastTransformer, sets forecast_horizon="year_ahead")
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["load_forecast_yearly"] (lines 129-131)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Year-ahead load forecast, <span class="italic fg-accent">A33 horizon.</span>

**Lede:** Year-ahead TSO load forecast in MW per bidding zone — same shape as day-ahead but with `forecast_horizon = "year_ahead"`, paired with generation_forecast in the canonical forecast_margin calculation.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A65/A33](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.load_forecast_yearly` |
| API PATH | `/api?documentType=A65&processType=A33` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | annual |
| VOLUME | 8760 points / zone / year |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A33 | Year-ahead processType |
| 2 | annual | Publication |
| 3 | `year_ahead` | `forecast_horizon` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- load_forecast
- load_forecast_weekly
- load_forecast_monthly
- forecast_margin
- actual_load

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU year-ahead load forecast · 8760 hours"
- **Subtitle:** "Line · MW · year 2026"
- **Seed:** 39
- **Toggles:** `year` (active) / `winter` / `summer`

# Schema

Reuses `gridflow/schemas/entsoe.py` · `EntsoeLoadForecast` (lines 87-102) — same fields as `load_forecast`. Transformer overrides `forecast_horizon = "year_ahead"`. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L90, L97-102` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone — `domain_style="out_bidding_zone"`. | `schemas/entsoe.py L91`; `endpoints.py L129-131` |
| `load_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L92` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L93` |
| `forecast_horizon` | `str` | No | _constant_ | `year_ahead` (subclass override). | `silver/entsoe/load_forecast_yearly.py L13` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L95` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/load_forecast.py L68` (inherited) |

**PARQUET PATH:** `data/silver/entsoe/load_forecast_yearly/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/load_forecast.py L63`, inherited)

# Sample data

| timestamp_utc | area_code | load_forecast_mw | resolution | forecast_horizon | data_provider |
|---|---|---|---|---|---|
| 2026-01-15T19:00:00+00:00 | 10Y1001A1001A82H | 67200.0 | PT60M | year_ahead | entsoe |
| 2026-03-15T19:00:00+00:00 | 10Y1001A1001A82H | 58400.0 | PT60M | year_ahead | entsoe |
| **2026-07-15T13:00:00+00:00** | **10Y1001A1001A82H** | **62100.0** | **PT60M** | **year_ahead** | **entsoe** |
| 2026-09-15T19:00:00+00:00 | 10Y1001A1001A82H | 60300.0 | PT60M | year_ahead | entsoe |
| 2026-12-15T19:00:00+00:00 | 10Y1001A1001A82H | 68900.0 | PT60M | year_ahead | entsoe |

**Sources:** Synthesised against typical DE-LU annual load shape — winter peaks (Jan / Dec evenings ~67-69 GW), shoulder season troughs (Mar / Sep ~58-60 GW), summer mid-load (Jul midday ~62 GW with air-conditioning demand). The highlighted **2026-07-15T13:00 (62.1 GW)** row is the summer-midday A/C peak — emerging as a new annual peak driver in DE-LU as climate shifts winter-evening dominance.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A65&processType=A33&outBiddingZone_Domain={EIC}&periodStart={YYYY01010000}&periodEnd={YYYY12310000}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/load_forecast_yearly/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.load_forecast_yearly.LoadForecastYearlyTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A65&processType=A33&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202601010000&periodEnd=202612310000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Year-ahead vs realised: monthly mean comparison
SELECT date_trunc('month', y.timestamp_utc) AS month, y.area_code,
       avg(y.load_forecast_mw) AS year_ahead_mean,
       avg(a.load_mw) AS actual_mean,
       avg(a.load_mw) - avg(y.load_forecast_mw) AS error_mw
FROM read_parquet('data/silver/entsoe/load_forecast_yearly/**/*.parquet') y
JOIN read_parquet('data/silver/entsoe/actual_load/**/*.parquet') a
  ON y.timestamp_utc = a.timestamp_utc AND y.area_code = a.area_code
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

yfc = pl.read_parquet("data/silver/entsoe/load_forecast_yearly/**/*.parquet")
gfc = pl.read_parquet("data/silver/entsoe/generation_forecast/**/*.parquet")
# Forecast margin (DIY) — should match the published forecast_margin dataset
margin = gfc.group_by(["timestamp_utc", "area_code"]).agg(
    pl.col("generation_forecast_mw").sum().alias("gen_mw")
).join(yfc, on=["timestamp_utc", "area_code"]).with_columns(
    (pl.col("gen_mw") - pl.col("load_forecast_mw")).alias("diy_margin_mw")
)
print(diy_margin.tail())
```

# Caveats

## 01 Reuses load_forecast Pydantic schema

Same `EntsoeLoadForecast` class as `load_forecast`; only the `forecast_horizon` constant differs (subclass override). Filter on `forecast_horizon` when combining horizons. *(Source: `silver/entsoe/load_forecast_yearly.py`.)*

## 02 `outBiddingZone_Domain` (not `in_Domain`)

A65/A33 uses `outBiddingZone_Domain`. *(Source: `endpoints.py L129-131`.)*

## 03 Use a yearly window

Year-ahead forecast — short windows may return EMPTY. Build period bounds at year boundaries. *(Source: vault Known Issues.)*

## 04 Pair with generation_forecast for margin

`generation_forecast - load_forecast_yearly` is the conceptual basis for the `forecast_margin` (A70/A33) dataset. *(Source: `forecast_margin.md` brief.)*

## 05 Not entitlement-blocked

A65/A33 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `load_forecast_yearly-http-401.md`.)*

# Related datasets

- **`load_forecast`** — Day-ahead version. `PT60M`. The closest-in revision; this yearly forecast is the structural baseline that day-ahead refines. `entsoe · load · hourly`
- **`load_forecast_weekly`** — Week-ahead version. `PT60M`. Intermediate horizon. `entsoe · load · weekly`
- **`load_forecast_monthly`** — Month-ahead version. `PT60M`. Intermediate horizon. `entsoe · load · monthly`
- **`forecast_margin`** — Year-ahead margin (generation - load). `PT60M`. The downstream dataset that uses this load forecast as its demand input. `entsoe · forecast · annual`
