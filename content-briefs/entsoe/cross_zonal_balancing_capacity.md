---
slug: cross_zonal_balancing_capacity
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A38/A51
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/11-cross-zonal-balancing-capacity-http-401.md)"
sources_consulted:
  - vault/entsoe/cross_zonal_balancing_capacity.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeCrossZonalBalancingCapacity (lines 659-677)
  - gridflow/src/gridflow/silver/entsoe/h8_balancing.py::CrossZonalBalancingCapacityTransformer (lines 164-191)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["cross_zonal_balancing_capacity"] (lines 353-360)
  - .planning/reconciliation/entsoe/11-cross-zonal-balancing-capacity-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/49-cross-zonal-balancing-capacity-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Cross-zonal balancing capacity, <span class="italic fg-accent">A38/A51.</span>

**Lede:** Cross-zonal balancing capacity allocation in MW per acquiring / connecting area pair — the capacity reserved on interconnectors for cross-border balancing energy exchange.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.cross_zonal_balancing_capacity` |
| API PATH | `/api?documentType=A38&processType=A51` |
| FREQUENCY | PT60M typical |
| PUBLICATION LAG | as published |
| VOLUME | varies by border |
| PRIMARY KEY | `(timestamp_utc, acquiring_area_code, connecting_area_code, market_agreement_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A38 | DocumentType |
| 2 | A51 | processType |
| 3 | zone-pair | Distinct: acquiring + connecting areas |
| 4 | 8 | Schema columns |

# Sidebar siblings

- procured_balancing_capacity
- contracted_reserves
- balancing_energy_bids
- aggregated_balancing_energy_bids
- net_transfer_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB ↔ FR cross-zonal balancing capacity · 24h"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 95
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeCrossZonalBalancingCapacity` (lines 659-677). Unique among H8 datasets: uses `acquiring_area_code` + `connecting_area_code` (not just `area_code`). Override `_rename_domain_columns` handles this.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC. | `schemas/entsoe.py L662, L672-677` |
| `acquiring_area_code` | `str` | No | `<Acquiring_Domain.mRID>` | Acquiring (importing) area EIC. | `schemas/entsoe.py L663`; `silver/entsoe/h8_balancing.py L188` |
| `connecting_area_code` | `str` | No | `<Connecting_Domain.mRID>` | Connecting (exporting) area EIC. | `schemas/entsoe.py L664`; `silver/entsoe/h8_balancing.py L189` |
| `quantity_mw` | `float` | No | `<Point><quantity>` | Cross-zonal capacity MW. | `schemas/entsoe.py L665` |
| `market_agreement_type` | `str` | Yes (default `""`) | `<Type_MarketAgreement.Type>` | Contract type (A01 daily, etc.). | `schemas/entsoe.py L666` |
| `business_type` | `str` | Yes (default `""`) | `<businessType>` | Reserve product code. | `schemas/entsoe.py L667` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L668` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L669` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L670` |

**PARQUET PATH:** `data/silver/entsoe/cross_zonal_balancing_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, acquiring_area_code, connecting_area_code, market_agreement_type)` (`silver/entsoe/h8_balancing.py L180-185`)

# Sample data

| timestamp_utc | acquiring_area_code | connecting_area_code | quantity_mw | market_agreement_type | business_type | resolution | data_provider |
|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10YGB----------A | 10YFR-RTE------C | 300.0 | A01 | B95 | PT60M | entsoe |
| **2026-05-06T17:00:00+00:00** | **10YGB----------A** | **10YFR-RTE------C** | **500.0** | **A01** | **B95** | **PT60M** | **entsoe** |
| 2026-05-06T17:00:00+00:00 | 10YFR-RTE------C | 10YGB----------A | 400.0 | A01 | B95 | PT60M | entsoe |

**Sources:** Synthesised. The highlighted **GB acquiring 500 MW from FR at 17:00** illustrates cross-border balancing capacity reservation: GB reserves 500 MW of IFA capacity for balancing energy import during the evening peak. This is a slice of the underlying NTC dedicated to balancing rather than commercial flow.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A38&processType=A51&Acquiring_Domain={EIC}&Connecting_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/cross_zonal_balancing_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.h8_balancing.CrossZonalBalancingCapacityTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A38&processType=A51&Acquiring_Domain=10YGB----------A&Connecting_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Cross-zonal balancing capacity per acquiring area (last 30 days)
SELECT acquiring_area_code, connecting_area_code,
       avg(quantity_mw) AS mean_capacity_mw,
       max(quantity_mw) AS peak_capacity_mw
FROM read_parquet('data/silver/entsoe/cross_zonal_balancing_capacity/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 30 DAY
GROUP BY 1, 2 ORDER BY peak_capacity_mw DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

xz = pl.read_parquet("data/silver/entsoe/cross_zonal_balancing_capacity/**/*.parquet")
ntc = pl.read_parquet("data/silver/entsoe/net_transfer_capacity/**/*.parquet")
# What fraction of NTC is reserved for balancing?
joined = xz.join(
    ntc.rename({"in_area_code": "connecting_area_code", "out_area_code": "acquiring_area_code"}),
    on=["timestamp_utc", "acquiring_area_code", "connecting_area_code"],
)
print(joined.with_columns(
    (pl.col("quantity_mw") / pl.col("ntc_mw")).alias("balancing_share")
).tail())
```

# Caveats

## 01 acquiring + connecting domains (not in/out)

A38 uses `Acquiring_Domain` / `Connecting_Domain` — distinct from the in_/out_Domain naming of cross-border flow datasets. *(Source: `endpoints.py L353-360`; `schemas/entsoe.py L663-664`.)*

## 02 Custom _rename_domain_columns

Unique among H8 datasets — the transformer overrides `_rename_domain_columns` to map both Acquiring_Domain and Connecting_Domain. *(Source: `silver/entsoe/h8_balancing.py L187-191`.)*

## 03 Type_MarketAgreement.Type optional

Connector exposes as optional. *(Source: `endpoints.py L359`.)*

## 04 Revisions overwrite

Same `(timestamp_utc, acquiring_area_code, connecting_area_code, market_agreement_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/h8_balancing.py L180-185`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/11-cross-zonal-balancing-capacity-http-401.md`.)*

# Related datasets

- **`procured_balancing_capacity`** — A15/A51 domestic procurement. `PT60M`. Domestic counterpart; cross-zonal supplements this. `entsoe · balancing · hourly`
- **`contracted_reserves`** — A81 contracted reserves. `PT60M`. Pre-arranged reserves include both domestic and cross-zonal sources. `entsoe · balancing · hourly`
- **`net_transfer_capacity`** — A61 day-ahead NTC. `PT60M`. Balancing-reserved capacity is a slice of this commercial-NTC denominator. `entsoe · transmission · hourly`
- **`activated_balancing_qty`** — A83/A16 activation. `PT60M`. Cross-zonal capacity allows imported balancing energy to count toward activation. `entsoe · balancing · hourly`
