---
source: entsoe
dataset_key: transfer_capacity_use
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Use of Transfer Capacity (A25, businessType=B05)

## Overview

How much of the offered explicit allocation capacity was actually used by
holders, in MW, per zone-pair and trading horizon. Article 12.1.A of
Regulation (EC) 543/2013. Distinct from `auction_revenue` (also A25) by
`businessType=B05` and the inclusion of `Auction.Category=A01`. Used to
analyse capacity-rights utilisation and unutilised-capacity returns.

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
| documentType | `A25` |
| processType | (none) |
| businessType | `B05` (use of transfer capacity) |
| `Auction.Category` (capitalised A) | `A01` |
| `contract_MarketAgreement.Type` (lowercase c) | `A01` (daily) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A25/B05 is directional. Default UK-centric pairs.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A25` | `A25` |
| `businessType` | str | Yes | `B05` | `B05` |
| `Auction.Category` | str | Yes | `A01` | `A01` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` | `A01` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-transfer_capacity_use.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A25&businessType=B05&Auction.Category=A01&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/transfer_capacity_use/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08 GB→FR: Acknowledgement, Reason 999 —
`USE_OF_TRANSFER_CAPACITY [12.1.A] (10YGB----------A, 10YFR-RTE------C)`.
Retried 30-day: also EMPTY. Populated payload mirrors A09 commercial
schedules in shape (TS quantity in MW).

---

## Silver layer

**Path pattern**: `data/silver/entsoe/transfer_capacity_use/year=YYYY/month=MM/transfer_capacity_use_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.TransferCapacityUseTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeTransmissionMarketQuantity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code, business_type)`
**Point-in-time field**: `none`

### Silver schema

H6 quantity envelope: `timestamp_utc`, `in_area_code`, `out_area_code`,
`quantity_mw`, `business_type`, `resolution`, `data_provider`,
`ingested_at`.

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 1100.0,
        "business_type": "B05",
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

- **MW, not money.** Despite sharing `documentType=A25` with the EUR-valued
  `auction_revenue` and `congestion_income`, this dataset uses the *quantity*
  schema (`EntsoeTransmissionMarketQuantity`).
- Param casing mix is real and intentional: `Auction.Category` is capitalised
  while `contract_MarketAgreement.Type` is lowercase. The connector preserves
  both casings.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A25, processType=none, businessType=B05, Auction.Category=A01, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code — the `transfer_capacity_use` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08 GB→FR daily and 30-day:** Acknowledgement, Reason 999. **EMPTY** — cause: "border has zero allocation in window" (use-of-capacity publication cadence does not align with the test daily window for GB borders).
- **Disambiguation from other A25 variants:**
  - `auction_revenue`: `businessType=B07`, no `Auction.Category`, unit EUR.
  - **`transfer_capacity_use`** (this page): `businessType=B05` + `Auction.Category=A01`, unit MW (capacity USE, not money).
  - `congestion_income`: `businessType=B10`, no `Auction.Category`, unit EUR.
  - `net_positions`: `businessType=B09`, no `Auction.Category`, **`domain_style=zone`** (single zone), unit MW.

---

## Modelling notes

- Combine with `total_capacity_allocated` (A26/A29) to compute
  `use_ratio = used / allocated`; useful for unutilised-capacity-return analysis.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
