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

**Lede:** Half-hourly GB imbalance cash-out prices and net volume — the canonical signal for short-term power value, cash-out forecasting, and BSC settlement.

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

1. <code>system_prices</code> is the half-hourly GB imbalance cash-out prices (SBP/SSP) and net imbalance volume — settled over a 7-run reconciliation cycle (II → SF → R1 → R2 → R3 → RF → DF). It is the canonical signal for short-term power value, cash-out forecasting, and BSC settlement.

2. Gridflow fetches it from <code>/balancing/settlement/system-prices/{date}</code> using the DATE-path style (date appended at request time). The raw JSON lands in bronze, is validated against <code>ElexonSystemPrice</code>, and written to silver via <code>SystemPriceTransformer</code> — <code>run_type</code> carries reconciliation-run precedence and serves as the PIT field.

3. Refreshed every 30 minutes with hours-to-weeks publication lag (reconciliation-run dependent). Verified against vendor docs on 2026-05-09.

# Sample chart

- **Type:** `priceLadder`
- **Title:** "SBP & SSP · 24-hour snapshot"
- **Subtitle:** "Price ladder · £/MWh · UTC · 6 May 2026"
- **Shape:** (legacy hardcoded — this brief is the gold standard for the default priceLadder path)
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

BSC reconciliation revises the same `(date, period)` (`II → SF → R1..R3 → RF → DF`); transformer keeps highest-rank run. PIT queries need bronze. *(Source: `silver/elexon/system_prices.py L121-125`.)*

## 02 SBP equals SSP under single-price reform

Post-Nov 2018 single-price reform — SBP usually equals SSP. Treat `system_buy_price` as the imbalance price. *(Source: GB single-price reform.)*

## 03 `price_derivation_code` ≠ `run_type` (V2-FIX-04)

V2-FIX-04 split `priceDerivationCode` into its own column (no regex); `run_type` is now `Optional[str]` and null from this endpoint. *(Source: `silver/elexon/system_prices.py L67-75`.)*

## 04 Settlement period range is 1..50

DST days have 46 (spring) or 50 (autumn) periods. Validator `ge=1, le=50`. *(Source: `schemas/elexon.py L43`.)*

## 05 NIV sign convention

Negative NIV = system short (SBP rises); positive = long. GB-specific. *(Source: GB cash-out semantics.)*

# Related datasets

- **netbsad** — Net Bid-Offer Acceptance Volumes. `daily`. The per-period totals that explain how the System Operator balanced. Pair with NIV to see why prices moved. `elexon · prices & balancing · daily`
- **disbsad** — Disaggregated settlement bid/offer acceptances. `daily`. The granular companion data behind the netted view in NETBSAD — useful for per-BMU attribution. `elexon · prices & balancing · daily`
- **mid** — Market Index Price. `hourly`. The day-ahead reference price. Compare against SBP/SSP to measure imbalance penalties versus the prevailing wholesale price. `elexon · prices & balancing · hourly`
- **fuelinst** — Real-time fuel mix. `~5 min`. When the system goes short and SBP spikes, fuelinst tells you which technologies were dispatched to close the gap. `elexon · generation · ~5 min`
