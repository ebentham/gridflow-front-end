---
source: entsoe
dataset_key: activated_balancing_prices
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Activated Balancing Energy Prices (A84/A16)

## Overview

Prices in EUR/MWh of activated balancing energy per control area, by reserve
type and activation direction. Article 12.3.F (`PRICES_OF_ACTIVATED_BALANCING_ENERGY_R3`).
Document type `A84` + process type `A16` ("Realised") +
`businessType=A96` (aFRR — automatic frequency restoration reserve, the
reserve type that gridflow currently fetches). Returned as
`Balancing_MarketDocument` with `<TimeSeries>` carrying both
`businessType` (reserve type) and `flowDirection.direction`
(activation direction).

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
| Historical depth | Vendor-bounded; varies per control area |
| Publication lag  | ~T+1 hour |
| Response format  | XML (Balancing_MarketDocument); ZIP-of-XML for large windows |
| Document type    | `A84` |
| Process type     | `A16` (Realised) |
| Domain param name | `controlArea_Domain` |
| Required businessType | `A96` (aFRR — codebase fixed; other reserve types not requested) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | yes | API key | `<your-entsoe-api-key>` |
| `documentType` | str | yes | `A84` | `A84` |
| `processType` | str | yes | `A16` | `A16` |
| `businessType` | str | yes | Reserve type — codebase sends `A96` (aFRR) | `A96` |
| `controlArea_Domain` | str (EIC) | yes | Control area EIC | `10YNL----------L` |
| `periodStart` | str | yes | `yyyyMMddHHmm` UTC | `202504010000` |
| `periodEnd` | str | yes | `yyyyMMddHHmm` UTC | `202504020000` |

### Working curl example

```bash
curl -X GET --ssl-no-revoke \
  "https://web-api.tp.entsoe.eu/api?securityToken=<your-entsoe-api-key>&documentType=A84&processType=A16&businessType=A96&controlArea_Domain=10YNL----------L&periodStart=202504010000&periodEnd=202504020000" \
  -H "Accept: application/xml"
```

GB returns code 999 (`PRICES_OF_ACTIVATED_BALANCING_ENERGY_R3 [TR 17.1.F, IF aFRR 3.16]`).
Use Elexon `boal` / `disbsad` for GB equivalents.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/activated_balancing_prices/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (or ZIP-of-XML, unpacked).
**Granularity**: One file per (control area, query window).

### Bronze sample

```json
{
  "envelope": "Balancing_MarketDocument",
  "type": "A84",
  "process.processType": "A16",
  "area_Domain.mRID": "10YNL----------L",
  "TimeSeries": [
    {
      "businessType": "A96",
      "flowDirection.direction": "A01",
      "currency_Unit.name": "EUR",
      "Period": {
        "resolution": "PT15M",
        "Point": [{"position": 1, "activation_Price.amount": 92.50}]
      }
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/activated_balancing_prices/year=YYYY/month=MM/activated_balancing_prices_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.activated_balancing_prices.ActivatedBalancingPricesTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeActivatedBalancingPrices`
**Dedup key**: `(timestamp_utc, area_code, reserve_type, direction)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` (tz-aware UTC) | No | derived | |
| `area_code` | `str` | No | `area_Domain.mRID`/`controlArea_Domain.mRID` | EIC |
| `reserve_type` | `str` | No | `businessType` mapped via `replace_strict` | `A95→fcr`, `A96→afrr`, `A97→mfrr`, `A98→rr` |
| `direction` | `str` | No | `flowDirection.direction` mapped via `replace_strict` | `A01→up`, `A02→down` |
| `price_eur_mwh` | `float` | No | `Point/*_Price.amount` | EUR/MWh |
| `currency` | `str` | No | `<currency_Unit.name>` | Default "EUR" in canonical; labels the price currency (e.g. GBP for GB) so `price_eur_mwh` is never silently trusted as EUR. |
| `resolution` | `str` | No (default `""`) | `Period/resolution` | `PT15M` typical |
| `data_provider` | `str` | No (default `"entsoe"`) | derived | Constant |
| `ingested_at` | `datetime` (tz-aware UTC) | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2025, 4, 1, 0, 0, tzinfo=UTC),
        "area_code": "10YNL----------L",
        "reserve_type": "afrr",
        "direction": "up",
        "price_eur_mwh": 92.50,
        "currency": "EUR",
        "resolution": "PT15M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 6, 30, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB empty post-Brexit**.
- **Codebase fetches only aFRR** (`businessType=A96`). The silver schema
  supports four reserve types (fcr/afrr/mfrr/rr) but the connector currently
  only requests aFRR. Other reserve types would require either
  per-businessType fetches or relaxing the request.
- **`replace_strict` for reserve_type and direction** — per ADR-022, an
  unknown `businessType` or `flowDirection` no longer raises: each maps to the
  `"unmapped"` sentinel (`reserve_type`/`direction = "unmapped"`), the affected
  rows are counted and a warning logs the distinct unmapped raw codes, and the
  run finishes as `completed_with_warnings` (rows still written). Downstream
  consumers must tolerate a `"unmapped"` value in `reserve_type`/`direction`.
- **Value tag** is `activation_Price.amount` (or similar `*_Price.amount`),
  matched by the parser's `_matches_value_tag` flexible rule.

---

## Implementation delta

- Code-tuple: `(A84, A16, A96, controlArea_Domain)`.
  Guide PDF unfetchable; tuple `unverified - PDF fetch failed` against
  canonical docs. Live NL response (older window 2025-04-01) returns
  `Balancing_MarketDocument` with `type=A84`, `process.processType=A16`,
  `businessType=A96`, and 2 `<TimeSeries>` — request shape accepted.
- **Connector restricts to aFRR** while the silver schema supports four
  reserve types. Either update the connector to iterate businessTypes
  `A95/A96/A97/A98`, or document the aFRR-only scope. Out of V1 scope —
  flag for follow-up.

---

## Modelling notes

- Activated balancing prices are a granular short-term cost-of-balancing
  signal. Pair with `contracted_reserves` for capacity-vs-energy modelling.
- For UK BM modelling, prefer Elexon `boal` (bid-offer-acceptance levels)
  + `disbsad` (BM unit balancing services adjustment) — these have GB-only
  market-specific structure not present in ENTSO-E's pan-European A84.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoints](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/activated_balancing_prices.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
- [Domain: balancing reserves](../../20-domain/markets/balancing-reserves.md)
