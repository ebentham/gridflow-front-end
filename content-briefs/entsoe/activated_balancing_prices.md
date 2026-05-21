---
slug: activated_balancing_prices
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A84/A16
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/activated_balancing_prices.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActivatedBalancingPrices (lines 409-431)
  - gridflow/src/gridflow/silver/entsoe/activated_balancing_prices.py::ActivatedBalancingPricesTransformer (lines 18-106)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["activated_balancing_prices"] (lines 302-308)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Activated balancing energy prices, <span class="italic fg-accent">A84.</span>

**Lede:** Activated balancing energy prices in EUR/MWh per control area, reserve_type and direction — the clearing price for each frequency-restoration reserve activation interval.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A84/A16](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.activated_balancing_prices` |
| API PATH | `/api?documentType=A84&processType=A16` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by area |
| PRIMARY KEY | `(timestamp_utc, area_code, reserve_type, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A84 | DocumentType |
| 2 | A16 | processType (realised) |
| 3 | 4 | reserve_type codes (fcr / afrr / mfrr / rr) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- activated_balancing_qty
- contracted_reserves
- procured_balancing_capacity
- balancing_energy_bids
- imbalance_prices

# Sample chart

- **Type:** `priceLadder`
- **Title:** "aFRR up/down prices · 24h"
- **Subtitle:** "Price ladder · EUR/MWh · UTC · 6 May 2026"
- **Seed:** 83
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActivatedBalancingPrices` (lines 409-431). Maps `businessType` (A95/A96/A97/A98) to `reserve_type` ("fcr"/"afrr"/"mfrr"/"rr") and `flowDirection` (A01/A02) to `direction` ("up"/"down").

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L417, L426-431` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC. | `schemas/entsoe.py L418`; `silver/entsoe/activated_balancing_prices.py L65` |
| `reserve_type` | `str` | No | derived from `<businessType>` | "fcr" (A95) / "afrr" (A96) / "mfrr" (A97) / "rr" (A98). | `schemas/entsoe.py L419`; `silver/entsoe/activated_balancing_prices.py L68-70` |
| `direction` | `str` | No | derived from `<flowDirection>` | "up" (A01) / "down" (A02). | `schemas/entsoe.py L420`; `silver/entsoe/activated_balancing_prices.py L71-73` |
| `price_eur_mwh` | `float` | No | `<Point><price.amount>` | EUR/MWh. | `schemas/entsoe.py L421` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L422` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L423` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L424` |

**PARQUET PATH:** `data/silver/entsoe/activated_balancing_prices/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, reserve_type, direction)` (`silver/entsoe/activated_balancing_prices.py L83`)

# Sample data

| timestamp_utc | area_code | reserve_type | direction | price_eur_mwh | resolution | data_provider |
|---|---|---|---|---|---|---|
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | afrr | up | 285.40 | PT60M | entsoe |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | afrr | down | -42.10 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **mfrr** | **up** | **412.80** | **PT60M** | **entsoe** |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | mfrr | down | -18.50 | PT60M | entsoe |
| 2026-05-06T17:00:00+00:00 | 10YGB----------A | rr | up | 220.00 | PT60M | entsoe |

**Sources:** Synthesised against typical GB evening-peak balancing prices. The highlighted **mFRR up (412.80 EUR/MWh)** row illustrates the deeper reserve cost — mFRR (manual frequency-restoration reserve) is slower than aFRR (automatic) and priced higher. Down prices are typically negative (TSO pays to receive surplus generation back).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A84&processType=A16&businessType=A96&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/activated_balancing_prices/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.activated_balancing_prices.ActivatedBalancingPricesTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A84&processType=A16&businessType=A96&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Up-direction reserve prices by reserve_type per zone (last 30 days)
SELECT reserve_type, area_code, count(*) AS hours,
       avg(price_eur_mwh) AS mean_up_price,
       max(price_eur_mwh) AS peak_up_price
FROM read_parquet('data/silver/entsoe/activated_balancing_prices/**/*.parquet')
WHERE direction = 'up'
  AND timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2 ORDER BY peak_up_price DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ap = pl.read_parquet("data/silver/entsoe/activated_balancing_prices/**/*.parquet")
# Up/down spread per reserve_type — width of the balancing-price ladder
print(ap.pivot(
    index=["timestamp_utc", "area_code", "reserve_type"],
    on="direction", values="price_eur_mwh"
).with_columns((pl.col("up") - pl.col("down")).alias("spread")).tail())
```

# Caveats

## 01 reserve_type code mapping

`businessType` A95/A96/A97/A98 → `reserve_type` "fcr"/"afrr"/"mfrr"/"rr" via `replace_strict`. Unknown businessType values fail the transformer. *(Source: `silver/entsoe/activated_balancing_prices.py L68-70`.)*

## 02 connector pins businessType=A96 (aFRR)

`endpoints.py` extra_params pins `businessType=A96` — only aFRR prices fetched by default. Override via `**params` to fetch other reserve types. *(Source: `endpoints.py L307`.)*

## 03 Down prices can be negative

Down activation means the TSO pays to receive surplus generation back. Negative prices are normal — don't filter them out. *(Source: domain knowledge.)*

## 04 controlArea_Domain (not bidding zone)

Control area and bidding zone EICs coincide for GB and the gridflow default zones, but may differ in some continental TSOs. *(Source: `endpoints.py L302-308`.)*

## 05 Not entitlement-blocked

A84/A16 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `activated_balancing_prices-http-401.md`.)*

# Related datasets

- **`activated_balancing_qty`** — A83/A16 quantity counterpart. `PT60M`. Pair on `(timestamp_utc, area_code, reserve_type, direction)` for €/MWh × MWh = activation revenue. `entsoe · balancing · hourly`
- **`contracted_reserves`** — A81 contracted reserves. `PT60M`. Pre-arranged reserves; activation is the realisation of these contracts. `entsoe · balancing · hourly`
- **`procured_balancing_capacity`** — A15/A51 procured capacity. `PT60M`. The capacity-side counterpart (€/MW/h reservation cost vs €/MWh activation here). `entsoe · balancing · hourly`
- **`imbalance_prices`** — A85 imbalance settlement prices. `PT30M`. Imbalance prices reflect the average activation price; pair to derive volume-weighted reserve cost. `entsoe · prices · 30 min`
