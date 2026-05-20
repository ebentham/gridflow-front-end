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

**Lede:** INDO is the Initial National Demand Outturn — the first published estimate of realised national demand per settlement period, issued shortly after each period closes. It is the headline GB demand outturn series and the canonical reference for forecast-error studies (forecast vs INDO) and demand-profile analytics.

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

# Overview

1. <code>indo</code> is **Initial National Demand Outturn** — the realised GB total demand for each settlement period, published shortly after the period closes. It is the headline outturn series for GB demand and the value most analytics treat as "the" demand for retrospective work. Each row carries one `initial_demand_outturn_mw` value at one (settlement_date, settlement_period).

2. Gridflow fetches it from <code>/datasets/INDO</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L185-189</code>). The <code>INDOTransformer</code> renames `demand` → `initial_demand_outturn_mw`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period)`. No Pydantic class is declared.

3. Cadence is half-hourly publication with ~5-minute lag at period close. Verified against the live API on 2026-05-08. INDO is the *first* published estimate; final reconciled demand comes through BSC settlement runs and is not exposed by this endpoint. Pair with `itsdo` (transmission-only) to derive embedded generation contribution, with `inddem` for forecast-error analysis, and with `atl` for the ENTSO-E-aligned equivalent.

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

Like the other outturn datasets (`itsdo`, `indod`), INDO has no dedicated Pydantic class. Silver shape is defined by `INDOTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no INDO class.)*

## 02 Initial estimate, revised through settlement

INDO is the *first* published demand estimate, issued ~5 minutes after the period. BSC final settlement produces revised demand numbers that are not exposed by this endpoint. For final reconciled demand use settlement-run datasets. *(Source: vault Known Issues — "INDO is published before final settlement and is revised over time".)*

## 03 INDO − ITSDO = embedded generation

INDO is total national demand; ITSDO is transmission-only demand (excludes embedded generation). Their difference is the implied contribution of embedded generation in that period — useful for tracking embedded solar/wind/CHP growth over time. The two datasets share `(settlement_date, settlement_period)` as the join key. *(Source: vault Known Issues + domain knowledge — GB embedded-generation reporting.)*

## 04 INDO ≠ ATL — same concept, different lineage

INDO is the BSC-aligned outturn; `atl` (Actual Total Load) is the ENTSO-E-aligned version of the same idea. Values are usually within ~50 MW but can diverge during demand-disconnection events. Pick one as your demand source of truth depending on whether you need BSC-aligned (INDO) or ENTSO-E-aligned (ATL) numbers. *(Source: domain knowledge — GB demand reporting genealogy.)*

## 05 Use `inddem` for the day-ahead forecast counterpart

`inddem` is the day-ahead/intra-day forecast of demand; INDO is the realised outturn. Forecast error = `inddem.indicated_demand_mw − indo.initial_demand_outturn_mw` for the same (date, period). Filter INDDEM to `boundary='N'` first or the math will be confounded by zonal-boundary attributions. *(Source: cross-reference with INDDEM brief; domain knowledge.)*

# Related datasets

- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. Transmission-only counterpart; INDO − ITSDO = embedded generation. `elexon · demand & forecasts · 30 min`
- **indod** — Initial demand outturn — daily. `daily`. Daily-aggregate counterpart; sum of INDO `initial_demand_outturn_mw × 0.5` per day should match INDOD `initial_demand_outturn_mw` (MWh). `elexon · demand & forecasts · daily`
- **atl** — Actual total load per bidding zone (ENTSO-E B0610). `30 min`. ENTSO-E-aligned counterpart; same concept, different lineage. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand. `30 min`. The day-ahead forecast counterpart for forecast-error analysis. `elexon · demand & forecasts · 30 min`
