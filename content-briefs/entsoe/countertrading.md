---
slug: countertrading
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A91
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/09-countertrading-http-401.md)"
sources_consulted:
  - vault/entsoe/countertrading.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::CountertradingTransformer (lines 150-152)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["countertrading"] (lines 174-179)
  - .planning/reconciliation/entsoe/09-countertrading-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/47-countertrading-no-silver-schema-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** TSO countertrading, <span class="italic fg-accent">A91.</span>

**Lede:** Hourly countertrading MW per zone-pair direction — TSO-initiated reverse-direction trade to relieve congestion, distinct from redispatching by using market-clearing rather than direct generation control.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.countertrading` |
| API PATH | `/api?documentType=A91` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | as published |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A91 | DocumentType |
| 2 | zone-pair | `domain_style` |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- redispatching_cross_border
- redispatching_internal
- congestion_management_costs
- net_transfer_capacity
- cross_border_flows

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU ↔ NL countertrading · 24h"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 67
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Countertrade MW (in reverse direction of congested flow). | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Carries the countertrade business code. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/countertrading/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | 10YNL----------L | 320.0 | A47 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T14:00:00+00:00** | **10Y1001A1001A82H** | **10YNL----------L** | **480.0** | **A47** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10Y1001A1001A82H | 10YNL----------L | 0.0 | A47 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **DE-LU → NL 14:00 (480 MW countertrade)** row reflects a typical solar-peak countertrade — when the day-ahead clearing has DE-LU sending power south while internal congestion requires reverse flow, the TSO buys reverse capacity through countertrading rather than direct generation control.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A91&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/countertrading/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.CountertradingTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A91&in_Domain=10Y1001A1001A82H&out_Domain=10YNL----------L&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Countertrading activity by border (last 90 days)
SELECT in_area_code, out_area_code,
       count(*) FILTER (WHERE quantity_mw > 0) AS active_hours,
       sum(quantity_mw) AS total_mwh
FROM read_parquet('data/silver/entsoe/countertrading/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 90 DAY
GROUP BY 1, 2
ORDER BY total_mwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ct = pl.read_parquet("data/silver/entsoe/countertrading/**/*.parquet")
rd = pl.read_parquet("data/silver/entsoe/redispatching_cross_border/**/*.parquet")
# Countertrade vs redispatch — alternative congestion mechanisms by border
ct_sum = ct.group_by(["in_area_code", "out_area_code"]).agg(pl.col("quantity_mw").sum().alias("ct_mwh"))
rd_sum = rd.group_by(["in_area_code", "out_area_code"]).agg(pl.col("quantity_mw").sum().alias("rd_mwh"))
print(ct_sum.join(rd_sum, on=["in_area_code", "out_area_code"], how="outer"))
```

# Caveats

## 01 Alternative to redispatching

Countertrading and redispatching are two TSO mechanisms for managing congestion — countertrading uses market clearing (the TSO buys reverse capacity at market prices), redispatching uses direct generation control. *(Source: domain knowledge.)*

## 02 Directional per border-pair

Each border-pair has two directions; pair both for full picture. *(Source: `endpoints.py L174-179`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `47-countertrading-no-silver-schema-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/09-countertrading-http-401.md`.)*

# Related datasets

- **`redispatching_cross_border`** — A63/A46 cross-border redispatching. `PT60M`. Alternative TSO congestion mechanism. `entsoe · transmission · hourly`
- **`redispatching_internal`** — A63/A85 internal redispatching. `PT60M`. Within-zone analogue. `entsoe · transmission · hourly`
- **`congestion_management_costs`** — A92 cost view. `PT60M`. The €-side of countertrading + redispatching combined. `entsoe · capacity · hourly`
- **`net_transfer_capacity`** — Day-ahead NTC. `PT60M`. NTC reductions often correlate with countertrading activity. `entsoe · transmission · hourly`
