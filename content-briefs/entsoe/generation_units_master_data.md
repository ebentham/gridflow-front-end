---
slug: generation_units_master_data
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A95
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/15-generation-units-master-data-http-401.md)"
sources_consulted:
  - vault/entsoe/generation_units_master_data.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeGenerationUnitsMasterData (lines 258-274)
  - gridflow/src/gridflow/silver/entsoe/generation_units_master_data.py::GenerationUnitsMasterDataTransformer (lines 18-90)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["generation_units_master_data"] (lines 115-122)
  - .planning/reconciliation/entsoe/15-generation-units-master-data-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/53-generation-units-master-data-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** EIC unit registry, <span class="italic fg-accent">name and type.</span>

**Lede:** Production and generation unit reference data — the EIC registry of human-readable names, PSR types, and implementation dates that enriches every unit-level dataset.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.generation_units_master_data` |
| API PATH | `/api?documentType=A95&BusinessType=B11` |
| FREQUENCY | static (on change) |
| PUBLICATION LAG | on change |
| VOLUME | varies by zone |
| PRIMARY KEY | `(area_code, unit_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A95 | DocumentType |
| 2 | static | Reference data |
| 3 | B11 | BusinessType filter |
| 4 | 7 | Schema columns |

# Sidebar siblings

- installed_capacity_units
- actual_generation_units
- installed_capacity
- outages_generation
- actual_generation

# Sample chart

- **Type:** `donut`
- **Title:** "Units registered per PSR type · DE-LU"
- **Subtitle:** "Donut · count · current"
- **Seed:** 23
- **Toggles:** `DE-LU` (active) / `FR` / `NL`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeGenerationUnitsMasterData` (lines 258-274). No `timestamp_utc` — this is a reference table keyed by `(area_code, unit_mrid)`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `area_code` | `str` | No | parsed from XML | EIC bidding zone — defaults to `""`. | `schemas/entsoe.py L261`; `silver/entsoe/generation_units_master_data.py L54` |
| `unit_mrid` | `str` | No | `<registeredResource.mRID>` | Unit identifier — opaque. Transformer filters out empty values. | `schemas/entsoe.py L262`; `silver/entsoe/generation_units_master_data.py L55, L64` |
| `unit_name` | `str` | Yes (default `""`) | `<registeredResource.name>` | Human-readable unit name. | `schemas/entsoe.py L263` |
| `production_type` | `str` | Yes (default `""`) | `<MktPSRType><psrType>` | EIC PSR code. | `schemas/entsoe.py L264` |
| `implementation_datetime_utc` | `Optional[datetime[UTC]]` | Yes | `<Implementation_DateAndOrTime>` | When the unit started operation; validator requires tzinfo if present. | `schemas/entsoe.py L265, L269-274` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L266` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L267` |

**PARQUET PATH:** `data/silver/entsoe/generation_units_master_data/year=YYYY/month=MM/`
**PARTITION BY:** ingestion month (no `timestamp_utc` partition)
**DEDUP KEY:** `(area_code, unit_mrid)` (`silver/entsoe/generation_units_master_data.py L65`)

# Sample data

| area_code | unit_mrid | unit_name | production_type | implementation_datetime_utc | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 10Y1001A1001A82H | 11W-NIEDERAUSSEM-K | Niederaussem K | B05 | 2003-01-01T00:00:00+00:00 | entsoe | 2026-05-08T18:00:00Z |
| 10Y1001A1001A82H | 11W-IRSCHING-5 | Irsching 5 | B04 | 2010-07-01T00:00:00+00:00 | entsoe | 2026-05-08T18:00:00Z |
| 10Y1001A1001A82H | 11W-AMRUMBANK-WEST | Amrumbank West | B18 | 2015-10-01T00:00:00+00:00 | entsoe | 2026-05-08T18:00:00Z |
| **10Y1001A1001A82H** | **11W-EMSLAND-C** | **Emsland C** | **B14** | **1988-04-19T00:00:00+00:00** | **entsoe** | **2026-05-08T18:00:00Z** |

**Sources:** Synthesised against typical DE-LU master-data shape. The highlighted **Emsland C (1988)** row illustrates the long history A95 captures — most nuclear units pre-date the EIC system, so `implementation_datetime_utc` is historical and stable. Note `production_type` is `B14` (nuclear) — but Germany phased out nuclear in 2023; the row would carry a retirement date if A95 published one (it does not — use `outages_production` for retirements).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A95&BusinessType=B11&BiddingZone_Domain={EIC}&Implementation_DateAndOrTime={YYYYMMDD}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/generation_units_master_data/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.generation_units_master_data.GenerationUnitsMasterDataTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A95&BusinessType=B11&BiddingZone_Domain=10Y1001A1001A82H&Implementation_DateAndOrTime=20260101
```

**Tab 2 — DuckDB · SQL**
```sql
-- Unit fleet by PSR type per zone
SELECT area_code, production_type, count(*) AS units,
       min(implementation_datetime_utc) AS oldest,
       max(implementation_datetime_utc) AS newest
FROM read_parquet('data/silver/entsoe/generation_units_master_data/**/*.parquet')
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

master = pl.read_parquet("data/silver/entsoe/generation_units_master_data/**/*.parquet")
gen = pl.read_parquet("data/silver/entsoe/actual_generation_units/**/*.parquet")
# Enrich output with unit names + age
enriched = gen.join(master, on=["area_code", "unit_mrid"], how="left")
print(enriched.select(["unit_name", "production_type", "generation_mw"]).tail())
```

# Caveats

## 01 No `timestamp_utc` — reference table

This dataset is keyed by `(area_code, unit_mrid)`; it doesn't carry a time-series timestamp. `implementation_datetime_utc` is the unit's commissioning date, not the row's publication time. *(Source: `schemas/entsoe.py L258-267`.)*

## 02 BusinessType `B11` is required

Connector pins `BusinessType=B11` (Production unit). Other BusinessType values (B14 generation unit, etc.) return different surfaces — out of scope for this dataset. *(Source: `endpoints.py L115-122`.)*

## 03 `date_param` uses `Implementation_DateAndOrTime`

Unlike most ENTSO-E endpoints which use `periodStart`/`periodEnd`, A95 uses `Implementation_DateAndOrTime` as the date param. *(Source: `endpoints.py L121`.)*

## 04 Empty `unit_mrid` rows filtered

Transformer drops rows where `unit_mrid == ""` (`silver/entsoe/generation_units_master_data.py L64`). *(Source: gridflow source.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/15-generation-units-master-data-http-401.md`.)*

# Related datasets

- **`installed_capacity_units`** — Per-unit installed MW capacity. `yearly`. Join on `(area_code, unit_mrid)` to enrich names + types onto capacity rows. `entsoe · generation · yearly`
- **`actual_generation_units`** — Realised per-unit output. `hourly`. Join on `unit_mrid` to attach unit names to output time series. `entsoe · generation · hourly`
- **`outages_generation`** — Per-unit outages (A80). `as published`. Join on `unit_mrid` to attach unit names to outage events. `entsoe · outages · as-published`
- **`bmunits_reference` (Elexon)** — GB BM-unit registry. `static`. The GB equivalent — A95 is empty for GB. `elexon · reference · static`
