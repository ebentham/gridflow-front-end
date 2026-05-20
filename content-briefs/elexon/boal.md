---
slug: boal
vendor: elexon
vendor_label: Elexon BMRS
api_code: BOALF
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/boal.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonBOAL (lines 99-123)
  - gridflow/src/gridflow/silver/elexon/boal.py::BOALTransformer (lines 19-125)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 67-73, PUBLISH_DATETIME style with from/to params)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/BOALF (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vendor / vault Overview heading"
    source_a_says: "Endpoint slug is `boal` but path is `/datasets/BOALF` — BOAL was deprecated/renamed by Elexon to BOALF"
    source_b: "gridflow connectors/elexon/endpoints.py L67-73"
    source_b_says: "ENDPOINTS['boal'] uses path='/datasets/BOALF'; old BOAL also in EXCLUDED_ENDPOINTS"
    orchestrator_recommendation: "documented and consistent — Gridflow slug retains `boal` for backward compat while the API path tracks BOALF; flag in editorial layer so users aren't confused"
  - source_a: "vault Silver schema includes `bid_offer_acceptance_number` as a distinct column"
    source_a_says: "Field is present and aliased to acceptance_number"
    source_b: "gridflow schemas/elexon.py L114"
    source_b_says: "ElexonBOAL has both `acceptance_number` (L106) and `bid_offer_acceptance_number` (L114) as separate Optional[int] fields"
    orchestrator_recommendation: "trust gridflow — both fields exist on the schema but the silver transformer only writes acceptance_number; bid_offer_acceptance_number is reserved for a future per-pair column and not populated today"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Every accepted balancing instruction, <span class="italic fg-accent">unit by unit.</span>

**Lede:** BOALF (Bid Offer Acceptance Level Flagged — the successor to deprecated BOAL) is the row-level record of every dispatch instruction the System Operator issues to a Balancing Mechanism Unit. Each row carries `level_from` / `level_to` MW, the acceptance time, and provenance flags (`so_flag`, `stor_flag`, `rr_flag`). It is the audit trail behind BSC settlement and the primary feature for BMU dispatch modelling.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · BOALF](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/BOALF)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.boal` |
| API PATH | `/datasets/BOALF` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~10 min |
| VOLUME | 1.1M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, bm_unit_id, acceptance_number)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Publication frequency |
| 2 | ~10 min | Publication lag |
| 3 | ~1.1M | Acceptances / month |
| 4 | 14 | Schema columns |

# Sidebar siblings

- pn
- bmunits_reference
- disbsad
- netbsad
- system_prices

# Overview

1. <code>boal</code> (silver slug) is Gridflow's name for the BMRS **BOALF** endpoint — Bid Offer Acceptance Level Flagged. Each row describes one accepted bid or offer issued to a BMU within a settlement period: which unit (`bm_unit_id`), what level change (`bid_offer_level_from` → `bid_offer_level_to` in MW), when it was issued (`acceptance_time`), and what flags accompany it (`so_flag` for System Operator-issued, `stor_flag` for STOR, `rr_flag` for Replacement Reserve).

2. Gridflow fetches it from <code>/datasets/BOALF</code> using <code>from</code>/<code>to</code> query params (NOT the standard `publishDateTimeFrom/To`) per the docs (connector entry at <code>connectors/elexon/endpoints.py L67-73</code>, <code>from_param="from"</code>, <code>to_param="to"</code>). The <code>BOALTransformer</code> renames camelCase to snake_case, derives `timestamp_utc` from the settlement period pair, and dedups on `(settlement_date, settlement_period, bm_unit_id, acceptance_number)`. Pydantic schema <code>ElexonBOAL</code> is declared.

3. Cadence is near-real-time — acceptances are published hourly with roughly 10-minute lag as instructions are issued. Verified against the live API on 2026-05-08. Pair with `pn` to compare ex-post acceptances against ex-ante notifications (the spread is the BMU's flexibility expressed); pair with `system_prices` to correlate dispatch volume with cash-out price spikes.

# Sample chart

- **Type:** `barsH`
- **Title:** "Top 10 BMUs by acceptance volume · last 24 hours"
- **Subtitle:** "Horizontal bars · |MW| accepted · UTC · 6 May 2026"
- **Seed:** 8
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonBOAL` (lines 99-123) and `gridflow/silver/elexon/boal.py` · `BOALTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `acceptance_time`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L102` |
| `settlement_period` | `int` | No | `settlementPeriodFrom` (or `settlementPeriod`) | 1..50. **Note**: an acceptance can span multiple periods (`settlementPeriodFrom` < `settlementPeriodTo`); silver keeps only `From`. See caveat 02. | `schemas/elexon.py L103`; `silver/elexon/boal.py L57-59` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/boal.py L91-100` |
| `bm_unit_id` | `str` | No | `bmUnit` | BM Unit identifier (e.g. `T_DRAXX-1`). Preserve raw casing. | `schemas/elexon.py L105` |
| `acceptance_number` | `Optional[int]` | Yes | `acceptanceNumber` | Acceptance instruction number; non-unique across (date, BM unit). | `schemas/elexon.py L106` |
| `acceptance_time` | `Optional[datetime[UTC]]` | Yes | `acceptanceTime` | Time the acceptance was issued. Point-in-time field. | `schemas/elexon.py L107` |
| `deem_flag` | `bool` | No (default `False`) | `deemedBoFlag` | Deemed bid/offer flag. | `schemas/elexon.py L108` |
| `so_flag` | `bool` | No (default `False`) | `soFlag` | System Operator flag (NESO-issued vs market-issued). | `schemas/elexon.py L109` |
| `stor_flag` | `bool` | No (default `False`) | `storProviderFlag` / `storFlag` | STOR flag. Note the API has used both field names. | `schemas/elexon.py L110`; `silver/elexon/boal.py L65-66` |
| `rr_flag` | `bool` | No (default `False`) | `rrFlag` | Replacement Reserve flag. | `schemas/elexon.py L111` |
| `bid_offer_level_from` | `Optional[float]` | Yes | `levelFrom` | MW. Starting level for the instruction. | `schemas/elexon.py L112` |
| `bid_offer_level_to` | `Optional[float]` | Yes | `levelTo` | MW. Ending level. Difference (`levelTo - levelFrom`) = redispatched MW. | `schemas/elexon.py L113` |
| `bid_offer_acceptance_number` | `Optional[int]` | Yes | _reserved_ | Schema field present (`schemas/elexon.py L114`) but NOT populated by the live transformer. See discrepancy in frontmatter. | `schemas/elexon.py L114` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L115` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L116` |

**PARQUET PATH:** `data/silver/elexon/boal/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, bm_unit_id, acceptance_number)` (silver/elexon/boal.py L102-105)

# Sample data

| settlement_date | settlement_period | timestamp_utc | bm_unit_id | acceptance_number | acceptance_time | deem_flag | so_flag | stor_flag | rr_flag | bid_offer_level_from | bid_offer_level_to | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | T_MRWD-1 | 217257 | 2026-05-06T02:31:00Z | false | true | false | false | 480.0 | 480.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 2__DUKPR008 | 1170 | 2026-05-06T02:46:00Z | false | false | false | false | -2.0 | -2.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | T_DRAXX-1 | 217301 | 2026-05-06T07:48:00Z | false | true | false | false | 510.0 | 645.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **17** | **2026-05-06T08:00:00+00:00** | **T_HOWAO-2** | **217305** | **2026-05-06T07:51:00Z** | **false** | **true** | **false** | **false** | **1100.0** | **820.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | T_PEHE-1 | 217311 | 2026-05-06T07:54:00Z | false | true | false | false | 220.0 | 380.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | T_DINGS-1 | 217502 | 2026-05-06T17:18:00Z | false | true | true | false | 0.0 | 88.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | T_DRAXX-1 | 217505 | 2026-05-06T17:21:00Z | false | true | false | false | 645.0 | 645.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | T_HEYM27 | 217681 | 2026-05-06T23:14:00Z | false | true | false | true | 605.0 | 605.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`T_MRWD-1`) and 2 (`2__DUKPR008`) verbatim from the vault Bronze Sample (vault/elexon/boal.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (settlement_period 1..50, level_from/to as floats, flags as booleans) and represent the typical SP17 morning-peak / SP36 evening-peak instruction pattern. The highlighted **T_HOWAO-2 SP17** row is the interesting case: a 280 MW offshore-wind down-instruction (`levelTo` < `levelFrom`) — System Operator constraining wind during a high-output period, exactly the dispatch signal a flexibility model is trying to predict.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: BOAL's notable enumerations — flag combinations and amendment types — are best surfaced as schema row notes; a pill grid would duplicate them)` — the four flags (`deem_flag`, `so_flag`, `stor_flag`, `rr_flag`) are documented inline in the schema.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/BOALF`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/boal/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.boal.BOALTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/BOALF?from=2026-05-06T00:00Z&to=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Top 20 BMUs by absolute redispatched MW in the last 24h
SELECT bm_unit_id,
       SUM(ABS(bid_offer_level_to - bid_offer_level_from)) AS abs_mw_redispatched,
       COUNT(*) AS n_acceptances
FROM read_parquet('data/silver/elexon/boal/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 1 DAY
GROUP BY bm_unit_id
ORDER BY abs_mw_redispatched DESC
LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/boal/**/*.parquet")
# STOR-flagged acceptances by hour-of-day
stor = (
    df.filter(pl.col("stor_flag"))
      .with_columns(pl.col("timestamp_utc").dt.hour().alias("hour"))
      .group_by("hour")
      .agg(pl.col("acceptance_number").count().alias("n_stor"))
      .sort("hour")
)
print(stor)
```

# Caveats

## 01 Slug `boal` ≠ API path `BOALF`

The Gridflow silver slug is `boal` (preserved for backward compatibility) but the API path is `/datasets/BOALF`. Elexon deprecated the original BOAL endpoint and replaced it with BOALF. The old `boal` is in `EXCLUDED_ENDPOINTS`. Don't construct URLs from the slug; use the connector's `path` attribute. *(Source: vault Implementation Delta; `connectors/elexon/endpoints.py L67-73`, `L44-48` for EXCLUDED_ENDPOINTS.)*

## 02 Acceptances can span multiple settlement periods

The API returns `settlementPeriodFrom` and `settlementPeriodTo`; an acceptance can cover multiple periods (e.g. a 1-hour SO instruction spans 2 SPs). The transformer collapses to `settlement_period = settlementPeriodFrom` and loses the span. Long acceptances may be deduped against shorter overlapping ones if the (date, period, bm_unit, acceptance_number) keys collide. For period-accurate accounting, parse the bronze JSON directly. *(Source: vault Known Issues; `silver/elexon/boal.py L57-59`.)*

## 03 `acceptance_number` is non-unique across (date, BM unit)

The same `acceptance_number` integer can appear for the same (settlement_date, bm_unit_id) across periods because the API issues per-period rows for spanning acceptances. The dedup key is the four-tuple `(settlement_date, settlement_period, bm_unit_id, acceptance_number)`; do not assume `(bm_unit_id, acceptance_number)` is unique. *(Source: vault Known Issues; `silver/elexon/boal.py L102-105`.)*

## 04 `from`/`to` query params, not `publishDateTimeFrom/To`

Unlike most BMRS dataset endpoints, BOALF uses `from`/`to` parameters. The connector overrides via `from_param="from", to_param="to"`. If you hand-craft a URL with `publishDateTimeFrom`, the API silently ignores it and returns the last ~24 hours of acceptances. *(Source: `connectors/elexon/endpoints.py L70-72`.)*

## 05 `bid_offer_acceptance_number` is declared but unpopulated

`ElexonBOAL` declares both `acceptance_number` and `bid_offer_acceptance_number` (`schemas/elexon.py L106, L114`). The live transformer only writes `acceptance_number`; `bid_offer_acceptance_number` is reserved for future bid/offer-pair-level disaggregation. Querying for non-null `bid_offer_acceptance_number` today returns empty. *(Source: discrepancy noted in frontmatter; cross-reference `silver/elexon/boal.py output_cols` L113-119.)*

## 06 `storProviderFlag` vs `storFlag` API drift

The API has used both `storProviderFlag` and `storFlag` for the STOR boolean. The transformer's column mapping renames both to `stor_flag` (`silver/elexon/boal.py L65-66`). New bronze files use `storFlag`; older archived ones use `storProviderFlag`. The silver column is the same. *(Source: `silver/elexon/boal.py L65-66`.)*

# Related datasets

- **pn** — Physical notifications. `hourly`. Compare ex-post acceptances (BOAL) against ex-ante notifications (PN) for the same `bm_unit_id` to derive the BMU's redispatched volume. `elexon · prices & balancing · hourly`
- **bmunits_reference** — BMU reference list. `weekly`. Join on `bm_unit_id` to attach fuel type, lead party, registered capacity. Essential for any BOAL aggregation by fuel/operator. `elexon · system & reference · weekly`
- **system_prices** — System buy / sell prices. `30 min`. Correlate BOAL volume per period against SBP/SSP — the cash-out price for the imbalance the acceptances were resolving. `elexon · prices & balancing · 30 min`
- **disbsad** — Disaggregated balancing services adjustment. `daily`. Sibling settlement record of non-BM balancing actions; BOAL covers BM-issued instructions, DISBSAD covers everything else. `elexon · prices & balancing · daily`
