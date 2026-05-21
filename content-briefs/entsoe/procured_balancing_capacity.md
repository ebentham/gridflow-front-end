---
slug: procured_balancing_capacity
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A15/A51
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/28-procured-balancing-capacity-http-401.md)"
sources_consulted:
  - vault/entsoe/procured_balancing_capacity.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeBalancingCapacity (lines 639-656)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::ProcuredBalancingCapacityTransformer (lines 146-161)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["procured_balancing_capacity"] (lines 345-352)
  - .planning/reconciliation/entsoe/28-procured-balancing-capacity-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/66-procured-balancing-capacity-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Procured balancing capacity, <span class="italic fg-accent">A15/A51.</span>

**Lede:** Procured balancing capacity in MW per single area — the capacity-procurement outcome that feeds the contracted reserves pool, paired with market agreement type.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.procured_balancing_capacity` |
| API PATH | `/api?documentType=A15&processType=A51` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by area |
| PRIMARY KEY | `(timestamp_utc, area_code, market_agreement_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A15 | DocumentType |
| 2 | A51 | processType |
| 3 | H8 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- contracted_reserves
- balancing_energy_bids
- aggregated_balancing_energy_bids
- cross_zonal_balancing_capacity
- activated_balancing_qty

# Sample chart

- **Type:** `barsH`
- **Title:** "Procured capacity by market_agreement_type · 24h"
- **Subtitle:** "Horizontal bars · MW · UTC · 6 May 2026"
- **Seed:** 89
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeBalancingCapacity` (lines 639-656). H8-family transformer; uses `area_Domain`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L642, L651-656` |
| `area_code` | `str` | No | `<area_Domain.mRID>` | Single area EIC (renamed from area_domain). | `schemas/entsoe.py L643`; `silver/entsoe/h8_balancing.py L107` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Procured MW. | `schemas/entsoe.py L644` |
| `market_agreement_type` | `str` | Yes (default `""`) | `<Type_MarketAgreement.Type>` | Contract duration code (A01 daily, A02 weekly, etc.). | `schemas/entsoe.py L645` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Reserve product code. | `schemas/entsoe.py L646` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L647` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L648` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L649` |

**PARQUET PATH:** `data/silver/entsoe/procured_balancing_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, market_agreement_type)` (`silver/entsoe/h8_balancing.py L161`)

# Sample data

| timestamp_utc | area_code | quantity_mw | market_agreement_type | business_type | resolution | data_provider |
|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 1200.0 | A01 | B95 | PT60M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 800.0 | A02 | B95 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **1450.0** | **A01** | **B95** | **PT60M** | **entsoe** |

**Sources:** Synthesised against typical GB procurement. The highlighted **17:00 procurement (1.45 GW daily product)** row illustrates the typical evening-peak tranche — procurement increases for hours where the TSO expects activation demand.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A15&processType=A51&area_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/procured_balancing_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.ProcuredBalancingCapacityTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A15&processType=A51&area_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Procurement by market agreement type per zone (last 30 days)
SELECT area_code, market_agreement_type, business_type,
       avg(quantity_mw) AS mean_mw
FROM read_parquet('data/silver/entsoe/procured_balancing_capacity/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2, 3 ORDER BY mean_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

proc = pl.read_parquet("data/silver/entsoe/procured_balancing_capacity/**/*.parquet")
cr = pl.read_parquet("data/silver/entsoe/contracted_reserves/**/*.parquet")
# Does procurement equal contracted? (Should within product type)
joined = proc.join(
    cr.group_by(["timestamp_utc", "area_code"]).agg(pl.col("quantity_mw").sum().alias("contracted")),
    on=["timestamp_utc", "area_code"], how="left"
)
print(joined.tail())
```

# Caveats

## 01 H8 transformer family

Uses shared `_H8BalancingTransformer` base. `area_domain` renamed to `area_code`. *(Source: `silver/entsoe/h8_balancing.py L146-161`.)*

## 02 `market_agreement_type` distinguishes products

A01 (daily), A02 (weekly), etc. — each contract product surfaces with the same DocumentType. Filter on this field to compare like-for-like. *(Source: `schemas/entsoe.py L645`.)*

## 03 Optional `Type_MarketAgreement.Type` filter

Connector exposes `Type_MarketAgreement.Type` as optional — callers can pin to one product or fetch all. *(Source: `endpoints.py L351`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code, market_agreement_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h8_balancing.py L161`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/28-procured-balancing-capacity-http-401.md`.)*

# Related datasets

- **`contracted_reserves`** — A81 contracted reserves. `PT60M`. Procurement outcome feeds the contracted pool. `entsoe · balancing · hourly`
- **`balancing_energy_bids`** — A37/A47 bid stack. `PT60M`. The bids procurement clears against. `entsoe · balancing · hourly`
- **`cross_zonal_balancing_capacity`** — A38/A51 cross-zonal capacity. `PT60M`. Cross-border procurement that supplements domestic A15. `entsoe · balancing · hourly`
- **`activated_balancing_qty`** — A83/A16 activations. `PT60M`. Pair to compute reserve-utilisation = activated / procured. `entsoe · balancing · hourly`
