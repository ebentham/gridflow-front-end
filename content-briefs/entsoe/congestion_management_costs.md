---
slug: congestion_management_costs
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A92
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/08-congestion-management-costs-http-401.md)"
sources_consulted:
  - vault/entsoe/congestion_management_costs.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketAmount (lines 577-594, H6 shared amount class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::CongestionManagementCostsTransformer (lines 190-192)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["congestion_management_costs"] (lines 180-185)
  - .planning/reconciliation/entsoe/08-congestion-management-costs-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/46-congestion-management-costs-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "endpoints.py L180-185 (CongestionManagementCosts)"
    source_a_says: "domain_style='zone' (single zone, not zone-pair)"
    source_b: "schemas/entsoe.py L577-594 (EntsoeTransmissionMarketAmount has in_area_code + out_area_code)"
    source_b_says: "H6 amount schema has both in/out area codes"
    orchestrator_recommendation: "Surface as Caveat — congestion_management_costs is the only H6 amount dataset with domain_style='zone' instead of 'zone_pair'. out_area_code may equal in_area_code or be empty."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Costs of congestion management, <span class="italic fg-accent">A92.</span>

**Lede:** Costs of congestion management in EUR per zone — the TSO's cost-side outlay (redispatching, countertrading) to resolve congestion, paired with congestion_income for net P&L.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.congestion_management_costs` |
| API PATH | `/api?documentType=A92` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by zone |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A92 | DocumentType |
| 2 | zone | `domain_style` (not zone-pair) |
| 3 | H6 (amount) | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- congestion_income
- redispatching_internal
- redispatching_cross_border
- countertrading
- auction_revenue

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU congestion-management costs · 30d"
- **Subtitle:** "Line · EUR · UTC · daily"
- **Seed:** 9
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Shared H6-family class `EntsoeTransmissionMarketAmount` (`schemas/entsoe.py L577-594`). For congestion_management_costs, `domain_style="zone"` — `out_area_code` may equal `in_area_code` or be empty.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L580` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Single zone EIC. | `schemas/entsoe.py L581` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | May equal in_area_code (single-zone surface). | `schemas/entsoe.py L582` |
| `amount_eur` | `float` | No | `<Point><price.amount>` | EUR cost. | `schemas/entsoe.py L583` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Cost category code. | `schemas/entsoe.py L584` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L585` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L586` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L587` |

**PARQUET PATH:** `data/silver/entsoe/congestion_management_costs/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | amount_eur | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | 18420.0 | A46 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T13:00:00+00:00** | **10Y1001A1001A82H** | **10Y1001A1001A82H** | **612400.0** | **A46** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T20:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | 32800.0 | A46 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **DE-LU 13:00 (€612 k congestion cost)** row mirrors the canonical solar-peak internal redispatch from `redispatching_internal` (6.12 GW at 13:00 × ~100 €/MW = €612 k). German Engpassmanagement is the largest line item in continental congestion costs.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A92&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/congestion_management_costs/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.CongestionManagementCostsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A92&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Monthly congestion costs by zone (last 12 months)
SELECT date_trunc('month', timestamp_utc) AS month,
       in_area_code AS zone,
       sum(amount_eur) AS monthly_cost_eur
FROM read_parquet('data/silver/entsoe/congestion_management_costs/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 365 DAY
GROUP BY 1, 2 ORDER BY 1 DESC, monthly_cost_eur DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cost = pl.read_parquet("data/silver/entsoe/congestion_management_costs/**/*.parquet")
income = pl.read_parquet("data/silver/entsoe/congestion_income/**/*.parquet")
# Net congestion P&L per zone (income - costs)
net = income.group_by(["timestamp_utc", "in_area_code"]).agg(
    pl.col("amount_eur").sum().alias("income_eur")
).join(
    cost.group_by(["timestamp_utc", "in_area_code"]).agg(
        pl.col("amount_eur").sum().alias("cost_eur")
    ),
    on=["timestamp_utc", "in_area_code"], how="outer"
)
print(net.with_columns(
    (pl.col("income_eur").fill_null(0) - pl.col("cost_eur").fill_null(0)).alias("net_eur")
).tail())
```

# Caveats

## 01 `domain_style="zone"` — not zone_pair

The only H6 amount dataset with single-zone scope. Query with `in_Domain` only; `out_area_code` may equal in_area_code or be empty. *(Source: `endpoints.py L184`; frontmatter discrepancy.)*

## 02 Pairs with congestion_income for net P&L

Cost-side counterpart to A25/B10. Net = income - cost; consistently negative for DE-LU (high redispatch costs) and positive for transit zones. *(Source: domain knowledge.)*

## 03 H6 amount transformer

Uses H6 amount-transformer variant. Output column is `amount_eur`. *(Source: `silver/entsoe/h6_market.py L121-124`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/08-congestion-management-costs-http-401.md`.)*

# Related datasets

- **`congestion_income`** — A25/B10 income counterpart. `PT60M`. Net P&L = income - this dataset. `entsoe · capacity · hourly`
- **`redispatching_internal`** — A63/A85 internal redispatching. `PT60M`. The MWh side of internal congestion management. `entsoe · transmission · hourly`
- **`redispatching_cross_border`** — A63/A46 cross-border redispatching. `PT60M`. Cross-border MWh contribution to congestion costs. `entsoe · transmission · hourly`
- **`countertrading`** — A91 countertrading. `PT60M`. Alternative mechanism — both this and countertrading produce congestion costs. `entsoe · transmission · hourly`
