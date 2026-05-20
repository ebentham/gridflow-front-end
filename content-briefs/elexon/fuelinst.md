---
slug: fuelinst
vendor: elexon
vendor_label: Elexon BMRS
api_code: FUELINST
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/fuelinst.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonFuelInst class; ElexonGenerationByFuel L61-76 is conceptually close but not used by this transformer)
  - gridflow/src/gridflow/silver/elexon/fuelinst.py::FuelInstTransformer (lines 18-112)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 120-124, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELINST (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "ElexonGenerationByFuel (L61-76) exists with shape (settlement_date, settlement_period, timestamp_utc, fuel_type, generation_mw, data_provider) but no dedicated ElexonFuelInst"
    source_b: "gridflow silver/elexon/fuelinst.py L104-107"
    source_b_says: "FuelInstTransformer drops settlement_date / settlement_period from output entirely; uses timestamp_utc + fuel_type as the row identity"
    orchestrator_recommendation: "trust gridflow — fuelinst is genuinely a 5-minute series, not a half-hour series, so the period concept does not cleanly apply; ElexonGenerationByFuel is shaped for fuelhh-like datasets and not appropriate here"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB generation mix, refreshed <span class="italic fg-accent">every five minutes.</span>

**Lede:** FUELINST is the instantaneous companion to `fuelhh` — the same fuel-type breakdown at ~5-minute resolution rather than half-hourly aggregates. Each row is one fuel category's MW reading at a single `timestamp_utc`. Used for near-real-time stack-and-fuel monitoring; the half-hour aggregates flow into FUELHH downstream.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · FUELINST](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELINST)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.fuelinst` |
| API PATH | `/datasets/FUELINST` |
| FREQUENCY | ~5 min |
| PUBLICATION LAG | ~1 min |
| VOLUME | 8.6M / mo |
| PRIMARY KEY | `(timestamp_utc, fuel_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | ~5 min | Sample interval |
| 2 | ~1 min | Publication lag |
| 3 | 8.6M | Rows / month |
| 4 | 5 | Schema columns |

# Sidebar siblings

- fuelhh
- agpt
- agws
- windfor
- freq

# Overview

1. <code>fuelinst</code> is **Instantaneous Generation Outturn by Fuel Type** — the 5-minute-resolution counterpart to `fuelhh`. Each row reports the MW for one `fuel_type` (CCGT, COAL, NUCLEAR, WIND, SOLAR, BIOMASS, NPSHYD, PS, OCGT, OIL, OTHER, INT*) at one `timestamp_utc`. Silver intentionally drops `settlement_date` and `settlement_period` — the data is sub-period and those columns are no longer the natural row identity.

2. Gridflow fetches it from <code>/datasets/FUELINST</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L120-124</code>). The <code>FuelInstTransformer</code> renames camelCase to snake_case, derives `timestamp_utc` from `publishTime` or `startTime`, and dedups on `(timestamp_utc, fuel_type)`. No Pydantic class is declared — `ElexonGenerationByFuel` is shaped for half-hourly data and is not used here.

3. Cadence is ~5-minute sampling with roughly 1-minute publication lag — the freshest fuel-mix signal in the BMRS feed. Verified against the live API on 2026-05-08. Volume is high (~8.6M rows/month, six times FUELHH). Use for live dashboards and intra-period dispatch tracking; aggregate to half-hourly and compare against `fuelhh` to validate the rollup.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "GB generation mix · 5-minute resolution"
- **Subtitle:** "Stacked area · MW · UTC · last 24h"
- **Seed:** 60
- **Toggles:** `1h` / `24h` (active) / `7d`

# Schema

Defined in `gridflow/silver/elexon/fuelinst.py` · `FuelInstTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month) — derived from `timestamp_utc`. Point-in-time field: `published_at` per intent (column mapping renames it) but transformer does not surface it in output.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `publishTime` / `startTime` (renamed `period_start`) | Sample time. Derived from `publishTime` if present, else from `startTime`. ISO-8601 UTC. | `silver/elexon/fuelinst.py L77-94` |
| `fuel_type` | `str` | No | `fuelType` | Fuel category — uppercase API codes, same vocabulary as `fuelhh`. | `silver/elexon/fuelinst.py L57, L73` |
| `generation_mw` | `float` | No | `generation` | MW. Cast to `Float64`. Can be negative for pumped hydro / interconnectors. | `silver/elexon/fuelinst.py L58, L74` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/fuelinst.py L100` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/fuelinst.py L101` |

**PARQUET PATH:** `data/silver/elexon/fuelinst/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)` — derived from `timestamp_utc`
**DEDUP KEY:** `(timestamp_utc, fuel_type)` (`silver/elexon/fuelinst.py L96`)

# Sample data

| timestamp_utc | fuel_type | generation_mw | data_provider | ingested_at |
|---|---|---|---|---|
| 2026-05-06T03:00:00Z | BIOMASS | 2712.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T03:00:00Z | CCGT | 7527.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T03:00:00Z | NUCLEAR | 4310.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T03:00:00Z | WIND | 9180.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T03:05:00Z | BIOMASS | 2718.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06T03:05:00Z | CCGT | 7544.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06T08:15:00Z** | **CCGT** | **12340.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06T08:15:00Z | WIND | 6420.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (BIOMASS, 2712) and 2 (CCGT, 7527) verbatim from the vault Bronze Sample (vault/elexon/fuelinst.md, live 2026-05-08 for `2026-05-06T02:55:00Z` startTime; transformer derives `timestamp_utc` from `publishTime` which was `2026-05-06T03:00:00Z`). Remaining rows synthesised — respect transformer constraints (`fuel_type` ∈ canonical 16-code list, `generation_mw` as float MW) and represent the ~5-minute cadence advancing through the morning. The highlighted **08:15Z CCGT** row is the interesting case: morning-peak ramp where CCGT dispatch nearly doubles within five hours — exactly the intra-period dispatch detail FUELINST exists to surface that FUELHH (half-hourly aggregate) flattens.

# Dataset-specific section: Fuel types

Same 16 codes as `fuelhh`. See the [fuelhh brief](./fuelhh.md#dataset-specific-section-fuel-types) for the full list. Interconnector codes (`INT*`) can be negative (export) or positive (import); `PS` (pumped storage) is negative when charging.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/fuelinst/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.fuelinst.FuelInstTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELINST?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Mean fuel mix per hour over the last 24h
SELECT date_trunc('hour', timestamp_utc) AS hour,
       fuel_type,
       AVG(generation_mw) AS mean_mw
FROM read_parquet('data/silver/elexon/fuelinst/**/*.parquet')
WHERE timestamp_utc >= now() - INTERVAL 24 HOUR
GROUP BY 1, 2
ORDER BY 1, mean_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/fuelinst/**/*.parquet")
# Rollup to half-hourly to validate against fuelhh
hh = (
    df.with_columns(
        pl.col("timestamp_utc").dt.truncate("30m").alias("settlement_period_utc")
    )
    .group_by(["settlement_period_utc", "fuel_type"])
    .agg(pl.col("generation_mw").mean().alias("mean_mw"))
    .sort(["settlement_period_utc", "fuel_type"])
)
print(hh.head(20))
```

# Caveats

## 01 Silver drops `settlement_date` and `settlement_period`

Unlike `fuelhh`, the silver output of `fuelinst` is `(timestamp_utc, fuel_type, generation_mw, data_provider, ingested_at)` — settlement date and period are intentionally absent. The data is sub-period and the column would lose information (which 5-minute sample of SP8 are we looking at?). Joins to period-keyed datasets need to truncate `timestamp_utc` first. *(Source: vault Implementation Delta; `silver/elexon/fuelinst.py L104-107`.)*

## 02 No Pydantic schema in `schemas/elexon.py`

`schemas/elexon.py` has `ElexonGenerationByFuel` (L61-76) which looks superficially relevant but is shaped for half-hourly data (includes `settlement_date`, `settlement_period`). The fuelinst transformer does NOT use it. Anything that imports `from gridflow.schemas.elexon import ElexonFuelInst` will fail. *(Source: vault Implementation Delta; `schemas/elexon.py` grep returns no `FuelInst` class.)*

## 03 Aggregate carefully when comparing to `fuelhh`

The half-hourly aggregate of `fuelinst` *should* equal `fuelhh` for the same (date, period, fuel) but small differences arise because fuelinst is sampled at irregular ~5-minute intervals while fuelhh uses Elexon's official period-averaging logic. Don't treat them as interchangeable — use fuelhh for settlement-aligned analysis, fuelinst for live monitoring. *(Source: domain knowledge — BMRS fuel-mix data flow.)*

## 04 High volume — 8.6M rows/month

A single month's silver is ~8.6 million rows; a year is ~100M. Partition pruning by year+month is essential. For seasonal-pattern analytics, downsample to hourly first or query `fuelhh` instead. *(Source: vault Known Issues; manifest `rows: "8.6M / mo"`.)*

## 05 `period_start` rename for `startTime`

The transformer renames `startTimeOfHalfHrPeriod` and `startTime` both to `period_start` (internal staging), then derives `timestamp_utc` from `publishTime` preferentially or `period_start` as fallback (`silver/elexon/fuelinst.py L77-94`). Bronze files arriving via different API versions may carry different field names — the transformer absorbs the variation but if you inspect raw bronze be aware of the dual mapping. *(Source: `silver/elexon/fuelinst.py L54-61`.)*

# Related datasets

- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. The settlement-aligned aggregate of fuelinst; use for daily/monthly analytics where period semantics matter. `elexon · generation · 30 min`
- **agpt** — Aggregated generation per PSR type. `30 min`. Provides the onshore/offshore wind split fuelinst (and fuelhh) collapses into a single `WIND` bucket. `elexon · generation · 30 min`
- **freq** — System frequency. `~2 s`. Even-finer-resolution telemetry; correlate frequency dips with fuelinst dispatch changes to attribute response actions. `elexon · system & reference · ~2 s` 
- **windfor** — Wind generation forecast. `hourly`. Compare fuelinst `WIND` actuals against forecast for live nowcast error. `elexon · generation · hourly`
