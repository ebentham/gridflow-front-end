---
slug: aggregated_balancing_energy_bids
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A24/A51
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/03-aggregated-balancing-energy-bids-http-401.md)"
sources_consulted:
  - vault/entsoe/aggregated_balancing_energy_bids.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeBalancingEnergyBid (lines 616-636, shared with balancing_energy_bids)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::AggregatedBalancingEnergyBidsTransformer (lines 141-143)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["aggregated_balancing_energy_bids"] (lines 339-344)
  - .planning/reconciliation/entsoe/03-aggregated-balancing-energy-bids-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/39-aggregated-balancing-energy-bids-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Aggregated balancing bid stack, <span class="italic fg-accent">A24/A51.</span>

**Lede:** Aggregated balancing energy bids in MW per single area — the area-aggregated version of A37 individual bids, with bid_mrid set per aggregated tranche rather than per individual bidder.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.aggregated_balancing_energy_bids` |
| API PATH | `/api?documentType=A24&processType=A51` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | low — aggregated rows |
| PRIMARY KEY | `(timestamp_utc, area_code, bid_mrid, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A24 | DocumentType |
| 2 | A51 | processType |
| 3 | aggregated | View granularity |
| 4 | 11 | Schema columns |

# Sidebar siblings

- balancing_energy_bids
- procured_balancing_capacity
- contracted_reserves
- activated_balancing_qty
- current_balancing_state

# Sample chart

- **Type:** `barsH`
- **Title:** "Aggregated bid stack by direction · 24h"
- **Subtitle:** "Horizontal bars · MW · UTC · 6 May 2026"
- **Seed:** 93
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Reuses `gridflow/schemas/entsoe.py` · `EntsoeBalancingEnergyBid` (lines 616-636) — same fields as `balancing_energy_bids`. Differs only in `area_columns=("area_domain",)` (single-area dispatch) vs `connecting_domain` for the individual-bid surface.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L619` |
| `area_code` | `str` | No | `<area_Domain.mRID>` | Single area EIC (renamed from area_domain). | `schemas/entsoe.py L620`; `silver/entsoe/h8_balancing.py L143` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Aggregated bid MW. | `schemas/entsoe.py L621` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Reserve product code. | `schemas/entsoe.py L622` |
| `bid_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` (renamed) | Per-aggregate identifier. | `schemas/entsoe.py L623` |
| `direction` | `str` | Yes (default `""`) | `<flow_Direction>` | Up / down direction. | `schemas/entsoe.py L624` |
| `original_market_product` | `str` | Yes (default `""`) | `<Original_Market_Product>` | Local product code. | `schemas/entsoe.py L625` |
| `standard_market_product` | `str` | Yes (default `""`) | `<Standard_Market_Product>` | Standardised product code. | `schemas/entsoe.py L626` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L627` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L628` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L629` |

**PARQUET PATH:** `data/silver/entsoe/aggregated_balancing_energy_bids/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, bid_mrid, direction)` (`silver/entsoe/h8_balancing.py L138`, inherited)

# Sample data

| timestamp_utc | area_code | quantity_mw | business_type | bid_mrid | direction | standard_market_product | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | 480.0 | B74 | agg-mfrr-up-001 | up | A04 | PT60M | entsoe |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | 120.0 | B74 | agg-mfrr-down-001 | down | A04 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **820.0** | **B74** | **agg-afrr-up-001** | **up** | **A02** | **PT60M** | **entsoe** |

**Sources:** Synthesised. The highlighted **aFRR up aggregate (820 MW)** row collapses what A37 publishes as many individual bids — useful when the use case is "how much was offered total" rather than per-bidder ladder analysis.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A24&processType=A51&area_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/aggregated_balancing_energy_bids/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.AggregatedBalancingEnergyBidsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A24&processType=A51&area_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Aggregated bid stack per zone per direction (last 7 days)
SELECT date_trunc('day', timestamp_utc) AS day, area_code, direction,
       sum(quantity_mw) AS total_aggregated_mw
FROM read_parquet('data/silver/entsoe/aggregated_balancing_energy_bids/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2, 3 ORDER BY 1 DESC, total_aggregated_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

agg = pl.read_parquet("data/silver/entsoe/aggregated_balancing_energy_bids/**/*.parquet")
ind = pl.read_parquet("data/silver/entsoe/balancing_energy_bids/**/*.parquet")
# Aggregate-vs-individual consistency (sanity check)
sum_ind = ind.group_by(["timestamp_utc", "area_code", "direction"]).agg(
    pl.col("quantity_mw").sum().alias("ind_total_mw")
)
sum_agg = agg.group_by(["timestamp_utc", "area_code", "direction"]).agg(
    pl.col("quantity_mw").sum().alias("agg_total_mw")
)
print(sum_ind.join(sum_agg, on=["timestamp_utc", "area_code", "direction"]).tail())
```

# Caveats

## 01 area_Domain (not connecting_Domain)

A24 uses `area_Domain` (different from A37's `connecting_Domain`). The H8 transformer renames both to `area_code` so silver consumers see a uniform column. *(Source: `silver/entsoe/h8_balancing.py L143`; `endpoints.py L339-344`.)*

## 02 Reuses balancing_energy_bids Pydantic schema

Same `EntsoeBalancingEnergyBid` class. The `bid_mrid` field here represents the aggregate identifier rather than an individual bidder. *(Source: `schemas/entsoe.py L616`.)*

## 03 Aggregation is by area + direction + product

A24/A51 aggregates A37 over individual bidders; rows are by area / direction / product combination. Use this dataset when the individual ladder is not needed. *(Source: domain knowledge.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code, bid_mrid, direction)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h8_balancing.py L138`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/03-aggregated-balancing-energy-bids-http-401.md`.)*

# Related datasets

- **`balancing_energy_bids`** — A37/A47 individual bid stack. `PT60M`. The per-bidder source that this dataset aggregates. `entsoe · balancing · hourly`
- **`procured_balancing_capacity`** — A15/A51 procurement. `PT60M`. Procurement decisions clear against the aggregated stack. `entsoe · balancing · hourly`
- **`activated_balancing_qty`** — A83/A16 activation. `PT60M`. Activation MWh is bounded by the procured fraction of this aggregated offer. `entsoe · balancing · hourly`
- **`current_balancing_state`** — A86/B33 area control error. `PT30M`. Drives whether up- or down-bids are activated. `entsoe · balancing · 30 min`
