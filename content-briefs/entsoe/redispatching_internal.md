---
slug: redispatching_internal
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A63 (businessType A85)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/30-redispatching-internal-http-401.md)"
sources_consulted:
  - vault/entsoe/redispatching_internal.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::RedispatchingInternalTransformer (lines 145-147)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["redispatching_internal"] (lines 167-173)
  - .planning/reconciliation/entsoe/30-redispatching-internal-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/68-redispatching-internal-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Internal redispatching, <span class="italic fg-accent">A63/A85.</span>

**Lede:** Internal redispatching MW per zone-pair direction — within-zone TSO re-allocation to manage congestion, distinct from cross-border redispatching but using the same A63 DocumentType.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.redispatching_internal` |
| API PATH | `/api?documentType=A63&businessType=A85` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | as published |
| VOLUME | varies by zone |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A63 | DocumentType |
| 2 | A85 | businessType (internal) |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- redispatching_cross_border
- countertrading
- congestion_management_costs
- cross_border_flows
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU internal redispatching · 24h"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 65
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). For internal redispatching, `in_area_code == out_area_code` (both bidding zones are the same — internal scope).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Zone EIC (equals out_area_code for internal). | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Same zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Internal redispatching MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | A85 — internal redispatching. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/redispatching_internal/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T10:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | 2840.0 | A85 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T13:00:00+00:00** | **10Y1001A1001A82H** | **10Y1001A1001A82H** | **6120.0** | **A85** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T20:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | 1280.0 | A85 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **DE-LU internal 13:00 (6.12 GW)** row illustrates the canonical north-south redispatch in Germany: midday solar peaks force massive internal redispatching from northern wind to southern load centres due to insufficient grid capacity. Note `in_area_code == out_area_code` — internal redispatching is within-zone by definition.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A63&businessType=A85&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/redispatching_internal/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.RedispatchingInternalTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A63&businessType=A85&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Internal redispatching cost per zone (last 30 days)
SELECT date_trunc('day', r.timestamp_utc) AS day, r.in_area_code AS zone,
       sum(r.quantity_mw) AS total_mwh,
       sum(c.amount_eur) AS total_cost_eur
FROM read_parquet('data/silver/entsoe/redispatching_internal/**/*.parquet') r
LEFT JOIN read_parquet('data/silver/entsoe/congestion_management_costs/**/*.parquet') c
  ON r.timestamp_utc = c.timestamp_utc AND r.in_area_code = c.in_area_code
WHERE r.timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2
ORDER BY total_cost_eur DESC NULLS LAST;
```

**Tab 3 — Python · polars**
```python
import polars as pl

rd = pl.read_parquet("data/silver/entsoe/redispatching_internal/**/*.parquet")
# Hours with significant internal redispatching by zone
heavy = rd.filter(pl.col("quantity_mw") > 1000).group_by("in_area_code").agg(
    pl.len().alias("heavy_hours"),
    pl.col("quantity_mw").mean().alias("mean_mw")
)
print(heavy.sort("heavy_hours", descending=True))
```

# Caveats

## 01 in_area_code == out_area_code

For internal redispatching, both domain params are the same zone EIC. The "from / to" interpretation is the internal sub-zone direction, encoded outside the silver schema. *(Source: vault Known Issues; `endpoints.py L167-173`.)*

## 02 A63 shared with redispatching_cross_border (businessType A46)

Select on dataset key, not DocumentType alone. *(Source: `endpoints.py L160-173`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `68-redispatching-internal-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/30-redispatching-internal-http-401.md`.)*

# Related datasets

- **`redispatching_cross_border`** — A63/A46 cross-border redispatching. `PT60M`. Same DocumentType, cross-zone scope. `entsoe · transmission · hourly`
- **`countertrading`** — A91 countertrading. `PT60M`. Alternative TSO mechanism. `entsoe · transmission · hourly`
- **`congestion_management_costs`** — A92 cost view. `PT60M`. The €-side of internal redispatching. `entsoe · capacity · hourly`
- **`actual_generation`** — Realised generation by PSR / zone. `PT15M-PT60M`. Internal redispatch is recoverable by comparing actual generation against day-ahead generation_forecast. `entsoe · generation · hourly`
