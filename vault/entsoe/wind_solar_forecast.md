---
source: entsoe
dataset_key: wind_solar_forecast
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Day-ahead wind / solar generation forecast (A69/A01)

## Overview

Day-ahead generation forecast in MW for the wind-onshore (B18), wind-offshore
(B16) and solar (B19) production types per bidding zone. Published once per
day around 18:00 D-1 UTC. Used as the canonical reference forecast for
pricing models and as a benchmark for in-house wind/solar nowcast skill.

→ [Actual generation](actual_generation.md), [Generation forecast](generation_forecast.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | not documented — code uses 1 req/s |
| Pagination       | None |
| Historical depth | 2014-12-05 onwards |
| Publication lag  | Published D-1 ~18:00 UTC; refreshed intraday |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A69 |
| Process type     | A01 (day-ahead) |
| Business type    | n/a |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A69` | `A69` |
| `processType` | str | yes | `A01` | `A01` |
| `in_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202605060000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605070000` |
| `psrType` | str | no | Filter to one of B16/B18/B19 | `B19` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A69&processType=A01&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB: HTTP 200, **EMPTY** (Acknowledgement reason 999 "GENERATION_FORECAST_WIND_SOLAR [14.1.D]"). Brexit-GB.
- DE-LU: HTTP 200, **PASS** — `GL_MarketDocument`, 3 TimeSeries (B16 / B18 / B19).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/wind_solar_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (DE-LU, truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <type>A69</type>
  <process.processType>A01</process.processType>
  <TimeSeries>
    <businessType>A01</businessType>
    <inBiddingZone_Domain.mRID>10Y1001A1001A82H</inBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <MktPSRType><psrType>B19</psrType></MktPSRType>
    <Period>
      <timeInterval>...</timeInterval>
      <resolution>PT15M</resolution>
      <Point><position>1</position><quantity>0</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/wind_solar_forecast/year=YYYY/month=MM/wind_solar_forecast_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.wind_solar_forecast.WindSolarForecastTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeWindSolarForecast`
**Dedup key**: `(timestamp_utc, area_code, production_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | derived from Period start + position | UTC tz-aware |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| production_type | str | No | `<MktPSRType><psrType>` | B16=wind offshore, B18=wind onshore, B19=solar |
| generation_forecast_mw | float | No | `<Point><quantity>` | renamed from `value` |
| resolution | str | No | parsed | Default "" in canonical. `PT15M` / `PT60M`. |
| data_provider | str | No | constant | "entsoe" |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-05T22:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "production_type": "B19",
        "generation_forecast_mw": 0.0,
        "resolution": "0:15:00",
        "data_provider": "entsoe",
    },
    {
        "timestamp_utc": "2026-05-06T11:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "production_type": "B19",
        "generation_forecast_mw": 31250.4,
        "resolution": "0:15:00",
        "data_provider": "entsoe",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB EMPTY post-Brexit.** Use Elexon `windfor` for GB wind forecasts.
- A69 only carries B16, B18, B19 — solar separation may merge B17 (solar thermal) historically; we observe only B19 for current periods.
- Forecast revisions during the day overwrite each other in silver — no point-in-time. Re-running ingestion late in the day may change historical files.
- DE-LU is published at PT15M; some smaller zones publish at PT60M only.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §14.1.D): `(documentType=A69, processType=A01, businessType=n/a, in_Domain)`.
  - Code: `("A69", "A01", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- `psrType` is documented as optional filter; not in `optional_params` tuple — `unverified` for connector callability.

---

## Modelling notes

- Day-ahead price models — wind/solar forecast is the dominant negative pressure on prices.
- Forecast-error features — `(actual - forecast) / forecast` per production type.
- Use as benchmark for in-house weather-driven nowcasts.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/wind_solar_forecast.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
