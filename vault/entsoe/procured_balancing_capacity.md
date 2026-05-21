---
source: entsoe
dataset_key: procured_balancing_capacity
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Procured balancing capacity (A15 / A51)

## Overview

Volume of balancing **capacity** (reserve) procured by a TSO ahead of
real-time, broken down by market agreement type (e.g. `A01` daily, `A02`
weekly). This is the **capacity** product (€/MW/h-style availability
payment), distinct from **balancing energy** (the activated MWh
products covered by `balancing_energy_bids` and the H7 activated
prices/quantity datasets).

A TSO procures capacity through tenders on rolling timeframes; this
dataset reports the total MW under contract for each interval. Useful
for: capacity-margin / reserve-adequacy modelling, capacity-payment
shadow-price modelling, and tracking how reserve procurement levels
respond to forecasted system stress.

A15 is paired with `processType=A51` (procurement), and the H8 spec
uses `area_Domain` (single control area). This dataset is one-area —
not cross-zonal — for the cross-zonal counterpart see
[cross_zonal_balancing_capacity.md](./cross_zonal_balancing_capacity.md).

→ Domain concepts:
  [Reserve products](../../20-domain/concepts/reserve-products.md)
  [Capacity vs energy products](../../20-domain/concepts/capacity-vs-energy.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=<ENTSOE_API_KEY>` |
| Rate limit       | Vendor-published: not documented. Project default: 1 req/s. |
| Pagination       | `offset` parameter (mandatory, start at 0) per ENTSOE API §4.1; not iterated by current connector. |
| Historical depth | TODO — H8 catalogue, varies by area. GB has no published data. |
| Publication lag  | After tender close — daily / weekly / monthly cadences depending on `Type_MarketAgreement.Type`. |
| Response format  | XML (`Balancing_MarketDocument`) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | string | Yes | `A15` | `A15` |
| `processType` | string | Yes | `A51` | `A51` |
| `offset` | int | Yes | Pagination offset, start at `0` | `0` |
| `area_Domain` | string (EIC) | Yes | Control area EIC. **Not** `controlArea_Domain`. | `10YGB----------A` |
| `periodStart` | string | Yes | UTC `yyyyMMddHHmm` | `202605070000` |
| `periodEnd` | string | Yes | UTC `yyyyMMddHHmm`, max 1 day | `202605080000` |
| `Type_MarketAgreement.Type` | string | Optional | `A01`=daily, `A02`=weekly, etc. — filter on procurement product | `A01` |
| `securityToken` | string | Yes | API key | `<UUID>` |

ENTSOE tuple: `(documentType=A15, processType=A51, businessType=n/a, area-param-name=area_Domain)`. Optional `(BusinessType, type_MarketAgreement.Type)`: `BusinessType` is **not** required at query level (the response carries `<businessType>` per TimeSeries); `Type_MarketAgreement.Type` is an optional filter — fixture carries `Type_MarketAgreement.Type=A01`.

### Working curl example

```bash
curl --ssl-no-revoke -fsS -H "Accept: application/xml" \
  "https://web-api.tp.entsoe.eu/api?documentType=A15&processType=A51&offset=0&area_Domain=10YGB----------A&periodStart=202605070000&periodEnd=202605080000&securityToken=${ENTSOE_API_KEY}" \
  -o /tmp/entsoe-procured_balancing_capacity.xml \
  -w "HTTP %{http_code} | %{size_download} bytes\n"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/procured_balancing_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML.
**Granularity**: One file per (control_area, fetch window, offset page).

### Bronze sample

From `tests/fixtures/entsoe/procured_balancing_capacity_gb.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Balancing_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:0">
  <mRID>fixture-procured-balancing-capacity-gb-20240115</mRID>
  <revisionNumber>1</revisionNumber>
  <type>A15</type>
  <process.processType>A51</process.processType>
  <TimeSeries>
    <mRID>capacity-1</mRID>
    <Type_MarketAgreement.Type>A01</Type_MarketAgreement.Type>
    <area_Domain.mRID codingScheme="A01">10YGB----------A</area_Domain.mRID>
    <Period>
      <timeInterval>
        <start>2024-01-15T00:00Z</start>
        <end>2024-01-15T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>500</quantity></Point>
      <Point><position>2</position><quantity>525</quantity></Point>
    </Period>
  </TimeSeries>
</Balancing_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/procured_balancing_capacity/year=YYYY/month=MM/procured_balancing_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h8_balancing.ProcuredBalancingCapacityTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeBalancingCapacity`
**Dedup key**: `(timestamp_utc, area_code, market_agreement_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived | UTC-aware. |
| `area_code` | `str` | No | `area_Domain.mRID` | Renamed from `area_domain`. |
| `quantity_mw` | `float` | No | `<quantity>` | Procured capacity in MW. |
| `market_agreement_type` | `str` | No | `<Type_MarketAgreement.Type>` | Default "" in canonical. `A01`=daily, `A02`=weekly, `A03`=monthly, `A04`=yearly. |
| `business_type` | `str` | No | `<businessType>` | Default "" in canonical. Often empty (TSO-specific tagging). |
| `resolution` | `str` | No | `<resolution>` | Default "" in canonical. |
| `data_provider` | `str` | No | derived | Default "entsoe" in canonical. |
| `ingested_at` | `datetime` | Yes | derived | Nullable (datetime or None). |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2024, 1, 15, 0, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": 500.0,
        "market_agreement_type": "A01",
        "business_type": "",
        "resolution": "1:00:00",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2024, 1, 15, 1, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": 525.0,
        "market_agreement_type": "A01",
        "business_type": "",
        "resolution": "1:00:00",
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

- **GB returns EMPTY.** Live curl on 2026-05-08 returned reason 999: `No matching data found for Data item PROCURED_BALANCING_CAPACITY_R3 [12.3.F] (10YGB----------A)...`.
- **Dedup includes `market_agreement_type`.** Multiple TimeSeries with the same `area_code` but different `Type_MarketAgreement.Type` (daily vs weekly procurement) coexist for the same timestamp. The dedup key `(timestamp_utc, area_code, market_agreement_type)` reflects this.
- **Pagination not iterated.** `offset=0` hardcoded — same caveat as `balancing_energy_bids`.
- **`business_type` often empty.** Unlike A86/A37, A15 responses do not always carry per-TimeSeries `businessType` — the dimension that distinguishes records is `Type_MarketAgreement.Type`.

### Control-area vs cross-zonal

A15 is single-area only (`area_Domain`). The cross-zonal capacity
counterpart is A38, see
[cross_zonal_balancing_capacity.md](./cross_zonal_balancing_capacity.md).

---

## Implementation delta

- **Connector hardcodes `offset=0`.** Same pagination caveat as `balancing_energy_bids` — for high-cardinality areas this caps results.
- **`Type_MarketAgreement.Type` filter is documented optional but the dedup key requires it to distinguish rows.** If a future call ever filters to a single agreement type, the dedup remains valid; if it does not filter, the response naturally splits across multiple TimeSeries with distinct `Type_MarketAgreement.Type` values, which the parser surfaces correctly.

---

## Modelling notes

- Procured-capacity volumes are leading indicators for **reserve scarcity** — when capacity below historical mean, balancing energy prices typically firm up.
- Use as a feature in: capacity-payment shadow-price models, reserve-margin nowcasts, and balancing market spreads.
- Pair with [aggregated_balancing_energy_bids.md](./aggregated_balancing_energy_bids.md) (capacity vs energy, before activation) and the H7 activated datasets (capacity vs realised activations).

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf) — Section 17 / 12.3.F
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoint registry](../../../../src/gridflow/connectors/entsoe/endpoints.py) — `procured_balancing_capacity`
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h8_balancing.py) — `ProcuredBalancingCapacityTransformer`
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py) — `EntsoeBalancingCapacity`
- [Fixture](../../../../tests/fixtures/entsoe/procured_balancing_capacity_gb.xml)
- [Cross-zonal counterpart](./cross_zonal_balancing_capacity.md)
