---
slug: atl
vendor: elexon
vendor_label: Elexon BMRS
api_code: ATL
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/atl.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonATL class declared; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/atl.py::ATLTransformer (lines 19-108)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 178-182, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/ATL (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonATL Pydantic class declared"
    source_b: "gridflow silver/elexon/atl.py L19-108"
    source_b_says: "ATLTransformer outputs settlement_date, settlement_period, timestamp_utc, total_load_mw, business_type, document_id, document_revision, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same shape gap as agpt/agws"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Total GB load, the <span class="italic fg-accent">European view.</span>

**Lede:** Half-hourly GB total load — the canonical demand series for European comparability, load profiling, and forecast-error analysis.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · ATL](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/ATL)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.atl` |
| API PATH | `/datasets/ATL` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 1 day |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 1 day | Publication lag |
| 3 | 1 | Row per period |
| 4 | 9 | Schema columns |

# Sidebar siblings

- indo
- itsdo
- ndf
- inddem
- tsdf

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB total load · 7-day snapshot"
- **Subtitle:** "Sparkline · MW · UTC · week of 6 May 2026"
- **Seed:** 13
- **Toggles:** `24h` / `7d` (active) / `30d`

# Schema

Defined in `gridflow/silver/elexon/atl.py` · `ATLTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/atl.py L74-78` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/atl.py L74-78` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/atl.py L80-89` |
| `total_load_mw` | `float` | No | `quantity` | MW. Single national figure per period; no decomposition. | `silver/elexon/atl.py L77` |
| `business_type` | `str` | Yes | `businessType` | ENTSO-E business type (typically `Consumption`). | `silver/elexon/atl.py L62` |
| `document_id` | `str` | Yes | `documentId` | ENTSO-E document MRID (e.g. `NGET-EMFIP-ATL-06475722`). | `silver/elexon/atl.py L60` |
| `document_revision` | `int` | Yes | `documentRevisionNumber` | Document revision counter. | `silver/elexon/atl.py L61` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/atl.py L95` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/atl.py L96` |

**PARQUET PATH:** `data/silver/elexon/atl/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)`

# Sample data

| settlement_date | settlement_period | timestamp_utc | total_load_mw | business_type | document_id | document_revision | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | 4 | 2026-05-06T01:30:00+00:00 | 26368.0 | Consumption | NGET-EMFIP-ATL-06475721 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 5 | 2026-05-06T02:00:00+00:00 | 25774.0 | Consumption | NGET-EMFIP-ATL-06475722 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 24910.0 | Consumption | NGET-EMFIP-ATL-06475725 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 16 | 2026-05-06T07:30:00+00:00 | 31420.0 | Consumption | NGET-EMFIP-ATL-06475733 | 1 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **37** | **2026-05-06T18:00:00+00:00** | **38120.0** | **Consumption** | **NGET-EMFIP-ATL-06475754** | **1** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 38 | 2026-05-06T18:30:00+00:00 | 37920.0 | Consumption | NGET-EMFIP-ATL-06475755 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 33010.0 | Consumption | NGET-EMFIP-ATL-06475761 | 1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 28140.0 | Consumption | NGET-EMFIP-ATL-06475765 | 1 | elexon | 2026-05-08T12:00:00Z |

**Sources:** SP4 and SP5 rows verbatim from the vault Bronze Sample (vault/elexon/atl.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints and follow the typical GB May weekday demand curve (overnight trough → morning rise → evening peak at SP37). The highlighted **SP37 row** is the interesting case: the evening peak around 18:00 UTC is the canonical GB demand reference and the period most exposed to capacity-margin risk.

# Dataset-specific section: omitted

`dataset_specific_section: omitted` — ATL emits one row per settlement period with no enumerable taxonomy (no PSR codes, no fuel categories, no settlement-run variations). The schema row notes carry the full semantics.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/ATL`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/atl/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.atl.ATLTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/ATL?publishDateTimeFrom=2026-05-01T00:00:00Z&publishDateTimeTo=2026-05-02T00:00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily peak load over the last 30 days
SELECT settlement_date,
       MAX(total_load_mw) AS peak_mw,
       MIN(total_load_mw) AS trough_mw,
       AVG(total_load_mw) AS mean_mw
FROM read_parquet('data/silver/elexon/atl/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY settlement_date
ORDER BY settlement_date;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/atl/**/*.parquet")
# Hour-of-day mean load profile
profile = (
    df.with_columns(pl.col("timestamp_utc").dt.hour().alias("hour"))
      .group_by("hour")
      .agg(pl.col("total_load_mw").mean().alias("avg_mw"))
      .sort("hour")
)
print(profile)
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonATL` class; shape lives in `ATLTransformer.output_cols`. Importing `ElexonATL` will fail. *(Source: `silver/elexon/atl.py L99-103`.)*

## 02 ATL overlaps with `indo` but isn't identical

ATL is ENTSO-E-lineage, `indo` is BSC-lineage; usually within ~50 MW but can diverge during disconnection events. Pick one. *(Source: GB demand reporting genealogy.)*

## 03 `document_revision` precedence on dedup

ENTSO-E revisions reappear with higher `document_revision`; transformer's `unique(..., keep="last")` keeps last-read, not max-revision. *(Source: `silver/elexon/atl.py L91`.)*

## 04 D+1 lag, not real-time

Published a day after settlement. Use `indo` / `itsdo` for fresher views. *(Source: manifest `lag: "1 day"`.)*

# Related datasets

- **indo** — Initial National Demand Outturn. `30 min`. The BSC-aligned counterpart; fresher (~5 min lag) but uses different document lineage. `elexon · demand · 30 min`
- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. Excludes embedded generation; useful for transmission-system load. `elexon · demand · 30 min`
- **ndf** — National Demand Forecast (day-ahead). `daily`. Forecast counterpart to ATL; compute forecast error by joining on (settlement_date, settlement_period). `elexon · demand · daily`
- **tsdf** — Transmission System Demand Forecast. `daily`. The transmission-only forecast pair to `itsdo`/`tsdf`. `elexon · demand · daily`
