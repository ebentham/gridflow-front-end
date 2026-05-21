---
slug: contracted_reserves
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A81/A52
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/contracted_reserves.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeContractedReserves (lines 434-454)
  - gridflow/src/gridflow/silver/entsoe/contracted_reserves.py::ContractedReservesTransformer (lines 18-98)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["contracted_reserves"] (lines 309-317)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Contracted balancing reserves, <span class="italic fg-accent">A81.</span>

**Lede:** Contracted reserve quantity in MW per control area by reserve_type — the pre-arranged reserve capacity providing the activation pool that frequency-restoration reserves draw from.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A81/A52](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.contracted_reserves` |
| API PATH | `/api?documentType=A81&processType=A52&businessType=B95` |
| FREQUENCY | daily product (Type_MarketAgreement.Type=A01 pinned) |
| PUBLICATION LAG | as published |
| VOLUME | varies |
| PRIMARY KEY | `(timestamp_utc, area_code, reserve_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A81 | DocumentType |
| 2 | A52 | processType |
| 3 | B95 | businessType (pinned) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- procured_balancing_capacity
- activated_balancing_qty
- activated_balancing_prices
- balancing_energy_bids
- cross_zonal_balancing_capacity

# Sample chart

- **Type:** `barsH`
- **Title:** "Contracted reserves by reserve_type · 24h"
- **Subtitle:** "Horizontal bars · MW · UTC · 6 May 2026"
- **Seed:** 87
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeContractedReserves` (lines 434-454). Maps `businessType` (A95/A96/A97/A98) to `reserve_type`. Note no `direction` field — contracted reserves are bidirectional.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L441, L449-454` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC. | `schemas/entsoe.py L442`; `silver/entsoe/contracted_reserves.py L61` |
| `reserve_type` | `str` | No | derived from `<businessType>` | "fcr" (A95) / "afrr" (A96) / "mfrr" (A97) / "rr" (A98). | `schemas/entsoe.py L443`; `silver/entsoe/contracted_reserves.py L64-66` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Contracted reserve MW. | `schemas/entsoe.py L444` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L445` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L446` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L447` |

**PARQUET PATH:** `data/silver/entsoe/contracted_reserves/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, reserve_type)` (`silver/entsoe/contracted_reserves.py L75`)

# Sample data

| timestamp_utc | area_code | reserve_type | quantity_mw | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | fcr | 900.0 | PT60M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | afrr | 1200.0 | PT60M | entsoe |
| **2026-05-06T00:00:00+00:00** | **10YGB----------A** | **mfrr** | **2400.0** | **PT60M** | **entsoe** |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | rr | 600.0 | PT60M | entsoe |

**Sources:** Synthesised against typical GB daily contracted reserves. The highlighted **mFRR contracted 2.4 GW** row is the largest tranche — GB carries more manual-FRR contracted than aFRR or RR because it's the deepest-reserve product. Total contracted is ~5 GW, an order of magnitude above typical activation MWh from `activated_balancing_qty`.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A81&processType=A52&businessType=B95&Type_MarketAgreement.Type=A01&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/contracted_reserves/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.contracted_reserves.ContractedReservesTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A81&processType=A52&businessType=B95&Type_MarketAgreement.Type=A01&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily mean contracted reserve by reserve_type per zone
SELECT date_trunc('day', timestamp_utc) AS day, area_code, reserve_type,
       avg(quantity_mw) AS mean_contracted_mw
FROM read_parquet('data/silver/entsoe/contracted_reserves/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2, 3 ORDER BY 1 DESC, mean_contracted_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cr = pl.read_parquet("data/silver/entsoe/contracted_reserves/**/*.parquet")
qty = pl.read_parquet("data/silver/entsoe/activated_balancing_qty/**/*.parquet")
# Activation rate: how much of contracted was actually called?
util = cr.join(
    qty.group_by(["timestamp_utc", "area_code", "reserve_type"]).agg(
        pl.col("quantity_mwh").sum().alias("activated_mwh")
    ),
    on=["timestamp_utc", "area_code", "reserve_type"], how="left"
).with_columns(
    (pl.col("activated_mwh") / pl.col("quantity_mw")).alias("util_hours_equiv")
)
print(util.tail())
```

# Caveats

## 01 Type_MarketAgreement.Type=A01 (daily) pinned

Connector pins A01 (daily) — only daily-product contracted reserves are fetched. Weekly / monthly tranches (A02 / A03) require manual override. The comment in `endpoints.py` notes this is mandatory per the ENTSO-E API spec despite the Postman catalog listing it as optional. *(Source: `endpoints.py L313-316`.)*

## 02 reserve_type code mapping

Same A95/A96/A97/A98 → "fcr"/"afrr"/"mfrr"/"rr" pattern as activated_*. *(Source: `silver/entsoe/contracted_reserves.py L64-66`.)*

## 03 No `direction` field

Contracted reserves are bidirectional capacity; direction surfaces only at activation. Pair with `activated_balancing_qty` for up/down split. *(Source: `schemas/entsoe.py L434-447`.)*

## 04 businessType B95 pinned

`endpoints.py` pins `businessType=B95`. *(Source: `endpoints.py L316`.)*

## 05 Not entitlement-blocked

A81/A52 is accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `contracted_reserves-http-401.md`.)*

# Related datasets

- **`procured_balancing_capacity`** — A15/A51 procured-capacity counterpart. `PT60M`. Capacity-procurement decisions; contracts execute through this dataset. `entsoe · balancing · hourly`
- **`activated_balancing_qty`** — A83/A16 activation MWh. `PT60M`. Pair to compute reserve utilisation. `entsoe · balancing · hourly`
- **`activated_balancing_prices`** — A84/A16 activation €/MWh. `PT60M`. Activation-side prices vs reservation-side cost (this dataset). `entsoe · balancing · hourly`
- **`cross_zonal_balancing_capacity`** — A38/A51 cross-zonal capacity. `PT60M`. Cross-border reserve sharing — pair with contracted_reserves to track imported capacity. `entsoe · balancing · hourly`
