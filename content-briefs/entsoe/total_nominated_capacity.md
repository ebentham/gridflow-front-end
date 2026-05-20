---
slug: total_nominated_capacity
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A26 (businessType B08)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/32-total-nominated-capacity-http-401.md)"
sources_consulted:
  - vault/entsoe/total_nominated_capacity.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::TotalNominatedCapacityTransformer (lines 175-177)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["total_nominated_capacity"] (lines 252-258)
  - .planning/reconciliation/entsoe/32-total-nominated-capacity-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/70-total-nominated-capacity-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Total nominated capacity, <span class="italic fg-accent">B08.</span>

**Lede:** Total nominated capacity in MW per zone-pair direction — capacity that holders have nominated for actual physical use, distinct from "allocated" (sold but not yet nominated).

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.total_nominated_capacity` |
| API PATH | `/api?documentType=A26&businessType=B08` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | varies |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A26 | DocumentType |
| 2 | B08 | businessType |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- total_capacity_allocated
- transfer_capacity_use
- commercial_schedules
- cross_border_flows
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR nominated capacity · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 59
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Nominated MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | B08 — "Total nominated capacity". | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/total_nominated_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1200.0 | B08 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2050.0** | **B08** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | -150.0 | B08 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → FR 19:00 (2.05 GW nominated)** row tracks just below the 2.1 GW allocated at the same hour from `total_capacity_allocated` — the 50 MW gap is typical "use-it-or-lose-it" capacity that holders chose not to nominate. Negative values (SP11) indicate reverse-direction nomination.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A26&businessType=B08&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/total_nominated_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.TotalNominatedCapacityTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A26&businessType=B08&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Allocated vs nominated gap (use-it-or-lose-it tracking)
SELECT a.timestamp_utc, a.in_area_code, a.out_area_code,
       a.quantity_mw AS allocated_mw,
       n.quantity_mw AS nominated_mw,
       a.quantity_mw - n.quantity_mw AS lost_mw
FROM read_parquet('data/silver/entsoe/total_capacity_allocated/**/*.parquet') a
JOIN read_parquet('data/silver/entsoe/total_nominated_capacity/**/*.parquet') n
  ON a.timestamp_utc = n.timestamp_utc
 AND a.in_area_code = n.in_area_code
 AND a.out_area_code = n.out_area_code
ORDER BY lost_mw DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

nom = pl.read_parquet("data/silver/entsoe/total_nominated_capacity/**/*.parquet")
phys = pl.read_parquet("data/silver/entsoe/cross_border_flows/**/*.parquet")
# Nominated vs realised — how often does nomination actually flow?
joined = nom.join(phys, on=["timestamp_utc", "in_area_code", "out_area_code"], suffix="_p")
print(joined.with_columns(
    (pl.col("flow_mw") - pl.col("quantity_mw")).alias("intraday_adj_mw")
).select(["timestamp_utc", "intraday_adj_mw"]).tail())
```

# Caveats

## 01 A26 shared with total_capacity_allocated

A26 is also used for `total_capacity_allocated` (A29 businessType). Select on dataset key. *(Source: `endpoints.py L259-270`.)*

## 02 businessType B08 pinned by connector

Connector pins `businessType=B08`. *(Source: `endpoints.py L257`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `70-total-nominated-capacity-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/32-total-nominated-capacity-http-401.md`.)*

# Related datasets

- **`total_capacity_allocated`** — Same A26 DocumentType, A29 businessType. `PT60M`. Allocated vs nominated gap = use-it-or-lose-it. `entsoe · transmission · hourly`
- **`commercial_schedules`** — Aggregated commercial nominations (A09). `PT60M`. Closely related to this surface but at the schedule level. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow. `PT60M`. Nominated vs realised = intraday adjustment. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — Settlement-side use of capacity. `PT60M`. Cross-check this dataset's nomination view. `entsoe · transmission · hourly`
