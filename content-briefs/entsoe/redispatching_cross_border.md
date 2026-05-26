---
slug: redispatching_cross_border
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A63 (businessType A46)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/29-redispatching-cross-border-http-401.md)"
sources_consulted:
  - vault/entsoe/redispatching_cross_border.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::RedispatchingCrossBorderTransformer (lines 140-142)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["redispatching_cross_border"] (lines 160-166)
  - .planning/reconciliation/entsoe/29-redispatching-cross-border-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/67-redispatching-cross-border-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Cross-border redispatching, <span class="italic fg-accent">A63/A46.</span>

**Lede:** Cross-border redispatching MW per zone-pair direction — TSO-initiated re-allocation of generation between zones to manage grid constraints, distinct from market-clearing flow.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.redispatching_cross_border` |
| API PATH | `/api?documentType=A63&businessType=A46` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | as published |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A63 | DocumentType |
| 2 | A46 | businessType (cross-border) |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- redispatching_internal
- countertrading
- cross_border_flows
- congestion_management_costs
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU ↔ FR cross-border redispatching · 24h"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 63
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Redispatching MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | A46 — cross-border redispatching. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/redispatching_cross_border/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T10:00:00+00:00 | 10Y1001A1001A82H | 10YFR-RTE------C | 850.0 | A46 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T15:00:00+00:00** | **10Y1001A1001A82H** | **10YFR-RTE------C** | **1240.0** | **A46** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T20:00:00+00:00 | 10Y1001A1001A82H | 10YFR-RTE------C | 320.0 | A46 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **DE-LU → FR 15:00 (1.24 GW)** row illustrates a typical solar-driven redispatch — DE-LU has excess solar mid-afternoon and the TSO redispatches generation toward FR to relieve internal congestion. Redispatching is a cost recovered through congestion management charges.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A63&businessType=A46&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/redispatching_cross_border/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.RedispatchingCrossBorderTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A63&businessType=A46&in_Domain=10Y1001A1001A82H&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Redispatching frequency by border (last 90 days)
SELECT in_area_code, out_area_code,
       count(*) FILTER (WHERE quantity_mw > 0) AS active_hours,
       sum(quantity_mw) AS total_redispatched_mwh
FROM read_parquet('data/silver/entsoe/redispatching_cross_border/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 90 DAY
GROUP BY 1, 2
ORDER BY total_redispatched_mwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

rd = pl.read_parquet("data/silver/entsoe/redispatching_cross_border/**/*.parquet")
cost = pl.read_parquet("data/silver/entsoe/congestion_management_costs/**/*.parquet")
# Pair redispatch MW with congestion cost €
joined = rd.join(cost, on=["timestamp_utc", "in_area_code", "out_area_code"], suffix="_c")
print(joined.with_columns(
    (pl.col("amount_eur") / pl.col("quantity_mw")).alias("eur_per_mw")
).tail())
```

# Caveats

## 01 A63 shared with redispatching_internal (businessType A85)

A63 has two variants: `A46` (cross-border, this dataset) and `A85` (internal, `redispatching_internal`). Select on dataset key. *(Source: `endpoints.py L160-173`.)*

## 02 businessType A46 pinned by connector

Connector pins `businessType=A46`. *(Source: `endpoints.py L165`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `67-redispatching-cross-border-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/29-redispatching-cross-border-http-401.md`.)*

# Related datasets

- **`redispatching_internal`** — A63/A85 internal redispatching. `PT60M`. Same DocumentType, internal scope. `entsoe · transmission · hourly`
- **`countertrading`** — A91 countertrading. `PT60M`. Alternative TSO mechanism to redispatching; both manage cross-border congestion. `entsoe · transmission · hourly`
- **`congestion_management_costs`** — A92 cost view. `PT60M`. The €-side of redispatching: where the money goes. `entsoe · capacity · hourly`
- **`cross_border_flows`** — Realised physical flow. `PT60M`. Compare market-clearing flow to redispatch-adjusted flow. `entsoe · transmission · hourly`
