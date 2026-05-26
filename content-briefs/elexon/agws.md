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

**Lede:** Half-hourly GB wind and solar generation — the canonical renewables-only series for forecast-error analysis, capacity factors, and embedded-solar attribution.

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

1. <code>agws</code> is the half-hourly GB wind and solar generation — the renewables-only B1630 cut, with wind split into onshore and offshore and solar reported separately. It is the canonical source for renewable-only forecast-error analysis, capacity-factor work, and embedded-solar attribution.

2. Gridflow fetches it from <code>/datasets/AGWS</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>AGWSTransformer</code> — same shape as <code>agpt</code> (no Pydantic class) but restricted to wind and solar PSR types.

3. Refreshed every 30 minutes with 1 day publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "Wind onshore + offshore + solar · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Shape:** `series` (3 explicit renewable layers — wind + solar only)
- **Series:** `[{"name":"Wind Onshore","color":"#3b6b4b","shape":"diurnal-wind","params":{"mean":3500,"volatility":1200,"persistence":0.75,"seed":21}}, {"name":"Wind Offshore","color":"#5a8aa6","shape":"diurnal-wind","params":{"mean":5200,"volatility":1500,"persistence":0.78,"seed":22}}, {"name":"Solar","color":"#d4a73a","shape":"diurnal-solar","params":{"peak":3800,"peak_hour":12.5,"half_width":5}}]`
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

No `ElexonAGWS` class; shape lives in `AGWSTransformer.output_cols`. Importing `ElexonAGWS` will fail. *(Source: `silver/elexon/agws.py L104-109`.)*

## 02 `Solar` is an estimate, not a meter

Embedded solar isn't metered at unit level; rows can carry `business_type=Estimated` from NESO's model. Treat as model output, not observation. *(Source: GB embedded-solar framework.)*

## 03 `document_revision` precedence on dedup

ENTSO-E revisions reappear with higher `document_revision`; transformer's `unique(..., keep="last")` keeps last-read, not max-revision. *(Source: `silver/elexon/agws.py L93-96`.)*

## 04 Decimal precision is higher than `fuelhh`

AGWS emits three-decimal floats (`1238.414`); `fuelhh` rounds to integer. Use tolerance when joining. *(Source: vault Bronze Sample.)*

## 05 D+1 lag, not real-time

Published a day after settlement (ENTSO-E revision cycle). Use `windfor` + `fuelinst` for real-time. *(Source: manifest `lag: "1 day"`.)*

# Related datasets

- **agpt** — Aggregated generation per PSR type. `30 min`. The superset of AGWS; includes thermal, nuclear, hydro alongside renewables. `elexon · generation · 30 min`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Coarser fuel grouping; collapses onshore + offshore wind into a single `WIND` bucket. `elexon · generation · 30 min`
- **windfor** — Wind generation forecast. `hourly`. Compute forecast error against AGWS `Wind Onshore` + `Wind Offshore` actuals. `elexon · generation · hourly`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. The real-time companion when D+1 lag is too slow; no PSR split, single `WIND` and `SOLAR` buckets. `elexon · generation · ~5 min`
