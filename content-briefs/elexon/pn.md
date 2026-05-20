---
slug: pn
vendor: elexon
vendor_label: Elexon BMRS
api_code: PN
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/pn.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonPN (lines 226-243)
  - gridflow/src/gridflow/silver/elexon/pn.py::PNTransformer (lines 19-113)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 97-101, SETTLEMENT_DATE_PERIOD style — period-iterating fetch)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/PN (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Physical notifications, <span class="italic fg-accent">every BM unit.</span>

**Lede:** PN is Physical Notifications — each BM unit's declared MW intent for each settlement period, submitted around gate closure. PN is the per-BMU baseline against which BOAL acceptances are deviations, the foundation of any BM-unit dispatch model, and the most voluminous per-unit dataset in BMRS (~2,500 rows per period, ~5.4M per month).

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · PN](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/PN)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.pn` |
| API PATH | `/datasets/PN` |
| FREQUENCY | hourly |
| PUBLICATION LAG | ~10 min |
| VOLUME | 5.4M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, bm_unit_id)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Publication frequency |
| 2 | ~10 min | Publication lag |
| 3 | ~2.5k | Rows per period |
| 4 | 8 | Schema columns |

# Sidebar siblings

- boal
- bmunits_reference
- disbsad
- fuelhh
- system_prices

# Overview

1. <code>pn</code> is **Physical Notifications** — every BM unit's pre-gate-closure declared MW level for each settlement period, with `level_from` (start-of-period MW) and `level_to` (end-of-period MW). PN is the dispatch baseline that the Balancing Mechanism deviates from when issuing BOALF acceptances. Each (settlement_date, settlement_period) typically carries ~2,500 rows — one per active BM unit.

2. Gridflow fetches it from <code>/datasets/PN</code> using <code>settlementDate</code> + <code>settlementPeriod</code> path/query params — the **SETTLEMENT_DATE_PERIOD** style (connector entry at <code>connectors/elexon/endpoints.py L97-101</code>). The connector iterates periods 1..50 per date (DST-safe), with stop-on-empty optimisation for short DST days. The <code>PNTransformer</code> renames `bmUnit` → `bm_unit_id`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period, bm_unit_id)`. Pydantic schema <code>ElexonPN</code> is declared.

3. Cadence is hourly publication with ~10-minute lag. Verified against the live API on 2026-05-08; the sample for 2026-05-06 SP24 returned per-BMU level changes (`levelFrom`/`levelTo` pairs). Pair with `bmunits_reference` to attach friendly names and fuel types, with `boal` to compute redispatched MW (`boal.level_from - pn.level_from`), and with `fuelhh` to validate that aggregated PN matches the actual generation outturn.

# Sample chart

- **Type:** `barsH`
- **Title:** "Top 15 BMUs by absolute PN delta · last 24h"
- **Subtitle:** "Horizontal bars · |level_to − level_from| MW · UTC · 6 May 2026"
- **Seed:** 9
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonPN` (lines 226-243) and `gridflow/silver/elexon/pn.py` · `PNTransformer.output_cols`. Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `schemas/elexon.py L229` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). Field validator `ge=1, le=50`. | `schemas/elexon.py L230` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. Validator requires tzinfo. | `schemas/elexon.py L231, L238-243` |
| `bm_unit_id` | `str` | No | `bmUnit` | BM Unit identifier (e.g. `T_DRAXX-1`, `E_BROFB-1`). Preserve raw casing. | `schemas/elexon.py L232` |
| `level_from` | `Optional[float]` | Yes | `levelFrom` | MW at start of period. Can be negative (storage charging, interconnector import). | `schemas/elexon.py L233` |
| `level_to` | `Optional[float]` | Yes | `levelTo` | MW at end of period. `level_to - level_from` = intra-period ramp. | `schemas/elexon.py L234` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L235` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L236` |

**PARQUET PATH:** `data/silver/elexon/pn/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, bm_unit_id)` (`silver/elexon/pn.py L93-96`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | bm_unit_id | level_from | level_to | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 2__FFSEN007 | -9.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | E_BROFB-1 | 11.0 | 0.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | T_DRAXX-1 | 645.0 | 645.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | T_HEYM27 | 605.0 | 605.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **24** | **2026-05-06T11:30:00+00:00** | **T_HOWAO-2** | **1080.0** | **1100.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | T_PEHE-1 | 220.0 | 380.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | T_DRAXX-1 | 645.0 | 645.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | T_HOWAO-2 | 820.0 | 700.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`2__FFSEN007`, level_from=-9, level_to=0) and 2 (`E_BROFB-1`, level_from=11, level_to=0) verbatim from the vault Bronze Sample (vault/elexon/pn.md, live 2026-05-08 SP24). Remaining rows synthesised — respect schema constraints (Optional float MW, prefixed BM unit IDs) and represent typical mid-day declarations from major BMUs across fuel categories (biomass, nuclear, offshore wind, CCGT). The highlighted **T_HOWAO-2 SP24 (1080 → 1100 MW)** row is the interesting case: Hornsea 2 offshore wind declaring a 20 MW intra-period ramp — exactly the unit-level granularity PN exists to surface, vs the FUELHH `WIND` aggregate which collapses all wind to a single number.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: PN's interesting structure is per-BMU, but enumerating BMUs would duplicate bmunits_reference. The level_from/level_to ramp semantics are documented in schema notes.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/PN`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/pn/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.pn.PNTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/PN?settlementDate=2026-05-06&settlementPeriod=24&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Sum PN level_from per period (proxy for total expected generation at gate closure)
SELECT settlement_date, settlement_period,
       SUM(GREATEST(level_from, 0)) AS total_pn_positive_mw,
       SUM(LEAST(level_from, 0))    AS total_pn_negative_mw
FROM read_parquet('data/silver/elexon/pn/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 1 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

pn = pl.read_parquet("data/silver/elexon/pn/**/*.parquet")
boal = pl.read_parquet("data/silver/elexon/boal/**/*.parquet")
# Redispatched MW = BOAL accepted level - PN declared level
redispatch = (
    pn.join(boal, on=["settlement_date", "settlement_period", "bm_unit_id"], how="inner")
      .with_columns(
          (pl.col("bid_offer_level_from") - pl.col("level_from"))
            .alias("redispatched_mw")
      )
      .filter(pl.col("redispatched_mw").abs() > 10)
      .select(["settlement_date", "settlement_period", "bm_unit_id", "redispatched_mw"])
)
print(redispatch.head(20))
```

# Caveats

## 01 Connector iterates periods 1..50 per date

The connector's `SETTLEMENT_DATE_PERIOD` style means each PN backfill makes 48-50 calls per date (one per period). Use stop-on-empty optimisation to break early when the API returns no rows for a period — DST short days have only 46 active periods. Budget API calls accordingly for long backfills (a year ≈ 18,000 calls). *(Source: vault Known Issues; `connectors/elexon/endpoints.py L97-101`.)*

## 02 Very high row volume — ~2,500 rows per period

PN emits roughly one row per active BM unit per period — about 2,500 rows for a typical period, 5.4M per month. Silver parquet is partitioned by month — query a single month at a time when possible. For multi-month analytics, downsample to BMU-day aggregates first. *(Source: vault Known Issues; manifest `rows: "5.4M / mo"`.)*

## 03 `bm_unit_id` casing preserved

Same as BOAL and bmunits_reference: PN returns prefixed IDs like `T_DRAXX-1`, `E_BROFB-1`, `2__FFSEN007`. The transformer preserves casing; downstream joins to bmunits_reference and BOAL must use the same form. *(Source: `silver/elexon/pn.py L75`.)*

## 04 `level_from` and `level_to` capture intra-period ramp

A BMU can declare different MW levels at start vs end of period — these are linear-ramp intents. `level_to - level_from` is the intra-period change. For mid-period MW estimates, linearly interpolate; for energy-summed analytics use `(level_from + level_to) / 2 * 0.5` as the period MWh. *(Source: domain knowledge — BMU PN ramp semantics.)*

## 05 Pair with BOAL for redispatched-MW model features

The canonical pattern for BM-unit dispatch modelling is to join PN (declared) with BOAL (accepted) on `(settlement_date, settlement_period, bm_unit_id)` and compute `boal.bid_offer_level_from − pn.level_from` as the SO-issued redispatch. This is the most common feature in BMU flexibility models — pre-build a gold view if you'll be reading it often. *(Source: domain knowledge — BMU dispatch modelling.)*

# Related datasets

- **boal** — Bid-offer acceptance (BOALF). `hourly`. Ex-post acceptances; PN is the ex-ante baseline. Join on (date, period, bm_unit_id) to compute redispatched MW. `elexon · prices & balancing · hourly`
- **bmunits_reference** — BMU reference list. `weekly`. Join on `bm_unit_id` to attach fuel type, lead party, registered capacity. Essential for any PN aggregation by fuel/operator. `elexon · system & reference · weekly`
- **disbsad** — Disaggregated balancing services adjustment. `daily`. Non-BM balancing actions; combine with PN/BOAL for full per-period dispatch attribution. `elexon · prices & balancing · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Aggregated PN ≈ FUELHH (with rounding/embedded differences); useful sanity check on PN completeness. `elexon · generation · 30 min`
