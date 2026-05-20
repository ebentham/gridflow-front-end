---
slug: net_positions
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A25 (businessType B09)
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/18-net-positions-http-401.md)"
sources_consulted:
  - vault/entsoe/net_positions.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::NetPositionsTransformer (lines 185-187)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["net_positions"] (lines 282-292)
  - .planning/reconciliation/entsoe/18-net-positions-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/56-net-positions-no-silver-schema-table.md (wontfix v3-candidate — stale; class now exists via H6 shared)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "endpoints.py L282-292 (NetPositions DOC_TYPE)"
    source_a_says: "domain_style='zone' (single zone, not zone-pair) — net_positions queries with just in_Domain"
    source_b: "schemas/entsoe.py L557-574 (EntsoeTransmissionMarketQuantity has in_area_code + out_area_code)"
    source_b_says: "H6 base schema has both in/out area codes; for net_positions out_area_code may equal in_area_code or be empty"
    orchestrator_recommendation: "Surface as a Caveat — net_positions is the only H6 dataset with domain_style='zone' instead of 'zone_pair'. Silver schema is shared, but out_area_code may be redundant or empty for this dataset."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Implicit-auction net positions, <span class="italic fg-accent">A25/B09.</span>

**Lede:** Hourly implicit-auction net positions in MW per bidding zone — the day-ahead clearing-time net position from coupling, distinct from physical flow or commercial schedule.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.net_positions` |
| API PATH | `/api?documentType=A25&businessType=B09` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | 24 points / zone / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A25 | DocumentType |
| 2 | B09 | businessType |
| 3 | zone | `domain_style` (not zone-pair) |
| 4 | 8 | Schema columns |

# Sidebar siblings

- commercial_schedules
- cross_border_flows
- day_ahead_prices
- offered_transfer_capacity_implicit
- auction_revenue

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU net position · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 69
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class `EntsoeTransmissionMarketQuantity` (`schemas/entsoe.py L557-574`). For net_positions, `domain_style="zone"` (single-zone surface), so `out_area_code` may equal `in_area_code` or be empty depending on API response shape.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L560` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Bidding zone EIC. | `schemas/entsoe.py L561` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | May equal in_area_code (single-zone surface). | `schemas/entsoe.py L562` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Net position MW (positive = export, negative = import). | `schemas/entsoe.py L563` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | B09 — implicit auction net positions. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/net_positions/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)`

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | 4820.0 | B09 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T11:00:00+00:00** | **10Y1001A1001A82H** | **10Y1001A1001A82H** | **8410.0** | **B09** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10Y1001A1001A82H | 10Y1001A1001A82H | -1820.0 | B09 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **DE-LU 11:00 (+8.41 GW export)** row reflects a typical solar-peak hour: Germany exports 8 GW net across all interconnectors. The 19:00 row shows -1.82 GW import — winter-evening pattern when DE-LU draws from neighbours.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A25&businessType=B09&contract_MarketAgreement.Type=A01&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/net_positions/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.NetPositionsTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B09&contract_MarketAgreement.Type=A01&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily net export hours per zone (last 30 days)
SELECT date_trunc('day', timestamp_utc) AS day, in_area_code AS zone,
       count(*) FILTER (WHERE quantity_mw > 0) AS export_hours,
       count(*) FILTER (WHERE quantity_mw < 0) AS import_hours,
       avg(quantity_mw) AS mean_net_mw
FROM read_parquet('data/silver/entsoe/net_positions/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2
ORDER BY 1, mean_net_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

np_ = pl.read_parquet("data/silver/entsoe/net_positions/**/*.parquet")
flows = pl.read_parquet("data/silver/entsoe/cross_border_flows/**/*.parquet")
# DIY net position from flows (sum over border-direction) vs published
diy = flows.group_by(["timestamp_utc", "in_area_code"]).agg(
    pl.col("flow_mw").sum().alias("diy_export_mw")
).rename({"in_area_code": "zone"})
print(diy.tail())
```

# Caveats

## 01 `domain_style="zone"` — not zone_pair

Net_positions is the only H6 dataset with `domain_style="zone"` (single zone). Query with `in_Domain` only; `out_area_code` may equal in_area_code or be empty. *(Source: `endpoints.py L286`; frontmatter discrepancy.)*

## 02 A25 is heavily overloaded

A25 covers `net_positions` (B09), `transfer_capacity_use` (B05), `auction_revenue` (B07), `congestion_income` (B10). Always select on `(documentType, businessType)` pair. *(Source: `endpoints.py L229-291`.)*

## 03 Net position vs net flow

Published net position is the implicit-auction clearing result; net physical flow may differ due to intraday adjustment. Both views are useful for different purposes. *(Source: vault Known Issues.)*

## 04 Pydantic class is shared (H6 family)

`EntsoeTransmissionMarketQuantity` covers 12 H6 datasets. Finding `56-net-positions-no-silver-schema-table.md` (wontfix v3-candidate) is stale — class exists. *(Source: `schemas/entsoe.py L557`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/18-net-positions-http-401.md`.)*

# Related datasets

- **`commercial_schedules`** — Aggregated commercial nominations. `PT60M`. The directional pair view; net_positions is the zonal aggregate. `entsoe · transmission · hourly`
- **`cross_border_flows`** — Realised physical flow per border-direction. `PT60M`. DIY net position = sum of zone-pair flows. `entsoe · transmission · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices. `PT60M`. Net positions and prices clear simultaneously in the implicit auction. `entsoe · prices · hourly`
- **`offered_transfer_capacity_implicit`** — Capacity offered to implicit auction. `PT60M`. Net position is bounded by sum of implicit OTC across borders. `entsoe · transmission · hourly`
