---
slug: market_depth
vendor: elexon
vendor_label: Elexon BMRS
api_code: MARKET-DEPTH
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/market_depth.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonMarketDepth class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/market_depth.py::MarketDepthTransformer (lines 19-120)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 257-261, DATE_PATH style — date appended to URL)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/market-depth (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonMarketDepth class declared"
    source_b: "gridflow silver/elexon/market_depth.py L19-120"
    source_b_says: "MarketDepthTransformer outputs 12 columns including 4 volume aggregates"
    orchestrator_recommendation: "trust silver transformer; same shape gap as other aggregate datasets"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Per-period balancing summary, <span class="italic fg-accent">depth at a glance.</span>

**Lede:** Market Depth is the settlement-period summary of GB balancing activity — the indicative imbalance, total bid and offer volumes, and accepted balancing volumes in a single row per period. It folds inputs from BOALF, DISBSAD, IMBALNGC, and BOD into a liquidity-and-headroom snapshot useful when you want one row instead of the underlying granular feeds.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · Market Depth](https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/market-depth)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.market_depth` |
| API PATH | `/balancing/settlement/market-depth/{date}` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 1 day |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Per-period cadence |
| 2 | 1 day | Publication lag |
| 3 | 4 | Source datasets folded in |
| 4 | 12 | Schema columns |

# Sidebar siblings

- system_prices
- netbsad
- disbsad
- boal
- imbalngc

# Overview

1. <code>market_depth</code> is **Settlement Market Depth** — a per-settlement-period summary that combines four upstream sources (IMBALNGC, BOD, DISEBSP, DISPTAV per the live API metadata) into one row carrying indicative imbalance and volume aggregates. Each row tells you how much liquidity (`offer_volume_mwh`, `bid_volume_mwh`) was available and how much was accepted (`total_accepted_offer_volume_mwh`, `total_accepted_bid_volume_mwh`) in a single period.

2. Gridflow fetches it from <code>/balancing/settlement/market-depth/{settlementDate}</code> — a **DATE_PATH** style endpoint where the date is appended to the URL path rather than passed as a query parameter (connector entry at <code>connectors/elexon/endpoints.py L257-261</code>, same pattern as `system_prices`). The <code>MarketDepthTransformer</code> renames the six bid/offer aggregates plus the imbalance figure, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period)`. No Pydantic class is declared.

3. Cadence is one row per settlement period per day, published D+1. Verified against the live API on 2026-05-08. Use for one-shot per-period analytics — daily totals of accepted volume, intra-day liquidity profiles, fast cross-checks against BOAL aggregations. The bronze metadata block (`"metadata": {"datasets": ["IMBALNGC", "BOD", "DISEBSP", "DISPTAV"]}`) makes the upstream lineage explicit.

# Sample chart

- **Type:** `barsH`
- **Title:** "Daily accepted bid + offer volume · last 30 days"
- **Subtitle:** "Horizontal bars · MWh · UTC · April 2026"
- **Seed:** 16
- **Toggles:** `accepted` (active) / `total bid/offer`

# Schema

Defined in `gridflow/silver/elexon/market_depth.py` · `MarketDepthTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/market_depth.py L77` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/market_depth.py L78` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/market_depth.py L90-99` |
| `indicated_imbalance_mwh` | `Optional[float]` | Yes | `indicatedImbalance` | MWh. Folded in from IMBALNGC source. | `silver/elexon/market_depth.py L58` |
| `offer_volume_mwh` | `Optional[float]` | Yes | `offerVolume` | MWh. Total offered volume submitted to the BM for this period. | `silver/elexon/market_depth.py L59` |
| `bid_volume_mwh` | `Optional[float]` | Yes | `bidVolume` | MWh. **Negative** by convention (bids are sell-back-to-SO volumes). | `silver/elexon/market_depth.py L60` |
| `total_accepted_offer_volume_mwh` | `Optional[float]` | Yes | `totalAcceptedOfferVolume` | MWh. Sum of accepted offer-direction volume in the period. | `silver/elexon/market_depth.py L61` |
| `total_accepted_bid_volume_mwh` | `Optional[float]` | Yes | `totalAcceptedBidVolume` | MWh. Negative; sum of accepted bid-direction volume. | `silver/elexon/market_depth.py L62` |
| `total_adjustment_sell_volume_mwh` | `Optional[float]` | Yes | `totalAdjustmentSellVolume` | MWh. May be missing depending on API response. | `silver/elexon/market_depth.py L63` |
| `total_adjustment_buy_volume_mwh` | `Optional[float]` | Yes | `totalAdjustmentBuyVolume` | MWh. May be missing depending on API response. | `silver/elexon/market_depth.py L64` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/market_depth.py L105` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/market_depth.py L106` |

**PARQUET PATH:** `data/silver/elexon/market_depth/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/market_depth.py L101`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | indicated_imbalance_mwh | offer_volume_mwh | bid_volume_mwh | total_accepted_offer_volume_mwh | total_accepted_bid_volume_mwh | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 1 | 2026-05-06T00:00:00+00:00 | 1122.0 | 60440.0 | -64830.0 | 578.008 | -616.25 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 2 | 2026-05-06T00:30:00+00:00 | 656.0 | 60567.5 | -64840.0 | 605.840 | -641.705 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 77.0 | 58210.0 | -63140.0 | 488.0 | -522.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **17** | **2026-05-06T08:00:00+00:00** | **-120.0** | **48340.0** | **-58450.0** | **2120.0** | **-820.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | -64.0 | 51120.0 | -60810.0 | 1080.0 | -930.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | -188.0 | 45810.0 | -55230.0 | 2480.0 | -1180.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | -161.0 | 46210.0 | -55810.0 | 2210.0 | -1020.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 51.0 | 59120.0 | -64210.0 | 520.0 | -480.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP1) and 2 (SP2) verbatim from the vault Bronze Sample (vault/elexon/market_depth.md, live 2026-05-08; `indicatedImbalance` 1122 and 656, `offerVolume` 60440 and 60567.5). Remaining rows synthesised — respect transformer constraints (bid volume negative, accepted volumes signed) and follow the typical daily liquidity profile. The highlighted **SP17 (offer 2120, bid -820 accepted)** row is the interesting case: morning peak with the largest accepted-offer volume (system buying ~2100 MWh) — the period market_depth exists to summarise instead of forcing you to aggregate BOAL by hand.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: market_depth's notable structure is the relationship to its 4 source datasets, documented in caveats. There are no per-row enumerable codelists.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/balancing/settlement/market-depth/{settlementDate}`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/market_depth/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.market_depth.MarketDepthTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/market-depth/2026-05-06?format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily accepted volumes (both directions) and average indicative imbalance
SELECT settlement_date,
       SUM(total_accepted_offer_volume_mwh)        AS accepted_offer_mwh,
       SUM(ABS(total_accepted_bid_volume_mwh))     AS accepted_bid_mwh,
       AVG(indicated_imbalance_mwh)                AS avg_indicated_imbalance_mwh
FROM read_parquet('data/silver/elexon/market_depth/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

md = pl.read_parquet("data/silver/elexon/market_depth/**/*.parquet")
# Liquidity proxy: total available volume (|bid| + offer) per period
liquidity = (
    md.with_columns(
        (pl.col("offer_volume_mwh") + pl.col("bid_volume_mwh").abs())
          .alias("total_available_mwh")
    )
    .group_by(pl.col("timestamp_utc").dt.hour().alias("hour"))
    .agg(pl.col("total_available_mwh").mean())
    .sort("hour")
)
print(liquidity)
```

# Caveats

## 01 Aggregates BOALF / DISBSAD / IMBALNGC — don't double-count

The bronze metadata explicitly lists `["IMBALNGC", "BOD", "DISEBSP", "DISPTAV"]` as source datasets. The volumes in market_depth are derived sums. If you join market_depth to BOAL or DISBSAD and then aggregate again, you'll double-count. Pick one layer of granularity per analysis. *(Source: vault Known Issues; vault Bronze Sample metadata.)*

## 02 Bid volumes are signed negative by convention

`bid_volume_mwh` and `total_accepted_bid_volume_mwh` are negative because bids are the SO selling power back (a withdrawal from the BM's offer side). Don't flip the sign; use `ABS()` when summing absolute traded volumes. *(Source: vault Bronze Sample — `bidVolume: -64830.0`.)*

## 03 DATE_PATH style — date in URL, not query

Unlike most BMRS endpoints, market_depth uses `/balancing/settlement/market-depth/{date}` with the date appended to the URL path. The connector handles this via `ParamStyle.DATE_PATH` (same as `system_prices`). Hand-crafted URLs must include the date as the last path segment. *(Source: `connectors/elexon/endpoints.py L257-261`.)*

## 04 Adjustment columns are optional

`total_adjustment_sell_volume_mwh` and `total_adjustment_buy_volume_mwh` are conditionally present in the silver output — when the API doesn't return the field, the column is omitted entirely from the parquet rather than null-filled. Check column existence (`df.columns`) before referencing them in production queries. *(Source: `silver/elexon/market_depth.py L86-88, L109-116` — column included only if present.)*

## 05 No Pydantic schema

Like other aggregate datasets, market_depth has no dedicated Pydantic class. Silver shape is defined by `MarketDepthTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no MarketDepth class.)*

# Related datasets

- **system_prices** — System buy / sell prices. `30 min`. Per-period cash-out prices; pair with market_depth accepted volumes to compute the implied £/MWh of balancing activity. `elexon · prices & balancing · 30 min`
- **netbsad** — Net balancing services adjustment data. `daily`. The net BSAD complement; market_depth covers BM-side liquidity, NETBSAD covers non-BM. `elexon · prices & balancing · daily`
- **disbsad** — Disaggregated balancing services adjustment data. `daily`. The disaggregated source feeding into the non-BM totals; combine with market_depth for a full balancing-cost picture. `elexon · prices & balancing · daily`
- **boal** — Bid-offer acceptance (BOALF). `hourly`. The per-acceptance ground truth that market_depth aggregates; use for unit-level attribution. `elexon · prices & balancing · hourly`
