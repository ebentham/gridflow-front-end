---
source: entsoe
dataset_key: net_transfer_capacity
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Forecasted Net Transfer Capacity (A61, day-ahead)

## Overview

Day-ahead Net Transfer Capacity (NTC) per zone-pair, in MW. Article 11.1
of Regulation (EC) 543/2013 — the maximum forecast commercial exchange
capacity offered to the market for the trading day. Published by TSOs
typically D-1 around mid-day after capacity calculation. Used in spread
models (NTC is the upper bound on commercial flow) and as an input to
congestion forecasts.

→ Domain: [Net transfer capacity](../../20-domain/markets/net-transfer-capacity.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s default, back off on 429 |
| Pagination       | None |
| Historical depth | 2014-12-05 onward, border-dependent |
| Publication lag  | D-1 mid-day |
| Response format  | XML (`Publication_MarketDocument`) |

### ENTSO-E parameter tuple (validation criterion)

| Field | Value |
|-------|-------|
| documentType | `A61` |
| processType | (none) |
| businessType (request) | (none — server returns `A27` on TimeSeries) |
| `contract_MarketAgreement.Type` | `A01` (daily) — **required by code** as a fixed extra param |
| domain-param-name | `in_Domain` + `out_Domain` (zone_pair) |

### Cross-zonal parameters

A61 is directional. Same border-pair table as A11 cross_border_flows.

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `securityToken` | str | Yes | API key | UUID |
| `documentType` | str | Yes | `A61` | `A61` |
| `contract_MarketAgreement.Type` | str | Yes | `A01` (daily product) | `A01` |
| `in_Domain` | str | Yes | EIC | `10YGB----------A` |
| `out_Domain` | str | Yes | EIC | `10YFR-RTE------C` |
| `periodStart` / `periodEnd` | str | Yes | `yyyymmddHHMM` UTC | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -o "/tmp/entsoe-net_transfer_capacity.xml" \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A61&contract_MarketAgreement.Type=A01&in_Domain=10YGB----------A&out_Domain=10YFR-RTE------C&periodStart=202605060000&periodEnd=202605070000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/net_transfer_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (in_Domain, out_Domain, day).

### Bronze sample

```xml
<?xml version="1.0" encoding="utf-8"?>
<Publication_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0">
  <mRID>67c3c08a2dbf4c1bbaa1a114f52eed6a</mRID>
  <type>A61</type>
  <createdDateTime>2026-05-08T18:05:26Z</createdDateTime>
  <period.timeInterval>
    <start>2026-05-06T00:00Z</start>
    <end>2026-05-07T00:00Z</end>
  </period.timeInterval>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>A27</businessType>
    <in_Domain.mRID codingScheme="A01">10YGB----------A</in_Domain.mRID>
    <out_Domain.mRID codingScheme="A01">10YFR-RTE------C</out_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <curveType>A03</curveType>
    <Period>
      <timeInterval>
        <start>2026-05-06T00:00Z</start>
        <end>2026-05-07T00:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>3028</quantity></Point>
    </Period>
  </TimeSeries>
</Publication_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/net_transfer_capacity/year=YYYY/month=MM/net_transfer_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.net_transfer_capacity.NetTransferCapacityTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeNetTransferCapacity`
**Dedup key**: `(timestamp_utc, in_area_code, out_area_code)`
**Point-in-time field**: `none`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived from period + position | |
| `in_area_code` | `str` | No | `TimeSeries.in_Domain.mRID` | EIC |
| `out_area_code` | `str` | No | `TimeSeries.out_Domain.mRID` | EIC |
| `ntc_mw` | `float` | No | `Point.quantity` | MW |
| `resolution` | `str` | No | `Period.resolution` | Default "" in canonical. e.g. `PT60M`. |
| `data_provider` | `str` | No | derived | `"entsoe"` |
| `ingested_at` | `datetime[UTC]` | Yes | derived | |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T00:00:00Z",
        "in_area_code": "10YGB----------A",
        "out_area_code": "10YFR-RTE------C",
        "ntc_mw": 3028.0,
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

- Most A61 publications use a **single Point with curveType A03** (variable
  resolution) — the published NTC is constant for a flat day-ahead window
  rather than 24 hourly points. Forward-fill or expand at modelling time.
- `contract_MarketAgreement.Type` is **mandatory** even though some examples
  in older guides show it as optional. Without it, A61 returns Acknowledgement
  with Reason 999.
- Possible direction: NTC(A→B) is generally not equal to NTC(B→A). Fetch both.
- Old NTC values may be revised via republished documents; silver dedup
  retains the latest by ingested_at.

---

## Implementation delta

- **Tuple recorded:** `(documentType=A61, processType=none, businessType=none-in-request, contract_MarketAgreement.Type=A01, domain=in_Domain+out_Domain)`. Matches code — the `net_transfer_capacity` entry in `endpoints.py` `DOC_TYPES`.
- **Live validation 2026-05-08:** GB → FR for 2026-05-06 returned `Publication_MarketDocument` with 1 TimeSeries, 1 point of 3028 MW. PASS.
- TimeSeries `<businessType>` returned as `A27` (capacity allocation) — undocumented in code but expected per Article 11.1.

---

## Modelling notes

- NTC is the upper bound on `flow_mw` from cross_border_flows. Compute
  `utilisation = flow / ntc`; values >1 indicate model staleness or revised
  NTC not yet ingested.
- Useful as a regime feature: low NTC days (outages, planned reductions) are
  systematically higher-spread.

---

## Links

- [Official API docs (PDF)](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsoe/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsoe/net_transfer_capacity.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py)
