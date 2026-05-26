---
slug: day_ahead_prices
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A44
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/day_ahead_prices.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeDayAheadPrice (lines 12-26)
  - gridflow/src/gridflow/silver/entsoe/day_ahead_prices.py::DayAheadPricesTransformer (lines 18-80)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["day_ahead_prices"] (line 30)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** EU day-ahead clearing prices, <span class="italic fg-accent">A44.</span>

**Lede:** Day-ahead market clearing prices in EUR/MWh per bidding zone — the canonical EU spot reference for cross-border spread modelling and baseline against which GB Elexon prices are compared.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A44](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.day_ahead_prices` |
| API PATH | `/api?documentType=A44` |
| FREQUENCY | PT60M (PT15M in some zones) |
| PUBLICATION LAG | D-1 ~12:55 CET |
| VOLUME | 24-96 points / zone / day |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A44 | DocumentType |
| 2 | D-1 12:55 CET | Publication |
| 3 | zone-pair | `domain_style` (in_Domain == out_Domain for intra-zone) |
| 4 | 6 | Schema columns |

# Sidebar siblings

- imbalance_prices
- imbalance_volume
- net_positions
- offered_transfer_capacity_implicit
- actual_load

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU day-ahead clearing prices · 24h"
- **Subtitle:** "Line · EUR/MWh · UTC · 6 May 2026"
- **Seed:** 99
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeDayAheadPrice` (lines 12-26). Partitioned by `timestamp_utc` (year + month). Day-ahead prices are not revised — `data_provider` and `ingested_at` are tracking-only.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + (position-1) × resolution | tz-aware UTC; validator rejects naive datetimes. | `schemas/entsoe.py L15, L21-26` |
| `area_code` | `str` | No | `<TimeSeries>/<in_Domain.mRID>` | EIC bidding zone mRID — `in_Domain == out_Domain` for intra-zone price. | `schemas/entsoe.py L16` |
| `price_eur_mwh` | `float` | No | `<Point><price.amount>` | EUR/MWh (currency_Unit + price_Measure_Unit). | `schemas/entsoe.py L17` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration: `PT60M` / `PT15M`. | `schemas/entsoe.py L18` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L19` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/day_ahead_prices.py L69` |

**PARQUET PATH:** `data/silver/entsoe/day_ahead_prices/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/day_ahead_prices.py L64`)

# Sample data

| timestamp_utc | area_code | price_eur_mwh | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 85.50 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T01:00:00+00:00 | 10Y1001A1001A82H | 82.30 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T11:00:00+00:00** | **10Y1001A1001A82H** | **-12.40** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10Y1001A1001A82H | 184.60 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YFR-RTE------C | 22.80 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T19:00:00+00:00 | 10YFR-RTE------C | 168.40 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Rows 1-2 verbatim from vault Silver Sample (DE-LU 2026-05-06). The highlighted **DE-LU 11:00 (-12.40 EUR/MWh)** row illustrates the canonical solar-driven negative-price hour — DE-LU surplus solar pushes price below zero, while FR (no excess solar) remains at +22.80 EUR/MWh. This 35 EUR/MWh spread is what `cross_border_flows` clears against.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A44&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/day_ahead_prices/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.day_ahead_prices.DayAheadPricesTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A44&in_Domain=10Y1001A1001A82H&out_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Cross-zone hourly spread (DE-LU vs FR) last 30 days
SELECT a.timestamp_utc,
       a.price_eur_mwh AS de_lu_price,
       b.price_eur_mwh AS fr_price,
       a.price_eur_mwh - b.price_eur_mwh AS spread
FROM read_parquet('data/silver/entsoe/day_ahead_prices/**/*.parquet') a
JOIN read_parquet('data/silver/entsoe/day_ahead_prices/**/*.parquet') b
  ON a.timestamp_utc = b.timestamp_utc
WHERE a.area_code = '10Y1001A1001A82H'
  AND b.area_code = '10YFR-RTE------C'
  AND a.timestamp_utc >= current_timestamp - INTERVAL 30 DAY
ORDER BY abs(spread) DESC LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

prices = pl.read_parquet("data/silver/entsoe/day_ahead_prices/**/*.parquet")
# Negative-price hours per zone (renewable surplus indicator)
neg = prices.filter(pl.col("price_eur_mwh") < 0).group_by(
    pl.col("timestamp_utc").dt.year().alias("year"), "area_code"
).agg(pl.len().alias("neg_hours"))
print(neg.sort("neg_hours", descending=True).head())
```

# Caveats

## 01 GB returns Acknowledgement code 999 post-Brexit

GB day-ahead prices not published via ENTSO-E. Use Elexon `system_prices` for GB market reference. `DEFAULT_ZONES` still includes GB; silver simply produces zero rows. *(Source: vault Known Issues.)*

## 02 in_Domain == out_Domain for intra-zone

A44 uses zone-pair domains, but for intra-zone prices both are set to the same EIC. Connector sends both. *(Source: vault Known Issues.)*

## 03 PT15M zones (15-min markets)

DE-LU and a growing list publish `PT15M`. Filter on `resolution` before joining settlement-period datasets — or aggregate PT15M → PT60M. *(Source: vault Known Issues.)*

## 04 ZIP-of-XML for large windows

Multi-day requests may return a ZIP archive of day-partitioned XML files. Connector auto-detects (PK magic bytes) and unpacks. *(Source: vault Known Issues.)*

## 05 Not entitlement-blocked

A44 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. No revisions — day-ahead prices are not republished post-clearing. *(Source: `.planning/reconciliation/entsoe/` — no `day_ahead_prices-http-401.md`; vault Known Issues "No revisions".)*

# Related datasets

- **`imbalance_prices`** — A85 imbalance settlement prices. `PT30M`. Pair to compute imbalance-vs-day-ahead premium. `entsoe · prices · 30 min`
- **`net_positions`** — A25/B09 implicit-auction net positions. `PT60M`. Prices and net positions clear simultaneously. `entsoe · capacity · hourly`
- **`offered_transfer_capacity_implicit`** — Implicit OTC. `PT60M`. The capacity constraint that the implicit auction clears against. `entsoe · transmission · hourly`
- **`system_prices` (Elexon)** — GB cash-out prices. `30 min`. Substitute for any GB query — A44 is empty for GB. `elexon · prices · 30 min`
