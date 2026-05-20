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

**Lede:** MID is Elexon's Market Index Data feed — accredited exchange prices and volumes used by the BSC to derive the Power Exchange Reference Price. Each row carries a per-MIDP (Market Index Data Provider — APXMIDP for EPEX, N2EXMIDP for Nord Pool) price (£/MWh) and traded volume (MWh) per settlement period. MID is the wholesale-market anchor that ties Balancing Mechanism cash-out to traded GB power prices.

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

1. <code>mid</code> is **Market Index Data** — published reference prices and volumes from accredited Market Index Data Providers (MIDPs). Two providers report into MID for GB: `APXMIDP` (EPEX-derived) and `N2EXMIDP` (Nord Pool-derived). The BSC uses MID values to derive the Power Exchange Reference Price, which in turn feeds the imbalance cash-out logic.

2. Gridflow fetches it from <code>/datasets/MID</code> using <code>from</code>/<code>to</code> query params (NOT `publishDateTimeFrom`/`To`) per the docs (connector entry at <code>connectors/elexon/endpoints.py L83-89</code>, `from_param="from", to_param="to"`). The <code>MIDTransformer</code> renames camelCase to snake_case, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period, data_provider_id)` so both MIDPs survive per period. Pydantic schema <code>ElexonMID</code> is declared.

3. Cadence is hourly with ~10-minute lag at period close. Verified against the live API on 2026-05-08; the sample returned two providers per period (`APXMIDP` with positive price/volume; `N2EXMIDP` with zero values). Worth noting: the live API field names (`dataProvider`, `price`) do not match the transformer's column mapping (`dataProviderId`, `midPrice`) — so `data_provider_id` and `market_index_price` are silent-null in fresh bronze until the mapping is updated.

# Sample chart

- **Type:** `sparkline`
- **Title:** "APX market index price · 7-day snapshot"
- **Subtitle:** "Sparkline · £/MWh · UTC · week of 6 May 2026"
- **Seed:** 12
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

The transformer maps `dataProviderId → data_provider_id` and `midPrice → market_index_price`, but the live API on 2026-05-08 returned `dataProvider` and `price` instead. Fresh bronze runs through the current code produce silver rows where both columns are null. Two fixes: extend the column mapping to also handle `dataProvider` / `price`, or document the gap and accept null until a fix lands. *(Source: discrepancies in frontmatter; cross-reference vault Bronze Sample field names vs `silver/elexon/mid.py L55-61`.)*

## 02 Two MIDP providers per period — preserve in dedup

The dedup key includes `data_provider_id` so both `APXMIDP` and `N2EXMIDP` rows survive per (date, period). Don't dedup on (date, period) alone or you'll lose one provider. For the "BSC reference price" use APXMIDP (primary GB liquidity); for cross-validation use both. *(Source: vault Known Issues — "Multiple data providers per period"; `silver/elexon/mid.py L93-95`.)*

## 03 `from`/`to` query params, not `publishDateTimeFrom`/`To`

Like BOALF and DISBSAD, MID uses `from`/`to` parameters. The connector overrides via `from_param="from", to_param="to"`. Wrong param names get silently ignored and the API returns the last ~24 hours. *(Source: `connectors/elexon/endpoints.py L86-87`.)*

## 04 N2EXMIDP typically zero post-2024

Nord Pool wound down significant GB MIDP operations; expect most N2EXMIDP rows to carry `price=0.0, volume=0.0`. This isn't a data error — it's the actual reported value. Filter on `market_index_volume > 0` for liquidity-weighted analytics. *(Source: domain knowledge — GB MIDP landscape circa 2024-2026.)*

## 05 MID is half-hourly indexed despite "hourly" cadence

The manifest lists `freq: hourly` because publication arrives roughly hourly, but the rows themselves are per settlement period (half-hourly). Don't confuse "row cadence" with "publication cadence" when aligning to other datasets. *(Source: cross-reference manifest `elexon.json` `freq: hourly` vs `settlement_period` schema column.)*

# Related datasets

- **system_prices** — System buy / sell prices. `30 min`. The imbalance cash-out; pair with MID to compute the imbalance premium (SBP − MID) per period. `elexon · prices & balancing · 30 min`
- **netbsad** — Net balancing services adjustment data. `daily`. Aggregate BSAD figure; MID's wholesale anchor + NETBSAD's balancing cost together explain total system cost. `elexon · prices & balancing · daily`
- **boal** — Bid-offer acceptance (BOALF). `hourly`. BMU dispatch instructions; the MID price is the reference against which BOAL acceptance prices are calibrated. `elexon · prices & balancing · hourly`
- **pn** — Physical notifications. `hourly`. Pre-gate-closure intentions; MID is the wholesale price at gate closure, PN tells you what BMUs were planning to deliver against that price. `elexon · prices & balancing · hourly`
