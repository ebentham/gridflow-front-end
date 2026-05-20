---
slug: congestion_income
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A25 (businessType B10)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/07-congestion-income-http-401.md)"
sources_consulted:
  - vault/entsoe/congestion_income.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketAmount (lines 577-594, H6 shared amount class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::CongestionIncomeTransformer (lines 200-202)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["congestion_income"] (lines 271-281)
  - .planning/reconciliation/entsoe/07-congestion-income-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/45-congestion-income-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Congestion-rent income, <span class="italic fg-accent">A25/B10.</span>

**Lede:** Congestion income in EUR per zone-pair direction — the rent collected by TSOs from price spreads across capacity-constrained borders in implicit and flow-based allocations.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.congestion_income` |
| API PATH | `/api?documentType=A25&businessType=B10` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A25 | DocumentType |
| 2 | B10 | businessType |
| 3 | H6 (amount) | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- congestion_management_costs
- auction_revenue
- transfer_capacity_use
- net_positions
- day_ahead_prices

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB ↔ FR congestion income · 30d"
- **Subtitle:** "Line · EUR · UTC · daily"
- **Seed:** 7
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Shared H6-family class `EntsoeTransmissionMarketAmount` (`schemas/entsoe.py L577-594`). See `auction_revenue.md` for column-by-column annotation — same shape.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L580` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L581` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L582` |
| `amount_eur` | `float` | No | `<Point><price.amount>` | EUR congestion income (directional). | `schemas/entsoe.py L583` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | B10 — congestion income. | `schemas/entsoe.py L584` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L585` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L586` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L587` |

**PARQUET PATH:** `data/silver/entsoe/congestion_income/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | amount_eur | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 22400.0 | B10 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **148200.0** | **B10** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 87600.0 | B10 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB ↔ FR 19:00 (€148.2 k congestion income)** row reflects implicit-auction rents — when prices diverge across borders, the implicit-allocated capacity earns the spread. Distinct from `auction_revenue` (explicit-auction proceeds) — both are TSO income streams but from different mechanisms.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A25&businessType=B10&contract_MarketAgreement.Type=A01&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/congestion_income/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.CongestionIncomeTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B10&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Annual congestion income by border (last 12 months)
SELECT in_area_code, out_area_code,
       sum(amount_eur) AS annual_income_eur,
       count(*) FILTER (WHERE amount_eur > 0) AS active_hours
FROM read_parquet('data/silver/entsoe/congestion_income/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 365 DAY
GROUP BY 1, 2 ORDER BY annual_income_eur DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ci = pl.read_parquet("data/silver/entsoe/congestion_income/**/*.parquet")
da = pl.read_parquet("data/silver/entsoe/day_ahead_prices/**/*.parquet")
# Congestion income vs implicit spread
gb = da.filter(pl.col("area_code") == "10YGB----------A").select(["timestamp_utc", "price_eur_mwh"]).rename({"price_eur_mwh": "gb_price"})
fr = da.filter(pl.col("area_code") == "10YFR-RTE------C").select(["timestamp_utc", "price_eur_mwh"]).rename({"price_eur_mwh": "fr_price"})
spread = gb.join(fr, on="timestamp_utc").with_columns((pl.col("gb_price") - pl.col("fr_price")).abs().alias("spread"))
print(ci.join(spread, on="timestamp_utc").tail())
```

# Caveats

## 01 A25 is heavily overloaded

A25 covers `congestion_income` (B10), `auction_revenue` (B07), `transfer_capacity_use` (B05), `net_positions` (B09). Always select on `(documentType, businessType)`. *(Source: `endpoints.py L229-291`.)*

## 02 Distinct from auction_revenue

Both are TSO income but from different allocation mechanisms — auction (explicit) vs congestion-rent (implicit). Sum both for total cross-border revenue. *(Source: domain knowledge.)*

## 03 H6 amount transformer

Uses H6 amount-transformer variant (`value_tag="price.amount"`). *(Source: `silver/entsoe/h6_market.py L121-124`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/07-congestion-income-http-401.md`.)*

# Related datasets

- **`congestion_management_costs`** — A92 costs counterpart. `PT60M`. Net congestion P&L = this dataset - congestion_management_costs. `entsoe · capacity · hourly`
- **`auction_revenue`** — A25/B07 explicit auction revenue. `PT60M`. Sister revenue stream from explicit allocations. `entsoe · capacity · hourly`
- **`day_ahead_prices`** — A44 prices. `PT60M`. Congestion income tracks spread × allocated capacity. `entsoe · prices · hourly`
- **`net_transfer_capacity`** — A61 NTC. `PT60M`. The capacity constraint that creates congestion. `entsoe · transmission · hourly`
