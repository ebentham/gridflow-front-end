---
slug: auction_revenue
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A25 (businessType B07)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/04-auction-revenue-http-401.md)"
sources_consulted:
  - vault/entsoe/auction_revenue.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketAmount (lines 577-594, H6 shared amount class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::AuctionRevenueTransformer (lines 195-197)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["auction_revenue"] (lines 229-239)
  - .planning/reconciliation/entsoe/04-auction-revenue-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/40-auction-revenue-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Explicit auction revenue, <span class="italic fg-accent">A25/B07.</span>

**Lede:** Revenue from explicit transfer-capacity auctions in EUR per zone-pair direction — the cash side of explicit capacity allocations, paired with offered_transfer_capacity_explicit for €/MW pricing.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.auction_revenue` |
| API PATH | `/api?documentType=A25&businessType=B07` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A25 | DocumentType |
| 2 | B07 | businessType |
| 3 | H6 (amount) | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- offered_transfer_capacity_explicit
- transfer_capacity_use
- congestion_income
- congestion_management_costs
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB ↔ FR explicit-auction revenue · 30d"
- **Subtitle:** "Line · EUR · UTC · daily"
- **Seed:** 5
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Shared H6-family class `EntsoeTransmissionMarketAmount` (`schemas/entsoe.py L577-594`). Used by 3 monetary H6 datasets (`auction_revenue`, `congestion_income`, `congestion_management_costs`). `value_tag="price.amount"` in the H6 amount transformer.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L580, L589-594` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L581` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L582` |
| `amount_eur` | `float` | No | `<Point><price.amount>` | EUR auction revenue (directional). | `schemas/entsoe.py L583` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | B07 — auction revenue. | `schemas/entsoe.py L584` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L585` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L586` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L587` |

**PARQUET PATH:** `data/silver/entsoe/auction_revenue/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)` (`silver/entsoe/h6_market.py L85-91`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | amount_eur | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 18420.0 | B07 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **184600.0** | **B07** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 0.0 | B07 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → FR 19:00 (€184.6 k revenue)** row reflects the typical evening-peak auction value — when implicit clearing produces a tight 100 EUR/MWh spread, 2 GW of explicit-allocated capacity earns ~€184 k for the hour. Pair with `offered_transfer_capacity_explicit` for €/MW pricing.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A25&businessType=B07&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/auction_revenue/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.AuctionRevenueTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B07&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Monthly auction revenue by border-direction
SELECT date_trunc('month', timestamp_utc) AS month,
       in_area_code, out_area_code,
       sum(amount_eur) AS monthly_revenue_eur
FROM read_parquet('data/silver/entsoe/auction_revenue/**/*.parquet')
GROUP BY 1, 2, 3 ORDER BY 1 DESC, monthly_revenue_eur DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

rev = pl.read_parquet("data/silver/entsoe/auction_revenue/**/*.parquet")
cap = pl.read_parquet("data/silver/entsoe/offered_transfer_capacity_explicit/**/*.parquet")
# €/MW: divide revenue by offered explicit capacity
joined = rev.join(
    cap.group_by(["timestamp_utc", "in_area_code", "out_area_code"]).agg(
        pl.col("quantity_mw").sum().alias("explicit_mw")
    ),
    on=["timestamp_utc", "in_area_code", "out_area_code"]
)
print(joined.with_columns(
    (pl.col("amount_eur") / pl.col("explicit_mw")).alias("eur_per_mw")
).tail())
```

# Caveats

## 01 A25 is heavily overloaded

A25 covers `auction_revenue` (B07), `transfer_capacity_use` (B05), `net_positions` (B09), `congestion_income` (B10). Always select on `(documentType, businessType)`. *(Source: `endpoints.py L229-291`.)*

## 02 H6 amount transformer (price.amount parsing)

Auction revenue uses the H6 amount-transformer variant; `value_tag="price.amount"` parses currency values. Output column is `amount_eur`. *(Source: `silver/entsoe/h6_market.py L121-124`.)*

## 03 Pydantic class is shared (H6 amount family)

`EntsoeTransmissionMarketAmount` covers 3 H6 amount datasets. *(Source: `schemas/entsoe.py L577`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/04-auction-revenue-http-401.md`.)*

# Related datasets

- **`offered_transfer_capacity_explicit`** — Capacity offered to explicit auction. `PT60M`. Pair on `(timestamp_utc, border)` for €/MW yield. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — A25/B05 use of capacity. `PT60M`. Pair on the same A25 family — different business view. `entsoe · transmission · hourly`
- **`congestion_income`** — A25/B10 implicit-auction rents. `PT60M`. Sister A25 amount surface — separate revenue stream. `entsoe · capacity · hourly`
- **`day_ahead_prices`** — A44 prices. `PT60M`. Spread × allocated capacity = implicit-auction equivalent yield. `entsoe · prices · hourly`
