---
slug: offered_transfer_capacity_continuous
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A31 (continuous allocation)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/20-offered-transfer-capacity-continuous-http-401.md)"
sources_consulted:
  - vault/entsoe/offered_transfer_capacity_continuous.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::OfferedTransferCapacityContinuousTransformer (lines 155-157)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["offered_transfer_capacity_continuous"] (lines 186-201)
  - .planning/reconciliation/entsoe/20-offered-transfer-capacity-continuous-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/58-offered-transfer-capacity-continuous-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Continuous-allocation transfer capacity, <span class="italic fg-accent">A31.</span>

**Lede:** Offered transfer capacity in MW per zone-pair direction for continuous allocations — capacity offered into the explicit continuous auction product (A01 Contract type).

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.offered_transfer_capacity_continuous` |
| API PATH | `/api?documentType=A31&Auction.Type=A01&Contract_MarketAgreement.Type=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A31 | DocumentType |
| 2 | A01/A01 | Auction.Type / Contract |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- offered_transfer_capacity_explicit
- offered_transfer_capacity_implicit
- net_transfer_capacity
- transfer_capacity_use
- total_capacity_allocated

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR continuous OTC · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 49
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). Used by 12 zone-pair quantity datasets — differentiated by dataset-key dispatch in `h6_market.py`. See `commercial_schedules.md` brief for full column-by-column annotation.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<In_Domain.mRID>` | Source zone EIC (capitalised param). | `schemas/entsoe.py L561`; `endpoints.py L195` |
| `out_area_code` | `str` | No | `<Out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Offered MW (directional). | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Carries the auction-type code. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/offered_transfer_capacity_continuous/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)` (`silver/entsoe/h6_market.py L85-91`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 4000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T11:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2800.0** | **A29** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 4000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 4000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → FR 11:00 (2.8 GW)** row mirrors the `net_transfer_capacity` derate — when NTC drops for maintenance, the offered capacity into the continuous auction follows down. Continuous allocation is the "buy capacity as you need it" product, distinct from explicit (yearly/monthly auctions) and implicit (clears with day-ahead price).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A31&Auction.Type=A01&Contract_MarketAgreement.Type=A01&In_Domain={EIC}&Out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/offered_transfer_capacity_continuous/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityContinuousTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&Auction.Type=A01&Contract_MarketAgreement.Type=A01&In_Domain=10YGB----------A&Out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Continuous-OTC offered vs realised flow (GB-FR)
SELECT o.timestamp_utc, o.quantity_mw AS offered,
       f.flow_mw AS realised, o.quantity_mw - abs(f.flow_mw) AS unused_mw
FROM read_parquet('data/silver/entsoe/offered_transfer_capacity_continuous/**/*.parquet') o
JOIN read_parquet('data/silver/entsoe/cross_border_flows/**/*.parquet') f
  ON o.timestamp_utc = f.timestamp_utc
 AND o.in_area_code = f.in_area_code
 AND o.out_area_code = f.out_area_code
ORDER BY o.timestamp_utc DESC LIMIT 24;
```

**Tab 3 — Python · polars**
```python
import polars as pl

otc = pl.read_parquet("data/silver/entsoe/offered_transfer_capacity_continuous/**/*.parquet")
# Per-border offered capacity profile — does it follow NTC?
print(otc.group_by(["in_area_code", "out_area_code"]).agg(
    pl.col("quantity_mw").mean().alias("mean_offered_mw")
))
```

# Caveats

## 01 A31 doc type shared across explicit / implicit / continuous

A31 is reused for three datasets — `offered_transfer_capacity_continuous`, `_explicit`, `_implicit` — differentiated by Auction.Type and Contract_MarketAgreement.Type extra params (capitalisation varies between variants). Select on dataset key, not DocumentType alone. *(Source: `endpoints.py L186-228`.)*

## 02 Capitalised domain params (In_Domain / Out_Domain)

A31 continuous uses `In_Domain` / `Out_Domain` (capitalised). The implicit and explicit variants use lowercase `in_Domain` / `out_Domain` — easy footgun. *(Source: `endpoints.py L195`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` is shared across 12 H6 datasets. Reconciliation finding `58-offered-transfer-capacity-continuous-no-table.md` (wontfix v3-candidate) is stale — class exists. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/20-offered-transfer-capacity-continuous-http-401.md`.)*

# Related datasets

- **`offered_transfer_capacity_explicit`** — Explicit yearly/monthly auction OTC (A31). `PT60M`. Same DocumentType, different Auction.Category. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_implicit`** — Implicit day-ahead auction OTC (A31). `PT60M`. Same DocumentType, lowercase params. `entsoe · transmission · hourly`
- **`net_transfer_capacity`** — Day-ahead NTC (A61). `PT60M`. Offered capacity is typically ≤ NTC. `entsoe · transmission · hourly`
- **`total_capacity_allocated`** — Capacity already allocated (A26). `PT60M`. Pair with offered to compute remaining capacity. `entsoe · transmission · hourly`
