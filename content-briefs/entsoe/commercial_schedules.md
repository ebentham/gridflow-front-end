---
slug: commercial_schedules
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A09
last_verified: 2026-05-11
entitlement_required: false
sources_consulted:
  - vault/entsoe/commercial_schedules.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeTransmissionMarketQuantity (lines 557-574, H6 shared class)
  - gridflow/src/gridflow/silver/entsoe/h6_market.py::CommercialSchedulesTransformer (lines 132-135, subclass of _H6QuantityTransformer)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["commercial_schedules"] (lines 148-154)
  - .planning/reconciliation/entsoe/43-commercial-schedules-manual-transformer-schema.md (wontfix v3-candidate — stale; class now exists)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found:
  - source_a: "reconciliation finding 43 (manual_transformer_schema)"
    source_a_says: "No importable Pydantic class declared for commercial_schedules"
    source_b: "schemas/entsoe.py L557-574 (EntsoeTransmissionMarketQuantity)"
    source_b_says: "The shared H6 class IS importable and used by silver/entsoe/h6_market.py L27 — finding is stale (closed by H6 refactor)"
    orchestrator_recommendation: "Surface in Caveats as a closed-but-stale finding. The class is real and shared across the H6 family."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Final commercial schedules, <span class="italic fg-accent">per border.</span>

**Lede:** Hourly aggregated final commercial schedules per zone-pair direction — the nominated commercial flow after capacity allocation, distinct from realised physical flow.

**Verified line:** Verified against vendor docs: 2026-05-11 · [ENTSO-E Transparency · A09](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.commercial_schedules` |
| API PATH | `/api?documentType=A09` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 after gate closure |
| VOLUME | 24 points / border-direction / day |
| PRIMARY KEY | `(timestamp_utc, in_area_code, out_area_code, business_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A09 | DocumentType |
| 2 | D-1 | Publication |
| 3 | H6 | Shared transformer family |
| 4 | 8 | Schema columns |

# Sidebar siblings

- cross_border_flows
- net_transfer_capacity
- net_positions
- redispatching_cross_border
- transfer_capacity_use

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB → FR commercial schedule · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 45
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Shared H6-family class in `gridflow/schemas/entsoe.py` · `EntsoeTransmissionMarketQuantity` (lines 557-574). Used by 12 zone-pair quantity datasets; differentiated by dataset-key dispatch in `silver/entsoe/h6_market.py`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L560, L569-574` |
| `in_area_code` | `str` | No | `<in_Domain.mRID>` | Source zone EIC. | `schemas/entsoe.py L561`; `silver/entsoe/h6_market.py L64` |
| `out_area_code` | `str` | No | `<out_Domain.mRID>` | Destination zone EIC. | `schemas/entsoe.py L562`; `silver/entsoe/h6_market.py L65` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Commercial nomination MW (directional). | `schemas/entsoe.py L563`; `silver/entsoe/h6_market.py L63` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Typically `A06` for commercial schedules. | `schemas/entsoe.py L564` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L565` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L566` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L567` |

**PARQUET PATH:** `data/silver/entsoe/commercial_schedules/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, in_area_code, out_area_code, business_type)` (`silver/entsoe/h6_market.py L85-91`)

# Sample data

| timestamp_utc | in_area_code | out_area_code | quantity_mw | business_type | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 1850.0 | A06 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-05-06T11:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | -200.0 | A06 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T19:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **3950.0** | **A06** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T19:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 0.0 | A06 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised against the typical GB ↔ FR commercial-schedule shape. The highlighted **GB → FR 19:00 (3.95 GW)** row mirrors the physical flow at the same hour (`cross_border_flows.flow_mw=3920 MW`) — the gap between commercial and physical (30 MW) is the typical intraday adjustment / loss. Note SP11 negative value: when GB imports cheaper FR power, the commercial nomination is signed in the reverse direction.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A09&in_Domain={EIC}&out_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/commercial_schedules/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h6_market.CommercialSchedulesTransformer` (shared H6 base)

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A09&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000&contract_MarketAgreement.Type=A01
```

**Tab 2 — DuckDB · SQL**
```sql
-- Commercial vs physical gap per hour (GB-FR)
SELECT c.timestamp_utc, c.quantity_mw AS commercial,
       p.flow_mw AS physical,
       p.flow_mw - c.quantity_mw AS gap_mw
FROM read_parquet('data/silver/entsoe/commercial_schedules/**/*.parquet') c
JOIN read_parquet('data/silver/entsoe/cross_border_flows/**/*.parquet') p
  ON c.timestamp_utc = p.timestamp_utc
 AND c.in_area_code = p.in_area_code
 AND c.out_area_code = p.out_area_code
WHERE c.in_area_code = '10YGB----------A' AND c.out_area_code = '10YFR-RTE------C'
ORDER BY abs(gap_mw) DESC LIMIT 20;
```

**Tab 3 — Python · polars**
```python
import polars as pl

sch = pl.read_parquet("data/silver/entsoe/commercial_schedules/**/*.parquet")
# Net commercial position per zone = sum of inbound - sum of outbound
inbound = sch.group_by(["timestamp_utc", "out_area_code"]).agg(
    pl.col("quantity_mw").sum().alias("inbound")
).rename({"out_area_code": "area"})
outbound = sch.group_by(["timestamp_utc", "in_area_code"]).agg(
    pl.col("quantity_mw").sum().alias("outbound")
).rename({"in_area_code": "area"})
net = inbound.join(outbound, on=["timestamp_utc", "area"]).with_columns(
    (pl.col("inbound") - pl.col("outbound")).alias("net_mw")
)
print(net.tail())
```

# Caveats

## 01 A09 dedup resolved in V2 — commercial_schedules_net_positions removed

Per ADR-019 (2026-05-09), the duplicate `commercial_schedules_net_positions` key was removed. This dataset is the sole active A09 surface. *(Source: `endpoints.py L155-159`; vault Implementation Delta.)*

## 02 Pydantic class is shared across H6 family

`EntsoeTransmissionMarketQuantity` covers 12 zone-pair quantity datasets. Reconciliation finding `43-commercial-schedules-manual-transformer-schema.md` is stale (closed by H6 refactor) — class IS importable. *(Source: `schemas/entsoe.py L557`.)*

## 03 Variable-resolution curveType A03

A09 payloads may use `curveType=A03` which compresses unchanged intervals; previous value persists until the next point. Downstream consumers must expand. *(Source: vault Known Issues.)*

## 04 Directional — sum both directions for true commercial position

Each border requires two requests. Net commercial position requires both directions paired. *(Source: vault Known Issues.)*

## 05 Not entitlement-blocked

A09 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key. *(Source: `.planning/reconciliation/entsoe/` — no `commercial_schedules-http-401.md`.)*

# Related datasets

- **`commercial_schedules_net_positions`** — Deprecated pointer (ADR-019). `n/a`. Removed registry duplicate — use this dataset instead. `entsoe · transmission · deprecated`
- **`cross_border_flows`** — Realised physical flow per border. `PT60M`. The physical counterpart; difference is intraday adjustment + losses. `entsoe · transmission · hourly`
- **`net_transfer_capacity`** — Day-ahead NTC denominator. `PT60M`. Commercial schedules clear against this NTC cap. `entsoe · transmission · hourly`
- **`net_positions`** — Implicit-auction net positions per zone. `PT60M`. Derived from commercial schedules via zone-pair aggregation. `entsoe · transmission · hourly`
