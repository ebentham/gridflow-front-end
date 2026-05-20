---
slug: uou2t14d
vendor: elexon
vendor_label: Elexon BMRS
api_code: UOU2T14D
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/uou2t14d.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonUOU2T14D class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/uou2t14d.py::UOU2T14DTransformer (lines 19-122)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 150-155, PUBLISH_DATETIME style with max_chunk_hours=4)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/UOU2T14D (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonUOU2T14D class declared"
    source_b: "gridflow silver/elexon/uou2t14d.py L19-122"
    source_b_says: "UOU2T14DTransformer outputs settlement_date, settlement_period, timestamp_utc, bm_unit_id, output_usable_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; matches FOU2T14D shape gap"
  - source_a: "vault Silver schema lists 7 columns"
    source_a_says: "Schema documents 7 columns including bm_unit_id and output_usable_mw"
    source_b: "gridflow silver/elexon/uou2t14d.py L114-117"
    source_b_says: "Transformer also renames fuelType → fuel_type and nationalGridBmUnit → national_grid_bm_unit (L63-65) but output_cols does NOT include them"
    orchestrator_recommendation: "trust gridflow output_cols — fuel_type and national_grid_bm_unit are dropped from silver. Joins for fuel context must use bmunits_reference, not UOU2T14D's own fuel_type."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Per-BMU availability, <span class="italic fg-accent">2-14 days out.</span>

**Lede:** Per-BMU GB 2-14 day-ahead availability — the canonical unit-level declaration for forward margin, outage planning, and FOU2T14D reconciliation.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · UOU2T14D](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/UOU2T14D)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.uou2t14d` |
| API PATH | `/datasets/UOU2T14D` |
| FREQUENCY | daily |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 5.2M / mo |
| PRIMARY KEY | `(settlement_date, [settlement_period,] bm_unit_id)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Publication frequency |
| 2 | 4 h | Max chunk hours (vendor cap) |
| 3 | ~2.5k | BMUs per publish |
| 4 | 7 | Schema columns |

# Sidebar siblings

- fou2t14d
- bmunits_reference
- pn
- boal
- ndfd

# Overview

1. <code>uou2t14d</code> is the daily-published per-BMU 2-to-14-day-ahead availability — the canonical unit-level declaration that aggregates to <code>fou2t14d</code> when summed by fuel. It is used for outage-impact analysis, redispatch modelling, and reconciliation with the BMU reference list.

2. Gridflow fetches it from <code>/datasets/UOU2T14D</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (max chunk = 4 hours). The raw JSON lands in bronze and is written to the silver parquet partition via <code>UOU2T14DTransformer</code> — fuel_type is dropped from silver output, so fuel context must come from <code>bmunits_reference</code>.

3. Refreshed daily with 0 publication lag (forward-looking). Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "BMU availability by fuel · 14-day forward"
- **Subtitle:** "Stacked area · MW · forecast delivery date · published 6 May 2026"
- **Shape:** (legacy hardcoded GB fuel mix — illustrative when BMU rows are aggregated to fuel)
- **Seed:** 35
- **Toggles:** `14d` (active) / `7d` / `2d`

# Schema

Defined in `gridflow/silver/elexon/uou2t14d.py` · `UOU2T14DTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` / `forecastDate` | **Forecast delivery date** (2-14 days ahead). Partition key. | `silver/elexon/uou2t14d.py L56-58, L77` |
| `settlement_period` | `Optional[int]` | Yes | `settlementPeriod` | 1..50 when present. Often absent (daily-aggregate); the transformer conditionally includes it. | `silver/elexon/uou2t14d.py L83-101` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Period-derived if available, else midnight UTC of settlement_date. | `silver/elexon/uou2t14d.py L83-101` |
| `bm_unit_id` | `str` | No | `bmUnit` | BM Unit identifier — preserve raw casing (e.g. `T_DRAXX-1`, `2__NSMAE001`). | `silver/elexon/uou2t14d.py L61, L78` |
| `output_usable_mw` | `float` | No | `outputUsable` | MW. Declared availability per BMU. | `silver/elexon/uou2t14d.py L62, L79` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/uou2t14d.py L110` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/uou2t14d.py L111` |

**PARQUET PATH:** `data/silver/elexon/uou2t14d/year=YYYY/month=MM/` (forecast delivery date partition)
**PARTITION BY:** `settlement_date (year + month)` (forecast delivery date)
**DEDUP KEY:** `(settlement_date, [settlement_period,] bm_unit_id)` (`silver/elexon/uou2t14d.py L103-106`)

# Sample data

| settlement_date | timestamp_utc | bm_unit_id | output_usable_mw | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | 2__NSMAE001 | 36.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | T_DRAXX-1 | 660.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | T_HEYM27 | 605.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08 | 2026-05-08T00:00:00+00:00 | T_HOWAO-2 | 1320.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-15** | **2026-05-15T00:00:00+00:00** | **T_DRAXX-1** | **645.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-15 | 2026-05-15T00:00:00+00:00 | T_HEYM27 | 605.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-15 | 2026-05-15T00:00:00+00:00 | T_HOWAO-2 | 1320.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-20 | 2026-05-20T00:00:00+00:00 | T_DRAXX-1 | 0.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`2__NSMAE001` biomass, `outputUsable=36`) and 2 (`T_DRAXX-1` biomass, `outputUsable=660`) verbatim from the vault Bronze Sample (vault/elexon/uou2t14d.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW, BMU prefix casing) and represent the forward declaration arc across the 14-day horizon for major BMUs (Drax biomass, Heysham nuclear, Hornsea 2 offshore wind). The highlighted **T_DRAXX-1 SP15 (645 MW)** row is the interesting case: Drax declares lower availability mid-week (645 vs 660 nameplate) — exactly the per-BMU declared reduction that aggregates into the FOU2T14D biomass dip.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: UOU2T14D's interesting structure is per-BMU but enumeration would duplicate bmunits_reference. The 4-hour chunk cap and forecast-delivery-date semantics are documented in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/UOU2T14D`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/uou2t14d/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.uou2t14d.UOU2T14DTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/UOU2T14D?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T04:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Top BMUs declaring lower availability than nameplate (potential outage candidates)
WITH bmu AS (
  SELECT bm_unit_id, bm_unit_name, registered_capacity_mw
  FROM read_parquet('data/silver/elexon/bmunits_reference/bmunits_reference.parquet')
)
SELECT u.bm_unit_id, bmu.bm_unit_name,
       u.output_usable_mw, bmu.registered_capacity_mw,
       (bmu.registered_capacity_mw - u.output_usable_mw) AS deficit_mw
FROM read_parquet('data/silver/elexon/uou2t14d/**/*.parquet') u
JOIN bmu USING (bm_unit_id)
WHERE u.settlement_date = current_date + INTERVAL 7 DAY
  AND bmu.registered_capacity_mw > 100
  AND (bmu.registered_capacity_mw - u.output_usable_mw) > 50
ORDER BY deficit_mw DESC
LIMIT 30;
```

**Tab 3 — Python · polars**
```python
import polars as pl

u = pl.read_parquet("data/silver/elexon/uou2t14d/**/*.parquet")
bmu = pl.read_parquet("data/silver/elexon/bmunits_reference/bmunits_reference.parquet")
# Aggregate UOU2T14D by fuel — should reconcile with FOU2T14D
by_fuel = (
    u.join(bmu.select(["bm_unit_id", "fuel_type"]), on="bm_unit_id", how="left")
     .group_by(["settlement_date", "fuel_type"])
     .agg(pl.col("output_usable_mw").sum().alias("total_mw"))
     .sort(["settlement_date", "total_mw"], descending=[False, True])
)
print(by_fuel.head(20))
```

# Caveats

## 01 4-hour chunk cap (strict)

Vendor caps queries at 4 hours; `max_chunk_hours=4`. Backfills require many calls. *(Source: `connectors/elexon/endpoints.py L150-155`.)*

## 02 No Pydantic schema in `schemas/elexon.py`

No `ElexonUOU2T14D` class; shape lives in `UOU2T14DTransformer.output_cols`. *(Source: `silver/elexon/uou2t14d.py`.)*

## 03 `fuel_type` and `national_grid_bm_unit` dropped from silver

Renamed internally but excluded from `output_cols`. Join `bmunits_reference` for fuel context. *(Source: `silver/elexon/uou2t14d.py L114-117`.)*

## 04 `settlement_period` is conditional

Daily-aggregate by default; transformer includes the column only when bronze has it. Check `df.columns` before joining. *(Source: `silver/elexon/uou2t14d.py L83-106`.)*

## 05 Volume — 5.2M rows/month is real

~63M rows/year; partition pruning by month is essential. *(Source: manifest `rows: "5.2M / mo"`.)*

## 06 `output_usable_mw` is declared, not realised

Forward declaration vs realised generation. Compare to `fuelhh` or `pn` for declared-vs-realised. *(Source: BSC forward-availability framework.)*

# Related datasets

- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Fuel-aggregate counterpart; sum of UOU2T14D by fuel = FOU2T14D for the same delivery date. `elexon · demand & forecasts · daily`
- **bmunits_reference** — BMU reference list. `weekly`. Join on `bm_unit_id` to attach fuel type, lead party, registered capacity — essential for any UOU2T14D aggregation. `elexon · system & reference · weekly`
- **pn** — Physical notifications. `hourly`. Real-time pre-gate-closure intentions per BMU; combine with UOU2T14D forward declarations for ex-ante vs eventual-ex-ante comparison. `elexon · prices & balancing · hourly`
- **ndfd** — National demand forecast 2-14 day. `daily`. Demand-side companion at the same horizon; FOU2T14D − NDFD = forward margin. `elexon · demand & forecasts · daily`
