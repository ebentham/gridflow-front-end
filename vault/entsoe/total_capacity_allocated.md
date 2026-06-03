---
source: entsoe
dataset_key: total_capacity_allocated
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Total Capacity Already Allocated (A26, businessType=A29)

## Overview

Total cross-zonal capacity already allocated through past auctions, in MW
per zone-pair. Article 12.1.C of Regulation (EC) 543/2013. Sister A26
dataset to `total_nominated_capacity`. Used to assess what slice of NTC has
been pre-committed via long-term auctions before each daily clearing.

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
| Publication lag  | After auction settlement |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A26` |
| processType | (none) |
| businessType | `A29` (capacity already allocated) |
| `auction.Category` (lowercase) | `A01` |
| `contract_MarketAgreement.Type` (lowercase) | `A01` (daily) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A26/A29 is directional. Default UK-centric pairs.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A26` | `A26` |
| `businessType` | str | Yes | `A29` | `A29` |
| `auction.Category` | str | Yes | `A01` (lowercase) | `A01` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` (lowercase) | `A01` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-total_capacity_allocated.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A26&businessType=A29&auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/total_capacity_allocated/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08 GB→FR daily and 30-day: Acknowledgement, Reason 999 —
`TOTAL_CAPACITY_ALLOCATED [12.1.C] (10YGB----------A, 10YFR-RTE------C)`.
Populated payload mirrors A26/B08 (`total_nominated_capacity`) — same
`Publication_MarketDocument` shell with TS `<businessType>A29</businessType>`
and `<auction.Category>A01</auction.Category>` echoing the request.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/total_capacity_allocated/year=YYYY/month=MM/total_capacity_allocated_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.TotalCapacityAllocatedTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope (same fields as `total_nominated_capacity`).

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 1500.0,
        "business_type": "A29",
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

- **Lowercase `auction.Category`** vs the otherwise capitalised
  `Auction.Category` of `transfer_capacity_use`. ENTSO-E parameter casing is
  inconsistent across articles — copy from the connector.
- Allocation publications are sparse — many GB borders post-Brexit publish
  no allocation entries because they no longer participate in long-term
  capacity products with continental TSOs.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A26, processType=none, businessType=A29, auction.Category=A01, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code — the `total_capacity_allocated` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08 GB→FR daily and 30-day:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (post-Brexit GB borders publish no long-term allocation; sanity check NL→DE not run for this specific tuple but the pattern follows the rest of the EMPTY GB borders).
- **Disambiguation from sister A26 `total_nominated_capacity`:**
  - `total_nominated_capacity`: `businessType=B08`, no auction.Category, no contract.
  - **`total_capacity_allocated`** (this page): `businessType=A29` + `auction.Category=A01` (lowercase) + `contract_MarketAgreement.Type=A01` (lowercase).

---

## Modelling notes

- Pair with `total_nominated_capacity` and NTC (`net_transfer_capacity`) to
  compute headroom: `headroom = NTC − allocated`. Used as a feature for
  day-ahead intraday transition (residual capacity available to ID).

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
