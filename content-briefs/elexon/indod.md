---
slug: indod
vendor: elexon
vendor_label: Elexon BMRS
api_code: INDOD
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/indod.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonINDOD class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/indod.py::INDODTransformer (lines 18-97)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 195-199, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDOD (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonINDOD class declared"
    source_b: "gridflow silver/elexon/indod.py L18-97"
    source_b_says: "INDODTransformer outputs settlement_date, timestamp_utc, initial_demand_outturn_mw, data_provider, ingested_at (no settlement_period)"
    orchestrator_recommendation: "trust silver transformer; INDOD is genuinely daily-only, no settlement_period applicable"
  - source_a: "vault Implementation Delta"
    source_a_says: "INDOD has sparse cadence — empty within 3-hour windows; V1 validation used a 1-day window"
    source_b: "gridflow silver/elexon/indod.py"
    source_b_says: "No special handling for sparseness; the connector just returns whatever the window contains"
    orchestrator_recommendation: "documented — query INDOD with at least a 1-day window or accept empty results within shorter publishing-time slices"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB demand outturn, <span class="italic fg-accent">rolled to days.</span>

**Lede:** Daily GB demand outturn — the canonical aggregate for peak-day comparisons, monthly totals, and year-on-year demand trends.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · INDOD](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDOD)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.indod` |
| API PATH | `/datasets/INDOD` |
| FREQUENCY | daily |
| PUBLICATION LAG | 1 day |
| VOLUME | 30 / mo |
| PRIMARY KEY | `(settlement_date)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 1 day | Publication lag |
| 3 | 30 | Rows / month |
| 4 | 5 | Schema columns |

# Sidebar siblings

- indo
- itsdo
- atl
- ndf
- ndfd

# Sample chart

- **Type:** `barsH`
- **Title:** "Daily GB demand · last 30 days"
- **Subtitle:** "Horizontal bars · MWh · UTC · April 2026"
- **Seed:** 14
- **Toggles:** `30d` (active) / `90d` / `12mo`

# Schema

Defined in `gridflow/silver/elexon/indod.py` · `INDODTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date. Partition key and dedup key. | `silver/elexon/indod.py L70` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Midnight UTC of `settlement_date`. | `silver/elexon/indod.py L75-79` |
| `initial_demand_outturn_mw` | `float` | No | `demand` | **MWh** (despite the column suffix `_mw`). Daily total. | `silver/elexon/indod.py L57, L71` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/indod.py L85` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/indod.py L86` |

**PARQUET PATH:** `data/silver/elexon/indod/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date)` (`silver/elexon/indod.py L81`)

# Sample data

| settlement_date | timestamp_utc | initial_demand_outturn_mw | data_provider | ingested_at |
|---|---|---|---|---|
| **2026-04-01** | **2026-04-01T00:00:00+00:00** | **676741.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-04-02 | 2026-04-02T00:00:00+00:00 | 682310.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-03 | 2026-04-03T00:00:00+00:00 | 691080.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-04 | 2026-04-04T00:00:00+00:00 | 685440.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-05 | 2026-04-05T00:00:00+00:00 | 624110.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-06 | 2026-04-06T00:00:00+00:00 | 612730.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-07 | 2026-04-07T00:00:00+00:00 | 698510.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-04-08 | 2026-04-08T00:00:00+00:00 | 703240.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Row 1 (`settlementDate=2026-04-01`, `demand=676741`) verbatim from the vault Bronze Sample (vault/elexon/indod.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MWh, daily) and follow the typical UK April demand pattern (weekday peaks around 700 GWh, weekends near 620 GWh). The highlighted **2026-04-01** row is the interesting case: it is the only row vendor-verified for this dataset and the anchor for the synthesised week.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: INDOD is a one-column daily time series; no enumerable taxonomies. Daily-vs-half-hourly relationship is captured in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/INDOD`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/indod/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.indod.INDODTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/INDOD?publishDateTimeFrom=2026-04-01T00:00Z&publishDateTimeTo=2026-04-02T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Monthly demand totals over the last 12 months
SELECT date_trunc('month', settlement_date) AS month,
       SUM(initial_demand_outturn_mw) AS monthly_mwh,
       AVG(initial_demand_outturn_mw) AS avg_daily_mwh
FROM read_parquet('data/silver/elexon/indod/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 12 MONTH
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

indod = pl.read_parquet("data/silver/elexon/indod/**/*.parquet")
# Year-on-year change in daily demand
yoy = (
    indod.with_columns([
        pl.col("settlement_date").dt.year().alias("year"),
        pl.col("settlement_date").dt.ordinal_day().alias("doy"),
    ])
    .pivot(index="doy", on="year", values="initial_demand_outturn_mw")
)
print(yoy.tail(10))
```

# Caveats

## 01 No Pydantic schema; daily dedup key

Dedup on `settlement_date` only; no `settlement_period` column. Joins to half-hourly data must aggregate the HH side first. *(Source: `silver/elexon/indod.py L81`.)*

## 02 `initial_demand_outturn_mw` is in MWh, not MW

Column suffix is `_mw` for consistency but value is daily MWh. Don't multiply by 0.5. *(Source: vault Bronze Sample.)*

## 03 Sparse cadence — use ≥1-day windows

Sub-day publish windows often return zero rows. Use 1-day minimum. *(Source: vault Implementation Delta.)*

## 04 INDOD ≈ sum of INDO × 0.5

Daily INDOD should equal `SUM(indo) × 0.5` for the date; >few-hundred MWh discrepancy signals data issue. *(Source: BSC settlement arithmetic.)*

## 05 Initial estimate, not final reconciled

INDOD is D+1 initial; BSC final-settlement values are not exposed. *(Source: vault Overview.)*

# Related datasets

- **indo** — Initial National Demand Outturn (half-hourly). `30 min`. The per-period source dataset that INDOD aggregates. `elexon · demand & forecasts · 30 min`
- **itsdo** — Initial Transmission System Demand Outturn. `30 min`. Sum to derive a daily transmission-only total parallel to INDOD. `elexon · demand & forecasts · 30 min`
- **atl** — Actual total load per bidding zone (ENTSO-E B0610). `30 min`. Sum to compare against INDOD as a sanity check on the two demand-reporting lineages. `elexon · demand & forecasts · 30 min`
- **ndf** — National demand forecast (day-ahead). `daily`. Daily-resolution forecast equivalent; subtract INDOD to compute annual forecast-accuracy stats. `elexon · demand & forecasts · daily`
