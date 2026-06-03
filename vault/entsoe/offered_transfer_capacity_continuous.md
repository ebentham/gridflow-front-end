---
source: entsoe
dataset_key: offered_transfer_capacity_continuous
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Offered Transfer Capacity: Continuous (A31, Auction.Type=A01)

## Overview

Capacity offered through *continuous* allocations (the auction style used by
intraday markets and some bilateral products). Article 11.1 of Regulation
(EC) 543/2013. Distinguished from `offered_transfer_capacity_implicit` and
`offered_transfer_capacity_explicit` by `(Auction.Type, Auction.Category)`
combinations and the casing of the `Auction.*` and
`Contract_MarketAgreement.*` parameters. Used as feature for intraday
spread models.

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
| Publication lag  | After auction allocation |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A31` |
| processType | (none) |
| `Auction.Type` (capitalised) | `A01` |
| `Contract_MarketAgreement.Type` (capitalised) | `A01` (daily) |
| businessType (request) | (none) |
| domain-param-name | `In_Domain` + `Out_Domain` (note capitalised — `domain_params=("In_Domain","Out_Domain")` in code) |

### Cross-zonal parameters

A31 continuous is directional. UK-centric default (GB→FR).

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A31` | `A31` |
| `Auction.Type` | str | Yes | `A01` continuous | `A01` |
| `Contract_MarketAgreement.Type` | str | Yes | `A01` daily | `A01` |
| `In_Domain` | str | Yes | Source zone EIC (capitalised) | `10YGB----------A` |
| `Out_Domain` | str | Yes | Destination zone EIC (capitalised) | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-offered_transfer_capacity_continuous.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A31&Auction.Type=A01&Contract_MarketAgreement.Type=A01&In_Domain=10YGB----------A&Out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/offered_transfer_capacity_continuous/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

Live 2026-05-08 (GB→FR, daily window): Acknowledgement, Reason 999 —
`OFFERED_TRANSFER_CAPACITIES_IMPLICIT [11.1] (10YGB----------A,
10YFR-RTE------C)`. (Note: even with `Auction.Type=A01` continuous, the
ENTSO-E acknowledgement labels the data item by aggregate Article 11.1
group and only fingerprints by domain — not auction type.) Retried with
30-day window: still EMPTY.

---

## Silver layer

**Path pattern**: `data/silver/entsoe/offered_transfer_capacity_continuous/year=YYYY/month=MM/offered_transfer_capacity_continuous_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.OfferedTransferCapacityContinuousTransformer`
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
        "quantity_mw": 1500.0,
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

- **Capitalised parameter names.** Unlike `_implicit` and `_explicit`, this
  variant uses `Auction.Type` (capital A) and `Contract_MarketAgreement.Type`
  (capital C). The connector's `domain_params=("In_Domain", "Out_Domain")`
  matches the same casing. ENTSO-E *appears* tolerant of casing for some
  parameters but the code follows the API guide section 11.1 exactly.
- All three A31 variants share the same data-item label
  (`OFFERED_TRANSFER_CAPACITIES_IMPLICIT [11.1]`) in EMPTY responses — the
  acknowledgement does not echo the auction type.
- EMPTY for GB borders is common post-Brexit: GB does not participate in EU
  capacity allocation auctions.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A31, processType=none, businessType=none-in-request, Auction.Type=A01, Contract_MarketAgreement.Type=A01, domain=In_Domain+Out_Domain)`. Matches code — the `offered_transfer_capacity_continuous` entry in `endpoints.py` `DOC_TYPES`. Note **capitalised** parameter names — distinct from `_implicit` and `_explicit`.
- **Live validation 2026-05-08 GB→FR daily window:** Acknowledgement, Reason 999. Retried 30-day: still EMPTY. **EMPTY** — cause: "border has zero allocation in window" (GB no longer participates in EU continuous auctions post-Brexit; sanity-checked NL→DE same window also EMPTY for A31 implicit, suggesting the data item is not actively published for the windows tested rather than a tuple-shape error).
- **Disambiguation from sister A31 variants:** continuous = `Auction.Type=A01` only (no `Auction.Category`); implicit also `Auction.Type=A01` but **lowercase** `auction.Type` parameter; explicit adds `auction.Category=A01` (lowercase). All three differ in casing, which the connector preserves via separate `EntsoeDocType` entries.

---

## Modelling notes

- Used as a feature for intraday spread models when the allocation regime
  matters (continuous vs explicit auction).
- Pair with A09 commercial schedules to study capacity-utilisation in the
  continuous segment.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
