---
slug: offered_transfer_capacity_implicit
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A31 (implicit allocation)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/22-offered-transfer-capacity-implicit-http-401.md)"
sources_consulted:
  - vault/entsoe/offered_transfer_capacity_implicit.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::OfferedTransferCapacityImplicitTransformer (lines 160-162)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["offered_transfer_capacity_implicit"] (lines 202-212)
  - .planning/reconciliation/entsoe/22-offered-transfer-capacity-implicit-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/60-offered-transfer-capacity-implicit-no-table.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Implicit-auction transfer capacity, <span class="italic fg-accent">day-ahead clearing.</span>

**Lede:** Offered transfer capacity in MW per zone-pair for implicit allocations — capacity that clears through the day-ahead implicit auction with the spot price, the residual after explicit allocations.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.offered_transfer_capacity_implicit` |
| API PATH | `/api?documentType=A31&auction.Type=A01&contract_MarketAgreement.Type=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A31 | DocumentType |
| 2 | A01 | auction.Type / contract |
| 3 | implicit | Allocation method |
| 4 | 8 | Schema columns |

# Sidebar siblings

- offered_transfer_capacity_continuous
- offered_transfer_capacity_explicit
- net_positions
- net_transfer_capacity
- day_ahead_prices

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR implicit OTC · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 53
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). See `commercial_schedules.md` for full annotation. Implicit OTC is the residual capacity after explicit (yearly/monthly) tranches and is the dominant allocation method for short-term spread arbitrage.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Offered MW (directional). | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Auction-type code. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/offered_transfer_capacity_implicit/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 2500.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1300.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2500.0** | **A29** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 2500.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → FR 19:00 (2.5 GW)** row is the implicit-auction-offered capacity for the winter-evening peak — typically the explicit allocation (1.5 GW from `_explicit`) plus implicit (2.5 GW here) sums to the full NTC of 4 GW. Implicit clearing aligns with the day-ahead price difference.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A31&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/offered_transfer_capacity_implicit/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityImplicitTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Implicit-OTC vs price spread (GB-FR — does offered cap match arb signal?)
SELECT i.timestamp_utc, i.quantity_mw AS implicit_mw,
       gb.price_eur_mwh - fr.price_eur_mwh AS spread_eur
FROM read_parquet('data/silver/entsoe/offered_transfer_capacity_implicit/**/*.parquet') i
JOIN read_parquet('data/silver/entsoe/day_ahead_prices/**/*.parquet') gb
  ON i.timestamp_utc = gb.timestamp_utc AND gb.area_code = '10YGB----------A'
JOIN read_parquet('data/silver/entsoe/day_ahead_prices/**/*.parquet') fr
  ON i.timestamp_utc = fr.timestamp_utc AND fr.area_code = '10YFR-RTE------C'
WHERE i.in_area_code = '10YGB----------A' AND i.out_area_code = '10YFR-RTE------C'
ORDER BY i.timestamp_utc DESC LIMIT 24;
```

**Tab 3 — Python · polars**
```python
import polars as pl

imp = pl.read_parquet("data/silver/entsoe/offered_transfer_capacity_implicit/**/*.parquet")
ntc = pl.read_parquet("data/silver/entsoe/net_transfer_capacity/**/*.parquet")
# What fraction of NTC is offered to implicit (vs explicit / continuous)?
joined = imp.join(ntc, on=["timestamp_utc", "in_area_code", "out_area_code"], suffix="_n")
print(joined.with_columns(
    (pl.col("quantity_mw") / pl.col("ntc_mw")).alias("implicit_share")
).select(["timestamp_utc", "implicit_share"]).tail())
```

# Caveats

## 01 Lowercase domain params (in_Domain / out_Domain)

Like `_explicit`, this variant uses lowercase. The `_continuous` variant uses capitalised. *(Source: `endpoints.py L202-212`.)*

## 02 Implicit allocation clears with day-ahead price

Unlike explicit (sold separately in advance) or continuous (sold on demand), implicit capacity clears as part of the day-ahead spot auction. *(Source: domain knowledge.)*

## 03 Residual after explicit allocations

Implicit OTC is typically `NTC - sum(explicit allocations)`. When explicit allocations are large, implicit shrinks. *(Source: domain knowledge.)*

## 04 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `60-offered-transfer-capacity-implicit-no-table.md` (wontfix v3-candidate) is stale. *(Source: `schemas/entsoe.py L557`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/22-offered-transfer-capacity-implicit-http-401.md`.)*

# Related datasets

- **`offered_transfer_capacity_continuous`** — Continuous allocation OTC. `PT60M`. Same DocumentType, different Auction.Type. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_explicit`** — Explicit yearly/monthly OTC. `PT60M`. Same DocumentType, third variant. `entsoe · transmission · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices. `PT60M`. Implicit OTC clears with these prices — pair on `(timestamp_utc, area_code)` for spread-vs-cap modelling. `entsoe · prices · hourly`
- **`net_positions`** — Implicit-auction net positions per zone. `PT60M`. Downstream consumer of implicit OTC allocation. `entsoe · capacity · hourly`
