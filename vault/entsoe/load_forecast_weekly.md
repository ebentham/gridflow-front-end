---
source: entsoe
dataset_key: load_forecast_weekly
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Week-ahead Load Forecast (A65/A31)

## Overview

Week-ahead total load forecast in MW per bidding zone — typically published
once per week with weekly resolution (`P7D`). Document type `A65` + process
type `A31` ("Week ahead"). Used as a longer-horizon reference for forecast
adaptation studies and weekly capacity planning.

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
| Publication lag  | Published weekly, lead-time ~7 days |
| Response format  | XML (GL_MarketDocument) |
| Document type    | `A65` |
| Process type     | `A31` (Week ahead) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A65` | `A65` |
| `processType` | str | yes | `A31` | `A31` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A65&processType=A31&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`TOTAL_LOAD_FORECAST [6.1.C&D&E]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/load_forecast_weekly/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

(First ~500 bytes of DE-LU 2026-05-06 response — week-ahead values are
sparse, typically one min and one max per week.)

```json
{
  "envelope": "GL_MarketDocument",
  "type": "A65",
  "process.processType": "A31",
  "TimeSeries": [
    {
      "businessType": "A60",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "Period": {"resolution": "P7D", "Point": [{"position": 1, "quantity": 60800}]}
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/load_forecast_weekly/year=YYYY/month=MM/load_forecast_weekly_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.load_forecast_weekly.LoadForecastWeeklyTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeLoadForecastWeekly`
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` | EIC |
| `load_forecast_mw` | `float` | No | `Point/quantity` | MW |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | typically `P7D` |
| `forecast_horizon` | `str` | No (default `"week_ahead"`) | derived | Constant |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_forecast_mw": 60800.0,
        "resolution": "P7D",
        "forecast_horizon": "week_ahead",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 30, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Sparse output**: typically only the weekly min and max load are
  published, with `businessType` distinguishing them (A60 / A61 / similar).
  The silver schema does not currently keep `businessType` — both rows
  collapse on the dedup key. Verify this is desired before treating it
  as ground truth.
- **`P7D` resolution** uses the parser's `_RESOLUTION_MAP` (P7D → 7 days).

---

## Implementation delta

- Code-tuple: `(A65, A31, None, outBiddingZone_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live DE-LU returns valid `GL_MarketDocument` with
  `process.processType=A31` — request shape accepted.
- **Possible silver bug**: dedup `(timestamp_utc, area_code)` may collapse
  the min/max weekly load into one row, losing the businessType
  distinction. Not validated here; flag for V1 follow-up.

---

## Modelling notes

- Long-horizon trend baseline. Used in seasonal capacity-mix studies.
- Drop GB rows for modelling.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/load_forecast_weekly.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: load forecast](../../20-domain/concepts/load-forecast.md)
