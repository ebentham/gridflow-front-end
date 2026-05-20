---
slug: mid
vendor: elexon
vendor_label: Elexon BMRS
api_code: MID
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/mid.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonMID (lines 149-166)
  - gridflow/src/gridflow/silver/elexon/mid.py::MIDTransformer (lines 19-113)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 83-89, PUBLISH_DATETIME style with from/to params)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MID (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Silver schema 'data_provider_id' source field"
    source_a_says: "Source field is `dataProviderId`"
    source_b: "gridflow silver/elexon/mid.py L58"
    source_b_says: "Column mapping is `dataProviderId → data_provider_id`, but the live API on 2026-05-08 returned `dataProvider` not `dataProviderId`"
    orchestrator_recommendation: "trust gridflow as currently coded — but the column mapping does not match the live API field name; data_provider_id will be null in bronze captured from the current API. Phase-7 mini-recon candidate."
  - source_a: "vault Silver schema 'market_index_price' source field"
    source_a_says: "Source field is `midPrice`"
    source_b: "gridflow silver/elexon/mid.py L59 + live API 2026-05-08"
    source_b_says: "Mapping is `midPrice → market_index_price`, but live API returns `price` not `midPrice`"
    orchestrator_recommendation: "documented vendor API rename; transformer column mapping needs updating to also handle `price` field. Currently `market_index_price` is silent-null in fresh bronze."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Wholesale price anchor, <span class="italic fg-accent">market-index data.</span>

**Lede:** Per-period GB market index prices and volumes — the canonical wholesale anchor for imbalance-premium analysis, cash-out reconciliation, and APX/N2EX liquidity comparison.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · MID](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MID)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.mid` |
| API PATH | `/datasets/MID` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~10 min |
| VOLUME | 22k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, data_provider_id)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Publication frequency |
| 2 | ~10 min | Publication lag |
| 3 | 2 | Market index providers |
| 4 | 8 | Schema columns |

# Sidebar siblings

- system_prices
- netbsad
- disbsad
- boal
- pn

# Overview

1. <code>mid</code> is the per-period GB market index prices and volumes — published hourly by data providers (APX, N2EX). It is the canonical wholesale anchor for imbalance-premium analysis, cash-out reconciliation, and APX/N2EX liquidity comparison.

2. Gridflow fetches it from <code>/datasets/MID</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze, is validated against <code>ElexonMID</code>, and written to silver via <code>MIDTransformer</code> — vendor field renames mean <code>data_provider_id</code> and <code>market_index_price</code> currently null in fresh bronze; remap pending.

3. Refreshed hourly with ~10 minute lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "APX market index price · 7-day snapshot"
- **Subtitle:** "Sparkline · £/MWh · UTC · week of 6 May 2026"
- **Shape:** `diurnal-price`
- **Params:** `{"base": 80, "morning_peak": 95, "evening_peak": 125, "trough": 50, "noise": 0.05, "seed": 12}`
- **Toggles:** `24h` / `7d` (active) / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonMID` (lines 149-166) and `gridflow/silver/elexon/mid.py` · `MIDTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L152` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `schemas/elexon.py L153` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/mid.py L82-91` |
| `data_provider_id` | `Optional[str]` | Yes | `dataProviderId` (transformer mapping) / `dataProvider` (live API) | MIDP code: `APXMIDP` (EPEX) or `N2EXMIDP` (Nord Pool). See discrepancy in frontmatter. | `schemas/elexon.py L155`; `silver/elexon/mid.py L58` |
| `market_index_price` | `Optional[float]` | Yes | `midPrice` (transformer mapping) / `price` (live API) | **£/MWh** at the reported half-hour. See discrepancy. | `schemas/elexon.py L156`; `silver/elexon/mid.py L59` |
| `market_index_volume` | `Optional[float]` | Yes | `volume` | MWh traded at the reported half-hour. Mapping name matches live API. | `schemas/elexon.py L157`; `silver/elexon/mid.py L60` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"` (note: distinct from `data_provider_id` which is the MIDP). | `schemas/elexon.py L158` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L159` |

**PARQUET PATH:** `data/silver/elexon/mid/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, data_provider_id)` (`silver/elexon/mid.py L93-95`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | data_provider_id | market_index_price | market_index_volume | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | APXMIDP | 105.43 | 1892.45 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | N2EXMIDP | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | APXMIDP | 148.20 | 3210.00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | N2EXMIDP | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **APXMIDP** | **211.04** | **4180.00** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | N2EXMIDP | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | APXMIDP | 102.50 | 2410.00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | APXMIDP | 81.10 | 1820.00 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (APXMIDP, `price=105.43`, `volume=1892.45`) and 2 (N2EXMIDP, `price=0.0`, `volume=0.0`) verbatim from the vault Bronze Sample (vault/elexon/mid.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (Optional float £/MWh, Optional float MWh, MIDP codes) and follow the typical daily APX price arc with N2EX consistently quiet (the two providers serve different liquidity pools). The highlighted **SP36 APXMIDP (£211.04)** row is the interesting case: evening-peak market price corresponds with the IMBALNGC SP36 (-188 MWh) and system_prices SP36 (~£211) — the three datasets reconcile during stress periods.

# Dataset-specific section: MIDP providers

Two accredited Market Index Data Providers report into MID for GB:

- **APXMIDP** — Index derived from EPEX SPOT GB short-term auctions. Primary liquidity source for GB intraday/spot trading; most non-zero MID rows come from here.
- **N2EXMIDP** — Index derived from Nord Pool GB. Historically the second leg of the GB MIDP set; volume is typically very low post-2024 as N2EX wound down its GB operations. Most live rows have `price=0.0, volume=0.0`.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/MID`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/mid/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.mid.MIDTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/MID?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- APX vs Nord Pool daily volume share over the last 30 days
SELECT settlement_date, data_provider_id,
       SUM(market_index_volume) AS total_volume_mwh,
       AVG(market_index_price)  AS avg_price_gbp_mwh
FROM read_parquet('data/silver/elexon/mid/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
  AND market_index_volume > 0
GROUP BY 1, 2
ORDER BY 1, total_volume_mwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

mid = pl.read_parquet("data/silver/elexon/mid/**/*.parquet").filter(
    pl.col("data_provider_id") == "APXMIDP"
)
sp = pl.read_parquet("data/silver/elexon/system_prices/**/*.parquet")
# Spread: imbalance SBP minus wholesale APX MID
spread = (
    mid.join(sp, on=["settlement_date", "settlement_period"], how="inner")
       .with_columns(
           (pl.col("system_buy_price") - pl.col("market_index_price"))
             .alias("imbalance_premium_gbp_mwh")
       )
       .select(["settlement_date", "settlement_period", "imbalance_premium_gbp_mwh"])
)
print(spread.tail(10))
```

# Caveats

## 01 Column-mapping drift vs live API

Transformer maps `dataProviderId`/`midPrice` but live API now returns `dataProvider`/`price`. Fresh bronze yields null `data_provider_id` and `market_index_price`. *(Source: `silver/elexon/mid.py L55-61`.)*

## 02 Two MIDP providers per period — preserve in dedup

Dedup includes `data_provider_id` so both `APXMIDP` and `N2EXMIDP` survive. Don't dedup on `(date, period)` alone. *(Source: `silver/elexon/mid.py L93-95`.)*

## 03 `from`/`to` query params, not `publishDateTimeFrom`/`To`

Connector overrides via `from_param="from"`. Wrong names return the default ~24h window. *(Source: `connectors/elexon/endpoints.py L86-87`.)*

## 04 N2EXMIDP typically zero post-2024

Nord Pool wound down GB MIDP; most `N2EXMIDP` rows carry `price=0.0`. Filter `market_index_volume > 0` for liquidity-weighted views. *(Source: GB MIDP landscape.)*

## 05 MID is half-hourly indexed despite "hourly" cadence

Manifest `freq: hourly` refers to publication, not row spacing — rows are per settlement period. *(Source: manifest vs schema.)*

# Related datasets

- **system_prices** — System buy / sell prices. `30 min`. The imbalance cash-out; pair with MID to compute the imbalance premium (SBP − MID) per period. `elexon · prices & balancing · 30 min`
- **netbsad** — Net balancing services adjustment data. `daily`. Aggregate BSAD figure; MID's wholesale anchor + NETBSAD's balancing cost together explain total system cost. `elexon · prices & balancing · daily`
- **boal** — Bid-offer acceptance (BOALF). `hourly`. BMU dispatch instructions; the MID price is the reference against which BOAL acceptance prices are calibrated. `elexon · prices & balancing · hourly`
- **pn** — Physical notifications. `hourly`. Pre-gate-closure intentions; MID is the wholesale price at gate closure, PN tells you what BMUs were planning to deliver against that price. `elexon · prices & balancing · hourly`
