---
source: entsoe
dataset_key: cross_zonal_balancing_capacity
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Allocation and use of cross-zonal balancing capacity (A38 / A51)

## Overview

Volume of balancing **capacity** reserved on cross-zonal interconnectors
between two TSO control areas — an extension of the procured-balancing-
capacity concept to interconnector reserve sharing. Each TimeSeries
represents capacity that one TSO (`Acquiring_Domain`) has reserved on
the connecting area (`Connecting_Domain`)'s side of an interconnector,
typically as part of cross-border reserve cooperation
(`PICASSO`, `MARI`, `TERRE`, etc.).

This is the only H8 balancing dataset that uses **two domain
parameters** (acquiring + connecting). It captures cross-zonal capacity
allocation rather than energy flows; for actual energy flows on
interconnectors, use `cross_border_flows` (A11) and for net transfer
capacity see `net_transfer_capacity` (A61).

A38 is paired with `processType=A51` (cross-zonal capacity allocation).

→ Domain concepts:
  [Cross-zonal markets](../../20-domain/markets/cross-zonal.md)
  [Reserve sharing](../../20-domain/concepts/reserve-sharing.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=<ENTSOE_API_KEY>` |
| Rate limit       | Vendor-published: not documented. Project default: 1 req/s. |
| Pagination       | None — typically one TimeSeries per (direction, agreement_type). |
| Historical depth | TODO — H8 catalogue, varies by interconnector. GB-FR has no published data. |
| Publication lag  | After cross-zonal allocation auction close. |
| Response format  | XML (`Balancing_MarketDocument`) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | string | Yes | `A38` | `A38` |
| `processType` | string | Yes | `A51` | `A51` |
| `Acquiring_Domain` | string (EIC) | Yes | TSO that procures capacity. | `10YGB----------A` |
| `Connecting_Domain` | string (EIC) | Yes | Area on the other side of the interconnector. | `10YFR-RTE------C` |
| `periodStart` | string | Yes | UTC `yyyyMMddHHmm` | `202605070000` |
| `periodEnd` | string | Yes | UTC `yyyyMMddHHmm`, max 1 day | `202605080000` |
| `Type_MarketAgreement.Type` | string | Optional | `A01`=daily, `A02`=weekly, etc. — filter | `A01` |
| `securityToken` | string | Yes | API key | `<UUID>` |

ENTSOE tuple: `(documentType=A38, processType=A51, businessType=n/a, area-param-name=Acquiring_Domain + Connecting_Domain)`. This is the **only** H8 balancing dataset with two domain parameters; both are required and they capitalise the leading letter (`Acquiring_`, `Connecting_`) per the ENTSOE API guide.

### Working curl example

```bash
curl --ssl-no-revoke -fsS -H "Accept: application/xml" \
  "https://web-api.tp.entsoe.eu/api?documentType=A38&processType=A51&Acquiring_Domain=10YGB----------A&Connecting_Domain=10YFR-RTE------C&periodStart=202605070000&periodEnd=202605080000&securityToken=${ENTSOE_API_KEY}" \
  -o /tmp/entsoe-cross_zonal_balancing_capacity.xml \
  -w "HTTP %{http_code} | %{size_download} bytes\n"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/cross_zonal_balancing_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (acquiring_area, connecting_area, fetch window).

### Bronze sample

From `tests/fixtures/entsoe/cross_zonal_balancing_capacity_gb_fr.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Balancing_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:0">
  <mRID>fixture-cross-zonal-balancing-capacity-gb-fr-20240115</mRID>
  <revisionNumber>1</revisionNumber>
  <type>A38</type>
  <process.processType>A51</process.processType>
  <TimeSeries>
    <mRID>cross-zonal-capacity-1</mRID>
    <Type_MarketAgreement.Type>A01</Type_MarketAgreement.Type>
    <Acquiring_Domain.mRID codingScheme="A01">10YGB----------A</Acquiring_Domain.mRID>
    <Connecting_Domain.mRID codingScheme="A01">10YFR-RTE------C</Connecting_Domain.mRID>
    <Period>
      <timeInterval>
        <start>2024-01-15T00:00Z</start>
        <end>2024-01-15T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>210</quantity></Point>
      <Point><position>2</position><quantity>215</quantity></Point>
    </Period>
  </TimeSeries>
</Balancing_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/cross_zonal_balancing_capacity/year=YYYY/month=MM/cross_zonal_balancing_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h8_balancing.CrossZonalBalancingCapacityTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeCrossZonalBalancingCapacity`
**Dedup key**: `(timestamp_utc, acquiring_area_code, connecting_area_code, market_agreement_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived | UTC-aware. |
| `acquiring_area_code` | `str` | No | `Acquiring_Domain.mRID` | Renamed from `acquiring_domain`. |
| `connecting_area_code` | `str` | No | `Connecting_Domain.mRID` | Renamed from `connecting_domain`. |
| `quantity_mw` | `float` | No | `<quantity>` | Capacity reserved in MW. |
| `market_agreement_type` | `str` | No | `<Type_MarketAgreement.Type>` | Default "" in canonical. E.g. `A01`. |
| `business_type` | `str` | No | `<businessType>` | Default "" in canonical. Often empty. |
| `resolution` | `str` | No | `<resolution>` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | Default "entsoe" in canonical. |
| `ingested_at` | `datetime` | Yes | derived | Nullable (datetime or None). |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2024, 1, 15, 0, 0, tzinfo=UTC),
        "acquiring_area_code": "10YGB----------A",
        "connecting_area_code": "10YFR-RTE------C",
        "quantity_mw": 210.0,
        "market_agreement_type": "A01",
        "business_type": "",
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2024, 1, 15, 1, 0, tzinfo=UTC),
        "acquiring_area_code": "10YGB----------A",
        "connecting_area_code": "10YFR-RTE------C",
        "quantity_mw": 215.0,
        "market_agreement_type": "A01",
        "business_type": "",
        "resolution": "PT60M",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **GB→FR returns EMPTY.** Live curl on 2026-05-08 returned reason 999: `No matching data found for Data item ALLOCATION_AND_USE_CROSS_ZONAL_CAPACITY [GL EB 12.3.H&I] (10YGB----------A, 10YFR-RTE------C)...`. National Grid ESO does not publish this for IFA.
- **Two domain parameters required.** Unlike all other H8 balancing datasets, A38 needs both `Acquiring_Domain` AND `Connecting_Domain`. Submitting only one returns reason 999 / 400.
- **Capitalisation matters.** ENTSOE expects `Acquiring_Domain` and `Connecting_Domain` (leading caps), not `acquiring_Domain` / `connecting_Domain`. The connector preserves casing from `endpoints.DOC_TYPES` correctly.
- **Direction is implicit.** Reserve sharing direction is encoded in the (acquiring, connecting) pair — there's no separate `direction` field. Reverse direction (FR acquiring on GB) is a separate API call with swapped domains.

### Control-area vs cross-zonal

This is the **cross-zonal** member of the H8 balancing-capacity family.
The single-area counterpart is A15
([procured_balancing_capacity.md](./procured_balancing_capacity.md)).
For balancing energy (not capacity), see
[balancing_energy_bids.md](./balancing_energy_bids.md) and
[aggregated_balancing_energy_bids.md](./aggregated_balancing_energy_bids.md).

---

## Implementation delta

- **`domain_style="zone_pair"` + `domain_params=("Acquiring_Domain", "Connecting_Domain")`.** The connector's `_domain_params` helper picks `domain_params` over `domain_style` when both are set, so `domain_style` is effectively informational here. Verified via tests/fixture parsing.
- **Connector iterates over `_FLOW_PAIRS`.** Only `(GB, FR), (GB, NL), (GB, BE), (GB, IE-SEM), (FR, BE), (FR, DE-LU), (NL, DE-LU), (NL, BE)` are queried — no programmatic way to add a new acquiring/connecting pair without code change.

---

## Modelling notes

- Cross-zonal balancing capacity volumes are leading indicators for **interconnector reserve sharing** — when GB or FR contractually reserves cross-zonal capacity, that reduces commercial capacity available for energy flows during balancing scarcity.
- Useful as a feature for: interconnector flow models (capacity displacement), cross-border price spread models (reserve costs).
- Sparse for the GB-FR pair — for active reserve-sharing pairs, use DE↔LU, FR↔DE-LU, etc.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf) — Section 17 / GL EB 12.3.H&I
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoint registry](../../../../src/gridflow/connectors/entsoe/endpoints.py) — `cross_zonal_balancing_capacity`
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h8_balancing.py) — `CrossZonalBalancingCapacityTransformer`
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py) — `EntsoeCrossZonalBalancingCapacity`
- [Fixture](../../../../tests/fixtures/entsoe/cross_zonal_balancing_capacity_gb_fr.xml)
- [Single-area counterpart](./procured_balancing_capacity.md)
