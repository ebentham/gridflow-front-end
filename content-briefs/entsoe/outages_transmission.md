---
slug: outages_transmission
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A78
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/27-outages-transmission-http-401.md)"
sources_consulted:
  - vault/entsoe/outages_transmission.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeOutagesTransmission (lines 480-503)
  - gridflow/src/gridflow/silver/entsoe/outages_h7.py::OutagesTransmissionTransformer (lines 129-158)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["outages_transmission"] (lines 66-74)
  - .planning/reconciliation/entsoe/27-outages-transmission-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/65-outages-transmission-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Transmission infrastructure outages, <span class="italic fg-accent">A78.</span>

**Lede:** Unavailability of transmission infrastructure per zone-pair direction — interconnector and cross-border line outages with asset identification, the canonical input for NTC derate explanation.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.outages_transmission` |
| API PATH | `/api?documentType=A78&BusinessType=A53` |
| FREQUENCY | as published |
| PUBLICATION LAG | real-time |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, asset_mrid, timeseries_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A78 | DocumentType |
| 2 | zone-pair | `domain_style` |
| 3 | H7 | Shared transformer family |
| 4 | 14 | Schema columns |

# Sidebar siblings

- outages_offshore_grid
- outages_generation
- outages_production
- net_transfer_capacity
- cross_border_flows

# Sample chart

- **Type:** `barsH`
- **Title:** "GB ↔ FR transmission outages by asset · 30d"
- **Subtitle:** "Horizontal bars · MW unavailable · UTC"
- **Seed:** 77
- **Toggles:** `30d` (active) / `90d` / `1y`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeOutagesTransmission` (lines 480-503). H7-family transformer. Zone-pair scope (`in_area_code` + `out_area_code`), and includes `asset_mrid` (cable / line identifier) rather than `unit_mrid`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L483, L498-503` |
| `in_area_code` | `str` | No | `<In_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L484` |
| `out_area_code` | `str` | No | `<Out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L485` |
| `asset_mrid` | `str` | Yes (default `""`) | `<RegisteredResource.mRID>` | Asset identifier (cable / line). | `schemas/entsoe.py L486` |
| `asset_name` | `str` | Yes (default `""`) | `<RegisteredResource.name>` | Human-readable asset name (e.g. "IFA2"). | `schemas/entsoe.py L487` |
| `outage_type` | `str` | No | derived from `<businessType>` | `"planned"` (A53) / `"unplanned"` (A54). | `schemas/entsoe.py L488`; `silver/entsoe/outages_h7.py L91-95` |
| `unavailable_mw` | `float` | No | `<Point><quantity>` | MW unavailable on the asset. | `schemas/entsoe.py L489` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` (raw) | A53 / A54. | `schemas/entsoe.py L490` |
| `document_mrid` | `str` | Yes (default `""`) | `<mRID>` (root) | Document-level identifier. | `schemas/entsoe.py L491` |
| `document_status` | `str` | Yes (default `""`) | `<docStatus>` | Status code. | `schemas/entsoe.py L492` |
| `timeseries_mrid` | `str` | Yes (default `""`) | `<TimeSeries><mRID>` | TimeSeries within document. | `schemas/entsoe.py L493` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L494` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L495` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L496` |

**PARQUET PATH:** `data/silver/entsoe/outages_transmission/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, asset_mrid, timeseries_mrid)` (`silver/entsoe/outages_h7.py L151-157`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | asset_mrid | asset_name | outage_type | unavailable_mw | business_type | document_mrid | document_status | timeseries_mrid | resolution | data_provider |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | IFA-CABLE-1 | IFA Pole 1 | planned | 500.0 | A53 | doc-201 | A05 | ts-001 | PT60M | entsoe |
| **2026-05-06T15:00:00+00:00** | **10YGB----------A** | **10YNL----------L** | **BRITNED-1** | **BritNed Pole 1** | **unplanned** | **500.0** | **A54** | **doc-202** | **A05** | **ts-001** | **PT60M** | **entsoe** |

**Sources:** Synthesised. The highlighted **BritNed Pole 1 unplanned 500 MW outage at 15:00** illustrates a HVDC interconnector trip — when published, it directly explains the corresponding NTC derate. Asset identification (`asset_name`) is the key A78 feature that allows linking outages to specific interconnector elements.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A78&BusinessType=A53&In_Domain={EIC}&Out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/outages_transmission/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.outages_h7.OutagesTransmissionTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A78&BusinessType=A53&In_Domain=10YGB----------A&Out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Asset-by-asset outage MW (last 30 days)
SELECT in_area_code, out_area_code, asset_name, outage_type,
       count(*) AS hours_unavail, max(unavailable_mw) AS peak_unavail_mw
FROM read_parquet('data/silver/entsoe/outages_transmission/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2, 3, 4 ORDER BY peak_unavail_mw DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

out = pl.read_parquet("data/silver/entsoe/outages_transmission/**/*.parquet")
ntc = pl.read_parquet("data/silver/entsoe/net_transfer_capacity/**/*.parquet")
# Outage → NTC derate causality (does NTC drop coincide with outages?)
joined = out.join(ntc, on=["timestamp_utc", "in_area_code", "out_area_code"])
print(joined.select(["timestamp_utc", "asset_name", "unavailable_mw", "ntc_mw"]).tail())
```

# Caveats

## 01 Zone-pair scope (In_Domain + Out_Domain capitalised)

A78 uses capitalised `In_Domain` / `Out_Domain` (per `domain_params=("In_Domain", "Out_Domain")` in `endpoints.py L70-72`). Different from lowercase used by most other H6/H7 surfaces. *(Source: `endpoints.py L66-74`.)*

## 02 asset_mrid not unit_mrid

A78 uses `asset_mrid` and `asset_name` (cable / line) rather than `unit_mrid` (generation unit). Don't confuse the two — they live in different columns. *(Source: `schemas/entsoe.py L486-487`.)*

## 03 H7 transformer family

Uses shared `_H7OutageTransformer` base. Adds `asset_mrid` / `asset_name` and zone-pair domains. *(Source: `silver/entsoe/outages_h7.py L129-158`.)*

## 04 Dedup includes asset_mrid

`(timestamp_utc, in_area_code, out_area_code, asset_mrid, timeseries_mrid)` — different assets and TimeSeries survive separately. *(Source: `silver/entsoe/outages_h7.py L151-157`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/27-outages-transmission-http-401.md`.)*

# Related datasets

- **`outages_offshore_grid`** — A79 offshore grid outages. `as published`. Subset of transmission outages — offshore wind cable connections. `entsoe · outages · as-published`
- **`net_transfer_capacity`** — Day-ahead NTC. `PT60M`. Outage MW directly explains NTC derate when published. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow. `PT60M`. Drops when transmission outages bind. `entsoe · transmission · hourly`
- **`dc_link_intraday_transfer_limits`** — A93 DC link limits. `PT60M`. Real-time view of intraday capacity reductions caused by transmission outages. `entsoe · transmission · hourly`
