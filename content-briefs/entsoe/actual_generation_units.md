---
slug: actual_generation_units
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A73/A16
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/02-actual-generation-units-http-401.md)"
sources_consulted:
  - vault/entsoe/actual_generation_units.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActualGenerationUnits (lines 219-237)
  - gridflow/src/gridflow/silver/entsoe/actual_generation_units.py::ActualGenerationUnitsTransformer (lines 18-87)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["actual_generation_units"] (lines 103-108)
  - .planning/reconciliation/entsoe/02-actual-generation-units-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/38-actual-generation-units-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Per-unit realised generation, <span class="italic fg-accent">plant by plant.</span>

**Lede:** Per-unit realised MW output identified by EIC unit mRID — the TSO-published equivalent of Elexon `pn` for European plant-by-plant capacity-factor modelling.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.actual_generation_units` |
| API PATH | `/api?documentType=A73&processType=A16` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | T+~1h (when published) |
| VOLUME | varies — many zones EMPTY |
| PRIMARY KEY | `(timestamp_utc, area_code, unit_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | unit-level | Granularity |
| 2 | T+1h | Best-case lag |
| 3 | XML | `GL_MarketDocument` |
| 4 | 9 | Schema columns |

# Sidebar siblings

- actual_generation
- installed_capacity_units
- generation_units_master_data
- generation_forecast
- outages_generation

# Sample chart

- **Type:** `barsH`
- **Title:** "GB nuclear units · realised MW · 24h snapshot"
- **Subtitle:** "Horizontal bars · MW · UTC · 6 May 2026"
- **Seed:** 13
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActualGenerationUnits` (lines 219-237). Partitioned by `timestamp_utc` (year + month). Unit-level filter: transformer drops rows with empty `unit_mrid`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L222, L232-237` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L223` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | EIC PSR code; `"unknown"` if absent. | `schemas/entsoe.py L224`; `silver/entsoe/actual_generation_units.py L59` |
| `unit_mrid` | `str` | No | `<registeredResource.mRID>` | Unit identifier — opaque string (IGCC / EIC / TSO internal). | `schemas/entsoe.py L225` |
| `unit_name` | `str` | Yes (default `""`) | `<registeredResource.name>` | Human-readable unit name; may be absent. | `schemas/entsoe.py L226` |
| `generation_mw` | `float` | No | `<Point><quantity>` | MW. | `schemas/entsoe.py L227` |
| `resolution` | `str` | Yes (default `""`) | parsed from `<Period><resolution>` | ISO duration; typically `PT60M`. | `schemas/entsoe.py L228` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L229` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L230` |

**PARQUET PATH:** `data/silver/entsoe/actual_generation_units/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, unit_mrid)` (`silver/entsoe/actual_generation_units.py L62-65`)

# Sample data

| timestamp_utc | area_code | production_type | unit_mrid | unit_name | generation_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | B14 | 48WSTN0000ABRBON | ABRBO | 100.5 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Sample row verbatim from vault Silver Sample (`vault/entsoe/actual_generation_units.md` L113-124). One row only — A73/A16 is generally EMPTY across most European zones (TSOs publish per-unit data via national portals like SMARD instead of ENTSO-E).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A73&processType=A16&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/actual_generation_units/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.actual_generation_units.ActualGenerationUnitsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A73&processType=A16&in_Domain=10YGB----------A&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Per-unit daily mean output (last 30 days)
SELECT date_trunc('day', timestamp_utc) AS day, unit_mrid, unit_name,
       avg(generation_mw) AS mean_mw
FROM read_parquet('data/silver/entsoe/actual_generation_units/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2, 3
ORDER BY 1, mean_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsoe/actual_generation_units/**/*.parquet")
# Per-unit capacity factor (vs declared capacity from installed_capacity_units)
cap = df.group_by("unit_mrid").agg(
    pl.col("generation_mw").mean().alias("mean_mw"),
    pl.col("generation_mw").max().alias("peak_mw"),
)
print(cap.sort("peak_mw", descending=True).head())
```

# Caveats

## 01 GB and most continental zones EMPTY

Both GB and DE-LU returned `Acknowledgement` reason 999 in live verification. Many TSOs publish per-unit data only via national portals (e.g. SMARD), not ENTSO-E. Use Elexon `pn` / `boal` for GB plant-by-plant. *(Source: vault Known Issues #1.)*

## 02 `unit_mrid` is opaque

Identifiers vary by TSO encoding (IGCC, EIC, internal). Treat as opaque strings; do not normalise or split. *(Source: vault Known Issues #2.)*

## 03 `psrType` filter ergonomics

`psrType` is documented as an optional query filter but is NOT in connector `optional_params` (`endpoints.py L103-108`). Callers can still inject via `**params`. *(Source: vault Implementation Delta.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code, unit_mrid)` re-publication overwrites silently on dedup (`keep="last"`). *(Source: `silver/entsoe/actual_generation_units.py L62-65`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/02-actual-generation-units-http-401.md`.)*

# Related datasets

- **`actual_generation`** — Aggregate version of this dataset by PSR type. `PT15M-PT60M`. Pair to see how aggregate generation decomposes by individual unit. `entsoe · generation · hourly`
- **`installed_capacity_units`** — Per-unit installed capacity. `yearly`. Provides the denominator for unit-level capacity-factor calculation. `entsoe · generation · yearly`
- **`generation_units_master_data`** — Per-unit reference data (name, type, area). `static`. Use to enrich unit_mrid into a human-readable taxonomy. `entsoe · generation · static`
- **`pn` (Elexon)** — GB physical notifications by BM unit. `30 min`. Substitute for any GB query — A73 is empty for GB. `elexon · units · 30 min`
