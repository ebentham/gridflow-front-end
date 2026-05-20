---
source: entsoe
dataset_key: load_forecast_monthly
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Month-ahead Load Forecast (A65/A32)

## Overview

Month-ahead total load forecast in MW per bidding zone — TSO long-horizon
forecast typically published once per month. Document type `A65` + process
type `A32` ("Month ahead"). Same schema and parser as week-ahead, with the
forecast_horizon flag changed.

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
| Publication lag  | Monthly |
| Response format  | XML (GL_MarketDocument) |
| Document type    | `A65` |
| Process type     | `A32` (Month ahead) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A65` | `A65` |
| `processType` | str | yes | `A32` | `A32` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A65&processType=A32&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`TOTAL_LOAD_FORECAST [6.1.C&D&E]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/load_forecast_monthly/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

```json
{
  "envelope": "GL_MarketDocument",
  "type": "A65",
  "process.processType": "A32",
  "TimeSeries": [
    {
      "businessType": "A60",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "Period": {"resolution": "P1M", "Point": [{"position": 1, "quantity": 58000}]}
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/load_forecast_monthly/year=YYYY/month=MM/load_forecast_monthly_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.load_forecast_monthly.LoadForecastMonthlyTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeLoadForecast` (shared base — the schema reuses `EntsoeLoadForecast` with `forecast_horizon="month_ahead"`)
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` | EIC |
| `load_forecast_mw` | `float` | No | `Point/quantity` | MW |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | typically `P1M` |
| `forecast_horizon` | `str` | No (default `"month_ahead"`) | derived | Constant |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_forecast_mw": 58000.0,
        "resolution": "P1M",
        "forecast_horizon": "month_ahead",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 32, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Sparse output**: monthly min/max — `businessType` distinguishes; silver
  schema does not preserve `businessType`, so dedup may collapse rows.
- **`P1M`** resolution — parser's `_RESOLUTION_MAP` approximates as 30
  days. Treat the timestamp as the start of the represented month rather
  than a precise sub-month timestamp.

---

## Implementation delta

- Code-tuple: `(A65, A32, None, outBiddingZone_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live DE-LU returns `GL_MarketDocument` with
  `process.processType=A32` — request shape accepted.
- **Resolution `P1M`** mapped to a `timedelta(days=30)` in the parser is
  a known approximation — month length varies, so position-derived
  timestamps within a multi-month window are not calendar-correct. Flag
  for V1 follow-up.

---

## Modelling notes

- Long-horizon trend feature in seasonal models. Coarse — typical use is
  to set monthly demand expectations as a baseline against which weekly
  / daily features modulate.
- Drop GB rows.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/load_forecast_monthly.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: load forecast](../../20-domain/concepts/load-forecast.md)
