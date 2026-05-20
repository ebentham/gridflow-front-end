---
slug: agws
vendor: elexon
vendor_label: Elexon BMRS
api_code: AGWS
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/agws.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonAGWS class declared; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/agws.py::AGWSTransformer (lines 19-114)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 173-177, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/AGWS (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonAGWS Pydantic class declared"
    source_b: "gridflow silver/elexon/agws.py L19-114"
    source_b_says: "AGWSTransformer outputs settlement_date, settlement_period, timestamp_utc, psr_type, generation_mw, business_type, document_id, document_revision, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer as schema source; same shape as agpt — both are B-series ENTSO-E pass-throughs without Pydantic"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB renewables, the <span class="italic fg-accent">B1630 cut.</span>

**Lede:** AGWS is Actual or Estimated Wind and Solar Power Generation — the same ENTSO-E PSR taxonomy as `agpt` but filtered to renewable categories (`Wind Onshore`, `Wind Offshore`, `Solar`). Where AGPT covers all PSR types, AGWS isolates the renewables of analytic interest and folds in `Estimated` values where metered data is unavailable (notably for embedded solar). Refreshed half-hourly with D+1 lag.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · AGWS](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/AGWS)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.agws` |
| API PATH | `/datasets/AGWS` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 1 day |
| VOLUME | 0.4M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, psr_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 1 day | Publication lag |
| 3 | 3 | PSR types (wind/solar) |
| 4 | 10 | Schema columns |

# Sidebar siblings

- agpt
- fuelhh
- windfor
- fuelinst
- nonbm

# Overview

1. <code>agws</code> is Elexon's pass-through of the ENTSO-E **B1630 Actual or Estimated Wind and Solar Power Generation** series for the GB bidding zone. Each row reports MW for one renewable <code>psr_type</code> (<code>Wind Onshore</code>, <code>Wind Offshore</code>, <code>Solar</code>) per settlement period. `businessType` of <code>Wind generation</code> or <code>Solar generation</code> marks metered values; values for embedded solar can carry an `Estimated` business type.

2. Gridflow fetches it from <code>/datasets/AGWS</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> window pattern (connector entry at <code>connectors/elexon/endpoints.py L173-177</code>). The <code>AGWSTransformer</code> mirrors <code>AGPTTransformer</code> field-for-field — same renames, same dedup key <code>(settlement_date, settlement_period, psr_type)</code>, same `output_cols`. No Pydantic class is declared.

3. Cadence is half-hourly with roughly D+1 publication lag (ENTSO-E document revision cycle). Verified against the live API on 2026-05-08; output volume is roughly a quarter of AGPT's because only renewable PSR types are emitted. Pair with <code>fuelhh</code> (single <code>WIND</code> bucket) when you need totals; pair with <code>agpt</code> when you need the embedded-solar `Estimated` flag explicitly.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "Wind onshore + offshore + solar · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Seed:** 21
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/agws.py` · `AGWSTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field on the API response).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/agws.py L75-78` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/agws.py L75-78` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/agws.py L82-91` |
| `psr_type` | `str` | No | `psrType` | One of `Wind Onshore`, `Wind Offshore`, `Solar`. Vendor-managed list. | `silver/elexon/agws.py L75-79` |
| `generation_mw` | `float` | No | `quantity` | MW. Decimal precision higher than `fuelhh` (e.g. `1238.414`). | `silver/elexon/agws.py L78` |
| `business_type` | `str` | Yes | `businessType` | `Wind generation` / `Solar generation`, occasionally `Estimated`. | `silver/elexon/agws.py L61` |
| `document_id` | `str` | Yes | `documentId` | ENTSO-E document MRID (e.g. `NGET-EMFIP-AGWS-20861078`). | `silver/elexon/agws.py L62` |
| `document_revision` | `int` | Yes | `documentRevisionNumber` | Document revision counter. | `silver/elexon/agws.py L63` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/agws.py L100` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/agws.py L101` |

**PARQUET PATH:** `data/silver/elexon/agws/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, psr_type)`

# Sample data

| settlement_date | settlement_period | timestamp_utc | psr_type | generation_mw | business_type | document_id | document_revision | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Wind Onshore | 1238.414 | Wind generation | NGET-EMFIP-AGWS-20861078 | 1 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **4** | **2026-05-06T01:30:00+00:00** | **Wind Offshore** | **4153.834** | **Wind generation** | **NGET-EMFIP-AGWS-20861078** | **1** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Solar | 0.0 | Solar generation | NGET-EMFIP-AGWS-20861078 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | Wind Onshore | 1102.310 | Wind generation | NGET-EMFIP-AGWS-20861084 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | Wind Offshore | 3902.117 | Wind generation | NGET-EMFIP-AGWS-20861084 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | Solar | 7480.500 | Solar generation | NGET-EMFIP-AGWS-20861084 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | Wind Onshore | 980.220 | Wind generation | NGET-EMFIP-AGWS-20861090 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | Solar | 1220.880 | Solar generation | NGET-EMFIP-AGWS-20861090 | 1 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Wind Onshore + Wind Offshore SP4 rows verbatim from the vault Bronze Sample (vault/elexon/agws.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (`psr_type` ∈ Wind/Solar codelist) and reproduce the typical solar peak at SP24 (noon). The highlighted **Wind Offshore SP4** row is the interesting case: offshore alone is contributing 4 GW pre-dawn, three times onshore, which matches the GB capacity ratio.

# Dataset-specific section: omitted

`dataset_specific_section: omitted` — AGWS's PSR list is short (3 codes); a pill-grid would add no information beyond what the schema row notes already convey.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/AGWS`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/agws/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.agws.AGWSTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/AGWS?publishDateTimeFrom=2026-05-01T00:00:00Z&publishDateTimeTo=2026-05-02T00:00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily wind onshore vs offshore totals
SELECT settlement_date,
       SUM(CASE WHEN psr_type = 'Wind Onshore'  THEN generation_mw END) AS onshore_mwh,
       SUM(CASE WHEN psr_type = 'Wind Offshore' THEN generation_mw END) AS offshore_mwh
FROM read_parquet('data/silver/elexon/agws/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY settlement_date
ORDER BY settlement_date;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/agws/**/*.parquet")
# Wind capacity-factor proxy: GB onshore vs offshore
wind = (
    df.filter(pl.col("psr_type").str.starts_with("Wind"))
      .group_by("psr_type")
      .agg(pl.col("generation_mw").mean().alias("avg_mw"))
)
print(wind)
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

Like `agpt`, AGWS has no dedicated Pydantic class. The silver-layer shape is defined by `AGWSTransformer.output_cols` in `silver/elexon/agws.py L104-109`. Anything that imports `from gridflow.schemas.elexon import ElexonAGWS` will fail. *(Source: gridflow Implementation Delta; cross-reference `schemas/elexon.py` grep returns no AGWS class.)*

## 02 `Solar` is an estimate, not a meter

Embedded solar is not metered at the unit level; AGWS uses NESO's embedded-solar estimate model. Expect `business_type` of `Estimated` on some Solar rows — treat these as model output, not observation. *(Source: domain knowledge — GB solar is dominated by sub-1 MW embedded sites; NESO publishes the estimation methodology.)*

## 03 `document_revision` precedence on dedup

Same `(settlement_date, settlement_period, psr_type)` can re-appear with a higher `document_revision` if ENTSO-E revises the document. The transformer's `unique(..., keep="last")` keeps whichever row arrived last in the bronze read. For strict bitemporal queries, dedup explicitly on `document_revision desc`. *(Source: `silver/elexon/agws.py L93-96`; same caveat as agpt.)*

## 04 Decimal precision is higher than `fuelhh`

AGWS reports values to three decimal places (`1238.414`) where `fuelhh` rounds to integer. Float comparisons across the two datasets will not be exact; use a tolerance or round consistently before joining. *(Source: vault Bronze Sample inspection.)*

## 05 D+1 lag, not real-time

AGWS is published a day after settlement (ENTSO-E revision cycle). For live wind monitoring use `windfor` (forecast) + `fuelinst` (real-time metered). AGWS is for retrospective wind/solar attribution and forecast-error analysis. *(Source: vault frontmatter `last_verified: 2026-05-08`; manifest `lag: "1 day"`.)*

# Related datasets

- **agpt** — Aggregated generation per PSR type. `30 min`. The superset of AGWS; includes thermal, nuclear, hydro alongside renewables. `elexon · generation · 30 min`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Coarser fuel grouping; collapses onshore + offshore wind into a single `WIND` bucket. `elexon · generation · 30 min`
- **windfor** — Wind generation forecast. `hourly`. Compute forecast error against AGWS `Wind Onshore` + `Wind Offshore` actuals. `elexon · generation · hourly`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. The real-time companion when D+1 lag is too slow; no PSR split, single `WIND` and `SOLAR` buckets. `elexon · generation · ~5 min`
