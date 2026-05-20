---
source: entsoe
dataset_key: load_forecast
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Day-ahead Load Forecast (A65/A01)

## Overview

Day-ahead total load forecast in MW per bidding zone — TSO-published
prediction for the following day, used as the reference forecast against
which actual load (A65/A16) measures forecast error. Document type `A65`
+ process type `A01` ("Day ahead"). Resolution typically PT15M.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Load forecast](../../20-domain/concepts/load-forecast.md)
  [Forecast error](../../20-domain/concepts/forecast-error.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken` from env var `ENTSOE_API_KEY` |
| Rate limit       | Not vendor-published; codebase 1 req/s |
| Pagination       | None |
| Historical depth | ~5 years |
| Publication lag  | Published D-1 ~12:00 CET, then revised |
| Response format  | XML (GL_MarketDocument) |
| Document type    | `A65` |
| Process type     | `A01` (Day ahead) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A65` | `A65` |
| `processType` | str | yes | `A01` | `A01` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A65&processType=A01&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`DAY_AHEAD_TOTAL_LOAD_FORECAST_R3 [6.1.B]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/load_forecast/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

(First ~500 bytes of DE-LU 2026-05-06 response.)

```json
{
  "envelope": "GL_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'",
  "type": "A65",
  "process.processType": "A01",
  "TimeSeries": [
    {
      "businessType": "A04",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "quantity_Measure_Unit.name": "MAW",
      "Period": {
        "timeInterval": {"start": "2026-05-06T00:00Z", "end": "2026-05-07T00:00Z"},
        "resolution": "PT15M",
        "Point": [{"position": 1, "quantity": 44175.567575}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/load_forecast/year=YYYY/month=MM/load_forecast_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.load_forecast.LoadForecastTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeLoadForecast`
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | UTC required |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` | EIC |
| `load_forecast_mw` | `float` | No | `Point/quantity` | MW |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | `PT15M`/`PT60M` |
| `forecast_horizon` | `str` | No (default `"day_ahead"`) | derived | Constant `"day_ahead"` |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_forecast_mw": 44175.567575,
        "resolution": "PT15M",
        "forecast_horizon": "day_ahead",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 28, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Forecast revisions**: TSOs revise the day-ahead load forecast in the
  intraday window; latest revision wins by dedup.
- **15-min resolution** typical for continental zones; older windows or
  specific zones may publish PT60M.

---

## Implementation delta

- Code-tuple: `(A65, A01, None, outBiddingZone_Domain)`.
  Guide PDF unfetchable (`HTTP 400` from
  `transparency.entsoe.eu/.../Guide.pdf`); tuple is `unverified - PDF
  fetch failed` against canonical docs. Live DE-LU response returns
  expected `GL_MarketDocument` with `process.processType=A01`, confirming
  the API accepts the connector's request shape.
- No discrepancies observed.

---

## Modelling notes

- Pair with `actual_load` (A65/A16) on `(timestamp_utc, area_code)` to
  derive the forecast error series. Common target for forecast-error-aware
  pricing or peak-detection models.
- Drop GB rows for modelling.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/load_forecast.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: forecast error](../../20-domain/concepts/forecast-error.md)
