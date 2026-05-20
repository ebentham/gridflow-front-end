---
slug: net_transfer_capacity
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A61/A01
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/19-net-transfer-capacity-http-401.md)"
sources_consulted:
  - vault/entsoe/net_transfer_capacity.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeNetTransferCapacity (lines 313-335)
  - gridflow/src/gridflow/silver/entsoe/net_transfer_capacity.py::NetTransferCapacityTransformer (lines 18-93)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["net_transfer_capacity"] (lines 135-141)
  - .planning/reconciliation/entsoe/19-net-transfer-capacity-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/57-net-transfer-capacity-resolution-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Forecasted transfer capacity, <span class="italic fg-accent">day-ahead.</span>

**Lede:** Day-ahead forecasted net transfer capacity in MW per zone-pair direction — the capacity denominator for interconnector utilisation modelling and the cap that day-ahead implicit auctions clear against.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.net_transfer_capacity` |
| API PATH | `/api?documentType=A61&contract_MarketAgreement.Type=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A61 | DocumentType |
| 2 | D-1 | Publication |
| 3 | zone-pair | `domain_style` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- cross_border_flows
- offered_transfer_capacity_continuous
- offered_transfer_capacity_implicit
- transfer_capacity_use
- commercial_schedules

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR NTC · 24-hour"
- **Subtitle:** "Line · MW · UTC · day-ahead"
- **Seed:** 43
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeNetTransferCapacity` (lines 313-335). G5-W3 (2026-05) added `ingested_at`. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L322, L330-335` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L323` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L324` |
| `ntc_mw` | `float` | No | `<Point><quantity>` | Net transfer capacity in MW (directional). | `schemas/entsoe.py L325` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L326` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L327` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. Added G5-W3 to match transformer. | `schemas/entsoe.py L328` |

**PARQUET PATH:** `data/silver/entsoe/net_transfer_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code)` (`silver/entsoe/net_transfer_capacity.py L73-75`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | ntc_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 4000.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T06:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 4000.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T11:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **2800.0** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 4000.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T19:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 4000.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised against typical GB-FR NTC shape — full 4 GW available most hours, derated to 2.8 GW during a planned outage at SP11. The highlighted **GB → FR 11:00 (2.8 GW)** row is the canonical derated-NTC hour: the TSOs reduce NTC for maintenance, which then caps how much commercial flow can clear in day-ahead. Pair with `cross_border_flows` for utilisation (`flow / ntc`).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A61&contract_MarketAgreement.Type=A01&In_Domain={EIC}&Out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/net_transfer_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.net_transfer_capacity.NetTransferCapacityTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A61&contract_MarketAgreement.Type=A01&In_Domain=10YGB----------A&Out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Interconnector utilisation per border-direction per hour
SELECT n.timestamp_utc, n.in_area_code, n.out_area_code,
       n.ntc_mw, f.flow_mw, f.flow_mw / n.ntc_mw AS utilisation
FROM read_parquet('data/silver/entsoe/net_transfer_capacity/**/*.parquet') n
JOIN read_parquet('data/silver/entsoe/cross_border_flows/**/*.parquet') f
  ON n.timestamp_utc = f.timestamp_utc
 AND n.in_area_code = f.in_area_code
 AND n.out_area_code = f.out_area_code
WHERE n.ntc_mw > 0
ORDER BY utilisation DESC LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ntc = pl.read_parquet("data/silver/entsoe/net_transfer_capacity/**/*.parquet")
# Per-border NTC profile — does NTC derate at predictable hours?
profile = ntc.with_columns(pl.col("timestamp_utc").dt.hour().alias("hour")).group_by(
    ["in_area_code", "out_area_code", "hour"]
).agg(pl.col("ntc_mw").mean().alias("mean_ntc"))
print(profile.sort(["in_area_code", "out_area_code", "hour"]).head(24))
```

# Caveats

## 01 Directional — same border has two NTC values

NTC is asymmetric — GB → FR can differ from FR → GB depending on which constraint binds. Pair both directions for full interconnector picture. *(Source: vault Known Issues.)*

## 02 `contract_MarketAgreement.Type=A01` pinned by connector

Connector pins `A01` (daily auction). Other contract types (intraday A02, monthly A03) return different surfaces. *(Source: `endpoints.py L135-141`.)*

## 03 Domain params capitalised

A61 uses `In_Domain` / `Out_Domain` (capitalised) — different from the lowercase `in_Domain` / `out_Domain` of most ENTSO-E surfaces. *(Source: `endpoints.py L135-141`; vault Known Issues.)*

## 04 Revisions overwrite

Same `(timestamp_utc, in_area_code, out_area_code)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/net_transfer_capacity.py L73-75`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/19-net-transfer-capacity-http-401.md`.)*

# Related datasets

- **`cross_border_flows`** — Realised physical flow per border-direction. `PT60M`. The numerator for utilisation; pair on `(timestamp_utc, in_area_code, out_area_code)` for `flow / ntc`. `entsoe · transmission · hourly`
- **`offered_transfer_capacity_implicit`** — Implicit-auction OTC. `PT60M`. The capacity offered into the day-ahead implicit auction; typically ≤ NTC. `entsoe · transmission · hourly`
- **`transfer_capacity_use`** — Settlement-side use of transfer capacity (A25/B05). `PT60M`. Cross-check against this dataset's NTC denominator. `entsoe · transmission · hourly`
- **`day_ahead_prices`** — Day-ahead clearing prices per zone. `PT60M`. NTC caps inform when price spreads can close — when NTC binds, spreads persist. `entsoe · prices · hourly`
