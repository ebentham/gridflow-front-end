---
slug: outages_generation
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A80
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/24-outages-generation-http-401.md)"
sources_consulted:
  - vault/entsoe/outages_generation.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeOutagesGeneration (lines 126-151)
  - gridflow/src/gridflow/silver/entsoe/outages_generation.py::OutagesGenerationTransformer (lines 19-113)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["outages_generation"] (lines 50-57)
  - .planning/reconciliation/entsoe/24-outages-generation-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/62-outages-generation-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Generation unit outages, <span class="italic fg-accent">A80.</span>

**Lede:** Unavailability of generation units per zone — MW unavailable per unit per interval, mapped from ENTSO-E businessType A53 (planned) / A54 (unplanned), the canonical EU outage feed for capacity-margin modelling.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.outages_generation` |
| API PATH | `/api?documentType=A80&BusinessType=A53` |
| FREQUENCY | as published (event-driven) |
| PUBLICATION LAG | real-time |
| VOLUME | varies by zone |
| PRIMARY KEY | `(timestamp_utc, unit_mrid)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A80 | DocumentType |
| 2 | bidding_zone | `domain_style` |
| 3 | A53/A54 | planned / unplanned |
| 4 | 9 | Schema columns |

# Sidebar siblings

- outages_production
- outages_consumption
- outages_transmission
- outages_offshore_grid
- actual_generation_units

# Sample chart

- **Type:** `barsH`
- **Title:** "DE-LU generation outages by unit · 24h"
- **Subtitle:** "Horizontal bars · MW unavailable · UTC · 6 May 2026"
- **Seed:** 71
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeOutagesGeneration` (lines 126-151). Has its own transformer file (older, A80-specific) — distinct from the H7 outages family that uses `outages_h7.py`. Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L136, L146-151` |
| `area_code` | `str` | No | `<BiddingZone_Domain.mRID>` | Control area / bidding zone EIC. | `schemas/entsoe.py L137` |
| `unit_mrid` | `str` | No | `<RegisteredResource.mRID>` | Unit identifier (opaque). | `schemas/entsoe.py L138` |
| `unit_name` | `str` | Yes (default `""`) | `<RegisteredResource.name>` | Human-readable unit name. | `schemas/entsoe.py L139` |
| `outage_type` | `str` | No | derived from `<businessType>` | `"planned"` (A53) / `"unplanned"` (A54). | `schemas/entsoe.py L140`; `silver/entsoe/outages_generation.py L73-77` |
| `unavailable_mw` | `float` | No | `<Point><quantity>` | MW unavailable during the interval. | `schemas/entsoe.py L141` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration. | `schemas/entsoe.py L142` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L143` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L144` |

**PARQUET PATH:** `data/silver/entsoe/outages_generation/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, unit_mrid)` (`silver/entsoe/outages_generation.py L88-90`)

# Sample data

| timestamp_utc | area_code | unit_mrid | unit_name | outage_type | unavailable_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | 11W-IRSCHING-5 | Irsching 5 | planned | 845.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-05-06T14:00:00+00:00** | **10Y1001A1001A82H** | **11W-WINDPARK-OSTSEE** | **Ostsee Wind 3** | **unplanned** | **620.0** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-05-06T20:00:00+00:00 | 10Y1001A1001A82H | 11W-IRSCHING-5 | Irsching 5 | planned | 845.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised. The highlighted **Ostsee Wind 3 unplanned 620 MW outage at 14:00** illustrates the high-MW unplanned outage profile that drives short-term price spikes — wind farm trips are the most frequent unplanned-outage category in DE-LU. Planned outages (Irsching 5 here) tend to be longer-duration and forecast days in advance.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A80&BusinessType=A53&BiddingZone_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/outages_generation/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.outages_generation.OutagesGenerationTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A80&BusinessType=A53&BiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Top-10 highest-MW unplanned outages last 30 days
SELECT timestamp_utc, area_code, unit_name, outage_type, unavailable_mw
FROM read_parquet('data/silver/entsoe/outages_generation/**/*.parquet')
WHERE outage_type = 'unplanned'
  AND timestamp_utc >= current_timestamp - INTERVAL 30 DAY
ORDER BY unavailable_mw DESC LIMIT 10;
```

**Tab 3 — Python · polars**
```python
import polars as pl

out = pl.read_parquet("data/silver/entsoe/outages_generation/**/*.parquet")
cap = pl.read_parquet("data/silver/entsoe/installed_capacity_units/**/*.parquet")
# Availability factor per unit (1 - sum(unavailable) / hours / capacity)
hours_unavail = out.group_by("unit_mrid").agg(
    pl.col("unavailable_mw").sum().alias("total_mwh_unavail")
).join(cap.select(["unit_mrid", "capacity_mw"]), on="unit_mrid")
print(hours_unavail.with_columns(
    (pl.col("total_mwh_unavail") / pl.col("capacity_mw")).alias("hours_equiv_unavail")
).sort("hours_equiv_unavail", descending=True).head())
```

# Caveats

## 01 outage_type derived from businessType

Transformer maps `businessType=A53` → `"planned"`, `A54` → `"unplanned"`. Other businessType values pass through unchanged. *(Source: `silver/entsoe/outages_generation.py L72-77`.)*

## 02 Connector pins `BusinessType=A53` by default

`endpoints.py` extra_params pins A53 — only planned outages are fetched by default. Unplanned outages (A54) require manual override via `**params`. *(Source: `endpoints.py L54-56`.)*

## 03 Dedup on `(timestamp_utc, unit_mrid)` — no area code

Unique key drops `area_code` because unit_mrid is globally unique. Caveat: if the same unit_mrid appears in multiple areas (rare), only one row survives. *(Source: `silver/entsoe/outages_generation.py L88-90`.)*

## 04 Distinct from H7 outages family

`outages_generation` has its own transformer file (older, A80-specific). The H7 family (`outages_consumption`, `_production`, `_transmission`, `_offshore_grid`) shares `outages_h7.py`. *(Source: gridflow source tree.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/24-outages-generation-http-401.md`.)*

# Related datasets

- **`outages_production`** — A77 production unit outages. `as published`. Similar shape with production_type field; H7 family. `entsoe · outages · as-published`
- **`outages_transmission`** — A78 transmission infrastructure outages. `as published`. Zone-pair scope (`in_area_code` + `out_area_code`). `entsoe · outages · as-published`
- **`installed_capacity_units`** — Per-unit installed capacity. `yearly`. The denominator for availability factor calculation. `entsoe · generation · yearly`
- **`actual_generation_units`** — Per-unit realised output. `hourly`. Outage should correlate with output drop on the same unit. `entsoe · generation · hourly`
