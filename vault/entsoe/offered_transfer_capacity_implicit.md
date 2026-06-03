---
source: entsoe
dataset_key: offered_transfer_capacity_implicit
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Offered Transfer Capacity: Implicit (A31, auction.Type=A01 lowercase)

## Overview

Capacity offered through *implicit* allocations — the standard day-ahead
implicit market-coupling scheme used by SDAC (Single Day-Ahead Coupling).
Article 11.1 of Regulation (EC) 543/2013. Distinguished from
`_continuous` and `_explicit` by the **lowercase** `auction.Type` and
`contract_MarketAgreement.Type` parameters and by the absence of an
`auction.Category` parameter. Used as feature for day-ahead spread models.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s default |
| Pagination       | None |
| Historical depth | 2014-12-05 onward |
| Publication lag  | After auction allocation (D-1 mid-day) |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A31` |
| processType | (none) |
| `auction.Type` (lowercase a) | `A01` |
| `contract_MarketAgreement.Type` (lowercase c) | `A01` (daily) |
| businessType (request) | (none) |
| domain-param-name | `in_Domain` + `out_Domain` (lowercase) |

### Cross-zonal parameters

A31 implicit is directional. UK-centric default (GB→FR).

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A31` | `A31` |
| `auction.Type` | str | Yes | `A01` (note **lowercase a**) | `A01` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` daily (note **lowercase c**) | `A01` |
| `in_Domain` | str | Yes | Source zone EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination zone EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-offered_transfer_capacity_implicit.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/offered_transfer_capacity_implicit/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08 (GB→FR): Acknowledgement, Reason 999 —
`OFFERED_TRANSFER_CAPACITIES_IMPLICIT [11.1] (10YGB----------A,
10YFR-RTE------C)`. Sanity check NL→DE same shape: also EMPTY for
2026-05-06.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/offered_transfer_capacity_implicit/year=YYYY/month=MM/offered_transfer_capacity_implicit_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityImplicitTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope (same as `_continuous`).

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 2000.0,
        "business_type": "",
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:05:30Z",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Lowercase parameter names** distinguish this variant from `_continuous`
  (capitalised). ENTSOE is case-sensitive on parameter parsing in some
  validation paths — copy the casing from the connector exactly.
- A31 implicit is the *primary* day-ahead capacity-offering data feed for
  EU continental borders.
- GB borders are post-Brexit no longer in SDAC, so GB pairs return EMPTY.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A31, processType=none, businessType=none-in-request, auction.Type=A01, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code — the `offered_transfer_capacity_implicit` entry in `endpoints.py` `DOC_TYPES`. **Lowercase** param names distinct from `_continuous`.
- **Live validation 2026-05-08:** GB→FR daily window: Acknowledgement, Reason 999. Sanity NL→DE: also Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" for GB (post-Brexit, GB not in SDAC); for NL→DE, the data item is published with a different cadence/window than tested.
- **Disambiguation from sister A31 variants:** implicit = lowercase `auction.Type=A01` + lowercase `contract_MarketAgreement.Type=A01` and **no** `auction.Category`. `_continuous` uses **capitalised** versions of the same params; `_explicit` adds **lowercase** `auction.Category=A01`.

---

## Modelling notes

- Useful as the canonical day-ahead capacity feature for SDAC borders.
- Pair with day-ahead prices (A44) at both ends to compute spread / capacity
  scarcity ratios.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
