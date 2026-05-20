---
slug: netbsad
vendor: elexon
vendor_label: Elexon BMRS
api_code: NETBSAD
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/netbsad.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonNETBSAD class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/netbsad.py::NETBSADTransformer (lines 19-114)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 90-96, PUBLISH_DATETIME with from/to params)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NETBSAD (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonNETBSAD class declared"
    source_b: "gridflow silver/elexon/netbsad.py L19-114"
    source_b_says: "NETBSADTransformer outputs 9 columns with 4 net adjustment values"
    orchestrator_recommendation: "trust silver transformer; same shape gap as DISBSAD/MARKET_DEPTH"
  - source_a: "vault Silver schema: 4 columns (net_buy_price_adjustment, net_sell_price_adjustment, net_buy_volume_adjustment, net_sell_volume_adjustment)"
    source_a_says: "Transformer renames `netBuyPriceAdjustment`/`netSellPriceAdjustment`/`netBuyVolumeAdjustment`/`netSellVolumeAdjustment`"
    source_b: "Live API 2026-05-08 returns: `netBuyPriceCostAdjustmentEnergy`, `netBuyPriceVolumeAdjustmentEnergy`, `netBuyPriceVolumeAdjustmentSystem`, `buyPricePriceAdjustment`, `netSellPriceCostAdjustmentEnergy`, `netSellPriceVolumeAdjustmentEnergy`, `netSellPriceVolumeAdjustmentSystem`, `sellPricePriceAdjustment`"
    source_b_says: "8 fields with finer-grained energy/system split, not the 4 the transformer expects"
    orchestrator_recommendation: "Phase-7 mini-recon — the transformer's 4-column mapping is incomplete vs current vendor API; fresh bronze will produce silver with all 4 columns null. Update mapping to cover the 8 actual fields, or document the gap explicitly."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Net BSAD, <span class="italic fg-accent">price + volume.</span>

**Lede:** NETBSAD is the Net Balancing Services Adjustment Data — the netted per-period price and volume adjustments applied to SBP/SSP so cash-out prices reflect the cost of balancing actions beyond direct energy dispatch. Computed at the API level from the disaggregated DISBSAD components and the canonical source for net BSAD attribution.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · NETBSAD](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/NETBSAD)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.netbsad` |
| API PATH | `/datasets/NETBSAD` |
| FREQUENCY | daily |
| PUBLICATION LAG | 1 day |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 1 day | Publication lag |
| 3 | 4 / 8 | Mapped / actual API fields |
| 4 | 9 | Schema columns |

# Sidebar siblings

- disbsad
- system_prices
- boal
- market_depth
- mid

# Overview

1. <code>netbsad</code> is **Net Balancing Services Adjustment Data** — the per-settlement-period netted view of BSAD price and volume adjustments that feed into SBP/SSP derivation. Where `disbsad` is the disaggregated record, NETBSAD is the aggregate already netted. Use it when you want one row per (date, period) carrying the net contribution to the imbalance price; use DISBSAD when you need component-level attribution.

2. Gridflow fetches it from <code>/datasets/NETBSAD</code> using <code>from</code>/<code>to</code> query params (NOT `publishDateTimeFrom`/`To`) per the docs (connector entry at <code>connectors/elexon/endpoints.py L90-96</code>, `from_param="from", to_param="to"`). The <code>NETBSADTransformer</code> derives `timestamp_utc` and dedups on `(settlement_date, settlement_period)`. No Pydantic class is declared.

3. Cadence is daily publication with 1-day lag (BSC settlement timetable). Verified against the live API on 2026-05-08; the sample returned the eight finer-grained API fields (`netBuyPriceCostAdjustmentEnergy`, etc.) — note that the transformer's current 4-column rename mapping does NOT cover these names, so fresh bronze produces silver with the four adjustment columns null. This is documented as a Phase-7 mini-recon candidate in the frontmatter.

# Sample chart

- **Type:** `barsH`
- **Title:** "Daily NETBSAD price adjustment · last 30 days"
- **Subtitle:** "Horizontal bars · £/MWh · UTC · April 2026"
- **Seed:** 18
- **Toggles:** `buy adjustment` (active) / `sell adjustment`

# Schema

Defined in `gridflow/silver/elexon/netbsad.py` · `NETBSADTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/netbsad.py L74` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/netbsad.py L75` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/netbsad.py L85-94` |
| `net_buy_price_adjustment` | `Optional[float]` | Yes | `netBuyPriceAdjustment` (transformer mapping) — **NOT** in live API as of 2026-05-08 | £/MWh. Current bronze returns finer-grained fields the transformer does not aggregate. See frontmatter discrepancy. | `silver/elexon/netbsad.py L58` |
| `net_sell_price_adjustment` | `Optional[float]` | Yes | `netSellPriceAdjustment` (transformer mapping) — same gap | £/MWh. Silent-null in fresh silver. | `silver/elexon/netbsad.py L59` |
| `net_buy_volume_adjustment` | `Optional[float]` | Yes | `netBuyVolumeAdjustment` (transformer mapping) — same gap | MWh. Silent-null in fresh silver. | `silver/elexon/netbsad.py L60` |
| `net_sell_volume_adjustment` | `Optional[float]` | Yes | `netSellVolumeAdjustment` (transformer mapping) — same gap | MWh. Silent-null in fresh silver. | `silver/elexon/netbsad.py L61` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/netbsad.py L100` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/netbsad.py L101` |

**PARQUET PATH:** `data/silver/elexon/netbsad/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/netbsad.py L96`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | net_buy_price_adjustment | net_sell_price_adjustment | net_buy_volume_adjustment | net_sell_volume_adjustment | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 0.0 | 0.0 | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 0.0 | 0.0 | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 14.20 | -8.40 | 120.0 | -60.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 6.10 | -3.20 | 80.0 | -42.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **38.20** | **-22.10** | **210.0** | **-150.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 31.50 | -18.20 | 180.0 | -120.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 4.80 | -2.10 | 65.0 | -32.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 0.0 | 0.0 | 0.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP8) and 2 (SP9) — zero placeholders — derived from vault Bronze Sample shape (vault/elexon/netbsad.md, live 2026-05-08; the actual SP9 row carries eight zeros across the finer-grained fields, which all collapse to "no adjustment" semantically). Remaining rows synthesised — respect transformer constraints (signed floats, sell direction negative, buy direction positive) and represent the typical morning-and-evening-peak BSAD activity. The highlighted **SP36 (buy +£38.20, sell -£22.10)** row is the interesting case: largest evening-peak NETBSAD price adjustment — the moment system stress translates most strongly into the imbalance cash-out.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: NETBSAD's interesting structure is the four adjustment categories — buy/sell × price/volume — but these are documented as schema rows. No additional codelists.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/NETBSAD`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/netbsad/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.netbsad.NETBSADTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/NETBSAD?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily NETBSAD-derived buy-side price contribution
SELECT settlement_date,
       SUM(net_buy_price_adjustment) AS total_buy_adjustment_gbp_mwh,
       AVG(net_buy_volume_adjustment) AS avg_buy_volume_mwh
FROM read_parquet('data/silver/elexon/netbsad/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
  AND net_buy_price_adjustment IS NOT NULL
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

nb = pl.read_parquet("data/silver/elexon/netbsad/**/*.parquet")
sp = pl.read_parquet("data/silver/elexon/system_prices/**/*.parquet")
# Net BSAD share of cash-out price
combo = nb.join(sp, on=["settlement_date", "settlement_period"], how="inner")
combo = combo.with_columns(
    (pl.col("net_buy_price_adjustment") / pl.col("system_buy_price"))
      .alias("bsad_share_of_sbp")
)
print(combo.tail(10))
```

# Caveats

## 01 Column-mapping incomplete vs live API

The transformer renames `netBuyPriceAdjustment` / `netSellPriceAdjustment` / `netBuyVolumeAdjustment` / `netSellVolumeAdjustment`, but the live API on 2026-05-08 returns finer-grained fields (`netBuyPriceCostAdjustmentEnergy`, `netBuyPriceVolumeAdjustmentEnergy`, etc.). Fresh bronze produces silver with all four NETBSAD columns null. This is documented as a Phase-7 mini-recon candidate. *(Source: discrepancy in frontmatter; vault Bronze Sample vs `silver/elexon/netbsad.py L55-62`.)*

## 02 No Pydantic schema in `schemas/elexon.py`

Like DISBSAD and the other indicated/aggregate datasets, NETBSAD has no dedicated Pydantic class. Silver shape is defined by `NETBSADTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no NETBSAD class.)*

## 03 Sum of DISBSAD = NETBSAD

By construction, `disbsad.volume` summed per `(settlement_date, settlement_period)` equals the NETBSAD net volume for the same period. Don't sum NETBSAD across components by joining to DISBSAD — you'll double-count. *(Source: vault Known Issues; vault Overview — "Computed from the disaggregated DISBSAD components".)*

## 04 `from`/`to` query params, not `publishDateTimeFrom`/`To`

Like DISBSAD, BOALF, and MID, NETBSAD uses `from`/`to` parameters. Connector overrides via `from_param="from", to_param="to"`. Wrong param names get silently ignored. *(Source: `connectors/elexon/endpoints.py L94-95`.)*

## 05 Sell adjustments are negative by convention

When non-null, `net_sell_price_adjustment` and `net_sell_volume_adjustment` are negative because they represent the SO selling power back. Don't take absolute values without thinking about which direction the adjustment is from. *(Source: cross-reference with DISBSAD sign convention.)*

# Related datasets

- **disbsad** — Disaggregated balancing services adjustment data. `daily`. The component source; sum DISBSAD by (date, period) to recover NETBSAD totals. `elexon · prices & balancing · daily`
- **system_prices** — System buy / sell prices. `30 min`. The downstream consumer; NETBSAD adjustments are an input to SBP/SSP derivation. `elexon · prices & balancing · 30 min`
- **boal** — Bid-offer acceptance (BOALF). `hourly`. The BM-side action record; combine with NETBSAD's non-BM totals for full balancing-cost analysis. `elexon · prices & balancing · hourly`
- **market_depth** — Settlement market depth. `30 min`. The per-period market summary that aggregates BOAL + DISBSAD + IMBALNGC; market_depth and NETBSAD overlap on the non-BM side. `elexon · prices & balancing · 30 min`
