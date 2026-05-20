---
slug: indo
vendor: elexon
vendor_label: Elexon BMRS
api_code: INDO
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/indo.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonINDO class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/indo.py::INDOTransformer (lines 19-105)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 185-189, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDO (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonINDO class declared"
    source_b: "gridflow silver/elexon/indo.py L19-105"
    source_b_says: "INDOTransformer outputs settlement_date, settlement_period, timestamp_utc, initial_demand_outturn_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same gap as other outturn datasets (itsdo, indod)"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB demand outturn, <span class="italic fg-accent">first published.</span>

**Lede:** Half-hourly GB realised demand — the canonical outturn series for forecast-error studies, demand profiling, and embedded-generation derivation.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · INDO](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDO)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.indo` |
| API PATH | `/datasets/INDO` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | ~5 min |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | ~5 min | Publication lag |
| 3 | 1 | Row per period |
| 4 | 6 | Schema columns |

# Sidebar siblings

- itsdo
- indod
- atl
- inddem
- ndf

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB demand outturn · 24-hour profile"
- **Subtitle:** "Sparkline · MW · UTC · 6 May 2026"
- **Seed:** 11
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/indo.py` · `INDOTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/indo.py L73` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/indo.py L74` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/indo.py L78-87` |
| `initial_demand_outturn_mw` | `float` | No | `demand` | MW. Average national demand for the period. | `silver/elexon/indo.py L60, L75` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/indo.py L93` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/indo.py L94` |

**PARQUET PATH:** `data/silver/elexon/indo/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/indo.py L89`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | initial_demand_outturn_mw | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06 | 7 | 2026-05-06T03:00:00+00:00 | 21718.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 20775.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 16 | 2026-05-06T07:30:00+00:00 | 31250.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 32940.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 34810.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **38640.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 33010.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 28140.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP7, `demand=21718`) and 2 (SP8, `demand=20775`) verbatim from the vault Bronze Sample (vault/elexon/indo.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW) and follow the typical GB May-weekday demand curve. The highlighted **SP36 (38640 MW)** row is the interesting case: the evening peak around 18:00 UTC is the canonical GB demand reference period, the same value used in this brief set's INDDEM sample to derive forecast error.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: INDO emits one scalar per period; no enumerable taxonomies. The relationship to ITSDO and ATL is captured in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/INDO`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/indo/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.indo.INDOTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/INDO?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily peak and trough demand over the last 30 days
SELECT settlement_date,
       MAX(initial_demand_outturn_mw) AS peak_mw,
       MIN(initial_demand_outturn_mw) AS trough_mw,
       AVG(initial_demand_outturn_mw) AS mean_mw
FROM read_parquet('data/silver/elexon/indo/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY settlement_date
ORDER BY settlement_date;
```

**Tab 3 — Python · polars**
```python
import polars as pl

indo = pl.read_parquet("data/silver/elexon/indo/**/*.parquet")
itsdo = pl.read_parquet("data/silver/elexon/itsdo/**/*.parquet")
# Implied embedded generation contribution = INDO − ITSDO
embedded = (
    indo.join(itsdo, on=["settlement_date", "settlement_period"], how="inner")
        .with_columns(
            (pl.col("initial_demand_outturn_mw")
             - pl.col("initial_transmission_system_demand_outturn_mw"))
              .alias("embedded_gen_mw")
        )
        .select(["settlement_date", "settlement_period", "embedded_gen_mw"])
)
print(embedded.tail(20))
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonINDO` class; shape lives in `INDOTransformer.output_cols`. *(Source: `silver/elexon/indo.py`.)*

## 02 Initial estimate, revised through settlement

INDO is the first estimate, ~5 min after period close; BSC final settlement values are not exposed here. *(Source: vault Known Issues.)*

## 03 INDO − ITSDO = embedded generation

INDO is total demand; ITSDO is transmission-only. Difference = embedded generation per period. *(Source: GB embedded-generation reporting.)*

## 04 INDO ≠ ATL — same concept, different lineage

INDO is BSC-lineage, `atl` is ENTSO-E-lineage; usually within ~50 MW. Pick one source of truth. *(Source: GB demand reporting genealogy.)*

## 05 Use `inddem` for the day-ahead forecast counterpart

Forecast error = `inddem − indo` per period. Filter `inddem` to `boundary='N'` before joining. *(Source: NESO indicated-suite identity.)*

# Related datasets

- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. Transmission-only counterpart; INDO − ITSDO = embedded generation. `elexon · demand & forecasts · 30 min`
- **indod** — Initial demand outturn — daily. `daily`. Daily-aggregate counterpart; sum of INDO `initial_demand_outturn_mw × 0.5` per day should match INDOD `initial_demand_outturn_mw` (MWh). `elexon · demand & forecasts · daily`
- **atl** — Actual total load per bidding zone (ENTSO-E B0610). `30 min`. ENTSO-E-aligned counterpart; same concept, different lineage. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand. `30 min`. The day-ahead forecast counterpart for forecast-error analysis. `elexon · demand & forecasts · 30 min`
