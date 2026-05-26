---
source: entsoe
dataset_key: offered_transfer_capacity_explicit
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Offered Transfer Capacity: Explicit (A31, auction.Category=A01 + auction.Type=A01)

## Overview

Capacity offered through *explicit* allocations — the auction style where
market participants bid for capacity rights independently of energy. Used
on borders that retain explicit auctions (some non-coupled borders and
several long-term products). Article 11.1 of Regulation (EC) 543/2013.
Distinguished from `_continuous` and `_implicit` by the presence of
`auction.Category=A01` (lowercase) **in addition to** the lowercase
`auction.Type=A01` and `contract_MarketAgreement.Type=A01`.

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
| Publication lag  | After auction allocation (D-1 to D-week depending on auction product) |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A31` |
| processType | (none) |
| `auction.Category` (lowercase) | `A01` |
| `auction.Type` (lowercase) | `A01` |
| `contract_MarketAgreement.Type` (lowercase) | `A01` (daily) |
| businessType (request) | (none) |
| domain-param-name | `in_Domain` + `out_Domain` (lowercase) |

### Cross-zonal parameters

A31 explicit is directional. UK-centric default (GB→FR).

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A31` | `A31` |
| `auction.Category` | str | Yes | `A01` | `A01` |
| `auction.Type` | str | Yes | `A01` | `A01` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` daily | `A01` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-offered_transfer_capacity_explicit.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&auction.Category=A01&auction.Type=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/offered_transfer_capacity_explicit/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08 GB→FR: Acknowledgement, Reason 999 —
`OFFERED_TRANSFER_CAPACITIES_IMPLICIT [11.1] (10YGB----------A,
10YFR-RTE------C)`. (Same data-item label as the other A31 variants because
the article reference is shared.)

---

## Silver layer

**Path pattern**: `data/silver/entsoe/offered_transfer_capacity_explicit/year=YYYY/month=MM/offered_transfer_capacity_explicit_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityExplicitTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope (same as the other two A31 variants).

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 1200.0,
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

- **`auction.Category=A01` is the discriminator** vs `_implicit`. Without it,
  the API treats the request as the implicit variant.
- All three A31 variants return the same `OFFERED_TRANSFER_CAPACITIES_IMPLICIT`
  acknowledgement label on EMPTY — this is misleading; the data items are
  actually distinct on the publication side.
- GB borders rarely populate post-Brexit.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A31, processType=none, businessType=none-in-request, auction.Category=A01, auction.Type=A01, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code `endpoints.py:211-226`.
- **Live validation 2026-05-08 GB→FR daily window:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (GB not in EU explicit allocation auctions on the test day).
- **Disambiguation from sister A31 variants:** explicit = lowercase `auction.Category=A01` + lowercase `auction.Type=A01` + lowercase `contract_MarketAgreement.Type=A01`. `_continuous` uses capitalised forms and **no** `auction.Category`. `_implicit` uses lowercase but **no** `auction.Category`.

---

## Modelling notes

- Used as a feature on borders that retain long-term explicit auctions
  (e.g. some non-SDAC interconnectors). For SDAC borders this tends to be
  superseded by `_implicit`.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
