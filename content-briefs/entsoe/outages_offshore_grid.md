---
slug: outages_offshore_grid
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A79
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/25-outages-offshore-grid-http-401.md)"
sources_consulted:
  - vault/entsoe/outages_offshore_grid.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeOutagesOffshoreGrid (lines 506-528)
  - gridflow/src/gridflow/silver/entsoe/outages_h7.py::OutagesOffshoreGridTransformer (lines 160-179)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["outages_offshore_grid"] (lines 75-81)
  - .planning/reconciliation/entsoe/25-outages-offshore-grid-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/63-outages-offshore-grid-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Offshore grid outages, <span class="italic fg-accent">A79.</span>

**Lede:** Unavailability of offshore grid infrastructure per zone — offshore wind cable and substation outages with asset identification, the dedicated surface for offshore-wind availability modelling.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.outages_offshore_grid` |
| API PATH | `/api?documentType=A79` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time |
| VOLUME | varies by zone |
| PRIMARY KEY | `(timestamp_utc, area_code, asset_mrid, timeseries_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A79 | DocumentType |
| 2 | bidding_zone | `domain_style` |
| 3 | H7 | Shared transformer family |
| 4 | 13 | Schema columns |

# Sidebar siblings

- outages_transmission
- outages_generation
- outages_production
- wind_solar_forecast
- actual_generation

# Sample chart

- **Type:** `barsH`
- **Title:** "Offshore grid outages by asset · 30d"
- **Subtitle:** "Horizontal bars · MW unavailable · UTC"
- **Seed:** 79
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeOutagesOffshoreGrid` (lines 506-528). H7-family transformer. Single-zone scope (not zone-pair) — offshore grid is attached to a host zone.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L509, L523-528` |
| `area_code` | `str` | No | `<BiddingZone_Domain.mRID>` | Host zone EIC. | `schemas/entsoe.py L510` |
| `asset_mrid` | `str` | Yes (default `""`) | `<RegisteredResource.mRID>` | Offshore asset identifier (cable / substation). | `schemas/entsoe.py L511` |
| `asset_name` | `str` | Yes (default `""`) | `<RegisteredResource.name>` | Human-readable name. | `schemas/entsoe.py L512` |
| `outage_type` | `str` | Yes (default `""`) | derived from `<businessType>` | `"planned"` (A53) / `"unplanned"` (A54). | `schemas/entsoe.py L513`; `silver/entsoe/outages_h7.py L91-95` |
| `unavailable_mw` | `float` | No | `<Point><quantity>` | MW unavailable. | `schemas/entsoe.py L514` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` (raw) | A53 / A54. | `schemas/entsoe.py L515` |
| `document_mrid` | `str` | Yes (default `""`) | `<mRID>` (root) | Document-level identifier. | `schemas/entsoe.py L516` |
| `document_status` | `str` | Yes (default `""`) | `<docStatus>` | Status code. | `schemas/entsoe.py L517` |
| `timeseries_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` | TimeSeries within document. | `schemas/entsoe.py L518` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L519` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L520` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L521` |

**PARQUET PATH:** `data/silver/entsoe/outages_offshore_grid/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, asset_mrid, timeseries_mrid)` (`silver/entsoe/outages_h7.py L179`)

# Sample data

| timestamp_utc | area_code | asset_mrid | asset_name | outage_type | unavailable_mw | business_type | document_mrid | document_status | timeseries_mrid | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | DOGGER-BANK-A-CBL | Dogger Bank A export cable | planned | 1200.0 | A53 | doc-301 | A05 | ts-001 | PT60M | entsoe |
| **2026-05-06T08:00:00+00:00** | **10Y1001A1001A82H** | **HORNSEA-2-SUB** | **Hornsea 2 substation** | **unplanned** | **1320.0** | **A54** | **doc-302** | **A05** | **ts-001** | **PT60M** | **entsoe** |

**Sources:** Synthesised. The highlighted **Hornsea 2 substation unplanned 1.32 GW outage** illustrates a high-impact offshore wind farm cable outage — these directly explain wind-generation drops that the meteorological forecast cannot anticipate. Offshore grid outages are particularly important for short-term wind forecast error attribution.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A79&BiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/outages_offshore_grid/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.outages_h7.OutagesOffshoreGridTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A79&BiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Offshore outage MW by host zone (last 90 days)
SELECT area_code, asset_name, outage_type,
       count(DISTINCT document_mrid) AS events,
       max(unavailable_mw) AS peak_unavail_mw
FROM read_parquet('data/silver/entsoe/outages_offshore_grid/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 90 DAY
GROUP BY 1, 2, 3 ORDER BY peak_unavail_mw DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

out = pl.read_parquet("data/silver/entsoe/outages_offshore_grid/**/*.parquet")
fc = pl.read_parquet("data/silver/entsoe/wind_solar_forecast/**/*.parquet")
# Offshore outages should produce a B18 (Wind offshore) forecast-actual gap
print(out.tail())
```

# Caveats

## 01 Optional parameters per connector

A79 has only `DocStatus` and `mRID` in `optional_params` (`endpoints.py L80`) — no `BusinessType` filter pinned. *(Source: `endpoints.py L75-81`.)*

## 02 asset_mrid not unit_mrid

A79 uses `asset_mrid` (cable / substation) — same shape as `outages_transmission`. *(Source: `schemas/entsoe.py L511-512`.)*

## 03 H7 transformer family

Uses shared `_H7OutageTransformer` base. Single-zone domain (not zone-pair). *(Source: `silver/entsoe/outages_h7.py L160-179`.)*

## 04 `outage_type` is Optional

For this dataset only, `outage_type` defaults to `""` (not required). Some A79 publications don't carry a businessType. *(Source: `schemas/entsoe.py L513`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/25-outages-offshore-grid-http-401.md`.)*

# Related datasets

- **`outages_transmission`** — A78 transmission outages. `as published`. Onshore counterpart; this dataset is a specialised offshore subset. `entsoe · outages · as-published`
- **`outages_generation`** — A80 generation unit outages. `as published`. Wind turbine outages would also surface there (when reported as unit outages). `entsoe · outages · as-published`
- **`wind_solar_forecast`** — Day-ahead wind / solar forecast. `PT60M`. Compare against realised generation to attribute forecast error to offshore outages. `entsoe · forecast · hourly`
- **`actual_generation`** — Realised generation by PSR / zone. `PT15M-PT60M`. Offshore outages produce a `B18` (Wind offshore) generation drop. `entsoe · generation · hourly`
