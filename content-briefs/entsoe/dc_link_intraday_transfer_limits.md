---
slug: dc_link_intraday_transfer_limits
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A93
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/13-dc-link-intraday-transfer-limits-http-401.md)"
sources_consulted:
  - vault/entsoe/dc_link_intraday_transfer_limits.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::DcLinkIntradayTransferLimitsTransformer (lines 127-129)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["dc_link_intraday_transfer_limits"] (lines 142-147)
  - .planning/reconciliation/entsoe/13-dc-link-intraday-transfer-limits-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/51-dc-link-intraday-transfer-limits-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Intraday DC-link transfer limits, <span class="italic fg-accent">A93.</span>

**Lede:** Hourly intraday transfer limits for HVDC cross-border links — the capacity ceiling applied to interconnectors like IFA, BritNed, and NordLink for intraday continuous trading.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.dc_link_intraday_transfer_limits` |
| API PATH | `/api?documentType=A93` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | intraday |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A93 | DocumentType |
| 2 | DC-only | Link type |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- net_transfer_capacity
- cross_border_flows
- offered_transfer_capacity_continuous
- transfer_capacity_use
- offered_transfer_capacity_implicit

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → NL DC-link transfer limit · 24-hour"
- **Subtitle:** "Line · MW · UTC · intraday"
- **Seed:** 55
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). See `commercial_schedules.md` for full annotation.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Transfer limit MW. | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | DC-link business type. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/dc_link_intraday_transfer_limits/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YNL----------L | 1000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T06:00:00+00:00 | 10YGB----------A | 10YNL----------L | 1000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T13:00:00+00:00** | **10YGB----------A** | **10YNL----------L** | **600.0** | **A29** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YGB----------A | 10YNL----------L | 1000.0 | A29 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **GB → NL 13:00 (600 MW)** row is a typical intraday derate for BritNed (full capacity 1 GW) — TSOs publish intraday limits to flag mid-day capacity reductions that day-ahead-only NTC misses.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A93&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/dc_link_intraday_transfer_limits/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.DcLinkIntradayTransferLimitsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A93&in_Domain=10YGB----------A&out_Domain=10YNL----------L&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Hours where DC-link limit derates below day-ahead NTC
SELECT d.timestamp_utc, d.in_area_code, d.out_area_code,
       n.ntc_mw, d.quantity_mw AS dc_intraday_limit,
       n.ntc_mw - d.quantity_mw AS derate_mw
FROM read_parquet('data/silver/entsoe/dc_link_intraday_transfer_limits/**/*.parquet') d
JOIN read_parquet('data/silver/entsoe/net_transfer_capacity/**/*.parquet') n
  ON d.timestamp_utc = n.timestamp_utc
 AND d.in_area_code = n.in_area_code
 AND d.out_area_code = n.out_area_code
WHERE n.ntc_mw - d.quantity_mw > 100
ORDER BY derate_mw DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

dc = pl.read_parquet("data/silver/entsoe/dc_link_intraday_transfer_limits/**/*.parquet")
# Per-link distribution of intraday derates
print(dc.group_by(["in_area_code", "out_area_code"]).agg(
    pl.col("quantity_mw").min().alias("min_mw"),
    pl.col("quantity_mw").max().alias("max_mw"),
).sort("min_mw"))
```

# Caveats

## 01 DC-only — not for AC interconnectors

A93 covers HVDC links (IFA, IFA2, ElecLink, BritNed, NordLink, NSL etc.). AC interconnectors use the standard A61 NTC surface. *(Source: vault Known Issues.)*

## 02 Intraday is the timing — not the cadence

The "intraday" in the name refers to which timeframe these limits apply to (intraday continuous trading), not how often they're published. Publication is hourly. *(Source: vault Known Issues.)*

## 03 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. *(Source: `schemas/entsoe.py L557`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code, business_type)` overwrites silently. *(Source: `silver/entsoe/h6_market.py L85-91`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/13-dc-link-intraday-transfer-limits-http-401.md`.)*

# Related datasets

- **`net_transfer_capacity`** — Day-ahead NTC. `PT60M`. The day-ahead capacity; intraday derates from this surface for DC links. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow. `PT60M`. Should never exceed this dataset's limit. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_continuous`** — Continuous OTC. `PT60M`. The continuous-allocation product DC-link operators sell. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — Settlement-side capacity use (A25/B05). `PT60M`. Pair to track DC-link utilisation. `entsoe · transmission · hourly`
