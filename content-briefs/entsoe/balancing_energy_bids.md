---
slug: balancing_energy_bids
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A37/A47/B74
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/05-balancing-energy-bids-http-401.md)"
sources_consulted:
  - vault/entsoe/balancing_energy_bids.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeBalancingEnergyBid (lines 616-636)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::BalancingEnergyBidsTransformer (lines 120-138)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["balancing_energy_bids"] (lines 326-338)
  - .planning/reconciliation/entsoe/05-balancing-energy-bids-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/41-balancing-energy-bids-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Balancing bid stack, <span class="italic fg-accent">A37/A47/B74.</span>

**Lede:** Individual balancing energy bids in MW per connecting area — the raw bid-stack that procurement clears against, with bid_mrid, direction, and standard / original market product identifiers.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.balancing_energy_bids` |
| API PATH | `/api?documentType=A37&processType=A47&businessType=B74` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | high — many bids per period |
| PRIMARY KEY | `(timestamp_utc, area_code, bid_mrid, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A37 | DocumentType |
| 2 | A47 | processType |
| 3 | B74 | businessType (pinned) |
| 4 | 11 | Schema columns |

# Sidebar siblings

- aggregated_balancing_energy_bids
- procured_balancing_capacity
- contracted_reserves
- activated_balancing_qty
- cross_zonal_balancing_capacity

# Sample chart

- **Type:** `priceLadder`
- **Title:** "Balancing bid stack · single period"
- **Subtitle:** "Price ladder · EUR/MWh · UTC · single hour"
- **Seed:** 91
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeBalancingEnergyBid` (lines 616-636). H8-family transformer with `connecting_Domain` (cross-area-pair-style dispatch).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L619, L631-636` |
| `area_code` | `str` | No | `<connecting_Domain.mRID>` | Connecting area EIC (renamed by H8 transformer from connecting_domain). | `schemas/entsoe.py L620`; `silver/entsoe/h8_balancing.py L107` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Bid MW. | `schemas/entsoe.py L621` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Bid business code. | `schemas/entsoe.py L622` |
| `bid_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` (renamed) | Individual bid identifier. | `schemas/entsoe.py L623`; `silver/entsoe/h8_balancing.py L109` |
| `direction` | `str` | Yes (default `""`) | `<flow_Direction>` (renamed) | Up / down direction code. | `schemas/entsoe.py L624` |
| `original_market_product` | `str` | Yes (default `""`) | `<Original_Market_Product>` | Bidder's product designation. | `schemas/entsoe.py L625` |
| `standard_market_product` | `str` | Yes (default `""`) | `<Standard_Market_Product>` | Standardised product designation. | `schemas/entsoe.py L626` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L627` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L628` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L629` |

**PARQUET PATH:** `data/silver/entsoe/balancing_energy_bids/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, bid_mrid, direction)` (`silver/entsoe/h8_balancing.py L138`)

# Sample data

| timestamp_utc | area_code | quantity_mw | business_type | bid_mrid | direction | original_market_product | standard_market_product | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | 50.0 | B74 | bid-001 | up | mFRR-up | A04 | PT60M | entsoe |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | 100.0 | B74 | bid-002 | up | mFRR-up | A04 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **150.0** | **B74** | **bid-003** | **up** | **mFRR-up** | **A04** | **PT60M** | **entsoe** |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | 80.0 | B74 | bid-004 | down | mFRR-down | A04 | PT60M | entsoe |

**Sources:** Synthesised. The highlighted **150 MW mFRR-up bid (bid-003)** illustrates a single bid in the stack — typical evening-peak hour has 20-50 separate bids per direction. Pair across all bid_mrids in a settlement period for the full ladder used to clear `procured_balancing_capacity`.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A37&processType=A47&businessType=B74&connecting_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}&offset=0`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/balancing_energy_bids/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.BalancingEnergyBidsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A37&processType=A47&businessType=B74&connecting_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000&offset=0
```

**Tab 2 — DuckDB · SQL**
```sql
-- Bid stack depth per direction per hour (count of bids)
SELECT timestamp_utc, area_code, direction,
       count(*) AS bid_count,
       sum(quantity_mw) AS total_offered_mw
FROM read_parquet('data/silver/entsoe/balancing_energy_bids/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2, 3 ORDER BY timestamp_utc DESC LIMIT 100;
```

**Tab 3 — Python · polars**
```python
import polars as pl

bids = pl.read_parquet("data/silver/entsoe/balancing_energy_bids/**/*.parquet")
# Bid concentration — which standard products dominate the stack?
print(bids.group_by(["standard_market_product", "direction"]).agg(
    pl.col("quantity_mw").sum().alias("total_mw"),
    pl.col("bid_mrid").n_unique().alias("n_bids"),
).sort("total_mw", descending=True).head())
```

# Caveats

## 01 connecting_Domain (not area_Domain)

A37 uses `connecting_Domain` for the area param (renamed by H8 transformer). *(Source: `endpoints.py L326-338`.)*

## 02 Offset paging

Connector exposes `offset` as optional — large bid stacks may require multiple requests with offset paging. Default offset is 0. *(Source: `endpoints.py L331-336`.)*

## 03 bid_mrid is the per-bid identifier

`bid_mrid` is renamed from `<TimeSeries><mRID>` — each bid is a separate TimeSeries. Dedup includes bid_mrid + direction. *(Source: `silver/entsoe/h8_balancing.py L109, L138`.)*

## 04 standard_market_product vs original_market_product

Standard = harmonised across TSOs (e.g. A04 = mFRR); original = bidder's local code. Use standard for cross-zone aggregation. *(Source: `schemas/entsoe.py L625-626`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/05-balancing-energy-bids-http-401.md`.)*

# Related datasets

- **`aggregated_balancing_energy_bids`** — A24/A51 aggregated version of this dataset. `PT60M`. Same schema but aggregated by area_Domain, no bid_mrid. `entsoe · balancing · hourly`
- **`procured_balancing_capacity`** — A15/A51 procurement. `PT60M`. Clears against this bid stack. `entsoe · balancing · hourly`
- **`activated_balancing_qty`** — A83/A16 activation MWh. `PT60M`. Identifies which bids were dispatched. `entsoe · balancing · hourly`
- **`contracted_reserves`** — A81 contracted reserves. `PT60M`. Pre-arranged capacity from cleared bids. `entsoe · balancing · hourly`
