---
slug: soso
vendor: elexon
vendor_label: Elexon BMRS
api_code: SOSO
last_verified: 2026-05-09
sources_consulted:
  - vault/elexon/soso.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonSOSO class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/soso.py::SOSOTransformer (lines 19-143)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 249-254, PUBLISH_DATETIME with max_chunk_hours=23)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/SOSO (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonSOSO class declared"
    source_b: "gridflow silver/elexon/soso.py L19-143"
    source_b_says: "SOSOTransformer outputs 15 columns covering contract, trader, TSO identification, and trade volumes"
    orchestrator_recommendation: "trust silver transformer; matches REMIT in chunk-cap policy and shape-gap"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Interconnector trades, <span class="italic fg-accent">TSO to TSO.</span>

**Lede:** Per-trade GB interconnector SO-SO prices — the canonical reference for cross-border arbitrage, interconnector flow analysis, and TSO-trade cost attribution.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Elexon BMRS · SOSO](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/SOSO)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.soso` |
| API PATH | `/datasets/SOSO` |
| FREQUENCY | daily |
| PUBLICATION LAG | 1 day |
| VOLUME | 8k / mo |
| PRIMARY KEY | `(settlement_date, contract_identification, trade_direction)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 23 h | Max chunk hours (vendor cap) |
| 3 | 8+ | GB interconnectors |
| 4 | 15 | Schema columns |

# Sidebar siblings

- system_prices
- mid
- netbsad
- remit
- fuelhh

# Sample chart

- **Type:** `barsH`
- **Title:** "SOSO trade volume by interconnector · last 30 days"
- **Subtitle:** "Horizontal bars · MW × trades · UTC · April 2026"
- **Seed:** 22
- **Toggles:** `imports` (active) / `exports`

# Schema

Defined in `gridflow/silver/elexon/soso.py` · `SOSOTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/soso.py L81` |
| `settlement_period` | `Optional[int]` | Yes | `settlementPeriod` | 1..50 when present. Some SOSO trades carry no period and rely on `start_time` / `end_time`. | `silver/elexon/soso.py L84-85` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Period-derived if available, else from `start_time` parse, else from `settlement_date` midnight UTC. | `silver/elexon/soso.py L84-106` |
| `contract_identification` | `str` | No | `contractIdentification` | SOSO contract MRID (e.g. `NG_20260507_0100_32`). | `silver/elexon/soso.py L61, L74` |
| `sender_identification` | `Optional[str]` | Yes | `senderIdentification` | EIC code of sending TSO (e.g. `10X1001A1001A515` for NESO). | `silver/elexon/soso.py L59` |
| `receiver_identification` | `Optional[str]` | Yes | `receiverIdentification` | EIC code of receiving TSO. | `silver/elexon/soso.py L60` |
| `resource_provider` | `Optional[str]` | Yes | `resourceProvider` | Resource provider EIC. | `silver/elexon/soso.py L62` |
| `trade_direction` | `Optional[str]` | Yes | `tradeDirection` | `Bid` or `Offer`. | `silver/elexon/soso.py L63` |
| `trade_quantity_mw` | `Optional[float]` | Yes | `tradeQuantity` | MW. | `silver/elexon/soso.py L64, L108-110` |
| `trade_price` | `Optional[float]` | Yes | `tradePrice` | £/MWh. | `silver/elexon/soso.py L65, L108-110` |
| `trader_unit` | `Optional[str]` | Yes | `traderUnit` | Interconnector identifier (e.g. `EWIC_NG`, `IFA_NG`, `BRITNED_NG`). | `silver/elexon/soso.py L66` |
| `start_time` | `Optional[datetime[UTC]]` | Yes | `startTime` | Trade start time. | `silver/elexon/soso.py L67, L112-119` |
| `end_time` | `Optional[datetime[UTC]]` | Yes | `endTime` | Trade end time. | `silver/elexon/soso.py L68, L112-119` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/soso.py L128` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/soso.py L129` |

**PARQUET PATH:** `data/silver/elexon/soso/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, contract_identification, trade_direction)` (`silver/elexon/soso.py L121-124`)

# Sample data

| settlement_date | timestamp_utc | contract_identification | sender_identification | receiver_identification | trade_direction | trade_quantity_mw | trade_price | trader_unit | start_time | end_time | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-07 | 2026-05-07T01:00:00+00:00 | NG_20260507_0100_32 | 10X1001A1001A515 | 10X1001A1001A59Q | Bid | 25.0 | 120.27 | EWIC_NG | 2026-05-07T01:00:00+00:00 | 2026-05-07T02:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 2026-05-07T01:00:00+00:00 | NG_20260507_0100_31 | 10X1001A1001A515 | 10X1001A1001A59Q | Bid | 25.0 | 114.27 | EWIC_NG | 2026-05-07T01:00:00+00:00 | 2026-05-07T02:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 2026-05-07T08:00:00+00:00 | NG_20260507_0800_18 | 10X1001A1001A515 | 10YFR-RTE------C | Offer | 50.0 | 142.50 | IFA_NG | 2026-05-07T08:00:00+00:00 | 2026-05-07T09:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 2026-05-07T08:00:00+00:00 | NG_20260507_0800_19 | 10X1001A1001A515 | 10YNL----------L | Bid | 100.0 | 138.20 | BRITNED_NG | 2026-05-07T08:00:00+00:00 | 2026-05-07T09:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-07** | **2026-05-07T17:00:00+00:00** | **NG_20260507_1700_42** | **10X1001A1001A515** | **10YFR-RTE------C** | **Offer** | **200.0** | **245.80** | **IFA_NG** | **2026-05-07T17:00:00+00:00** | **2026-05-07T18:00:00+00:00** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-07 | 2026-05-07T17:00:00+00:00 | NG_20260507_1700_43 | 10X1001A1001A515 | 10YNO-0--------C | Bid | 80.0 | 162.40 | NSL_NG | 2026-05-07T17:00:00+00:00 | 2026-05-07T18:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 2026-05-07T22:00:00+00:00 | NG_20260507_2200_11 | 10X1001A1001A515 | 10YIE-1001A00010 | Bid | 25.0 | 88.10 | EWIC_NG | 2026-05-07T22:00:00+00:00 | 2026-05-07T23:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 2026-05-07T23:00:00+00:00 | NG_20260507_2300_15 | 10X1001A1001A515 | 10YBE----------2 | Bid | 50.0 | 92.30 | NEMO_NG | 2026-05-07T23:00:00+00:00 | 2026-05-08T00:00:00+00:00 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`NG_20260507_0100_32`, EWIC, price 120.27) and 2 (`NG_20260507_0100_31`, EWIC, price 114.27) verbatim from the vault Bronze Sample (vault/elexon/soso.md, live 2026-05-08 for delivery 2026-05-07). Remaining rows synthesised — respect transformer constraints (Bid/Offer string, MW + £/MWh floats, EIC strings for sender/receiver, GB-specific trader_unit names) and represent the typical interconnector trade mix across France (IFA), Netherlands (BritNed), Norway (NSL), Ireland (EWIC), and Belgium (NEMO). The highlighted **NG_20260507_1700_42 IFA Offer (200 MW @ £245.80)** row is the interesting case: large evening-peak export to France at near-£250/MWh — the kind of cross-border arbitrage signal interconnector commercial teams trade against.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: interconnector identification is via trader_unit (~10 codes) and TSO EICs, both documented inline in schema rows. The full enumerated list of interconnectors changes as new links commission.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/SOSO`
- AUTH: None required for tested endpoints (2026-05-08/09). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/soso/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.soso.SOSOTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/SOSO?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily SOSO trade volume by interconnector
SELECT settlement_date, trader_unit,
       SUM(CASE WHEN trade_direction = 'Bid'   THEN trade_quantity_mw END) AS import_mw,
       SUM(CASE WHEN trade_direction = 'Offer' THEN trade_quantity_mw END) AS export_mw,
       COUNT(*) AS n_trades,
       AVG(trade_price) AS avg_price_gbp_mwh
FROM read_parquet('data/silver/elexon/soso/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

soso = pl.read_parquet("data/silver/elexon/soso/**/*.parquet")
sp = pl.read_parquet("data/silver/elexon/system_prices/**/*.parquet")
# SOSO price vs same-period SBP — implied trade-vs-imbalance spread
arbitrage = (
    soso.join(sp, on=["settlement_date", "settlement_period"], how="inner")
        .with_columns(
            (pl.col("system_buy_price") - pl.col("trade_price"))
              .alias("imbalance_premium_gbp_mwh")
        )
        .select(["settlement_date", "trader_unit", "trade_direction",
                 "trade_price", "system_buy_price", "imbalance_premium_gbp_mwh"])
)
print(arbitrage.head())
```

# Caveats

## 01 23-hour chunk cap (V2-FIX-03, shared with REMIT)

Vendor caps queries at ~1 day; `max_chunk_hours=23` for DST safety. 25h fails. *(Source: V2-FIX-03; `connectors/elexon/endpoints.py L249-254`.)*

## 02 No Pydantic schema in `schemas/elexon.py`

No `ElexonSOSO` class; shape lives in `SOSOTransformer.output_cols`. *(Source: `silver/elexon/soso.py`.)*

## 03 `settlement_period` often missing

Trades are hour-based; transformer derives `timestamp_utc` from `start_time` when period absent. Period-keyed joins must accept span semantics. *(Source: `silver/elexon/soso.py L84-106`.)*

## 04 `trade_direction` semantics from GB perspective

`Bid` = GB importing; `Offer` = GB exporting. Confirm with `sender_identification`/`receiver_identification` when uncertain. *(Source: NESO SO-SO convention.)*

## 05 EIC codes, not friendly names, for TSOs

Sender/receiver are EICs (`10X1001A1001A515` = NESO, `10YFR-RTE------C` = RTE). Use `trader_unit` for readable names. *(Source: vault Bronze Sample.)*

# Related datasets

- **system_prices** — System buy / sell prices. `30 min`. SBP/SSP are the cash-out prices SOSO trades are compared against. Pair to derive imbalance premium. `elexon · prices & balancing · 30 min`
- **mid** — Market index data. `hourly`. Wholesale benchmark prices; SOSO trade prices can be compared to MID for inter-market spread. `elexon · prices & balancing · hourly`
- **netbsad** — Net balancing services adjustment data. `daily`. NETBSAD includes SOSO-derived adjustments; cross-check totals when reconciling balancing cost. `elexon · prices & balancing · daily`
- **remit** — REMIT outage messages. `as published`. Interconnector outages disrupt SOSO trades; cross-reference REMIT `event_status=Active` rows with `affected_unit` matching interconnectors. `elexon · system & reference · as published`
