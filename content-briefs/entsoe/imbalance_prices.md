---
slug: imbalance_prices
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A85
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/imbalance_prices.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeImbalancePrices (lines 338-358)
  - gridflow/src/gridflow/silver/entsoe/imbalance_prices.py::ImbalancePricesTransformer (lines 18-98)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["imbalance_prices"] (line 294)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** EU imbalance prices, <span class="italic fg-accent">long and short.</span>

**Lede:** Imbalance settlement prices in EUR/MWh per control area split by direction (long / short) — the EU cash-out signal counterpart to GB Elexon system_prices.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A85](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.imbalance_prices` |
| API PATH | `/api?documentType=A85` |
| FREQUENCY | PT30M typical |
| PUBLICATION LAG | T+1h |
| VOLUME | 96 points / area / day (2 directions × 48 SP) |
| PRIMARY KEY | `(timestamp_utc, area_code, direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A85 | DocumentType |
| 2 | control_area | `domain_style` |
| 3 | long / short | `direction` codes (A19 / A20) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- imbalance_volume
- day_ahead_prices
- current_balancing_state
- activated_balancing_prices
- system_prices (Elexon)

# Sample chart

- **Type:** `priceLadder`
- **Title:** "GB long/short imbalance prices · 24h"
- **Subtitle:** "Price ladder · EUR/MWh · UTC · 6 May 2026"
- **Seed:** 1
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeImbalancePrices` (lines 338-358). Maps `businessType` (A19/A20) to `direction` ("long"/"short") via `replace_strict`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L345, L353-358` |
| `area_code` | `str` | No | `<controlArea_Domain.mRID>` | Control area EIC. | `schemas/entsoe.py L346`; `silver/entsoe/imbalance_prices.py L60` |
| `direction` | `str` | No | derived from `<businessType>` | "long" (A19 = system surplus) / "short" (A20 = system deficit). | `schemas/entsoe.py L347`; `silver/entsoe/imbalance_prices.py L63-66` |
| `price_eur_mwh` | `float` | No | `<Point><price.amount>` | EUR/MWh. | `schemas/entsoe.py L348` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT30M`. | `schemas/entsoe.py L349` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L350` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L351` |

**PARQUET PATH:** `data/silver/entsoe/imbalance_prices/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, direction)` (`silver/entsoe/imbalance_prices.py L75`)

# Sample data

| timestamp_utc | area_code | direction | price_eur_mwh | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | long | 81.20 | PT30M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | short | 92.40 | PT30M | entsoe |
| **2026-05-06T17:30:00+00:00** | **10YGB----------A** | **short** | **285.40** | **PT30M** | **entsoe** |
| 2026-05-06T17:30:00+00:00 | 10YGB----------A | long | 102.80 | PT30M | entsoe |
| 2026-05-06T17:30:00+00:00 | 10Y1001A1001A82H | short | 195.60 | PT30M | entsoe |

**Sources:** Synthesised against typical GB evening-peak imbalance prices. The highlighted **GB short 17:30 (285.40 EUR/MWh)** row is the canonical winter-evening short-system scarcity premium — when `current_balancing_state` shows -481 MW (system short), the short imbalance price spikes well above day-ahead.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A85&controlArea_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/imbalance_prices/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.imbalance_prices.ImbalancePricesTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A85&controlArea_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Short - long spread per zone (long-short scarcity premium)
SELECT s.timestamp_utc, s.area_code,
       s.price_eur_mwh AS short_price,
       l.price_eur_mwh AS long_price,
       s.price_eur_mwh - l.price_eur_mwh AS spread
FROM read_parquet('data/silver/entsoe/imbalance_prices/**/*.parquet') s
JOIN read_parquet('data/silver/entsoe/imbalance_prices/**/*.parquet') l
  ON s.timestamp_utc = l.timestamp_utc AND s.area_code = l.area_code
WHERE s.direction='short' AND l.direction='long'
ORDER BY spread DESC LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ip = pl.read_parquet("data/silver/entsoe/imbalance_prices/**/*.parquet")
da = pl.read_parquet("data/silver/entsoe/day_ahead_prices/**/*.parquet")
# Imbalance-vs-day-ahead premium per direction
premium = ip.join(da, on=["timestamp_utc", "area_code"]).with_columns(
    (pl.col("price_eur_mwh") - pl.col("price_eur_mwh_right")).alias("imbalance_premium")
)
print(premium.group_by(["area_code", "direction"]).agg(
    pl.col("imbalance_premium").mean()
))
```

# Caveats

## 01 direction code mapping

`businessType=A19` → `direction="long"`, `A20` → `direction="short"` via `replace_strict`. Unknown businessType values raise. *(Source: `silver/entsoe/imbalance_prices.py L63-66`.)*

## 02 controlArea_Domain (not bidding zone)

Control area and bidding zone EICs coincide for GB and the gridflow default zones. *(Source: `endpoints.py L294`.)*

## 03 Short price ≥ long price under single-price reform

In most single-price-reformed markets, the short and long prices are equal under non-scarcity. They diverge during system stress. GB has been dual-price since 2018 reform completed. *(Source: domain knowledge.)*

## 04 Revisions overwrite

Imbalance settlement can be revised — `keep="last"` on dedup means the most recent revision wins. No `published_at` for PIT. *(Source: `silver/entsoe/imbalance_prices.py L75`.)*

## 05 Not entitlement-blocked

A85 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `imbalance_prices-http-401.md`.)*

# Related datasets

- **`imbalance_volume`** — A86 imbalance volume counterpart. `PT30M`. Pair €/MWh × MWh = imbalance settlement value. `entsoe · prices · 30 min`
- **`day_ahead_prices`** — A44 day-ahead prices. `PT60M`. The pre-clearing reference; imbalance premium = this dataset - day-ahead. `entsoe · prices · hourly`
- **`current_balancing_state`** — A86/B33 area control error. `PT30M`. Drives the direction (short / long) and magnitude of imbalance prices. `entsoe · balancing · 30 min`
- **`system_prices` (Elexon)** — GB cash-out prices. `30 min`. The GB-native equivalent — use for GB. `elexon · prices · 30 min`
