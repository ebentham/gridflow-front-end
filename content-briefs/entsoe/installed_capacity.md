---
slug: installed_capacity
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A68/A33
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/16-installed-capacity-http-401.md)"
sources_consulted:
  - vault/entsoe/installed_capacity.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeInstalledCapacity (lines 154-173)
  - gridflow/src/gridflow/silver/entsoe/installed_capacity.py::InstalledCapacityTransformer (lines 18-95)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["installed_capacity"] (lines 90-92)
  - .planning/reconciliation/entsoe/16-installed-capacity-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/54-installed-capacity-resolution-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Installed capacity by zone and PSR, <span class="italic fg-accent">year-ahead snapshot.</span>

**Lede:** Yearly installed generation capacity in MW per bidding zone broken out by PSR — the structural denominator for capacity-factor models and new-build / closure trend tracking.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.installed_capacity` |
| API PATH | `/api?documentType=A68&processType=A33` |
| FREQUENCY | annual (P1Y) |
| PUBLICATION LAG | year boundary |
| VOLUME | ~20 TimeSeries / zone / year |
| PRIMARY KEY | `(timestamp_utc, area_code, production_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | P1Y | Resolution |
| 2 | A33 | Year-ahead processType |
| 3 | XML | `GL_MarketDocument` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- installed_capacity_units
- generation_units_master_data
- actual_generation
- generation_forecast
- water_reservoirs

# Sample chart

- **Type:** `barsH`
- **Title:** "DE-LU installed capacity by PSR · 2026"
- **Subtitle:** "Horizontal bars · MW · year-ahead"
- **Seed:** 19
- **Toggles:** `2026` (active) / `2025` / `2024`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeInstalledCapacity` (lines 154-173). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start (year boundary) | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L161, L168-173` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L162` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | EIC PSR code (B01..B25); `"unknown"` if absent. | `schemas/entsoe.py L163`; `silver/entsoe/installed_capacity.py L70-75` |
| `capacity_mw` | `float` | No | `<Point><quantity>` | MW installed capacity. | `schemas/entsoe.py L164` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `P1Y`. | `schemas/entsoe.py L165` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L166` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/installed_capacity.py L84` |

**PARQUET PATH:** `data/silver/entsoe/installed_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, production_type)` (`silver/entsoe/installed_capacity.py L77-79`)

# Sample data

| timestamp_utc | area_code | production_type | capacity_mw | resolution | data_provider |
|---|---|---|---|---|---|
| **2026-01-01T00:00:00+00:00** | **10Y1001A1001A82H** | **B16** | **9000.0** | **P1Y** | **entsoe** |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B19 | 60800.0 | P1Y | entsoe |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B18 | 8420.0 | P1Y | entsoe |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B14 | 0.0 | P1Y | entsoe |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B05 | 17500.0 | P1Y | entsoe |
| 2026-01-01T00:00:00+00:00 | 10Y1001A1001A82H | B04 | 32100.0 | P1Y | entsoe |

**Sources:** Highlighted **B16 (Solar) 9 GW** row verbatim from vault Silver Sample (`capacity_mw=9000.0`); remaining rows synthesised against DE-LU 2026 declared mix (post-nuclear-phaseout: `B14 = 0`). Illustrative — the solar / wind / coal / gas mix shape is what makes A68 useful as a structural denominator.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A68&processType=A33&in_Domain={EIC}&periodStart={YYYY01010000}&periodEnd={YYYY12310000}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/installed_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.installed_capacity.InstalledCapacityTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A68&processType=A33&in_Domain=10Y1001A1001A82H&periodStart=202601010000&periodEnd=202612310000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Year-over-year mix change per zone
SELECT timestamp_utc::date AS year_start, area_code, production_type,
       capacity_mw, lag(capacity_mw) OVER (
         PARTITION BY area_code, production_type ORDER BY timestamp_utc
       ) AS prev_year_mw
FROM read_parquet('data/silver/entsoe/installed_capacity/**/*.parquet')
ORDER BY area_code, production_type, year_start;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cap = pl.read_parquet("data/silver/entsoe/installed_capacity/**/*.parquet")
gen = pl.read_parquet("data/silver/entsoe/actual_generation/**/*.parquet")
# Capacity factor per PSR per zone (annual mean output / installed capacity)
util = gen.group_by(["area_code", "production_type"]).agg(
    pl.col("generation_mw").mean().alias("mean_mw"),
).join(cap, on=["area_code", "production_type"])
print(util.with_columns(
    (pl.col("mean_mw") / pl.col("capacity_mw")).alias("cf")
).sort("cf", descending=True).head())
```

# Caveats

## 01 Use a yearly window — P1Y resolution

Short windows return EMPTY. Build period bounds at year boundaries. *(Source: vault Known Issues #1.)*

## 02 GB EMPTY post-Brexit

GB capacity registry is via Elexon and DUKES instead of ENTSO-E. *(Source: vault Known Issues #2.)*

## 03 Distinct from installed_capacity_units

A68 is aggregate by PSR type. A71/A33 (`installed_capacity_units`) is unit-level. Same `processType` A33; select on dataset key. *(Source: vault Known Issues #4.)*

## 04 Intra-year ingestion is idempotent

Values change at year boundaries; intra-year re-ingestion just rewrites the same data on `keep="last"` dedup. *(Source: `silver/entsoe/installed_capacity.py L77-79`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/16-installed-capacity-http-401.md`.)*

# Related datasets

- **`installed_capacity_units`** — Per-unit version of this dataset. `yearly`. Disaggregates the aggregate PSR-type rows into individual plants. `entsoe · generation · yearly`
- **`actual_generation`** — Realised output by PSR per zone. `PT15M-PT60M`. Combine with this dataset for utilisation rates (capacity factor). `entsoe · generation · hourly`
- **`generation_units_master_data`** — Per-unit reference data for the EIC unit registry. `static`. Use to enrich unit-level capacity rows. `entsoe · generation · static`
- **`forecast_margin`** — Year-ahead margin between generation and load forecasts. `annual`. Demand-side companion to this supply-side annual view. `entsoe · forecast · annual`
