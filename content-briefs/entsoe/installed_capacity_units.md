---
slug: installed_capacity_units
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A71/A33
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/17-installed-capacity-units-http-401.md)"
sources_consulted:
  - vault/entsoe/installed_capacity_units.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeInstalledCapacityUnits (lines 176-194)
  - gridflow/src/gridflow/silver/entsoe/installed_capacity_units.py::InstalledCapacityUnitsTransformer (lines 18-94)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["installed_capacity_units"] (lines 93-98)
  - .planning/reconciliation/entsoe/17-installed-capacity-units-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/55-installed-capacity-units-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Plant-level installed capacity, <span class="italic fg-accent">EIC registry.</span>

**Lede:** Yearly installed MW capacity per EIC generation unit — the unit-level disaggregation of A68 and denominator for plant-by-plant capacity-factor calculation.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.installed_capacity_units` |
| API PATH | `/api?documentType=A71&processType=A33` |
| FREQUENCY | annual (P1Y) |
| PUBLICATION LAG | year boundary |
| VOLUME | varies — many zones EMPTY |
| PRIMARY KEY | `(timestamp_utc, area_code, unit_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | unit-level | Granularity |
| 2 | A33 | Year-ahead processType |
| 3 | XML | `GL_MarketDocument` |
| 4 | 9 | Schema columns |

# Sidebar siblings

- installed_capacity
- generation_units_master_data
- actual_generation_units
- outages_generation
- actual_generation

# Sample chart

- **Type:** `barsH`
- **Title:** "DE-LU top-20 generation units by capacity"
- **Subtitle:** "Horizontal bars · MW · year 2026"
- **Seed:** 21
- **Toggles:** `2026` (active) / `2025`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeInstalledCapacityUnits` (lines 176-194). Transformer filters empty `unit_mrid` rows.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start | Year boundary, tz-aware UTC. | `schemas/entsoe.py L179, L189-194` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L180` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | EIC PSR code; `"unknown"` if absent. | `schemas/entsoe.py L181`; `silver/entsoe/installed_capacity_units.py L65-67` |
| `unit_mrid` | `str` | No | `<registeredResource.mRID>` | Unit identifier — opaque. | `schemas/entsoe.py L182` |
| `unit_name` | `str` | Yes (default `""`) | `<registeredResource.name>` | Human-readable unit name. | `schemas/entsoe.py L183` |
| `capacity_mw` | `float` | No | `<Point><quantity>` | MW installed capacity for this unit. | `schemas/entsoe.py L184` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `P1Y`. | `schemas/entsoe.py L185` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L186` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L187` |

**PARQUET PATH:** `data/silver/entsoe/installed_capacity_units/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, unit_mrid)` (`silver/entsoe/installed_capacity_units.py L69-72`)

# Sample data

| timestamp_utc | area_code | production_type | unit_mrid | unit_name | capacity_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B05 | 11W-NIEDERAUSSEM-K | Niederaussem K | 944.0 | P1Y | entsoe | 2026-05-08T18:00:00Z |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B04 | 11W-IRSCHING-5 | Irsching 5 | 845.0 | P1Y | entsoe | 2026-05-08T18:00:00Z |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B18 | 11W-AMRUMBANK-WEST | Amrumbank West | 302.0 | P1Y | entsoe | 2026-05-08T18:00:00Z |
| **2026-01-01T00:00:00+00:00** | **10Y1001A1001A82H** | **B19** | **11W-WINDPARK-LISTERFEHRDA** | **Listerfehrda** | **20.0** | **P1Y** | **entsoe** | **2026-05-08T18:00:00Z** |

**Sources:** Synthesised — respects schema constraints (`unit_mrid` non-empty, `production_type` ∈ B-series, `capacity_mw` ≥ 0); shape matches typical A71/A33 DE-LU output. The highlighted **wind farm (`B19` onshore 20 MW)** row illustrates the long-tail of small generators that A71/A33 surfaces but A68 collapses into the aggregate.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A71&processType=A33&in_Domain={EIC}&periodStart={YYYY01010000}&periodEnd={YYYY12310000}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/installed_capacity_units/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.installed_capacity_units.InstalledCapacityUnitsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A71&processType=A33&in_Domain=10Y1001A1001A82H&periodStart=202601010000&periodEnd=202612310000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Top-20 largest units per zone (current year)
SELECT area_code, unit_mrid, unit_name, production_type, capacity_mw
FROM read_parquet('data/silver/entsoe/installed_capacity_units/**/*.parquet')
WHERE timestamp_utc = (
    SELECT max(timestamp_utc)
    FROM read_parquet('data/silver/entsoe/installed_capacity_units/**/*.parquet')
)
ORDER BY area_code, capacity_mw DESC
LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cap = pl.read_parquet("data/silver/entsoe/installed_capacity_units/**/*.parquet")
gen = pl.read_parquet("data/silver/entsoe/actual_generation_units/**/*.parquet")
# Per-unit capacity factor (annual mean output / installed capacity)
util = gen.group_by("unit_mrid").agg(
    pl.col("generation_mw").mean().alias("mean_mw"),
).join(cap.select(["unit_mrid", "capacity_mw"]), on="unit_mrid")
print(util.with_columns(
    (pl.col("mean_mw") / pl.col("capacity_mw")).alias("cf")
).sort("cf", descending=True).head())
```

# Caveats

## 01 A71 doc type shared with generation_forecast

A71 is reused for `generation_forecast` (A71/A01) with a different `processType`. Select on dataset key, not `documentType` alone. *(Source: `endpoints.py L100-102`.)*

## 02 Empty `unit_mrid` rows filtered

Transformer drops rows where `unit_mrid == ""`. Aggregate-only data passes through other A71 surfaces, not here. *(Source: `silver/entsoe/installed_capacity_units.py L68`.)*

## 03 `unit_mrid` is opaque

Identifiers vary by TSO encoding (IGCC, EIC, internal). Treat as opaque strings. *(Source: vault Known Issues.)*

## 04 GB EMPTY post-Brexit

GB unit registry is via Elexon `bmunits` / BMRS, not ENTSO-E. *(Source: vault Known Issues.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/17-installed-capacity-units-http-401.md`.)*

# Related datasets

- **`installed_capacity`** — Aggregate-by-PSR version of this dataset. `yearly`. Sum this dataset over `unit_mrid` recovers the aggregate. `entsoe · generation · yearly`
- **`generation_units_master_data`** — Per-unit reference data (name, type, area). `static`. Use to enrich unit metadata across years. `entsoe · generation · static`
- **`actual_generation_units`** — Realised output per unit. `hourly`. Pair with this dataset for plant-level capacity-factor calculation. `entsoe · generation · hourly`
- **`bmunits_reference` (Elexon)** — GB BM-unit registry. `static`. Substitute for any GB query — A71/A33 is empty for GB. `elexon · reference · static`
