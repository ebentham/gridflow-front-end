---
slug: outages_production
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A77
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/26-outages-production-http-401.md)"
sources_consulted:
  - vault/entsoe/outages_production.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeOutagesProduction (lines 531-554)
  - gridflow/src/gridflow/silver/entsoe/outages_h7.py::OutagesProductionTransformer (lines 182-202)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["outages_production"] (lines 82-89)
  - .planning/reconciliation/entsoe/26-outages-production-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/64-outages-production-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Production unit outages, <span class="italic fg-accent">A77.</span>

**Lede:** Unavailability of production units per zone — A77 outages enriched with production_type and document-level metadata (mrid / status), one of the H7 outages family.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.outages_production` |
| API PATH | `/api?documentType=A77&BusinessType=A53` |
| FREQUENCY | as published (event-driven) |
| PUBLICATION LAG | real-time |
| VOLUME | varies by zone |
| PRIMARY KEY | `(timestamp_utc, area_code, unit_mrid, timeseries_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A77 | DocumentType |
| 2 | bidding_zone | `domain_style` |
| 3 | H7 | Shared transformer family |
| 4 | 13 | Schema columns |

# Sidebar siblings

- outages_generation
- outages_consumption
- outages_transmission
- outages_offshore_grid
- generation_units_master_data

# Sample chart

- **Type:** `barsH`
- **Title:** "DE-LU production unit outages · 24h"
- **Subtitle:** "Horizontal bars · MW unavailable · UTC"
- **Seed:** 73
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeOutagesProduction` (lines 531-554). Carries richer document-level metadata than the older `EntsoeOutagesGeneration` (A80). H7-family transformer.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L534, L549-554` |
| `area_code` | `str` | No | `<BiddingZone_Domain.mRID>` | Bidding zone EIC. | `schemas/entsoe.py L535` |
| `unit_mrid` | `str` | No | `<RegisteredResource.mRID>` | Unit identifier (opaque). | `schemas/entsoe.py L536` |
| `unit_name` | `str` | Yes (default `""`) | `<RegisteredResource.name>` | Human-readable unit name. | `schemas/entsoe.py L537` |
| `production_type` | `str` | Yes (default `""`) | `<MktPSRType><psrType>` | EIC PSR code. | `schemas/entsoe.py L538` |
| `outage_type` | `str` | No | derived from `<businessType>` | `"planned"` (A53) / `"unplanned"` (A54) — mapped via `replace_strict` | `schemas/entsoe.py L539`; `silver/entsoe/outages_h7.py L91-95` |
| `unavailable_mw` | `float` | No | `<Point><quantity>` | MW unavailable. | `schemas/entsoe.py L540` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` (raw) | Original code preserved alongside derived `outage_type`. | `schemas/entsoe.py L541` |
| `document_mrid` | `str` | Yes (default `""`) | `<mRID>` (root) | Document-level identifier — distinguishes outage publications. | `schemas/entsoe.py L542` |
| `document_status` | `str` | Yes (default `""`) | `<docStatus>` | Document status code. | `schemas/entsoe.py L543` |
| `timeseries_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` | TimeSeries identifier within document. | `schemas/entsoe.py L544` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L545` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L546` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L547` |

**PARQUET PATH:** `data/silver/entsoe/outages_production/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, unit_mrid, timeseries_mrid)` (`silver/entsoe/outages_h7.py L202`)

# Sample data

| timestamp_utc | area_code | unit_mrid | unit_name | production_type | outage_type | unavailable_mw | business_type | document_mrid | document_status | timeseries_mrid | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 11W-NIEDERAUSSEM-K | Niederaussem K | B05 | planned | 944.0 | A53 | doc-001 | A05 | ts-001 | PT60M | entsoe |
| **2026-05-06T14:00:00+00:00** | **10Y1001A1001A82H** | **11W-EMSLAND-C** | **Emsland C** | **B14** | **unplanned** | **1329.0** | **A54** | **doc-002** | **A05** | **ts-001** | **PT60M** | **entsoe** |
| 2026-05-06T20:00:00+00:00 | 10Y1001A1001A82H | 11W-NIEDERAUSSEM-K | Niederaussem K | B05 | planned | 944.0 | A53 | doc-001 | A05 | ts-002 | PT60M | entsoe |

**Sources:** Synthesised. The highlighted **Emsland C nuclear unplanned 1.33 GW outage** illustrates the high-impact unplanned-nuclear event that drives multi-day price spikes. Note `business_type` (raw A53/A54) is preserved alongside the derived `outage_type` — useful when querying with the raw code.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A77&BusinessType=A53&BiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/outages_production/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.outages_h7.OutagesProductionTransformer` (shared H7 base)

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A77&BusinessType=A53&BiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Unplanned outages by production type (last 90 days)
SELECT production_type, count(DISTINCT document_mrid) AS events,
       sum(unavailable_mw) AS total_mwh_unavail
FROM read_parquet('data/silver/entsoe/outages_production/**/*.parquet')
WHERE outage_type = 'unplanned'
  AND timestamp_utc >= current_timestamp - INTERVAL 90 DAY
GROUP BY 1 ORDER BY total_mwh_unavail DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

out = pl.read_parquet("data/silver/entsoe/outages_production/**/*.parquet")
# Document-status timeline: how often does an outage get revised?
print(out.group_by("document_mrid").agg(
    pl.col("document_status").unique().alias("statuses"),
    pl.col("timeseries_mrid").n_unique().alias("timeseries_count")
).head())
```

# Caveats

## 01 H7 transformer family

This dataset uses the shared `_H7OutageTransformer` base in `outages_h7.py`, distinct from the standalone `outages_generation.py` (A80). H7 family adds document-level metadata. *(Source: `silver/entsoe/outages_h7.py L24-106`.)*

## 02 outage_type derived via replace_strict

`businessType` (A53/A54/other) maps to `outage_type` ("planned"/"unplanned"/passthrough) via `replace_strict`. Unknown business types pass through as the raw code. *(Source: `silver/entsoe/outages_h7.py L91-95`.)*

## 03 Document and TimeSeries metadata preserved

Unlike A80, A77 preserves `document_mrid`, `document_status`, and `timeseries_mrid` — useful for tracking outage revisions and document-status changes (active → withdrawn). *(Source: `schemas/entsoe.py L541-544`.)*

## 04 Dedup includes timeseries_mrid

`(timestamp_utc, area_code, unit_mrid, timeseries_mrid)` — different TimeSeries within the same document survive. *(Source: `silver/entsoe/outages_h7.py L202`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/26-outages-production-http-401.md`.)*

# Related datasets

- **`outages_generation`** — A80 generation unit outages. `as published`. Older A80 surface; subset of what A77 publishes. `entsoe · outages · as-published`
- **`outages_transmission`** — A78 transmission infrastructure outages. `as published`. Zone-pair scope (asset rather than unit). `entsoe · outages · as-published`
- **`outages_consumption`** — A76 aggregated consumption-unit outages. `as published`. Aggregated zone view (no unit_mrid). `entsoe · outages · as-published`
- **`generation_units_master_data`** — Per-unit reference data. `static`. Use to enrich unit_mrid into human-readable names. `entsoe · generation · static`
