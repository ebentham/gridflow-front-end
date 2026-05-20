---
slug: offered_transfer_capacity_explicit
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A31 (explicit allocation)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/21-offered-transfer-capacity-explicit-http-401.md)"
sources_consulted:
  - vault/entsoe/offered_transfer_capacity_explicit.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::OfferedTransferCapacityExplicitTransformer (lines 165-167)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["offered_transfer_capacity_explicit"] (lines 213-228)
  - .planning/reconciliation/entsoe/21-offered-transfer-capacity-explicit-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/59-offered-transfer-capacity-explicit-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Explicit-auction transfer capacity, <span class="italic fg-accent">A31 explicit.</span>

**Lede:** Offered transfer capacity in MW per zone-pair for explicit allocations — capacity offered into yearly / monthly explicit auctions (Auction.Category A01).

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.offered_transfer_capacity_explicit` |
| API PATH | `/api?documentType=A31&auction.Category=A01&auction.Type=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | varies (yearly / monthly auction timing) |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A31 | DocumentType |
| 2 | A01 | auction.Category / Type |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- offered_transfer_capacity_continuous
- offered_transfer_capacity_implicit
- net_transfer_capacity
- transfer_capacity_use
- auction_revenue

# Sample chart

- **Type:** `barsH`
- **Title:** "GB ↔ FR explicit OTC by month"
- **Subtitle:** "Horizontal bars · MW · 2026"
- **Seed:** 51
- **Toggles:** `2026` (active) / `2025`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). See `commercial_schedules.md` brief for full column-by-column annotation.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC (lowercase param). | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Offered MW (directional). | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Auction-type code. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/offered_transfer_capacity_explicit/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-01-01T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1500.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-02-01T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1500.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-01T00:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2000.0** | **A29** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-01T00:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 2000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **May 2026 monthly auction allocation (2 GW)** row illustrates the typical step-up in explicit-auction capacity heading into summer. Explicit allocation is the "buy capacity in advance" product — annual and monthly tranches sold separately from the continuous and implicit products.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A31&auction.Category=A01&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/offered_transfer_capacity_explicit/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityExplicitTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&auction.Category=A01&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605010000&periodEnd=202606010000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Monthly explicit-OTC by border-direction (last 12 months)
SELECT date_trunc('month', timestamp_utc) AS month,
       in_area_code, out_area_code,
       avg(quantity_mw) AS mean_offered_mw
FROM read_parquet('data/silver/entsoe/offered_transfer_capacity_explicit/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 12 MONTH
GROUP BY 1, 2, 3
ORDER BY 1 DESC, mean_offered_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ex = pl.read_parquet("data/silver/entsoe/offered_transfer_capacity_explicit/**/*.parquet")
cont = pl.read_parquet("data/silver/entsoe/offered_transfer_capacity_continuous/**/*.parquet")
# Capacity split: explicit vs continuous
print(ex.group_by(["in_area_code", "out_area_code"]).agg(
    pl.col("quantity_mw").sum().alias("explicit_total_mwh")
).join(
    cont.group_by(["in_area_code", "out_area_code"]).agg(
        pl.col("quantity_mw").sum().alias("continuous_total_mwh")
    ),
    on=["in_area_code", "out_area_code"],
))
```

# Caveats

## 01 Lowercase domain params (in_Domain / out_Domain)

Unlike `_continuous` which uses capitalised `In_Domain`/`Out_Domain`, this variant uses lowercase. *(Source: `endpoints.py L213-228`.)*

## 02 Explicit auction is yearly + monthly product

Annual auctions sell baseload allocations; monthly auctions sell remaining capacity. Both surface through this dataset. *(Source: domain knowledge.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `59-offered-transfer-capacity-explicit-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/21-offered-transfer-capacity-explicit-http-401.md`.)*

# Related datasets

- **`offered_transfer_capacity_continuous`** — Continuous allocation OTC. `PT60M`. Same DocumentType, different Auction.Type. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_implicit`** — Implicit day-ahead allocation OTC. `PT60M`. Same DocumentType, third variant. `entsoe · transmission · hourly`
- **`auction_revenue`** — Revenue from explicit auctions (A25/B07). `PT60M`. Pair with this offered capacity for €/MW revenue calculations. `entsoe · capacity · hourly`
- **`total_capacity_allocated`** — Capacity already allocated (A26). `PT60M`. Pair to compute remaining capacity per allocation type. `entsoe · transmission · hourly`
