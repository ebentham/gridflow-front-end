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

**Lede:** AGPT is Actual Aggregated Generation Per Type — every ENTSO-E PSR (Production-Storage Resource) code's MW output per GB settlement period. It is the GB row of the pan-European generation-transparency feed and the canonical source for splitting wind into onshore versus offshore (a distinction `fuelhh` collapses into one bucket). Refreshed half-hourly with D+1 settlement lag.

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

1. <code>agpt</code> is Elexon's pass-through of the ENTSO-E **B1620 Actual Aggregated Generation Per Type** series for the GB bidding zone. Each row reports realised MW for one <code>psr_type</code> (e.g. <code>Wind Onshore</code>, <code>Wind Offshore</code>, <code>Nuclear</code>, <code>Fossil Gas</code>) in one settlement period — the same shape ENTSO-E exposes through its Transparency Platform, surfaced through Elexon's BMRS gateway.

2. Gridflow fetches it from <code>/datasets/AGPT</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> window pattern (connector entry at <code>connectors/elexon/endpoints.py L168-172</code>). The raw JSON lands in bronze; the <code>AGPTTransformer</code> renames camelCase to snake_case, derives <code>timestamp_utc</code> from the settlement-period pair, and dedups on <code>(settlement_date, settlement_period, psr_type)</code>. No Pydantic class is declared — silver shape is enforced by the transformer's <code>output_cols</code> list.

3. Cadence is half-hourly with roughly D+1 publication lag (ENTSO-E document revision timing). Verified against the live API on 2026-05-08; documents arrive with a <code>document_revision</code> counter and the latest revision wins on dedup. Useful for capacity-factor and emissions analytics that need an onshore/offshore wind split rather than the single <code>WIND</code> bucket in <code>fuelhh</code>.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "Generation per PSR type · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Seed:** 42
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

Unlike `fuelhh` (which has `ElexonFuelHH`) or `system_prices` (`ElexonSystemPrice`), AGPT has no dedicated Pydantic class. The silver-layer shape is defined by `AGPTTransformer.output_cols` in `silver/elexon/agpt.py L104-109`. Anything that imports `from gridflow.schemas.elexon import ElexonAGPT` will fail. *(Source: gridflow Implementation Delta in vault; cross-reference `schemas/elexon.py` grep returns no AGPT class.)*

## 02 PSR types are human-readable strings, not B-codes

The API returns labels like `Wind Onshore` and `Hydro Pumped Storage` rather than the ENTSO-E B-codes (`B19`, `B10`). String comparisons must be exact and case-sensitive. Map to friendly names or B-codes in a gold view rather than mutating the silver column. *(Source: vault Known Issues — "PSR types follow ENTSO-E codelist (B01-B25). Silver preserves codes".)*

## 03 `document_revision` precedence on dedup

Same `(settlement_date, settlement_period, psr_type)` can re-appear with a higher `document_revision` if ENTSO-E revises the document. The transformer's `unique(..., keep="last")` keeps whichever row arrived last in the bronze read — which usually but not always corresponds to the highest revision. For strict bitemporal queries, dedup explicitly on `document_revision desc`. *(Source: vault Known Issues; `silver/elexon/agpt.py L93-96`.)*

## 04 Hydro Pumped Storage can be negative

`generation_mw` for `Hydro Pumped Storage` is negative when the units are charging (consuming grid power) and positive when discharging. Sum-of-PSR ≠ total GB generation if you naïvely add it; either filter to `generation_mw > 0` or net it explicitly. *(Source: domain knowledge — GB pumped hydro convention.)*

## 05 D+1 lag, not real-time

AGPT is published a day after settlement (ENTSO-E document revision cycle). For real-time monitoring use `fuelinst` (~5 min) or `fuelhh` (~5 min lag at SP close). AGPT is the right source for retrospective analysis where the onshore/offshore wind split matters. *(Source: vault frontmatter `last_verified: 2026-05-08`; manifest `lag: "1 day"`.)*

# Related datasets

- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Same time grid; coarser fuel groupings (collapses wind into one bucket); useful when the PSR-level split isn't needed. `elexon · generation · 30 min`
- **agws** — Actual or estimated wind & solar generation (B1630). `30 min`. The wind/solar-only sibling to AGPT; includes embedded estimates AGPT excludes. `elexon · generation · 30 min`
- **windfor** — Wind generation forecast. `hourly`. Pair with AGPT (`Wind Onshore` + `Wind Offshore` actuals) to compute forecast error. `elexon · generation · hourly`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. The real-time companion when you need a fresher view; coarser fuel buckets, no D+1 lag. `elexon · generation · ~5 min`
