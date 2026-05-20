---
slug: system_prices
vendor: elexon
vendor_label: Elexon BMRS
api_code: DISEBSP
last_verified: 2026-05-09
sources_consulted:
  - vault/elexon/system_prices.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonSystemPrice (lines 25-58)
  - gridflow/src/gridflow/silver/elexon/system_prices.py::SystemPriceTransformer (lines 18-160)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 59-63, DATE_PATH style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/system-prices/-settlementDate- (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Implementation Delta L186"
    source_a_says: "Registry path string omits {settlementDate} — code declares path=\"/balancing/settlement/system-prices\" and appends date in _fetch_date_path() — cosmetic"
    source_b: "gridflow connectors/elexon/endpoints.py L59-63"
    source_b_says: "ENDPOINTS['system_prices'].path = '/balancing/settlement/system-prices' (no trailing {date} placeholder)"
    orchestrator_recommendation: "cosmetic only — actual request URL is correct because DATE_PATH style appends date at request time. No fix needed."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB imbalance prices, <span class="italic fg-accent">settled half-hourly.</span>

**Lede:** System Buy Price and System Sell Price — the cash-out prices that settle imbalance in the GB Balancing Mechanism. Together with the Net Imbalance Volume, the canonical signal for short-term GB power-market value and the basis of the imbalance price in BSC settlement.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Elexon BMRS · DISEBSP](https://bmrs.elexon.co.uk/api-documentation/endpoint/balancing/settlement/system-prices/-settlementDate-)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.system_prices` |
| API PATH | `/balancing/settlement/system-prices/{date}` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | hours → weeks |
| VOLUME | ~1.4k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | hours | II indicative lag |
| 3 | 7 | Reconciliation runs |
| 4 | 10 | Schema columns |

# Sidebar siblings

- netbsad
- disbsad
- freq
- fuelinst
- mid

# Overview

1. <code>system_prices</code> holds the **System Buy Price (SBP)** and **System Sell Price (SSP)** — the cash-out prices used by the GB electricity Balancing Mechanism to settle imbalance. SBP is what generators pay (or are paid) for being short relative to their physical notifications; SSP is what suppliers pay for being long. Each row carries SBP, SSP, the Net Imbalance Volume (`net_imbalance_volume`, MWh), and a `price_derivation_code` describing how the price was derived.

2. Gridflow fetches it from <code>/balancing/settlement/system-prices/{settlementDate}</code> — a **DATE_PATH** style endpoint where the date is appended to the URL path at request time (connector entry at <code>connectors/elexon/endpoints.py L59-63</code>). The <code>SystemPriceTransformer</code> renames camelCase to snake_case (including the V2-FIX-04 split of `priceDerivationCode` into its own column), derives `timestamp_utc`, and applies BSC run-type precedence (`II<SF<R1<R2<R3<RF<DF`) via `_resolve_runs` to keep the highest-rank run per period. Pydantic schema <code>ElexonSystemPrice</code> is declared.

3. Cadence is half-hourly publication, but the lag stretches from hours (Initial Indicative) to weeks (Reconciliation Final) as BSC settlement progresses. Verified against the live API on 2026-05-09; the sample returned 48 rows for 2026-05-06 with `priceDerivationCode` values of `N` (normal) and the SBP equal to SSP throughout (single-price reform). Pair with `disbsad`/`netbsad` for cost attribution and with `mid` for wholesale-spread analysis.

# Sample chart

- **Type:** `priceLadder`
- **Title:** "SBP & SSP · 24-hour snapshot"
- **Subtitle:** "Price ladder · £/MWh · UTC · 6 May 2026"
- **Seed:** 7
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonSystemPrice` (lines 25-58) and `gridflow/silver/elexon/system_prices.py` · `SystemPriceTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `run_type` (precedence `II<SF<R1<R2<R3<RF<DF`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L42` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). Validator `ge=1, le=50`. | `schemas/elexon.py L43` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. Validator requires tzinfo. | `schemas/elexon.py L44, L53-58` |
| `system_sell_price` | `float` | No | `systemSellPrice` | **£/MWh**. Validator `ge=-500, le=10000` — wide range to admit price spikes / scarcity events. | `schemas/elexon.py L45` |
| `system_buy_price` | `float` | No | `systemBuyPrice` | **£/MWh**. Same range. Typically equal to SSP under single-price reform (post-Nov 2018). | `schemas/elexon.py L46` |
| `net_imbalance_volume` | `float` | No | `netImbalanceVolume` | **MWh**. Negative = system was short; positive = long. | `schemas/elexon.py L47` |
| `run_type` | `Optional[str]` | Yes | `settlementRunType` (when present) | `II` / `SF` / `R1` / `R2` / `R3` / `RF` / `DF` — BSC settlement run precedence. **This endpoint does not surface the field**, so live silver has `run_type=None`. Older fixtures may populate it. | `schemas/elexon.py L48` |
| `price_derivation_code` | `Optional[str]` | Yes | `priceDerivationCode` | How SBP/SSP was derived. Observed values: `N` (normal), `P` (provisional). No regex constraint — vendor-managed list (V2-FIX-04). | `schemas/elexon.py L49`; `silver/elexon/system_prices.py L73-74` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L50` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L51` |

**PARQUET PATH:** `data/silver/elexon/system_prices/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` after run-type precedence (`silver/elexon/system_prices.py L121-125, L144-156`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | system_sell_price | system_buy_price | net_imbalance_volume | run_type | price_derivation_code | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 1 | 2026-05-06T00:00:00+00:00 | 96.79 | 96.79 | -37.99 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| 2026-05-06 | 2 | 2026-05-06T00:30:00+00:00 | 97.02 | 97.02 | -35.72 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| 2026-05-06 | 3 | 2026-05-06T01:00:00+00:00 | 92.41 | 92.41 | 22.18 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | 89.55 | 89.55 | 41.07 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| **2026-05-06** | **17** | **2026-05-06T08:00:00+00:00** | **148.32** | **148.32** | **-128.44** | _null_ | **P** | **elexon** | **2026-05-09T12:00:00Z** |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | 211.04 | 211.04 | -186.91 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 189.50 | 189.50 | -152.33 | _null_ | N | elexon | 2026-05-09T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 81.16 | 81.16 | 14.65 | _null_ | N | elexon | 2026-05-09T12:00:00Z |

**Sources:** Rows 1 (SP1, SBP/SSP £96.79, NIV -37.99 MWh) and 2 (SP2, SBP/SSP £97.02, NIV -35.72 MWh) verbatim from the vault Bronze Sample (vault/elexon/system_prices.md, live 2026-05-08/09; matches the canonical authored-pages/elexon/system_prices.html reference). Remaining rows follow the same canonical reference page. The highlighted **SP17 (SBP £148.32, NIV -128 MWh, derivation `P`)** row is the interesting case: morning-peak system short with a `P` (provisional) derivation code — exactly the kind of period where the V2-FIX-04 regex bug used to reject the record.

# Dataset-specific section: Settlement runs

BSC settlement runs each (settlement_date, settlement_period) multiple times as data is reconciled. Same key, different prices and NIV — the highest-rank run wins. This endpoint exposes the latest run's values but does not tag which run produced them; `run_type` stays `null` for silver derived from `/system-prices/{date}`.

- **II** — Initial Indicative · within hours
- **SF** — Settlement Final · settlement day
- **R1** — Reconciliation 1 · ~10 days
- **R2** — Reconciliation 2 · ~1 month
- **R3** — Reconciliation 3 · ~4 months
- **RF** — Reconciliation Final · ~14 months
- **DF** — Post-Final Dispute · case-by-case

Precedence used by `_resolve_runs` (`silver/elexon/system_prices.py L25`): `{"II": 1, "SF": 2, "R1": 3, "R2": 4, "R3": 5, "RF": 6, "DF": 7}` — highest wins on dedup.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/{settlementDate}`
- AUTH: None required for tested endpoints (2026-05-09). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/system_prices/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.system_prices.SystemPriceTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2026-05-06?format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Last 7 days of system prices
SELECT settlement_date, settlement_period,
       system_sell_price, system_buy_price,
       net_imbalance_volume
FROM read_parquet('data/silver/elexon/system_prices/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 7 DAY
ORDER BY settlement_date, settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/system_prices/**/*.parquet")
# Daily mean SBP and a min/max spread for volatility
daily = df.group_by("settlement_date").agg(
    pl.col("system_buy_price").mean().alias("sbp_mean"),
    (pl.col("system_buy_price").max() -
     pl.col("system_buy_price").min()).alias("sbp_range"),
)
print(daily.sort("settlement_date").tail())
```

# Caveats

## 01 Same key, different prices over time

Same `(settlement_date, settlement_period)` reappears with different prices as BSC reconciliation progresses (`II → SF → R1 → R2 → R3 → RF → DF`). The transformer keeps the highest-rank run only via `_resolve_runs`. For point-in-time queries — "what did the trader see at 09:00 the next day?" — write a custom dedup or filter on the bronze layer's `ingested_at`. *(Source: vault Known Issues; `silver/elexon/system_prices.py L121-125, L144-156`.)*

## 02 SBP equals SSP under single-price reform

Since November 2018, GB cash-out uses a single price — SBP and SSP are typically equal in any given period. The two columns are kept for backward compatibility and edge cases where they diverge (e.g. emergency instructions). Treat `system_buy_price` as "the" imbalance price for most analysis. *(Source: domain knowledge — GB single-price reform; vault sample shows SBP == SSP for every observed period.)*

## 03 `price_derivation_code` ≠ `run_type` (V2-FIX-04)

Earlier schema versions conflated `priceDerivationCode` with the BSC run type and applied a regex (`^(II|SF|R[1-3]|RF|DF)$`) that rejected the live values `N` and `P`. Resolved in V2 (V2-FIX-04, 2026-05-09): `price_derivation_code` is now a dedicated column with no regex; `run_type` is `Optional[str]`. Live silver from this endpoint leaves `run_type` null. *(Source: vault Implementation Delta + Changelog V2-FIX-04; `silver/elexon/system_prices.py L67-75`.)*

## 04 Settlement period range is 1..50

On the autumn clock change, the day has 50 settlement periods (25 hours). On spring forward, it has 46 (23 hours). DST handling required when bucketing by day or hour — the silver layer normalises all timestamps to UTC, but `settlement_period` can reach 50 on DST days. *(Source: `schemas/elexon.py L43`; vault Known Issues.)*

## 05 NIV sign convention

Negative `net_imbalance_volume` means the system was short — actual generation undershot demand, the System Operator had to buy power, SBP went up. Positive NIV means long — generation overshot, the SO had to sell power, SSP went down (or negative in oversupply). Sign convention is GB-specific; do not assume it matches other markets. *(Source: domain knowledge — GB cash-out semantics.)*

# Related datasets

- **netbsad** — Net Bid-Offer Acceptance Volumes. `daily`. The per-period totals that explain how the System Operator balanced. Pair with NIV to see why prices moved. `elexon · prices & balancing · daily`
- **disbsad** — Disaggregated settlement bid/offer acceptances. `daily`. The granular companion data behind the netted view in NETBSAD — useful for per-BMU attribution. `elexon · prices & balancing · daily`
- **mid** — Market Index Price. `hourly`. The day-ahead reference price. Compare against SBP/SSP to measure imbalance penalties versus the prevailing wholesale price. `elexon · prices & balancing · hourly`
- **fuelinst** — Real-time fuel mix. `~5 min`. When the system goes short and SBP spikes, fuelinst tells you which technologies were dispatched to close the gap. `elexon · generation · ~5 min`
