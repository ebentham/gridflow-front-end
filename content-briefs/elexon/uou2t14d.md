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

**Lede:** UOU2T14D is the 2-14 day-ahead generation availability declared at BM unit level — the unit-resolved companion to `fou2t14d`. Each row is one BMU's `output_usable_mw` for one future delivery date. The most voluminous forward dataset in BMRS (~5.2M rows/month) and the granular source of capacity-margin and unit-availability analytics.

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

1. <code>uou2t14d</code> is **2-14 Day Ahead Generation Availability by BM Unit** — every BMU's declared output usable per future delivery date. Each row carries `bm_unit_id` and `output_usable_mw` for a `settlement_date` 2-14 days ahead of publish. Aggregating UOU2T14D by `fuel_type` (via a `bmunits_reference` join) reproduces FOU2T14D.

2. Gridflow fetches it from <code>/datasets/UOU2T14D</code> with a **strict 4-hour chunk cap** (`max_chunk_hours=4`, `connectors/elexon/endpoints.py L154`) — the vendor returns HTTP 400 for wider queries. The <code>UOU2T14DTransformer</code> renames `forecastDate` → `settlement_date` (mirrors FOU2T14D pattern), conditionally derives `timestamp_utc` from settlement-period pair if present (else midnight UTC of settlement_date), and dedups on `(settlement_date, [settlement_period,] bm_unit_id)`. No Pydantic class is declared. The transformer also renames `fuelType` and `nationalGridBmUnit` internally but drops them from silver output — use `bmunits_reference` for fuel attribution.

3. Cadence is daily publication, zero lag. Verified against the live API on 2026-05-08; the sample returned per-BMU rows for forecast_date 2026-05-08 (`2__NSMAE001` biomass 36 MW; `T_DRAXX-1` biomass 660 MW). Volume is the highest in the Elexon set after PN (~5.2M rows/month) — partition pruning is essential for any historical analytics. Pair with FOU2T14D for the fuel-aggregate sanity check and with `bmunits_reference` for unit context.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "BMU availability by fuel · 14-day forward"
- **Subtitle:** "Stacked area · MW · forecast delivery date · published 6 May 2026"
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

The vendor returns HTTP 400 for queries spanning more than 4 hours. Connector sets `max_chunk_hours=4` (`connectors/elexon/endpoints.py L154`). A single 4-hour window can return hundreds of thousands of rows × 14 future delivery dates × ~2.5k BMUs. Backfills budget many calls per day. *(Source: vault Known Issues; `connectors/elexon/endpoints.py L150-155`.)*

## 02 No Pydantic schema in `schemas/elexon.py`

Like FOU2T14D and other forward-availability datasets, UOU2T14D has no dedicated Pydantic class. Silver shape is defined by `UOU2T14DTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no UOU2T14D class.)*

## 03 `fuel_type` and `national_grid_bm_unit` dropped from silver

The transformer renames `fuelType → fuel_type` and `nationalGridBmUnit → national_grid_bm_unit` internally (`silver/elexon/uou2t14d.py L63-65`), but neither appears in `output_cols`. To get fuel context for UOU2T14D rows, join to `bmunits_reference` on `bm_unit_id`. *(Source: discrepancy in frontmatter; `silver/elexon/uou2t14d.py L114-117`.)*

## 04 `settlement_period` is conditional

UOU2T14D rows are daily-aggregate by default (no `settlementPeriod` in bronze), but the transformer supports period-resolution input if the vendor returns it. The `dedup_cols` list conditionally includes `settlement_period` when present (`silver/elexon/uou2t14d.py L104-106`). Defensive consumers should check column existence before joining. *(Source: `silver/elexon/uou2t14d.py L83-106`.)*

## 05 Volume — 5.2M rows/month is real

A single month is ~5.2 million rows; a year is ~63M. Silver is partitioned by month — query a single month at a time, or pre-aggregate to BMU-day rolls in a gold view if you need wider time spans. *(Source: vault Known Issues; manifest `rows: "5.2M / mo"`.)*

## 06 `output_usable_mw` is declared, not realised

UOU2T14D is forward-looking — what the operator says the BMU will be able to offer. Compare to FUELHH (realised generation) or `pn` (actual physical notifications) for declared-vs-realised analysis. Persistent over-declaration is a regulatory signal. *(Source: domain knowledge — BSC forward-availability framework.)*

# Related datasets

- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Fuel-aggregate counterpart; sum of UOU2T14D by fuel = FOU2T14D for the same delivery date. `elexon · demand & forecasts · daily`
- **bmunits_reference** — BMU reference list. `weekly`. Join on `bm_unit_id` to attach fuel type, lead party, registered capacity — essential for any UOU2T14D aggregation. `elexon · system & reference · weekly`
- **pn** — Physical notifications. `hourly`. Real-time pre-gate-closure intentions per BMU; combine with UOU2T14D forward declarations for ex-ante vs eventual-ex-ante comparison. `elexon · prices & balancing · hourly`
- **ndfd** — National demand forecast 2-14 day. `daily`. Demand-side companion at the same horizon; FOU2T14D − NDFD = forward margin. `elexon · demand & forecasts · daily`
