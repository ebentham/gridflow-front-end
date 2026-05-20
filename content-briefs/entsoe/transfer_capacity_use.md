---
slug: transfer_capacity_use
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A25 (businessType B05)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/33-transfer-capacity-use-http-401.md)"
sources_consulted:
  - vault/entsoe/transfer_capacity_use.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::TransferCapacityUseTransformer (lines 170-172)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["transfer_capacity_use"] (lines 240-251)
  - .planning/reconciliation/entsoe/33-transfer-capacity-use-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/71-transfer-capacity-use-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Use of explicit transfer capacity, <span class="italic fg-accent">A25/B05.</span>

**Lede:** Use of explicitly-allocated transfer capacity in MW per zone-pair direction — the settlement-side view of how much pre-allocated capacity holders actually nominated for physical flow.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.transfer_capacity_use` |
| API PATH | `/api?documentType=A25&businessType=B05` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | T+1h |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A25 | DocumentType |
| 2 | B05 | businessType |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- total_capacity_allocated
- total_nominated_capacity
- cross_border_flows
- net_positions
- auction_revenue

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR transfer capacity used · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 61
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Used capacity MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | B05. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/transfer_capacity_use/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1100.0 | B05 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2050.0** | **B05** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | -160.0 | B05 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → FR 19:00 (2.05 GW used)** row exactly matches `total_nominated_capacity` for the same hour — a sanity check that the settlement side and capacity-management side agree. Negative values indicate reverse-direction use.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A25&businessType=B05&Auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/transfer_capacity_use/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.TransferCapacityUseTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B05&Auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Transfer capacity use vs realised flow (sanity check)
SELECT u.timestamp_utc, u.quantity_mw AS used_capacity,
       f.flow_mw, abs(u.quantity_mw - f.flow_mw) AS gap_mw
FROM read_parquet('data/silver/entsoe/transfer_capacity_use/**/*.parquet') u
JOIN read_parquet('data/silver/entsoe/cross_border_flows/**/*.parquet') f
  ON u.timestamp_utc = f.timestamp_utc
 AND u.in_area_code = f.in_area_code
 AND u.out_area_code = f.out_area_code
ORDER BY gap_mw DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

use = pl.read_parquet("data/silver/entsoe/transfer_capacity_use/**/*.parquet")
# Per-border average use over a window
print(use.group_by(["in_area_code", "out_area_code"]).agg(
    pl.col("quantity_mw").abs().mean().alias("mean_abs_use_mw")
).sort("mean_abs_use_mw", descending=True))
```

# Caveats

## 01 A25 DocumentType is heavily overloaded

A25 is used for `transfer_capacity_use` (B05), `auction_revenue` (B07), `net_positions` (B09), `congestion_income` (B10). Always select on `(documentType, businessType)` pair. *(Source: `endpoints.py L229-291`.)*

## 02 businessType B05 pinned by connector

Connector pins `businessType=B05`. *(Source: `endpoints.py L245`.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `71-transfer-capacity-use-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/33-transfer-capacity-use-http-401.md`.)*

# Related datasets

- **`total_nominated_capacity`** — A26/B08 nomination view. `PT60M`. Same number from the capacity-management side. `entsoe · transmission · hourly`
- **`total_capacity_allocated`** — A26/A29 allocation view. `PT60M`. Pair with use to compute use-it-or-lose-it. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow. `PT60M`. Should approximately equal use after intraday adjustments. `entsoe · transmission · hourly`
- **`auction_revenue`** — A25/B07 revenue stream. `PT60M`. Pair to compute €/MW used capacity. `entsoe · capacity · hourly`
