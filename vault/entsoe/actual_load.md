---
source: entsoe
dataset_key: actual_load
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Actual Total Load (A65/A16)

## Overview

Realised (metered) total load in MW per bidding zone, published per ENTSO-E
Transparency Platform Article 6.1.A (`ACTUAL_TOTAL_LOAD_R3`). Document type
`A65` ("System total load") with process type `A16` ("Realised") returns
`<TimeSeries>` keyed by `outBiddingZone_Domain` with `<quantity>` values.
Resolution is typically PT15M for continental zones. This is the canonical
demand series used for forecast-error analysis, peak detection, and
weather-vs-demand modelling.

→ Link to relevant domain concept notes if they exist, e.g.:
  [System load](../../20-domain/concepts/system-load.md)
  [EIC codes](../../20-domain/concepts/eic-codes.md)

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
| Historical depth | ~5 years on most zones |
| Publication lag  | ~1 hour after settlement period close |
| Response format  | XML (GL_MarketDocument) |
| Document type    | `A65` |
| Process type     | `A16` (Realised) |
| Domain param name | `outBiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A65` | `A65` |
| `processType` | str | yes | `A16` | `A16` |
| `outBiddingZone_Domain` | str (EIC) | yes | Bidding zone EIC | `10Y1001A1001A82H` |
| `periodStart` | str (`yyyyMMddHHmm` UTC) | yes | Window start | `202605060000` |
| `periodEnd` | str (`yyyyMMddHHmm` UTC) | yes | Window end | `202605070000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A65&processType=A16&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202605060000&periodEnd=202605070000" \
  -H "Accept: application/xml"
```

GB (`10YGB----------A`) returns Acknowledgement 999
(`ACTUAL_TOTAL_LOAD_R3 [6.1.A]`). Use Elexon `indo`/`itsdo` for GB realised
demand.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/actual_load/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (zone, query window).

### Bronze sample

(First ~500 bytes of a DE-LU 2026-05-06 response.)

```json
{
  "envelope": "GL_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'",
  "type": "A65",
  "process.processType": "A16",
  "TimeSeries": [
    {
      "businessType": "A04",
      "outBiddingZone_Domain.mRID": "10Y1001A1001A82H",
      "quantity_Measure_Unit.name": "MAW",
      "Period": {
        "timeInterval": {"start": "2026-05-06T00:00Z", "end": "2026-05-07T00:00Z"},
        "resolution": "PT15M",
        "Point": [{"position": 1, "quantity": 43236.25422}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/actual_load/year=YYYY/month=MM/actual_load_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.actual_load.ActualLoadTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeActualLoad`
**Dedup key**: `(timestamp_utc, area_code)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | `Period.timeInterval.start + (position-1)*resolution` | tz-aware UTC required |
| `area_code` | `str` | No | `outBiddingZone_Domain.mRID` (parser remaps to `in_domain`) | EIC, no normalisation |
| `load_mw` | `float` | No | `Point/quantity` | Megawatts (unit `MAW` = MW) |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | `PT15M`, `PT30M`, `PT60M` |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | Set by transformer |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 0, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_mw": 43236.25422,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 26, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2026, 5, 6, 0, 15, tzinfo=UTC),
        "area_code": "10Y1001A1001A82H",
        "load_mw": 43011.13,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 4, 26, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit** — code 999 returned for `10YGB----------A`.
  Use Elexon `indo`/`itsdo` for GB realised demand instead.
- **Quantity unit `MAW`** — the ENTSO-E XML reports `quantity_Measure_Unit.name = "MAW"`,
  which is megawatts (the standard ENTSO-E unit code for MW). The silver
  field is named `load_mw` to match the convention.
- **15-minute resolution by default** for continental zones. Some smaller
  zones still publish PT60M.
- **outBiddingZone_Domain** is the parameter — NOT `BiddingZone_Domain` or
  `in_Domain`. Mismatch silently returns wrong scope or 400.
- **Revisions** can occur within ~24 hours as TSO meter data is
  back-validated. Re-running `ingest` for a recent date is the simplest
  way to absorb revisions; the dedup `(timestamp_utc, area_code)` keeps
  the most-recent value.

---

## Implementation delta

- **Tuple comparison**: code-tuple `(documentType=A65, processType=A16, businessType=None, domain=outBiddingZone_Domain)`.
  Static Content Guide PDF could not be fetched (`HTTP 400` — CDN
  protection); tuple is `unverified - PDF fetch failed` against the
  canonical guide. Live DE-LU response confirms the API accepts the shape
  and returns the documented `GL_MarketDocument` envelope with `type=A65`,
  `process.processType=A16`, and `outBiddingZone_Domain.mRID` matching the
  request — so the live API is consistent with the connector's tuple.
- No discrepancies observed between connector and live API behaviour.

---

## Modelling notes

- Target variable for short-term load forecasting models. Typical features:
  weather (temperature, irradiance, wind), calendar (hour-of-day,
  day-of-week, public holiday), lagged load (load_t-24h, load_t-168h).
- Pair with `load_forecast` (A65/A01) to build forecast-error series for
  error-distribution modelling.
- Drop GB rows when modelling — always empty.
- For UK demand modelling, prefer Elexon `indo` (instantaneous national
  demand, half-hourly) — same physical signal, fully populated.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/actual_load.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: system load](../../20-domain/concepts/system-load.md)
