---
source: entsoe
dataset_key: total_nominated_capacity
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Total Nominated Capacity (A26, businessType=B08)

## Overview

Total commercial capacity nominated by market participants per zone-pair.
Article 12.1.B of Regulation (EC) 543/2013. Distinct from
`commercial_schedules` (A09) in that A26/B08 is the *aggregated nominated
total* (a sum over participants) at the auction-product level. One of two
A26-document variants. Used in capacity-utilisation models alongside A09.

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
| Publication lag  | D-1 |
| Response format  | XML |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A26` |
| processType | (none) |
| businessType | `B08` (total nominated capacity) |
| `contract_MarketAgreement.Type` | (not in request — server returns `A01` on TS) |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A26/B08 is directional. Default UK-centric pairs.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A26` | `A26` |
| `businessType` | str | Yes | `B08` | `B08` |
| `in_Domain` | str | Yes | Source EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | Destination EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-total_nominated_capacity.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A26&businessType=B08&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/total_nominated_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (border, day).

### Bronze sample

```xml
<?xml version="1.0" encoding="utf-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0">
  <mRID>b0ce3ea9d6484aeeb014676a3e30e644</mRID>
  <type>A26</type>
  <createdDateTime>2026-05-08T18:06:25Z</createdDateTime>
  <period.timeInterval>
    <start>2026-05-06T00:00Z</start>
    <end>2026-05-07T00:00Z</end>
  </period.timeInterval>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>B08</businessType>
    <in_Domain.mRID codingScheme="A01">10YGB----------A</in_Domain.mRID>
    <out_Domain.mRID codingScheme="A01">10YFR-RTE------C</out_Domain.mRID>
    <contract_MarketAgreement.type>A01</contract_MarketAgreement.type>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <curveType>A03</curveType>
    <Period>
      <timeInterval>
        <start>2026-05-06T00:00Z</start>
        <end>2026-05-07T00:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>3028</quantity></Point>
      <Point><position>6</position><quantity>2928</quantity></Point>
      <Point><position>22</position><quantity>2029</quantity></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/total_nominated_capacity/year=YYYY/month=MM/total_nominated_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h6_market.TotalNominatedCapacityTransformer`
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
        "quantity_mw": 3028.0,
        "business_type": "B08",
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:05:30Z",
    },
    {
        "timestamp_utc": "2026-05-06T05:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "quantity_mw": 2928.0,
        "business_type": "B08",
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

- A26/B08 returns *aggregated* nominations — sum across all explicit auction
  holders, not per-holder data.
- `<contract_MarketAgreement.type>` on the TS payload is `A01` (daily) by
  default — even though it is not required in the request.
- `curveType=A03` returns sparse positions (compressed-resolution); silver
  preserves the as-published positions.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A26, processType=none, businessType=B08, domain=in_Domain+out_Domain)`. Matches code `endpoints.py:250-256`.
- **Live validation 2026-05-08 GB→FR for 2026-05-06:** `Publication_MarketDocument` with 3 TimeSeries (one per nominated MarketAgreement / direction split), variable-resolution points, MW values 2029-3028 across 24h. **PASS**.
- **Disambiguation from sister A26 `total_capacity_allocated`** (this is critical because both share `documentType=A26`):
  - **`total_nominated_capacity`** (this page): `businessType=B08`, no `auction.Category`, no `contract_MarketAgreement.Type` in request.
  - `total_capacity_allocated`: `businessType=A29` + `auction.Category=A01` + `contract_MarketAgreement.Type=A01`.

---

## Modelling notes

- Pair with `total_capacity_allocated` to compute
  `nomination_ratio = nominated / allocated`. <100% indicates unutilised
  rights; >100% would indicate over-nomination (rare and a data flag).
- Useful as a feature for capacity-rights utilisation models.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h6_market.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
