---
slug: generation_forecast
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A71/A01
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/14-generation-forecast-http-401.md)"
sources_consulted:
  - vault/entsoe/generation_forecast.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeGenerationForecast (lines 197-216)
  - gridflow/src/gridflow/silver/entsoe/generation_forecast.py::GenerationForecastTransformer (lines 18-94)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["generation_forecast"] (lines 100-102)
  - .planning/reconciliation/entsoe/14-generation-forecast-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/52-generation-forecast-resolution-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** TSO day-ahead generation forecast, <span class="italic fg-accent">all PSR types.</span>

**Lede:** Day-ahead total generation forecast in MW per bidding zone — the TSO-published reference covering all dispatchable + non-dispatchable PSR types, distinct from the wind-and-solar-only A69 surface.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.generation_forecast` |
| API PATH | `/api?documentType=A71&processType=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 ~18:00 UTC |
| VOLUME | 1 TimeSeries / zone / day (aggregate) |
| PRIMARY KEY | `(timestamp_utc, area_code, production_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A71 | DocumentType |
| 2 | D-1 | Publication |
| 3 | XML | `GL_MarketDocument` |
| 4 | 7 | Schema columns |

# Sidebar siblings

- actual_generation
- wind_solar_forecast
- load_forecast
- forecast_margin
- installed_capacity

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU day-ahead generation forecast · 24-hour"
- **Subtitle:** "Line · MW · UTC · 6 May 2026"
- **Seed:** 17
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeGenerationForecast` (lines 197-216). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L204, L211-216` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L205` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` if present | A71/A01 aggregate often has no `MktPSRType` — `"unknown"` fallback. | `schemas/entsoe.py L206`; `silver/entsoe/generation_forecast.py L69-74` |
| `generation_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L207` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L208` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L209` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/generation_forecast.py L83` |

**PARQUET PATH:** `data/silver/entsoe/generation_forecast/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, production_type)` (`silver/entsoe/generation_forecast.py L76-78`)

# Sample data

| timestamp_utc | area_code | production_type | generation_forecast_mw | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-05T22:00:00+00:00 | 10Y1001A1001A82H | unknown | 52310.0 | PT60M | entsoe |
| 2026-05-05T23:00:00+00:00 | 10Y1001A1001A82H | unknown | 49802.0 | PT60M | entsoe |
| **2026-05-06T11:00:00+00:00** | **10Y1001A1001A82H** | **unknown** | **78420.0** | **PT60M** | **entsoe** |
| 2026-05-06T18:00:00+00:00 | 10Y1001A1001A82H | unknown | 68150.0 | PT60M | entsoe |

**Sources:** First row verbatim from vault Silver Sample (DE-LU 2026-05-05/06, `generation_forecast_mw=52310`); remaining synthesised to illustrate the diurnal shape. The highlighted **SP12 (78.4 GW)** row is the typical morning peak forecast — when this aggregate diverges from `wind_solar_forecast` + thermal `installed_capacity` the gap is the TSO's load expectation.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A71&processType=A01&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/generation_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.generation_forecast.GenerationForecastTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A71&processType=A01&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily peak forecast generation per zone (last 7 days)
SELECT date_trunc('day', timestamp_utc) AS day, area_code,
       max(generation_forecast_mw) AS peak_forecast_mw
FROM read_parquet('data/silver/entsoe/generation_forecast/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

gen = pl.read_parquet("data/silver/entsoe/generation_forecast/**/*.parquet")
load = pl.read_parquet("data/silver/entsoe/load_forecast/**/*.parquet")
# Demand-supply imbalance forecast — a baseline price-direction feature
gap = gen.join(load, on=["timestamp_utc", "area_code"]).with_columns(
    (pl.col("generation_forecast_mw") - pl.col("load_forecast_mw")).alias("gap_mw"),
)
print(gap.select(["timestamp_utc", "area_code", "gap_mw"]).tail())
```

# Caveats

## 01 GB EMPTY post-Brexit

GB returns `Acknowledgement` reason 999. No GB equivalent — Elexon `ndf` is residual demand forecast, not gross generation. *(Source: vault Known Issues #1.)*

## 02 A71 doc type shared with installed_capacity_units

`A71` is reused for `installed_capacity_units` (A71/A33) with a different `processType`. Select on dataset key, not `documentType` alone. *(Source: `endpoints.py L93-98`.)*

## 03 `production_type` defaults to `"unknown"`

Aggregate A71/A01 often contains no `MktPSRType` element — silver fills with `"unknown"`. *(Source: `silver/entsoe/generation_forecast.py L69-74`.)*

## 04 Forecast revisions overwrite

Same `(timestamp_utc, area_code, production_type)` re-publication overwrites silently on dedup. No `published_at` for PIT. *(Source: `silver/entsoe/generation_forecast.py L76-78`.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/14-generation-forecast-http-401.md`.)*

# Related datasets

- **`wind_solar_forecast`** — Wind / solar subset of generation forecast (A69). `PT60M`. The variable-renewable component that this aggregate sums over. `entsoe · forecast · hourly`
- **`actual_generation`** — Realised counterpart to this forecast. `PT15M-PT60M`. Forecast skill metric: `forecast_error = actual - generation_forecast`. `entsoe · generation · hourly`
- **`load_forecast`** — TSO day-ahead load forecast. `PT60M`. Pair to compute demand-supply imbalance forecast. `entsoe · load · hourly`
- **`forecast_margin`** — Year-ahead margin between generation forecast and load forecast. `annual`. Long-horizon complement to the day-ahead view this dataset provides. `entsoe · forecast · annual`
