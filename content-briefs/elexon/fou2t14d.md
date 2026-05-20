---
slug: fou2t14d
vendor: elexon
vendor_label: Elexon BMRS
api_code: FOU2T14D
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/fou2t14d.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonFOU2T14D class declared; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/fou2t14d.py::FOU2T14DTransformer (lines 19-134, APPEND_ONLY=True)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 145-149, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FOU2T14D (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonFOU2T14D Pydantic class declared"
    source_b: "gridflow silver/elexon/fou2t14d.py L19-134"
    source_b_says: "FOU2T14DTransformer outputs settlement_date, settlement_period, timestamp_utc, fuel_type, output_usable_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same gap as agpt/agws/atl"
  - source_a: "vault Silver schema lists `settlement_period` as required (Nullable=No)"
    source_a_says: "settlement_period present in silver"
    source_b: "gridflow silver/elexon/fou2t14d.py L93-117"
    source_b_says: "settlement_period is conditionally included only when present in bronze; forecast-only payloads use settlement_date alone with midnight UTC timestamp"
    orchestrator_recommendation: "trust gridflow — silver schema documentation should mark settlement_period nullable; forecast horizon is daily, not half-hourly"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** 2-14 days ahead, fuel by fuel, <span class="italic fg-accent">availability declared.</span>

**Lede:** FOU2T14D is the 2-14 day-ahead generation-availability forecast aggregated by fuel type. Issued daily, each row reports the usable MW for a future delivery date split by fuel category — what plant operators say they will offer over the next fortnight. Used for medium-term margin and capacity-factor projections.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · FOU2T14D](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FOU2T14D)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.fou2t14d` |
| API PATH | `/datasets/FOU2T14D` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 |
| VOLUME | 440k / mo |
| PRIMARY KEY | `(settlement_date, fuel_type)` (when no `settlement_period`) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 12 | Forecast horizon (days) |
| 3 | append-only | Silver write mode |
| 4 | 7 | Schema columns |

# Sidebar siblings

- uou2t14d
- tsdf
- tsdfd
- ndf
- ndfd

# Overview

1. <code>fou2t14d</code> is **2-14 Day Ahead Generation Availability by Fuel Type** — a forward-looking declaration aggregated to fuel category (CCGT, NUCLEAR, WIND, BIOMASS, ...). Each row carries `output_usable_mw` — the MW each fuel category says it will be able to offer — for a future `settlement_date`. Note the silver `settlement_date` is the *forecast delivery date* (2-14 days ahead), not the publish date.

2. Gridflow fetches it from <code>/datasets/FOU2T14D</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L145-149</code>). The <code>FOU2T14DTransformer</code> renames `forecastDate` → `settlement_date`, dedups on `(settlement_date[, settlement_period], fuel_type)`, and writes **append-only** silver files (`APPEND_ONLY=True`, `silver/elexon/fou2t14d.py L35`) — each daily run produces a run-suffixed parquet so revised forecasts coexist with prior runs.

3. Cadence is daily publication with 0 lag (forecast is future-looking). Verified against the live API on 2026-05-08. The append-only silver layout means downstream consumers must select the latest run per `(event_time, fuel_type)` at read time. Used for medium-term margin (vs `melngc`), capacity-factor projections, and fuel-mix forward forecasting.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "2-14 day availability by fuel · forward snapshot"
- **Subtitle:** "Stacked area · MW · forecast delivery date · published 6 May 2026"
- **Seed:** 33
- **Toggles:** `14d` (active) / `7d` / `2d`

# Schema

Defined in `gridflow/silver/elexon/fou2t14d.py` · `FOU2T14DTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at` (no native PIT field — but see append-only `available_at` per ADR-019). Write mode: **append-only** (each run leaves prior parquet files in place).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` / `forecastDate` | **The forecast delivery date** (2-14 days ahead), not the publish date. Partition key. | `silver/elexon/fou2t14d.py L69-71` |
| `settlement_period` | `Optional[int]` | Yes | `settlementPeriod` | 1..50 when present. Many FOU2T14D rows are daily-aggregate and omit the period — silver leaves the column out for those runs. | `silver/elexon/fou2t14d.py L93-117` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | If `settlement_period` present: derived via `utils/time.settlement_period_to_utc`. Else: midnight UTC of `settlement_date`. | `silver/elexon/fou2t14d.py L96-113` |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, NUCLEAR, WIND, BIOMASS, ...). Vendor-managed list, same vocab as `fuelhh`. | `silver/elexon/fou2t14d.py L74` |
| `output_usable_mw` | `float` | No | `outputUsable` | MW. Cast to `Float64`. Declared usable output, not realised generation. | `silver/elexon/fou2t14d.py L75, L90` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/fou2t14d.py L122` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. Under `--reingest` this diverges from `available_at` (BaseSilverTransformer). | `silver/elexon/fou2t14d.py L123` |

**PARQUET PATH:** `data/silver/elexon/fou2t14d/year=YYYY/month=MM/fou2t14d_YYYYMMDD_run<available_at>.parquet` (run-suffixed; append-only)
**PARTITION BY:** `settlement_date (year + month)` (forecast delivery date)
**DEDUP KEY:** `(settlement_date, [settlement_period,] fuel_type)` (per-run dedup; latest-revision selection is read-time)

# Sample data

| settlement_date | timestamp_utc | fuel_type | output_usable_mw | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | BIOMASS | 2931.0 | elexon | 2026-05-08T03:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | CCGT | 22274.0 | elexon | 2026-05-08T03:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | NUCLEAR | 4810.0 | elexon | 2026-05-08T03:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | WIND | 12440.0 | elexon | 2026-05-08T03:00:00Z |
| **2026-05-15** | **2026-05-15T00:00:00+00:00** | **CCGT** | **24120.0** | **elexon** | **2026-05-08T03:00:00Z** |
| 2026-05-15 | 2026-05-15T00:00:00+00:00 | NUCLEAR | 4810.0 | elexon | 2026-05-08T03:00:00Z |
| 2026-05-15 | 2026-05-15T00:00:00+00:00 | WIND | 13800.0 | elexon | 2026-05-08T03:00:00Z |
| 2026-05-19 | 2026-05-19T00:00:00+00:00 | CCGT | 19840.0 | elexon | 2026-05-08T03:00:00Z |

**Sources:** Rows 1 (BIOMASS) and 2 (CCGT) for forecast date 2026-05-08 verbatim from the vault Bronze Sample (vault/elexon/fou2t14d.md, live 2026-05-08; `outputUsable` 2931 and 22274 respectively). Remaining rows synthesised — respect transformer constraints (`output_usable_mw` as float MW) and represent a typical forward declaration spanning the 2-14 day horizon. The highlighted **2026-05-15 CCGT** row is the interesting case: the CCGT declaration *rises* into the second week (24120 vs 22274) as planned-outage units return — exactly the dispatch-planning signal this dataset exists to surface.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: the fuel codelist mirrors fuelhh's; surfacing it would duplicate. The interesting structure is the append-only run lineage, documented in schema notes.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/FOU2T14D`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/fou2t14d/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.fou2t14d.FOU2T14DTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/FOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Latest-revision forward availability by fuel and delivery date
-- (manual latest-run selection; append-only silver requires it)
SELECT settlement_date, fuel_type, output_usable_mw
FROM (
  SELECT settlement_date, fuel_type, output_usable_mw, ingested_at,
         ROW_NUMBER() OVER (
           PARTITION BY settlement_date, fuel_type
           ORDER BY ingested_at DESC
         ) AS rn
  FROM read_parquet('data/silver/elexon/fou2t14d/**/*.parquet')
)
WHERE rn = 1
  AND settlement_date BETWEEN current_date AND current_date + INTERVAL 14 DAY
ORDER BY settlement_date, fuel_type;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/fou2t14d/**/*.parquet")
# Latest-revision selection per (settlement_date, fuel_type)
latest = (
    df.sort("ingested_at", descending=True)
      .group_by(["settlement_date", "fuel_type"])
      .first()
      .sort(["settlement_date", "fuel_type"])
)
print(latest.head(20))
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

Like `agpt`/`agws`/`atl`, FOU2T14D has no dedicated Pydantic class. The silver-layer shape is defined by `FOU2T14DTransformer.output_cols` in `silver/elexon/fou2t14d.py L126-129`. Anything that imports `from gridflow.schemas.elexon import ElexonFOU2T14D` will fail. *(Source: gridflow Implementation Delta; `schemas/elexon.py` grep returns no FOU2T14D class.)*

## 02 `settlement_date` is the forecast delivery date, not the publish date

The silver `settlement_date` column is the *future* date being forecast (2 to 14 days ahead of `published_at`). Don't filter `settlement_date >= current_date - INTERVAL 30 DAY` expecting "recent publishes" — that returns recent *deliveries*, which include forecasts published up to two weeks earlier. Use `ingested_at` or `published_at` to filter by publish time. *(Source: vault Known Issues; `silver/elexon/fou2t14d.py L71` — `forecastDate` is aliased to `settlement_date`.)*

## 03 Append-only silver: latest revision is a read-time concern

The transformer sets `APPEND_ONLY=True` (`silver/elexon/fou2t14d.py L35`) — each daily run leaves prior parquet files in place. The same `(settlement_date, fuel_type)` can therefore appear in multiple files with different `output_usable_mw` values across forecast revisions. Latest-revision selection is the consumer's job — see the SQL example for the canonical pattern. Reference: ADR-019 in the gridflow_models repo. *(Source: docstring at `silver/elexon/fou2t14d.py L20-31`.)*

## 04 `settlement_period` is sometimes absent

The transformer conditionally includes `settlement_period` only when present in bronze (`silver/elexon/fou2t14d.py L93-117`). Daily-aggregate forecast runs omit it; period-resolution runs (rarer) include it. Defensive consumers should `COALESCE(settlement_period, 0)` or filter `WHERE settlement_period IS NOT NULL` when joining to period-resolution datasets. *(Source: code at L93-117; bronze sample on 2026-05-08 carried `forecastDate` but no `settlementPeriod`.)*

## 05 `output_usable_mw` is declared, not realised

This is a forward-looking declaration — what the plant operators say they will be able to offer, not what they end up generating. Compare against `fuelhh` (realised generation by fuel) to derive forecast error. Sustained over-declaration is a regulatory signal (overstated availability inflates the market's perceived margin). *(Source: domain knowledge — BSC Section Q forecasting framework.)*

# Related datasets

- **uou2t14d** — 2-14 day availability by BM unit. `daily`. The unit-resolved counterpart; FOU2T14D aggregates these by fuel. Use `uou2t14d` when you need per-BMU attribution. `elexon · demand & forecasts · daily`
- **tsdfd** — 2-14 day transmission demand forecast. `daily`. Pairs with FOU2T14D to compute forward margin (availability minus demand) over the same horizon. `elexon · demand & forecasts · daily`
- **melngc** — Indicated margin (day & day-ahead). `30 min`. Near-term margin equivalent of FOU2T14D's medium-term view. `elexon · demand & forecasts · 30 min`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. The realised counterpart for forecast-error analysis (declared availability vs actual generation). `elexon · generation · 30 min`
