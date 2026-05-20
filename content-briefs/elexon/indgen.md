---
slug: indgen
vendor: elexon
vendor_label: Elexon BMRS
api_code: INDGEN
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/indgen.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonINDGEN class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/indgen.py::INDGENTransformer (lines 19-108)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 212-216, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDGEN (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonINDGEN class declared"
    source_b: "gridflow silver/elexon/indgen.py L19-108"
    source_b_says: "INDGENTransformer outputs settlement_date, settlement_period, timestamp_utc, indicated_generation_mw, boundary, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; mirrors inddem precisely (only differs in column name)"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Indicated generation, the day-ahead <span class="italic fg-accent">generation half.</span>

**Lede:** Half-hourly GB indicated generation forecast — the canonical day-ahead generation signal for imbalance reconstruction, forecast-error analysis, and zonal attribution.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · INDGEN](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDGEN)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.indgen` |
| API PATH | `/datasets/INDGEN` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, boundary)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 0 | Lag (day-ahead) |
| 3 | N + zonal | Boundary granularities |
| 4 | 7 | Schema columns |

# Sidebar siblings

- inddem
- imbalngc
- melngc
- fou2t14d
- uou2t14d

# Overview

1. <code>indgen</code> is the half-hourly day-ahead GB indicated-generation forecast — boundary-attributed and the supply-side companion to <code>inddem</code>. It is the canonical signal for imbalance reconstruction, forecast-error analysis, and zonal attribution.

2. Gridflow fetches it from <code>/datasets/INDGEN</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>INDGENTransformer</code> — no Pydantic class; mirrors <code>inddem</code> precisely except for the column name.

3. Refreshed every 30 minutes with 0 publication lag (day-ahead). Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Indicated generation · 24-hour forecast"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Shape:** `flat-baseload`
- **Params:** `{"mean": 34000, "noise": 0.08, "seed": 28}`
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/indgen.py` · `INDGENTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/indgen.py L73` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/indgen.py L74` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/indgen.py L78-87` |
| `indicated_generation_mw` | `Optional[float]` | Yes | `generation` | MW. Same boundary semantics as INDDEM — zonal rows are attributed deltas. | `silver/elexon/indgen.py L59, L75` |
| `boundary` | `Optional[str]` | Yes | `boundary` | `N` (national), `Z` (zonal aggregate), or a specific zone code (`B1`, ...). | `silver/elexon/indgen.py L60, L100` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/indgen.py L96` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/indgen.py L97` |

**PARQUET PATH:** `data/silver/elexon/indgen/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, boundary)` (`silver/elexon/indgen.py L89-92`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | indicated_generation_mw | boundary | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 272.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | 261.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 31100.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 35080.0 | N | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **38452.0** | **N** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 37959.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 32448.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 28191.0 | N | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `generation=272`, `boundary=B1`) and 2 (SP10, `generation=261`, `boundary=B1`) verbatim from the vault Bronze Sample (vault/elexon/indgen.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW, boundary string) and represent typical `boundary='N'` national-generation forecasts. The highlighted **SP36 (38452 MW national)** row is the interesting case: pairs with the INDDEM SP36 (38640 MW) row to give an imbalance of ~−188 MWh — matches the IMBALNGC SP36 value in this brief set's sample data.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: INDGEN's only enumerable is the boundary code, documented inline; structurally identical to INDDEM.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/INDGEN`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/indgen/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.indgen.INDGENTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/INDGEN?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Reproduce IMBALNGC from INDGEN − INDDEM (national boundary only)
WITH g AS (
  SELECT settlement_date, settlement_period, indicated_generation_mw
  FROM read_parquet('data/silver/elexon/indgen/**/*.parquet')
  WHERE boundary = 'N'
), d AS (
  SELECT settlement_date, settlement_period, indicated_demand_mw
  FROM read_parquet('data/silver/elexon/inddem/**/*.parquet')
  WHERE boundary = 'N'
)
SELECT g.settlement_date, g.settlement_period,
       g.indicated_generation_mw - d.indicated_demand_mw AS implied_imbalance_mwh
FROM g JOIN d USING (settlement_date, settlement_period)
WHERE g.settlement_date = current_date
ORDER BY g.settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ig = pl.read_parquet("data/silver/elexon/indgen/**/*.parquet").filter(pl.col("boundary") == "N")
id_ = pl.read_parquet("data/silver/elexon/inddem/**/*.parquet").filter(pl.col("boundary") == "N")
joined = (
    ig.join(id_, on=["settlement_date", "settlement_period"], how="inner")
      .with_columns(
          (pl.col("indicated_generation_mw") - pl.col("indicated_demand_mw"))
            .alias("implied_imbalance_mwh")
      )
)
print(joined.tail())
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonINDGEN` class; shape lives in `INDGENTransformer.output_cols`. *(Source: `silver/elexon/indgen.py`.)*

## 02 Boundary semantics — small values are zonal deltas

Zonal boundaries (e.g. `B1`) emit small attributed deltas, not national generation. Filter `boundary='N'` for totals. *(Source: vault Bronze Sample.)*

## 03 Forecast revisions collapse on dedup

Dedup `keep="last"` on `(date, period, boundary)` collapses intra-day revisions. Forecast-error studies need bronze. *(Source: `silver/elexon/indgen.py L89-92`.)*

## 04 The indicated-suite identity

`imbalngc ≈ indgen − inddem` at the same boundary. Failure to reconcile means mixed boundaries or stale data. *(Source: NESO indicated-suite arithmetic.)*

## 05 Outturn counterpart is `fuelhh` or the sum of `agpt`

INDGEN is forecast; `fuelhh` is realised. Forecast error = `indgen − sum(fuelhh)`; exclude `INT*` for GB-internal only. *(Source: GB generation reporting hierarchy.)*

# Related datasets

- **inddem** — Indicated demand. `30 min`. The demand half of the indicated-suite identity; structurally identical. Pair on (date, period, boundary). `elexon · demand & forecasts · 30 min`
- **imbalngc** — Indicated imbalance. `30 min`. INDGEN − INDDEM = IMBALNGC for the same boundary; the published version with the subtraction already done. `elexon · demand & forecasts · 30 min`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Medium-horizon companion; INDGEN is intra-day, FOU2T14D extends 2-14 days. `elexon · demand & forecasts · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. The realised generation outturn for forecast-vs-outturn analysis. `elexon · generation · 30 min`
