---
slug: balancing_financial_expenses_income
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A87
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/06-balancing-financial-expenses-income-http-401.md)"
sources_consulted:
  - vault/entsoe/balancing_financial_expenses_income.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeBalancingFinancial (lines 680-696)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::BalancingFinancialExpensesIncomeTransformer (lines 194-210)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["balancing_financial_expenses_income"] (lines 361-366)
  - .planning/reconciliation/entsoe/06-balancing-financial-expenses-income-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/42-balancing-financial-expenses-income-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Balancing financial expenses and income, <span class="italic fg-accent">A87.</span>

**Lede:** Financial expenses and income for balancing in EUR per control area — the €-side P&L of the balancing mechanism, distinct from MWh activations and MW capacity.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.balancing_financial_expenses_income` |
| API PATH | `/api?documentType=A87` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies |
| PRIMARY KEY | `(timestamp_utc, area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A87 | DocumentType |
| 2 | control_area | `domain_style` |
| 3 | H8 | Shared transformer family (amount_eur variant) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- activated_balancing_prices
- contracted_reserves
- procured_balancing_capacity
- congestion_income
- auction_revenue

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB balancing P&L · 90d"
- **Subtitle:** "Line · EUR · UTC · daily"
- **Seed:** 97
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeBalancingFinancial` (lines 680-696). H8-family transformer with `value_tag="price.amount"` instead of "quantity" — outputs `amount_eur` instead of `quantity_mw`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L683, L691-696` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC (renamed from control_area_domain). | `schemas/entsoe.py L684`; `silver/entsoe/h8_balancing.py L200` |
| `amount_eur` | `float` | No | `<Point><price.amount>` | EUR (expense if positive, income if negative depending on businessType). | `schemas/entsoe.py L685` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Distinguishes expense / income line items. | `schemas/entsoe.py L686` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L687` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L688` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L689` |

**PARQUET PATH:** `data/silver/entsoe/balancing_financial_expenses_income/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, business_type)` (`silver/entsoe/h8_balancing.py L210`)

# Sample data

| timestamp_utc | area_code | amount_eur | business_type | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 42180.0 | B45 | PT60M | entsoe |
| 2026-05-06T08:00:00+00:00 | 10YGB----------A | 81420.0 | B45 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **184600.0** | **B45** | **PT60M** | **entsoe** |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | -28500.0 | B47 | PT60M | entsoe |

**Sources:** Synthesised. The highlighted **GB 17:00 (€184.6 k expense, B45)** row is the typical evening-peak balancing cost — the TSO paid ~€185 k that hour to acquire upward balancing. The companion B47 row of -€28.5 k is income from downward bids (where the TSO was paid to absorb surplus).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A87&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/balancing_financial_expenses_income/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.BalancingFinancialExpensesIncomeTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A87&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily net balancing P&L per zone
SELECT date_trunc('day', timestamp_utc) AS day, area_code,
       sum(CASE WHEN amount_eur > 0 THEN amount_eur ELSE 0 END) AS expense_eur,
       sum(CASE WHEN amount_eur < 0 THEN amount_eur ELSE 0 END) AS income_eur,
       sum(amount_eur) AS net_eur
FROM read_parquet('data/silver/entsoe/balancing_financial_expenses_income/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2 ORDER BY 1, net_eur DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

fin = pl.read_parquet("data/silver/entsoe/balancing_financial_expenses_income/**/*.parquet")
qty = pl.read_parquet("data/silver/entsoe/activated_balancing_qty/**/*.parquet")
# €/MWh implied by financial / quantity
joined = fin.group_by(["timestamp_utc", "area_code"]).agg(
    pl.col("amount_eur").sum().alias("total_eur")
).join(
    qty.group_by(["timestamp_utc", "area_code"]).agg(
        pl.col("quantity_mwh").sum().alias("total_mwh")
    ),
    on=["timestamp_utc", "area_code"]
)
print(joined.with_columns((pl.col("total_eur") / pl.col("total_mwh")).alias("eur_per_mwh")).tail())
```

# Caveats

## 01 value_tag="price.amount" (not quantity)

A87 carries currency values, so the transformer parses `<Point><price.amount>` rather than `<Point><quantity>`. Output column is `amount_eur`. *(Source: `silver/entsoe/h8_balancing.py L197-199`.)*

## 02 Sign convention varies by businessType

Different businessType codes denote different P&L line items — sign convention varies. Aggregate over businessType for full P&L. *(Source: domain knowledge.)*

## 03 controlArea_Domain

Uses `controlArea_Domain` for the area param (renamed by H8 transformer). *(Source: `silver/entsoe/h8_balancing.py L200`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code, business_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h8_balancing.py L210`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/06-balancing-financial-expenses-income-http-401.md`.)*

# Related datasets

- **`activated_balancing_prices`** — A84/A16 activation €/MWh. `PT60M`. Per-MWh activation cost; sum over MWh gives the total €. `entsoe · balancing · hourly`
- **`activated_balancing_qty`** — A83/A16 activation MWh. `PT60M`. Pair to derive implied €/MWh. `entsoe · balancing · hourly`
- **`procured_balancing_capacity`** — A15/A51 procurement. `PT60M`. The reservation cost (€/MW/h) layer; total cost = reservation + activation. `entsoe · balancing · hourly`
- **`congestion_income`** — A25/B10 congestion-rent income. `PT60M`. A separate income stream (capacity allocation rents) that supports the balancing P&L. `entsoe · capacity · hourly`
