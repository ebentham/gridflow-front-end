---
slug: total_capacity_allocated
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A26 (businessType A29)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/31-total-capacity-allocated-http-401.md)"
sources_consulted:
  - vault/entsoe/total_capacity_allocated.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::TotalCapacityAllocatedTransformer (lines 180-182)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["total_capacity_allocated"] (lines 259-270)
  - .planning/reconciliation/entsoe/31-total-capacity-allocated-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/69-total-capacity-allocated-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Total capacity already allocated, <span class="italic fg-accent">cumulative.</span>

**Lede:** Cumulative MW already allocated through explicit and continuous auctions per zone-pair direction — the "already taken" denominator paired with offered capacity to compute remaining.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.total_capacity_allocated` |
| API PATH | `/api?documentType=A26&businessType=A29` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | varies |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A26 | DocumentType |
| 2 | A29 | businessType |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- total_nominated_capacity
- offered_transfer_capacity_continuous
- offered_transfer_capacity_explicit
- transfer_capacity_use
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR allocated capacity · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 57
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Cumulative allocated MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | A29 — "Total capacity already allocated". | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/total_capacity_allocated/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1500.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1800.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2100.0** | **A29** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |

**Sources:** Synthesised. The highlighted **GB → FR 19:00 (2.1 GW already allocated)** row mirrors the typical evening accumulation: yearly + monthly + day-ahead explicit allocations net to ~2.1 GW out of the 4 GW NTC, leaving 1.9 GW available for the implicit auction.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A26&businessType=A29&auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/total_capacity_allocated/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.TotalCapacityAllocatedTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A26&businessType=A29&auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Capacity remaining: NTC - allocated
SELECT a.timestamp_utc, a.in_area_code, a.out_area_code,
       n.ntc_mw, a.quantity_mw AS allocated_mw,
       n.ntc_mw - a.quantity_mw AS remaining_mw
FROM read_parquet('data/silver/entsoe/total_capacity_allocated/**/*.parquet') a
JOIN read_parquet('data/silver/entsoe/net_transfer_capacity/**/*.parquet') n
  ON a.timestamp_utc = n.timestamp_utc
 AND a.in_area_code = n.in_area_code
 AND a.out_area_code = n.out_area_code
ORDER BY a.timestamp_utc DESC LIMIT 48;
```

**Tab 3 — Python · polars**
```python
import polars as pl

alloc = pl.read_parquet("data/silver/entsoe/total_capacity_allocated/**/*.parquet")
# Allocation share per border-direction (% of period)
print(alloc.group_by(["in_area_code", "out_area_code"]).agg(
    pl.col("quantity_mw").mean().alias("mean_allocated_mw")
).sort("mean_allocated_mw", descending=True))
```

# Caveats

## 01 A26 shared with total_nominated_capacity

A26 is also used for `total_nominated_capacity` (B08 businessType). Select on dataset key, not DocumentType alone. *(Source: `endpoints.py L252-258`.)*

## 02 businessType A29 pinned by connector

Connector pins `businessType=A29` (Total already allocated). Other A26/businessType combinations return different surfaces. *(Source: `endpoints.py L264-266`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `69-total-capacity-allocated-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/31-total-capacity-allocated-http-401.md`.)*

# Related datasets

- **`total_nominated_capacity`** — Same A26 DocumentType, B08 businessType. `PT60M`. Tracks what was *nominated* vs what was *allocated*. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_explicit`** — Capacity offered for explicit auction. `PT60M`. Difference between offered and allocated = unsold capacity. `entsoe · transmission · hourly`
- **`net_transfer_capacity`** — Day-ahead NTC. `PT60M`. NTC - allocated = remaining capacity. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — A25/B05 settlement view. `PT60M`. Settlement-side cross-check. `entsoe · transmission · hourly`
