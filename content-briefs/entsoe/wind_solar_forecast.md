---
slug: wind_solar_forecast
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A69/A01
last_verified: 2026-05-08
entitlement_required: true
entitlement_reason: "ENTSO-E API key for this DOC_TYPE requires extended registration tier (HTTP 401 with the gridflow default key — see .planning/reconciliation/entsoe/35-wind-solar-forecast-http-401.md)"
sources_consulted:
  - vault/entsoe/wind_solar_forecast.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeWindSolarForecast (lines 105-123)
  - gridflow/src/gridflow/silver/entsoe/wind_solar_forecast.py::WindSolarForecastTransformer (lines 18-92)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["wind_solar_forecast"] (lines 42-46)
  - .planning/reconciliation/entsoe/35-wind-solar-forecast-http-401.md (entitlement-blocked, needs-info)
  - .planning/reconciliation/entsoe/73-wind-solar-forecast-resolution-nullability.md (closed)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Day-ahead wind and solar forecast, <span class="italic fg-accent">B16 B18 B19.</span>

**Lede:** Day-ahead TSO-published wind onshore, wind offshore, and solar generation forecast in MW per bidding zone — the canonical input for renewable-driven price-direction models and forecast-skill assessment.

**Verified line:** Schema verified against gridflow source 2026-05-20 · live API requires extended ENTSO-E registration · [ENTSO-E Transparency](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.wind_solar_forecast` |
| API PATH | `/api?documentType=A69&processType=A01` |
| FREQUENCY | PT60M |
| PUBLICATION LAG | D-1 |
| VOLUME | ~3 TimeSeries / zone / day (one per PSR) |
| PRIMARY KEY | `(timestamp_utc, area_code, production_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A69 | DocumentType |
| 2 | D-1 | Publication |
| 3 | 3 | PSR types (B16 B18 B19) |
| 4 | 7 | Schema columns |

# Sidebar siblings

- generation_forecast
- actual_generation
- load_forecast
- forecast_margin
- day_ahead_prices

# Sample chart

- **Type:** `stackedArea`
- **Title:** "DE-LU day-ahead wind + solar forecast · 24-hour"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Seed:** 27
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeWindSolarForecast` (lines 105-123). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L111, L118-123` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L112` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | `B16` = Solar; `B18` = Wind Offshore; `B19` = Wind Onshore. | `schemas/entsoe.py L113` |
| `generation_forecast_mw` | `float` | No | `<Point><quantity>` | Forecast MW. | `schemas/entsoe.py L114` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L115` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L116` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `silver/entsoe/wind_solar_forecast.py L81` |

**PARQUET PATH:** `data/silver/entsoe/wind_solar_forecast/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, production_type)` (`silver/entsoe/wind_solar_forecast.py L74-76`)

# Sample data

| timestamp_utc | area_code | production_type | generation_forecast_mw | resolution | data_provider |
|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | B19 | 18420.0 | PT60M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | B18 | 4280.0 | PT60M | entsoe |
| 2026-05-06T00:00:00+00:00 | 10Y1001A1001A82H | B16 | 0.0 | PT60M | entsoe |
| **2026-05-06T11:00:00+00:00** | **10Y1001A1001A82H** | **B16** | **28940.0** | **PT60M** | **entsoe** |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | B19 | 14200.0 | PT60M | entsoe |
| 2026-05-06T18:00:00+00:00 | 10Y1001A1001A82H | B16 | 4810.0 | PT60M | entsoe |

**Sources:** Synthesised against typical DE-LU spring forecast shape — solar (`B16`) rises from 0 at night to ~29 GW at midday, wind onshore (`B19`) varies independently of sun. The highlighted **B16 midday (28.94 GW)** row is the canonical solar peak that drives middle-of-day price suppression in continental zones.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A69&processType=A01&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — extended registration required.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/wind_solar_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.wind_solar_forecast.WindSolarForecastTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A69&processType=A01&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000&psrType=B16
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily peak solar + wind forecast per zone
SELECT date_trunc('day', timestamp_utc) AS day, area_code,
       max(CASE WHEN production_type='B16' THEN generation_forecast_mw END) AS peak_solar,
       max(CASE WHEN production_type='B19' THEN generation_forecast_mw END) AS peak_wind_on,
       max(CASE WHEN production_type='B18' THEN generation_forecast_mw END) AS peak_wind_off
FROM read_parquet('data/silver/entsoe/wind_solar_forecast/**/*.parquet')
WHERE timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2 ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

fc = pl.read_parquet("data/silver/entsoe/wind_solar_forecast/**/*.parquet")
act = pl.read_parquet("data/silver/entsoe/actual_generation/**/*.parquet")
# Forecast skill: per-PSR forecast error
joined = fc.join(
    act.filter(pl.col("production_type").is_in(["B16", "B18", "B19"])),
    on=["timestamp_utc", "area_code", "production_type"],
)
err = joined.with_columns(
    (pl.col("generation_mw") - pl.col("generation_forecast_mw")).alias("err_mw")
)
print(err.group_by(["area_code", "production_type"]).agg(
    pl.col("err_mw").std().alias("rmse")
))
```

# Caveats

## 01 Only 3 PSR types (B16 B18 B19)

A69 covers solar (`B16`), wind offshore (`B18`), wind onshore (`B19`). Not other renewables (hydro, biomass) — for those use `generation_forecast` (A71/A01). *(Source: `schemas/entsoe.py L108`.)*

## 02 GB EMPTY post-Brexit

GB renewable forecasts are via Elexon `windfor` (wind only). No GB solar forecast on ENTSO-E. *(Source: vault Known Issues.)*

## 03 Forecast revisions overwrite

Same `(timestamp_utc, area_code, production_type)` re-publication overwrites silently on dedup. *(Source: `silver/entsoe/wind_solar_forecast.py L74-76`.)*

## 04 Resolution may be PT15M for some zones

Most zones publish `PT60M`, but a few publish `PT15M`. Filter on `resolution` before joining settlement-period datasets. *(Source: vault Known Issues.)*

## 05 Entitlement-blocked on default API key

Live API returns HTTP 401 for the unregistered gridflow default key. Schema verified from gridflow source. *(Source: `.planning/reconciliation/entsoe/35-wind-solar-forecast-http-401.md`.)*

# Related datasets

- **`actual_generation`** — Realised counterpart. `PT15M-PT60M`. Forecast skill = actual - this dataset on `(timestamp_utc, area_code, production_type)` where psr_type ∈ {B16, B18, B19}. `entsoe · generation · hourly`
- **`generation_forecast`** — All-PSR aggregate forecast. `PT60M`. This dataset is the variable-renewable subset of the aggregate; sum-check the wind+solar share. `entsoe · forecast · hourly`
- **`day_ahead_prices`** — Clearing prices. `PT60M`. Solar / wind forecast is the dominant short-term price-direction feature in DE-LU / NL / IE-SEM. `entsoe · prices · hourly`
- **`windfor` (Elexon)** — GB wind forecast. `hourly`. Substitute for any GB wind query — A69 is empty for GB. `elexon · generation · hourly`
