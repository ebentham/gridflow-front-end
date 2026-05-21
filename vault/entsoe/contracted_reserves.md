---
source: entsoe
dataset_key: contracted_reserves
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Contracted Reserves (A81/A52)

## Overview

Contracted balancing reserve quantities in MW per control area, by reserve
type. Article 17.1.B&C (`AMOUNT_AND_PRICES_PAID_OF_BALANCING_RESERVES_UNDER_CONTRACT_R3`).
Document type `A81` + process type `A52` (Capacity allocated/contracted)
+ `businessType=B95` (codebase) + `Type_MarketAgreement.Type=A01` (daily
products). Returns `Balancing_MarketDocument` with `<TimeSeries>` carrying
the reserve type via businessType inside the time series.

The codebase comment notes: "Type_MarketAgreement.Type is mandatory per
ENTSO-E API (despite the Postman catalog listing it as optional). A01=daily
products."

→ Link to relevant domain concept notes if they exist, e.g.:
  [Balancing reserves](../../20-domain/markets/balancing-reserves.md)

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
| Historical depth | Vendor-bounded |
| Publication lag  | ~T+1 day |
| Response format  | XML (Balancing_MarketDocument); ZIP-of-XML for large windows |
| Document type    | `A81` |
| Process type     | `A52` (Capacity contracted) |
| Domain param name | `controlArea_Domain` |
| Required businessType | `B95` |
| Required Type_MarketAgreement.Type | `A01` (daily products) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A81` | `A81` |
| `processType` | str | yes | `A52` | `A52` |
| `businessType` | str | yes | Reserve type — codebase sends `B95` | `B95` |
| `Type_MarketAgreement.Type` | str | **yes** (per API; Postman lists optional) | `A01` (daily) | `A01` |
| `controlArea_Domain` | str (EIC) | yes | Control area EIC | `10YFR-RTE------C` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202504010000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202504020000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A81&processType=A52&businessType=B95&Type_MarketAgreement.Type=A01&controlArea_Domain=10YFR-RTE------C&periodStart=202504010000&periodEnd=202504020000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`AMOUNT_AND_PRICES_PAID_OF_BALANCING_RESERVES_UNDER_CONTRACT_R3 [17.1.B&C]`).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/contracted_reserves/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (or ZIP-of-XML, unpacked).
**Granularity**: One file per (control area, query window).

### Bronze sample

```json
{
  "envelope": "Balancing_MarketDocument xmlns='urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:4'",
  "type": "A81",
  "process.processType": "A52",
  "area_Domain.mRID": "10YFR-RTE------C",
  "TimeSeries": [
    {
      "businessType": "A96",
      "Period": {
        "resolution": "PT15M",
        "Point": [{"position": 1, "quantity": 540}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/contracted_reserves/year=YYYY/month=MM/contracted_reserves_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.contracted_reserves.ContractedReservesTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeContractedReserves`
**Dedup key**: `(timestamp_utc, area_code, reserve_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `area_Domain.mRID`/`controlArea_Domain.mRID` | EIC |
| `reserve_type` | `str` | No | `TimeSeries.businessType` mapped via `replace_strict` | `A95→fcr`, `A96→afrr`, `A97→mfrr`, `A98→rr` |
| `quantity_mw` | `float` | No | `Point/quantity` | MW |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | `PT15M` typical |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 4, 1, 0, 0, tzinfo=UTC),
        "area_code": "10YFR-RTE------C",
        "reserve_type": "afrr",
        "quantity_mw": 540.0,
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 7, 0, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Request `businessType` (B95) is the request-level filter** while the
  per-TimeSeries `businessType` (A95/A96/A97/A98) carries the reserve
  type that the silver schema maps. The two `businessType` fields are
  semantically distinct — a request-level B95 filter does not constrain
  the per-series reserve types returned.
- **`Type_MarketAgreement.Type=A01` is mandatory** despite Postman
  documentation listing it as optional — gridflow code documents this
  with an inline comment in `endpoints.py`. Submitting without it returns
  a 400 reason "MISSING_OR_DUPLICATE_VALUES".
- **`replace_strict` reserve-type mapping** raises on any unknown
  TimeSeries-level businessType — protects against silent schema drift.

---

## Implementation delta

- Code-tuple: `(A81, A52, B95 + Type_MarketAgreement.Type=A01, controlArea_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live FR response (older window 2025-04-01) returns
  `Balancing_MarketDocument` with `type=A81`, `process.processType=A52`
  — request shape accepted.
- **Postman vs. live API conflict**: Postman documents
  `Type_MarketAgreement.Type` as optional, but the live API rejects
  without it. Already documented in `endpoints.py` with an inline comment;
  retain the existing override.

---

## Modelling notes

- Capacity-side complement to `activated_balancing_prices`. Pair on
  `(timestamp_utc, area_code, reserve_type)` to compute capacity-utilisation
  features (activated MWh / contracted MW).
- Drop GB rows.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/contracted_reserves.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: balancing reserves](../../20-domain/markets/balancing-reserves.md)
