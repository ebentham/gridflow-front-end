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

**Lede:** INDGEN is the GB generation component of the NESO indicated-imbalance forecast — the symmetric counterpart to `inddem`. Each row reports the expected generation (MW) for one settlement period, optionally split by boundary. Together with INDDEM it produces IMBALNGC (`imbalngc ≈ indgen − inddem`).

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

1. <code>indgen</code> is **Day and Day-Ahead Indicated Generation** — NESO's forecast of GB generation per settlement period. Each row carries `indicated_generation_mw` and a `boundary` discriminator (`N` for national, zonal codes like `B1`). It is the generation half of the indicated-suite identity (`imbalngc ≈ indgen − inddem`).

2. Gridflow fetches it from <code>/datasets/INDGEN</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L212-216</code>). The <code>INDGENTransformer</code> renames `generation` → `indicated_generation_mw`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period, boundary)`. Structurally identical to `inddem` apart from the column name. No Pydantic class is declared.

3. Cadence is half-hourly publication, zero lag (day-ahead and intra-day). Verified against the live API on 2026-05-08; the live sample returned small `generation=272` and `generation=261` values on `boundary=B1` — these are zonal-attributed contributions, not national totals. National generation forecast appears under `boundary='N'` (when present). Pair with `inddem` to reproduce IMBALNGC and with `fuelhh` for forecast-vs-outturn analysis.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Indicated generation · 24-hour forecast"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Seed:** 28
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

Like the rest of the indicated-suite, INDGEN has no dedicated Pydantic class. Silver shape is defined by `INDGENTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no INDGEN class.)*

## 02 Boundary semantics — small values are zonal deltas

Same as INDDEM: the small `generation` values returned for `boundary=B1` (e.g. 272, 261) are zonal-boundary attributed contributions, not national totals. National generation appears under `boundary='N'`. Filter by boundary before aggregating. *(Source: vault Bronze Sample; matches INDDEM boundary structure.)*

## 03 Forecast revisions collapse on dedup

The transformer dedups on `(settlement_date, settlement_period, boundary)` keeping the latest. Multiple intra-day forecast publishes for the same period are collapsed. For forecast-vs-outturn studies preserving revision history, read bronze. *(Source: vault Known Issues; `silver/elexon/indgen.py L89-92`.)*

## 04 The indicated-suite identity

`imbalngc.indicated_imbalance ≈ indgen.indicated_generation_mw − inddem.indicated_demand_mw` at the same boundary. Useful sanity check — if your INDGEN/INDDEM/IMBALNGC parquets don't reconcile, you've likely mixed boundaries or have stale data in one but not the other. *(Source: domain knowledge — NESO indicated-suite arithmetic.)*

## 05 Outturn counterpart is `fuelhh` or the sum of `agpt`

INDGEN is a forecast. Realised generation comes from `fuelhh` (sum of `generation_mw` across fuels per period). For forecast-error analysis: forecast_error = `indgen.indicated_generation_mw − sum(fuelhh.generation_mw)`. Filter `fuelhh` to exclude interconnector imports if you want pure GB-internal generation. *(Source: domain knowledge — GB generation reporting hierarchy.)*

# Related datasets

- **inddem** — Indicated demand. `30 min`. The demand half of the indicated-suite identity; structurally identical. Pair on (date, period, boundary). `elexon · demand & forecasts · 30 min`
- **imbalngc** — Indicated imbalance. `30 min`. INDGEN − INDDEM = IMBALNGC for the same boundary; the published version with the subtraction already done. `elexon · demand & forecasts · 30 min`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Medium-horizon companion; INDGEN is intra-day, FOU2T14D extends 2-14 days. `elexon · demand & forecasts · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. The realised generation outturn for forecast-vs-outturn analysis. `elexon · generation · 30 min`
