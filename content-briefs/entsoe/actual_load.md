---
slug: actual_load
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A65/A16
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/actual_load.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActualLoad (lines 29-43)
  - gridflow/src/gridflow/silver/entsoe/actual_load.py::ActualLoadTransformer (lines 18-78)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["actual_load"] (lines 31-33)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Realised total load, <span class="italic fg-accent">per zone.</span>

**Lede:** Realised total load in MW per EIC bidding zone — the canonical EU demand observation series, the denominator in residual-load modelling and counterpart to GB Elexon settlement demand.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A65/A16](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.actual_load` |
| API PATH | `/api?documentType=A65&processType=A16` |
| FREQUENCY | PT15M / PT30M / PT60M |
| PUBLICATION LAG | T+1h |
| VOLUME | varies by zone & resolution |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | PT60M | Most common resolution |
| 2 | T+1h | Best-case lag |
| 3 | XML | `GL_MarketDocument` |
| 4 | 6 | Schema columns |

# Sidebar siblings

- load_forecast
- load_forecast_weekly
- load_forecast_monthly
- load_forecast_yearly
- actual_generation

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU realised load · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 31
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActualLoad` (lines 29-43). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L32, L38-43` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone — `domain_style="out_bidding_zone"`. | `schemas/entsoe.py L33`; `endpoints.py L31-33` |
| `load_mw` | `float` | No | `<Point><quantity>` | Realised load MW. | `schemas/entsoe.py L34` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration: `PT15M` / `PT30M` / `PT60M`. | `schemas/entsoe.py L35` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L36` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/actual_load.py L67` |

**PARQUET PATH:** `data/silver/entsoe/actual_load/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/actual_load.py L62`)

# Sample data

| timestamp_utc | area_code | load_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 42850.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T06:00:00+00:00 | 10Y1001A1001A82H | 51420.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10Y1001A1001A82H** | **64180.0** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | 58740.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T23:00:00+00:00 | 10Y1001A1001A82H | 45620.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 26840.0 | PT30M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T18:00:00+00:00 | 10YGB----------A | 38120.0 | PT30M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised against typical DE-LU + GB load shapes (DE-LU 43-64 GW range, GB 27-38 GW range). The highlighted **DE-LU 19:00 (64.18 GW)** row is the canonical winter-evening peak — when joined against `actual_generation` it produces the residual load (`load - wind - solar`) that drives short-term prices. Note GB rows publish `PT30M` (Elexon settlement-period resolution), continental zones publish `PT60M`.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A65&processType=A16&outBiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/actual_load/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.actual_load.ActualLoadTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A65&processType=A16&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily peak load per zone (last 30 days)
SELECT date_trunc('day', timestamp_utc) AS day, area_code,
       max(load_mw) AS peak_mw, min(load_mw) AS trough_mw,
       max(load_mw) - min(load_mw) AS swing_mw
FROM read_parquet('data/silver/entsoe/actual_load/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2
ORDER BY 1, peak_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

load = pl.read_parquet("data/silver/entsoe/actual_load/**/*.parquet")
gen = pl.read_parquet("data/silver/entsoe/actual_generation/**/*.parquet")
# Residual load (renewables-net demand) — the canonical EU price feature
renewables = gen.filter(
    pl.col("production_type").is_in(["B16", "B18", "B19"])
).group_by(["timestamp_utc", "area_code"]).agg(
    pl.col("generation_mw").sum().alias("renew_mw")
)
res = load.join(renewables, on=["timestamp_utc", "area_code"], how="left").with_columns(
    (pl.col("load_mw") - pl.col("renew_mw").fill_null(0)).alias("residual_mw")
)
print(res.tail())
```

# Caveats

## 01 `outBiddingZone_Domain` (not `in_Domain`)

A65/A16 uses `outBiddingZone_Domain` (`domain_style="out_bidding_zone"`). Wrong param style returns EMPTY. *(Source: `endpoints.py L31-33`.)*

## 02 Resolution varies by zone

DE/AT/FR are `PT15M`; GB is `PT30M`; most continental zones are `PT60M`. Filter on `resolution` before joining settlement-period datasets. *(Source: vault Known Issues.)*

## 03 GB publishes — unlike actual_generation

Unlike A75 (which is empty for GB post-Brexit), GB continues to publish total load on A65/A16 via ENTSO-E. Both Elexon `ndf` and ENTSO-E `actual_load` (GB) are usable. *(Source: vault Known Issues.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code)` re-publication overwrites silently on dedup `keep="last"`. No `published_at` for PIT. *(Source: `silver/entsoe/actual_load.py L62`.)*

## 05 Not entitlement-blocked

A65/A16 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `actual_load-http-401.md`.)*

# Related datasets

- **`load_forecast`** — Day-ahead forecast counterpart. `PT60M`. Forecast skill = `actual_load - load_forecast` on the same `(timestamp_utc, area_code)`. `entsoe · load · hourly`
- **`actual_generation`** — Realised generation by PSR. `PT15M-PT60M`. Pair to compute residual load (renewables-net demand) — the canonical EU price-direction feature. `entsoe · generation · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices. `PT60M`. Demand is the dominant short-term price-direction feature in load-driven zones (BE, NL, FR). `entsoe · prices · hourly`
- **`fuelhh` (Elexon)** — GB generation by fuel. `30 min`. Combine with this dataset filtered on GB to recover residual demand for the GB market. `elexon · generation · 30 min`
