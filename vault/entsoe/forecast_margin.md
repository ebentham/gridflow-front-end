---
source: entsoe
dataset_key: forecast_margin
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Year-ahead Forecast Margin (A70/A33)

## Overview

Year-ahead forecast margin in MW per bidding zone — TSO-published reserve
margin metric for the year ahead, indicating capacity surplus over expected
peak demand. Article 8.1 (`YEAR_AHEAD_FORECAST_MARGIN_R3`). Document type
`A70` + process type `A33` ("Year ahead"). Used in capacity-adequacy
analyses and as a market-tightness signal.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Capacity adequacy](../../20-domain/concepts/capacity-adequacy.md)

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
| Document type    | `A70` |
| Process type     | `A33` (Year ahead) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A70` | `A70` |
| `processType` | str | yes | `A33` | `A33` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202605060000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A70&processType=A33&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`YEAR_AHEAD_FORECAST_MARGIN_R3 [8.1]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/forecast_margin/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

```json
{
  "envelope": "GL_MarketDocument",
  "type": "A70",
  "process.processType": "A33",
  "TimeSeries": [
    {
      "businessType": "A91",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "Period": {"resolution": "P1Y", "Point": [{"position": 1, "quantity": 12500}]}
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/forecast_margin/year=YYYY/month=MM/forecast_margin_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.forecast_margin.ForecastMarginTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeForecastMargin`
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` | EIC |
| `forecast_margin_mw` | `float` | No | `Point/quantity` | MW (positive = surplus) |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | typically `P1Y` |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "forecast_margin_mw": 12500.0,
        "resolution": "P1Y",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 34, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Annual resolution**: see month/year resolution caveats — `P1Y` mapped
  to 365 days approximation.
- **Negative or zero margin** indicates expected capacity shortfall — a
  market-stress signal worth flagging downstream.
- **Schema validation**: the silver transformer constructs a Pydantic
  `EntsoeForecastMargin` from the first row to surface schema drift. Watch
  for `ValidationError` in the silver step on unexpected schema changes.

---

## Implementation delta

- Code-tuple: `(A70, A33, None, outBiddingZone_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live DE-LU returns `GL_MarketDocument` with
  `process.processType=A33` and `type=A70` — request shape accepted.

---

## Modelling notes

- Capacity-adequacy feature for longer-horizon GB-EU spread modelling.
  Lower margin in adjacent zones can signal price upside via interconnector
  flows.
- Drop GB rows.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/forecast_margin.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: capacity adequacy](../../20-domain/concepts/capacity-adequacy.md)
