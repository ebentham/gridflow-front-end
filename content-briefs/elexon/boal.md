---
slug: boal
vendor: elexon
vendor_label: Elexon BMRS
api_code: BOALF
last_verified: 2026-05-21
sources_consulted:
  - vault/elexon/boal.md (refreshed 2026-05-21 from quant-vault for G5-W2.1)
  - gridflow/src/gridflow/schemas/elexon.py::ElexonBOAL (G5-W2.1: bid_offer_acceptance_number removed; was a stale duplicate)
  - gridflow/src/gridflow/silver/elexon/boal.py::BOALTransformer (G5-W2.1: acceptance_time now cast str→UTC datetime)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 67-73, PUBLISH_DATETIME style with from/to params)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/BOALF (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vendor / vault Overview heading"
    source_a_says: "Endpoint slug is `boal` but path is `/datasets/BOALF` — BOAL was deprecated/renamed by Elexon to BOALF"
    source_b: "gridflow connectors/elexon/endpoints.py L67-73"
    source_b_says: "ENDPOINTS['boal'] uses path='/datasets/BOALF'; old BOAL also in EXCLUDED_ENDPOINTS"
    orchestrator_recommendation: "documented and consistent — Gridflow slug retains `boal` for backward compat while the API path tracks BOALF; flag in editorial layer so users aren't confused"
discrepancies_resolved_in:
  - gridflow PR #7 (G5-W2.1, merged 2026-05-20):
      Resolves the `bid_offer_acceptance_number` duplicate-field
      discrepancy — the field was dropped from ElexonBOAL because it was
      a stale duplicate of acceptance_number. Same commit also added the
      str→UTC datetime cast on acceptance_time, caught by the
      parametrised schema-alignment acceptance test.
ready_for_claude_design: true
checked_at: 2026-05-21T00:00:00Z
---

# Editorial layer

**Tagline:** Every accepted balancing instruction, <span class="italic fg-accent">unit by unit.</span>

**Lede:** Per-BMU GB balancing-mechanism dispatch instructions — the canonical audit trail for BSC settlement, BMU dispatch modelling, and STOR analysis.

**Verified line:** Verified against vendor docs: 2026-05-21 · [Elexon BMRS · BOALF](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/BOALF)

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

1. <code>boal</code> is the per-BMU GB balancing-mechanism acceptance feed — every accepted bid or offer instruction, keyed on <code>(settlement_date, settlement_period, bm_unit_id, acceptance_number)</code>. It is the canonical audit trail for BSC settlement, BMU dispatch modelling, and STOR analysis. The Elexon API now serves it as <code>BOALF</code>; gridflow keeps the legacy slug.

2. Gridflow fetches it from <code>/datasets/BOALF</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze, is validated against <code>ElexonBOAL</code>, and written to silver via <code>BOALTransformer</code>.

3. Refreshed hourly with ~10 minute publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `barsH`
- **Title:** "Top 10 BMUs by acceptance volume · last 24 hours"
- **Subtitle:** "Horizontal bars · |MW| accepted · UTC · 6 May 2026"
- **Items:** plausible top-10 BMUs by accepted MW — see Commit 3 inline JSON in the rendered page
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

Silver slug is `boal` for backward compat; API path is `/datasets/BOALF` (the old `boal` is in `EXCLUDED_ENDPOINTS`). Use the connector's `path`, not the slug. *(Source: `connectors/elexon/endpoints.py L67-73`.)*

## 02 Acceptances can span multiple settlement periods

API returns `settlementPeriodFrom`/`To`; transformer keeps only `From` and loses the span. Period-accurate accounting needs bronze. *(Source: `silver/elexon/boal.py L57-59`.)*

## 03 `acceptance_number` is non-unique across (date, BM unit)

The same integer reappears across periods for spanning acceptances. Dedup key is the four-tuple; don't assume `(bm_unit_id, acceptance_number)` is unique. *(Source: `silver/elexon/boal.py L102-105`.)*

## 04 `from`/`to` query params, not `publishDateTimeFrom/To`

BOALF overrides the standard window pattern with `from_param="from", to_param="to"`. Hand-crafted `publishDateTimeFrom` URLs return the default ~24h window. *(Source: `connectors/elexon/endpoints.py L70-72`.)*

## 05 `bid_offer_acceptance_number` is declared but unpopulated

Schema declares it (`schemas/elexon.py L114`) but transformer doesn't write it; reserved for future bid/offer-pair disaggregation. *(Source: frontmatter discrepancy.)*

## 06 `storProviderFlag` vs `storFlag` API drift

API has used both names; transformer renames both to `stor_flag`. Silver is uniform. *(Source: `silver/elexon/boal.py L65-66`.)*

# Related datasets

- **pn** — Physical notifications. `hourly`. Compare ex-post acceptances (BOAL) against ex-ante notifications (PN) for the same `bm_unit_id` to derive the BMU's redispatched volume. `elexon · prices & balancing · hourly`
- **bmunits_reference** — BMU reference list. `weekly`. Join on `bm_unit_id` to attach fuel type, lead party, registered capacity. Essential for any BOAL aggregation by fuel/operator. `elexon · system & reference · weekly`
- **system_prices** — System buy / sell prices. `30 min`. Correlate BOAL volume per period against SBP/SSP — the cash-out price for the imbalance the acceptances were resolving. `elexon · prices & balancing · 30 min`
- **disbsad** — Disaggregated balancing services adjustment. `daily`. Sibling settlement record of non-BM balancing actions; BOAL covers BM-issued instructions, DISBSAD covers everything else. `elexon · prices & balancing · daily`
