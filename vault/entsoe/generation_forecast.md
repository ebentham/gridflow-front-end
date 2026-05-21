---
source: entsoe
dataset_key: generation_forecast
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Day-ahead generation forecast aggregated (A71/A01)

## Overview

Day-ahead total aggregated generation forecast in MW per bidding zone,
broken out per production type. Distinct from `wind_solar_forecast` (A69)
in that A71/A01 covers all dispatchable + non-dispatchable types, whereas
A69 covers only the variable renewables. Used as a TSO-published reference
for total generation expectation.

→ [Wind/solar forecast](wind_solar_forecast.md), [Actual generation](actual_generation.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None |
| Historical depth | 2014-12-05 onwards |
| Publication lag  | Published D-1 ~18:00 UTC |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A71 |
| Process type     | A01 (day-ahead) |
| Business type    | n/a |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A71` | `A71` |
| `processType` | str | yes | `A01` | `A01` |
| `in_Domain` | EIC | yes | Bidding zone | `10Y1001A1001A82H` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202605060000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605070000` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A71&processType=A01&in_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB: HTTP 200, **EMPTY** (Ack 999 "DAY_AHEAD_AGGREGATED_GENERATION_R3 [14.1.C]"). Brexit-GB.
- DE-LU: HTTP 200, **PASS** — `GL_MarketDocument`, 1 TimeSeries.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/generation_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (DE-LU, truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <type>A71</type>
  <process.processType>A01</process.processType>
  <TimeSeries>
    <businessType>A01</businessType>
    <inBiddingZone_Domain.mRID>10Y1001A1001A82H</inBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <Period>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>52310</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/generation_forecast/year=YYYY/month=MM/generation_forecast_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.generation_forecast.GenerationForecastTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeGenerationForecast`
**Dedup key**: `(timestamp_utc, area_code, production_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Period start + position * resolution | tz-aware UTC |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| production_type | str | No | `<MktPSRType><psrType>` if present, else "" | A71/A01 aggregate often has no MktPSRType — value defaults to "unknown" |
| generation_forecast_mw | float | No | `<Point><quantity>` | MW |
| resolution | str | No | parsed | Default "" in canonical. `PT60M` typical. |
| data_provider | str | No | constant | "entsoe" |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-05T22:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "production_type": "unknown",
        "generation_forecast_mw": 52310.0,
        "resolution": "1:00:00",
        "data_provider": "entsoe",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB EMPTY post-Brexit.** No GB equivalent — Elexon publishes residual demand forecast (`ndf`) but not gross generation forecast.
- A71 is a **shared documentType with `installed_capacity_units`** — they're disambiguated by `processType` (A01 vs A33). Building the wrong tuple silently returns the other dataset's payload.
- Aggregate A71/A01 often contains no `MktPSRType` element so `production_type` falls back to `"unknown"` in silver.
- Forecast revisions overwrite each other.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §14.1.C): `(documentType=A71, processType=A01, businessType=n/a, in_Domain)`.
  - Code (`endpoints.py:DOC_TYPES["generation_forecast"]`): `("A71", "A01", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- A71 doc type is reused in code for `installed_capacity_units` (A71/A33) — different process type. Make sure consumers select on dataset key, not documentType alone.

---

## Modelling notes

- Demand-supply imbalance feature for price modelling: `generation_forecast - load_forecast`.
- Use as cross-check vs sum of A75 actual generation per zone — TSO forecast skill metric.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/generation_forecast.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
