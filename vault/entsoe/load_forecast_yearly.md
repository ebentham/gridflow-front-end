---
source: entsoe
dataset_key: load_forecast_yearly
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Year-ahead Load Forecast (A65/A33)

## Overview

Year-ahead total load forecast in MW per bidding zone — long-horizon TSO
demand outlook with annual resolution. Document type `A65` + process type
`A33` ("Year ahead"). Schema and parser are identical to the day-/week-/
month-ahead siblings, distinguished only by `forecast_horizon` and the
`processType`.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Load forecast](../../20-domain/concepts/load-forecast.md)

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
| Publication lag  | Yearly |
| Response format  | XML (GL_MarketDocument) |
| Document type    | `A65` |
| Process type     | `A33` (Year ahead) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A65` | `A65` |
| `processType` | str | yes | `A33` | `A33` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A65&processType=A33&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`TOTAL_LOAD_FORECAST [6.1.C&D&E]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/load_forecast_yearly/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

```json
{
  "envelope": "GL_MarketDocument",
  "type": "A65",
  "process.processType": "A33",
  "TimeSeries": [
    {
      "businessType": "A60",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "Period": {"resolution": "P1Y", "Point": [{"position": 1, "quantity": 540000}]}
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/load_forecast_yearly/year=YYYY/month=MM/load_forecast_yearly_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.load_forecast_yearly.LoadForecastYearlyTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeLoadForecast` (shared — `forecast_horizon="year_ahead"`)
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` | EIC |
| `load_forecast_mw` | `float` | No | `Point/quantity` | MW |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | typically `P1Y` |
| `forecast_horizon` | `str` | No (default `"year_ahead"`) | derived | Constant |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_forecast_mw": 540000.0,
        "resolution": "P1Y",
        "forecast_horizon": "year_ahead",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 33, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Sparse output**: typically annual min/max — `businessType` distinguishes,
  silver schema does not preserve.
- **`P1Y`** resolution mapped to `timedelta(days=365)` — leap years and
  calendar drift are not handled correctly for multi-year windows. Treat
  the timestamp as the start of the represented year.

---

## Implementation delta

- Code-tuple: `(A65, A33, None, outBiddingZone_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live DE-LU returns `GL_MarketDocument` with
  `process.processType=A33` — request shape accepted.
- **Resolution `P1Y` approximation**: parser uses 365 days, so timestamps
  within a multi-year window are not calendar-correct. Flag for V1
  follow-up.

---

## Modelling notes

- Annual demand baseline for capacity-adequacy and longer-horizon market
  scenarios. Used in conjunction with `forecast_margin` (year-ahead).
- Drop GB rows.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/load_forecast_yearly.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: load forecast](../../20-domain/concepts/load-forecast.md)
