---
slug: outages_consumption
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A76
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/23-outages-consumption-http-401.md)"
sources_consulted:
  - vault/entsoe/outages_consumption.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeOutagesConsumption (lines 457-477)
  - gridflow/src/gridflow/silver/entsoe/outages_h7.py::OutagesConsumptionTransformer (lines 109-127)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["outages_consumption"] (lines 58-65)
  - .planning/reconciliation/entsoe/23-outages-consumption-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/61-outages-consumption-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Consumption unit outages, <span class="italic fg-accent">A76.</span>

**Lede:** Aggregated unavailability of consumption units per zone — large-load outages (industrial consumers, smelters) without unit identification, useful for demand-side capacity-margin modelling.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.outages_consumption` |
| API PATH | `/api?documentType=A76&BusinessType=A53` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time |
| VOLUME | varies by zone (rare) |
| PRIMARY KEY | `(timestamp_utc, area_code, business_type, timeseries_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A76 | DocumentType |
| 2 | bidding_zone | `domain_style` |
| 3 | aggregated | Unit identification |
| 4 | 11 | Schema columns |

# Sidebar siblings

- outages_generation
- outages_production
- outages_transmission
- outages_offshore_grid
- actual_load

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU consumption outages · 90 days"
- **Subtitle:** "Line · MW unavailable · UTC"
- **Seed:** 75
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeOutagesConsumption` (lines 457-477). H7-family transformer. No unit_mrid — aggregated at zone level.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L460, L472-477` |
| `area_code` | `str` | No | `<BiddingZone_Domain.mRID>` | Bidding zone EIC. | `schemas/entsoe.py L461` |
| `outage_type` | `str` | No | derived from `<businessType>` | `"planned"` (A53) / `"unplanned"` (A54). | `schemas/entsoe.py L462`; `silver/entsoe/outages_h7.py L91-95` |
| `unavailable_mw` | `float` | No | `<Point><quantity>` | MW unavailable (aggregated). | `schemas/entsoe.py L463` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` (raw) | A53 / A54. | `schemas/entsoe.py L464` |
| `document_mrid` | `str` | Yes (default `""`) | `<mRID>` (root) | Document-level identifier. | `schemas/entsoe.py L465` |
| `document_status` | `str` | Yes (default `""`) | `<docStatus>` | Status code. | `schemas/entsoe.py L466` |
| `timeseries_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` | TimeSeries within document. | `schemas/entsoe.py L467` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L468` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L469` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L470` |

**PARQUET PATH:** `data/silver/entsoe/outages_consumption/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, business_type, timeseries_mrid)` (`silver/entsoe/outages_h7.py L126`)

# Sample data

| timestamp_utc | area_code | outage_type | unavailable_mw | business_type | document_mrid | document_status | timeseries_mrid | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T08:00:00+00:00 | 10Y1001A1001A82H | planned | 120.0 | A53 | doc-101 | A05 | ts-001 | PT60M | entsoe |
| **2026-05-06T14:00:00+00:00** | **10Y1001A1001A82H** | **unplanned** | **480.0** | **A54** | **doc-102** | **A05** | **ts-001** | **PT60M** | **entsoe** |

**Sources:** Synthesised. The highlighted **DE-LU unplanned 480 MW consumption outage** illustrates a large industrial consumer trip (e.g. aluminium smelter line) — these are rare events but affect short-term demand forecast accuracy. Consumption-side outages are aggregated; no unit identification is published (privacy / commercial-sensitivity).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A76&BusinessType=A53&BiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/outages_consumption/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.outages_h7.OutagesConsumptionTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A76&BusinessType=A53&BiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Consumption outage events by zone (last 90 days)
SELECT area_code, outage_type, count(DISTINCT document_mrid) AS events,
       sum(unavailable_mw) AS total_mwh
FROM read_parquet('data/silver/entsoe/outages_consumption/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 90 DAY
GROUP BY 1, 2 ORDER BY total_mwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cons = pl.read_parquet("data/silver/entsoe/outages_consumption/**/*.parquet")
load = pl.read_parquet("data/silver/entsoe/actual_load/**/*.parquet")
# Demand-side outage attribution: did published outage MW match the load drop?
# (Simple matching — production code would window-align)
print(cons.tail())
```

# Caveats

## 01 No unit identification

A76 publishes aggregated zone-level outages — no `unit_mrid` field. Individual consumer plants are not identified (privacy / commercial-sensitivity). *(Source: vault Known Issues.)*

## 02 H7 transformer family

Uses shared `_H7OutageTransformer` base. Dedup on `(timestamp_utc, area_code, business_type, timeseries_mrid)` — no unit_mrid in the key. *(Source: `silver/entsoe/outages_h7.py L109-127`.)*

## 03 Rare events

Consumption outages are published infrequently — many days have zero events. Empty silver partitions are normal. *(Source: vault Known Issues.)*

## 04 Use load_forecast for the demand-side capacity view

For forecast-side demand modelling, `load_forecast` already incorporates expected consumption outages. This dataset is for *unexpected* outages after the forecast is published. *(Source: domain knowledge.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/23-outages-consumption-http-401.md`.)*

# Related datasets

- **`outages_production`** — A77 production unit outages. `as published`. Supply-side analogue. `entsoe · outages · as-published`
- **`outages_generation`** — A80 generation unit outages. `as published`. Older A80 supply-side surface. `entsoe · outages · as-published`
- **`actual_load`** — Realised demand per zone. `PT15M-PT60M`. Compare to identify the demand drop from a published consumption outage. `entsoe · load · hourly`
- **`load_forecast`** — Day-ahead load forecast. `PT60M`. Includes expected consumption outages already; this dataset reports surprises. `entsoe · load · hourly`
