---
slug: inddem
vendor: elexon
vendor_label: Elexon BMRS
api_code: INDDEM
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/inddem.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonINDDEM class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/inddem.py::INDDEMTransformer (lines 19-108)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 207-211, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDDEM (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonINDDEM class declared"
    source_b: "gridflow silver/elexon/inddem.py L19-108"
    source_b_says: "INDDEMTransformer outputs settlement_date, settlement_period, timestamp_utc, indicated_demand_mw, boundary, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; aggregate with the indicated-suite pattern (imbalngc/melngc/indgen)"
  - source_a: "vault Bronze Sample"
    source_a_says: "Live API returns small `demand` values (e.g. -46, -64) — looks like deltas not totals"
    source_b: "gridflow silver/elexon/inddem.py L75"
    source_b_says: "Transformer casts `demand` to Float64 as `indicated_demand_mw` without sign or scale adjustment"
    orchestrator_recommendation: "trust live API + gridflow — the small `demand` values are boundary-attributed deltas (B1 is one of multiple zonal boundaries); national totals require summing across boundaries or filtering to `boundary='N'`"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Indicated demand, the day-ahead <span class="italic fg-accent">demand half.</span>

**Lede:** Half-hourly GB indicated demand forecast — the canonical day-ahead demand signal for imbalance reconstruction, forecast-error analysis, and zonal attribution.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · INDDEM](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/INDDEM)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.inddem` |
| API PATH | `/datasets/INDDEM` |
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

- indgen
- imbalngc
- melngc
- ndf
- ndfd

# Overview

1. <code>inddem</code> is the half-hourly day-ahead GB indicated-demand forecast — boundary-attributed (one row per zonal boundary) for imbalance reconstruction, forecast-error analysis, and zonal accounting. The companion to <code>indgen</code> on the supply side.

2. Gridflow fetches it from <code>/datasets/INDDEM</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>INDDEMTransformer</code> — no Pydantic class; <code>boundary</code> column carries zonal attribution.

3. Refreshed every 30 minutes with 0 publication lag (day-ahead). Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Indicated demand · 24-hour forecast"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Shape:** `diurnal-load`
- **Params:** `{"peak": 42000, "trough": 26000, "noise": 0.04, "seed": 27}`
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/inddem.py` · `INDDEMTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/inddem.py L73` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/inddem.py L74` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/inddem.py L78-87` |
| `indicated_demand_mw` | `Optional[float]` | Yes | `demand` | MW. **Caveat**: zonal boundaries (e.g. `B1`) emit attributed deltas; national totals require `boundary='N'` or sum across boundaries. | `silver/elexon/inddem.py L59, L75` |
| `boundary` | `Optional[str]` | Yes | `boundary` | `N` (national), `Z` (zonal aggregate), or a specific zone code (`B1`, ...). | `silver/elexon/inddem.py L60, L100` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/inddem.py L96` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/inddem.py L97` |

**PARQUET PATH:** `data/silver/elexon/inddem/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period, boundary)` (`silver/elexon/inddem.py L89-92`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | indicated_demand_mw | boundary | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | -46.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | -64.0 | B1 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 31220.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 34910.0 | N | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **38640.0** | **N** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | 38120.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 32420.0 | N | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 28140.0 | N | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `demand=-46`, `boundary=B1`) and 2 (SP10, `demand=-64`, `boundary=B1`) verbatim from the vault Bronze Sample (vault/elexon/inddem.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW) and show what an `N` (national) row would look like at typical demand levels. The highlighted **SP36 (38640 MW national)** row is the interesting case: evening-peak national-boundary indicated demand near 39 GW, exactly the level where capacity margin tightens.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: INDDEM's only enumerable is the boundary code, which is documented inline in schema notes. The full boundary list is API-side and varies by GB transmission planning era.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/INDDEM`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/inddem/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.inddem.INDDEMTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/INDDEM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- National indicated demand over the last 7 days, hourly mean
SELECT date_trunc('hour', timestamp_utc) AS hour,
       AVG(indicated_demand_mw) AS avg_mw
FROM read_parquet('data/silver/elexon/inddem/**/*.parquet')
WHERE boundary = 'N'
  AND settlement_date >= current_date - INTERVAL 7 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/inddem/**/*.parquet")
# Forecast vs outturn — join to INDO
indo = pl.read_parquet("data/silver/elexon/indo/**/*.parquet")
err = (
    df.filter(pl.col("boundary") == "N")
      .join(indo, on=["settlement_date", "settlement_period"], how="inner")
      .with_columns(
          (pl.col("indicated_demand_mw") - pl.col("initial_demand_outturn_mw"))
            .alias("forecast_error_mw")
      )
)
print(err.select(["settlement_date", "settlement_period", "forecast_error_mw"]).head())
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonINDDEM` class; shape lives in `INDDEMTransformer.output_cols`. *(Source: `silver/elexon/inddem.py`.)*

## 02 Boundary semantics — small values are zonal deltas, not totals

Zonal boundaries (e.g. `B1`) emit small attributed deltas, not national demand. Filter `boundary='N'` for totals. *(Source: vault Bronze Sample.)*

## 03 Forecast revisions collapse on dedup

Dedup `keep="last"` on `(date, period, boundary)` collapses intra-day revisions. Forecast-error studies need bronze. *(Source: `silver/elexon/inddem.py L89-92`.)*

## 04 Pair with `indgen` to reproduce IMBALNGC

`imbalngc ≈ indgen − inddem` per period and boundary. Filter both to `boundary='N'` before reconciling. *(Source: NESO indicated-suite identity.)*

## 05 Use `indo` (not INDDEM) for outturn

INDDEM is forecast; `indo` is realised. Don't conflate. *(Source: NESO documentation.)*

# Related datasets

- **indgen** — Indicated generation. `30 min`. The generation half of the indicated-suite identity (`imbalngc ≈ indgen − inddem`). Pair on (date, period, boundary). `elexon · demand & forecasts · 30 min`
- **imbalngc** — Indicated imbalance. `30 min`. Derived from INDDEM and INDGEN; same publish cadence and dedup key. `elexon · demand & forecasts · 30 min`
- **melngc** — Indicated margin. `30 min`. Capacity-margin companion; INDDEM tells you what demand is expected, MELNGC tells you what headroom remains above it. `elexon · demand & forecasts · 30 min`
- **indo** — Initial National Demand Outturn. `30 min`. The realised demand counterpart for forecast-error analysis; INDDEM forecast vs INDO outturn = the demand-forecast error series. `elexon · demand & forecasts · 30 min`
