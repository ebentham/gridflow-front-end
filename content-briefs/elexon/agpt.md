---
slug: agpt
vendor: elexon
vendor_label: Elexon BMRS
api_code: AGPT
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/agpt.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonAGPT class declared; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/agpt.py::AGPTTransformer (lines 19-114)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 168-172, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/AGPT (fetched 2026-05-20 — javascript-rendered, no extractable content)
  - https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T01:00Z&format=json (fetched 2026-05-20 — live API, confirmed field names)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonAGPT Pydantic class declared"
    source_b: "gridflow silver/elexon/agpt.py L19-114"
    source_b_says: "AGPTTransformer outputs settlement_date, settlement_period, timestamp_utc, psr_type, generation_mw, business_type, document_id, document_revision, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer as schema source; flag for Phase-7 mini-recon — same shape affects ~23 of 33 Elexon datasets"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB generation per PSR type, the European <span class="italic fg-accent">B1620 view.</span>

**Lede:** Half-hourly GB generation per ENTSO-E PSR type — the canonical source for the onshore/offshore wind split, capacity factors, and pan-European comparability.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · AGPT](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/AGPT)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.agpt` |
| API PATH | `/datasets/AGPT` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 1 day |
| VOLUME | 1.6M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, psr_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 1 day | Publication lag |
| 3 | ~25 | PSR types observed |
| 4 | 10 | Schema columns |

# Sidebar siblings

- fuelhh
- fuelinst
- agws
- windfor
- nonbm

# Overview

1. <code>agpt</code> is the half-hourly GB generation by ENTSO-E Production-Source-of-Resource (PSR) type — the European B1620 cut that splits Wind into onshore and offshore, separates pumped storage from non-pumped hydro, and pulls each fuel into its own row. It is the canonical source for capacity factors and pan-European comparability.

2. Gridflow fetches it from <code>/datasets/AGPT</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>AGPTTransformer</code> — no Pydantic class; shape is enforced by the transformer's <code>output_cols</code> (~25 PSR types per period).

3. Refreshed every 30 minutes with 1 day publication lag. Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "Generation per PSR type · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Shape:** `series` (explicit PSR layers, not the default GB fuel mix)
- **Series:** `[{"name":"Wind Onshore","color":"#3b6b4b","shape":"diurnal-wind","params":{"mean":3500,"volatility":1200,"persistence":0.75,"seed":42}}, {"name":"Wind Offshore","color":"#5a8aa6","shape":"diurnal-wind","params":{"mean":5200,"volatility":1500,"persistence":0.78,"seed":43}}, {"name":"Solar","color":"#d4a73a","shape":"diurnal-solar","params":{"peak":3800,"peak_hour":12.5,"half_width":5}}, {"name":"Biomass","color":"#c9a96e","shape":"flat-baseload","params":{"mean":2200,"noise":0.04}}, {"name":"Pumped Storage","color":"#86627d","shape":"bipolar-flow","params":{"amplitude":900,"period":12,"noise":0.2}}]`
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/agpt.py` · `AGPTTransformer.output_cols` (no dedicated Pydantic class). The silver table is partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field on the API response).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/agpt.py L75-78` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/agpt.py L75-78` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/agpt.py L82-91` |
| `psr_type` | `str` | No | `psrType` | ENTSO-E PSR type code (e.g. "Wind Onshore", "Biomass"). Vendor-managed list. | `silver/elexon/agpt.py L75-79` |
| `generation_mw` | `float` | No | `quantity` | MW. Cast to `Float64`. | `silver/elexon/agpt.py L78` |
| `business_type` | `str` | Yes | `businessType` | ENTSO-E business type (typically "Production"). | `silver/elexon/agpt.py L61` |
| `document_id` | `str` | Yes | `documentId` | ENTSO-E document MRID (e.g. `NGET-EMFIP-AGPT-06476951`). | `silver/elexon/agpt.py L62` |
| `document_revision` | `int` | Yes | `documentRevisionNumber` | Document revision counter; latest revision wins on dedup. | `silver/elexon/agpt.py L63` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/agpt.py L99` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. Useful for pipeline debugging. | `silver/elexon/agpt.py L100` |

**PARQUET PATH:** `data/silver/elexon/agpt/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, psr_type)`

# Sample data

| settlement_date | settlement_period | timestamp_utc | psr_type | generation_mw | business_type | document_id | document_revision | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Biomass | 2974.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Hydro Pumped Storage | 1.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Fossil Gas | 7729.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Nuclear | 4310.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **4** | **2026-05-06T01:30:00+00:00** | **Wind Onshore** | **3210.0** | **Production** | **NGET-EMFIP-AGPT-06476951** | **1** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Wind Offshore | 6010.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Solar | 0.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | Hydro Run-of-river and poundage | 410.0 | Production | NGET-EMFIP-AGPT-06476951 | 1 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Biomass + Hydro Pumped Storage rows verbatim from the vault Bronze Sample (vault/elexon/agpt.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (`generation_mw` float, `psr_type` from ENTSO-E codelist) and mirror the typical SP4 profile for an early-morning May day. The highlighted **Wind Onshore** row is the interesting case: AGPT is the only Elexon endpoint that splits wind by technology — `fuelhh` collapses all 9,220 MW of wind into one `WIND` bucket.

# Dataset-specific section: PSR types

PSR types follow the ENTSO-E A.11 codelist. The Elexon API returns the human-readable label rather than the B-code (e.g. `Fossil Gas` not `B04`). Categories regularly observed in GB AGPT:

- `Fossil Gas` — CCGTs (largest single category)
- `Nuclear`
- `Wind Onshore`
- `Wind Offshore`
- `Solar`
- `Biomass`
- `Hydro Pumped Storage` (negative when charging)
- `Hydro Run-of-river and poundage`
- `Fossil Hard coal` (rare post-2024)
- `Fossil Oil` (emergency reserve)
- `Other`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/AGPT`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/agpt/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.agpt.AGPTTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/AGPT?publishDateTimeFrom=2026-05-01T00:00:00Z&publishDateTimeTo=2026-05-02T00:00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Wind split (onshore vs offshore) over the last 30 days
SELECT settlement_date, settlement_period,
       psr_type, generation_mw
FROM read_parquet('data/silver/elexon/agpt/**/*.parquet')
WHERE psr_type IN ('Wind Onshore', 'Wind Offshore')
  AND settlement_date >= current_date - INTERVAL 30 DAY
ORDER BY settlement_date, settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/agpt/**/*.parquet")
# Pivot PSR-type to columns to compute wind onshore/offshore share
mix = df.pivot(
    index=["settlement_date", "settlement_period"],
    on="psr_type",
    values="generation_mw",
    aggregate_function="sum",
)
print(mix.head())
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonAGPT` class exists; shape lives in `AGPTTransformer.output_cols`. Importing `ElexonAGPT` will fail. *(Source: `silver/elexon/agpt.py L104-109`.)*

## 02 PSR types are human-readable strings, not B-codes

API returns labels like `Wind Onshore`, not `B19`. Joins must be exact and case-sensitive. *(Source: ENTSO-E A.11 codelist.)*

## 03 `document_revision` precedence on dedup

ENTSO-E revisions reappear with higher `document_revision`; transformer's `unique(..., keep="last")` keeps last-read, not max-revision. For bitemporal correctness, dedup on `document_revision desc`. *(Source: `silver/elexon/agpt.py L93-96`.)*

## 04 Hydro Pumped Storage can be negative

`Hydro Pumped Storage` goes negative when charging; naive SUM over `psr_type` misrepresents GB generation. *(Source: GB pumped-hydro sign convention.)*

## 05 D+1 lag, not real-time

Published a day after settlement (ENTSO-E document cycle). Use `fuelinst` or `fuelhh` for fresher views. *(Source: manifest `lag: "1 day"`.)*

# Related datasets

- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Same time grid; coarser fuel groupings (collapses wind into one bucket); useful when the PSR-level split isn't needed. `elexon · generation · 30 min`
- **agws** — Actual or estimated wind & solar generation (B1630). `30 min`. The wind/solar-only sibling to AGPT; includes embedded estimates AGPT excludes. `elexon · generation · 30 min`
- **windfor** — Wind generation forecast. `hourly`. Pair with AGPT (`Wind Onshore` + `Wind Offshore` actuals) to compute forecast error. `elexon · generation · hourly`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. The real-time companion when you need a fresher view; coarser fuel buckets, no D+1 lag. `elexon · generation · ~5 min`
