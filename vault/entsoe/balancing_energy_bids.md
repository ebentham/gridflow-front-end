---
source: entsoe
dataset_key: balancing_energy_bids
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Balancing energy bids (A37 / A47 / B74)

## Overview

Individual balancing energy bid offers submitted by Balance Service
Providers (BSPs) into a TSO's reserve activation pool. Each TimeSeries
in the response represents one bid (one mRID), tagged with direction
(up/down regulation) and product type (Original_MarketProduct,
Standard_MarketProduct), with a Period containing the offered MW
volumes per resolution interval.

This is the **bid-level** view — each row represents one bidder's offer
for one timestamp. For aggregate (summed-across-bidders) balancing
energy quantities, use
[aggregated_balancing_energy_bids.md](./aggregated_balancing_energy_bids.md).
For activation outcomes (how much of those bids were actually called
on), use the H7 activated balancing prices/quantity datasets.

A37 is paired with `processType=A47` (balancing energy bid submission).
The H8 spec uses `connecting_Domain` here, not `area_Domain`, because
balancing energy bids can come from cross-zonal market participants
that connect via interconnectors. `connecting_Domain` is the area at
which the bid connects to the reserve pool.

→ Domain concepts:
  [Balancing market](../../20-domain/markets/balancing-market.md)
  [Reserve products](../../20-domain/concepts/reserve-products.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://web-api.tp.entsoe.eu` |
| Path             | `/api` |
| Method           | GET |
| Auth             | Query param `securityToken=<ENTSOE_API_KEY>` |
| Rate limit       | Vendor-published: not documented. Project default: 1 req/s. |
| Pagination       | `offset` parameter (mandatory). API documents up to 4800 TimeSeries; if exceeded, increment `offset` by 100 until pages exhausted (per ENTSOE API guide §4.1). |
| Historical depth | TODO — H8 catalogue, varies by control area. GB has no published data (EMPTY). |
| Publication lag  | Near real-time after gate closure of the relevant balancing market interval. |
| Response format  | XML (`Balancing_MarketDocument`) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | string | Yes | `A37` | `A37` |
| `processType` | string | Yes | `A47` (balancing energy bid submission) | `A47` |
| `businessType` | string | Yes | `B74` (offer) | `B74` |
| `offset` | int | Yes | Pagination offset, start at `0` | `0` |
| `connecting_Domain` | string (EIC) | Yes | Connecting area EIC. Note: not `area_Domain` and not `controlArea_Domain`. | `10YGB----------A` |
| `periodStart` | string | Yes | UTC `yyyyMMddHHmm` | `202605070000` |
| `periodEnd` | string | Yes | UTC `yyyyMMddHHmm`, max 1 day window | `202605080000` |
| `securityToken` | string | Yes | API key | `<UUID>` |
| `Direction` | string | Optional | `A01` (up) / `A02` (down) — filter | `A01` |
| `Original_MarketProduct` | string | Optional | Filter on bidder's original market product | `A01` |
| `Standard_MarketProduct` | string | Optional | Filter on standardised product | `A05` |

ENTSOE tuple: `(documentType=A37, processType=A47, businessType=B74, area-param-name=connecting_Domain)`. Optional `(BusinessType, type_MarketAgreement.Type)` not applicable — A37 carries Original_MarketProduct / Standard_MarketProduct instead.

### Working curl example

```bash
curl --ssl-no-revoke -fsS -H "Accept: application/xml" \
  "https://web-api.tp.entsoe.eu/api?documentType=A37&processType=A47&businessType=B74&offset=0&connecting_Domain=10YGB----------A&periodStart=202605070000&periodEnd=202605080000&securityToken=${ENTSOE_API_KEY}" \
  -o /tmp/entsoe-balancing_energy_bids.xml \
  -w "HTTP %{http_code} | %{size_download} bytes\n"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/balancing_energy_bids/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML (`Balancing_MarketDocument`), as-received.
**Granularity**: One file per (connecting_area, fetch window, offset page).

### Bronze sample

From `tests/fixtures/entsoe/balancing_energy_bids_gb.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Balancing_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:balancingdocument:4:0">
  <mRID>fixture-balancing-energy-bids-gb-20240115</mRID>
  <revisionNumber>1</revisionNumber>
  <type>A37</type>
  <process.processType>A47</process.processType>
  <TimeSeries>
    <mRID>bid-1</mRID>
    <businessType>B74</businessType>
    <Direction>A01</Direction>
    <Original_MarketProduct><marketProductType>A01</marketProductType></Original_MarketProduct>
    <Standard_MarketProduct><marketProductType>A05</marketProductType></Standard_MarketProduct>
    <connecting_Domain.mRID codingScheme="A01">10YGB----------A</connecting_Domain.mRID>
    <Period>
      <timeInterval>
        <start>2024-01-15T00:00Z</start>
        <end>2024-01-15T02:00Z</end>
      </timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>45</quantity></Point>
      <Point><position>2</position><quantity>52</quantity></Point>
    </Period>
  </TimeSeries>
</Balancing_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/balancing_energy_bids/year=YYYY/month=MM/balancing_energy_bids_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.h8_balancing.BalancingEnergyBidsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeBalancingEnergyBid`
**Dedup key**: `(timestamp_utc, area_code, bid_mrid, direction)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime[UTC]` | No | derived (Period start + position * resolution) | UTC-aware. |
| `area_code` | `str` | No | `connecting_Domain.mRID` | Renamed from `connecting_domain`. |
| `quantity_mw` | `float` | No | `<quantity>` | Bid volume offered in MW. |
| `business_type` | `str` | No | `<businessType>` | Default "" in canonical. `B74` for bids. |
| `bid_mrid` | `str` | No | `TimeSeries/<mRID>` | Default "" in canonical. Renamed from `timeseries_mrid` — the bid identity. |
| `direction` | `str` | No | `<Direction>` (or `flowDirection.direction`) | Default "" in canonical. `A01`=up, `A02`=down. |
| `original_market_product` | `str` | No | `Original_MarketProduct/marketProductType` | Default "" in canonical. Bidder-side product. |
| `standard_market_product` | `str` | No | `Standard_MarketProduct/marketProductType` | Default "" in canonical. Standardised product code. |
| `resolution` | `str` | No | `<resolution>` (resolved to timedelta string) | Default "" in canonical. |
| `data_provider` | `str` | No | derived | Default "entsoe" in canonical. |
| `ingested_at` | `datetime` | Yes | derived | Nullable (datetime or None). |

### Silver sample

```python
[
    {
        "timestamp_utc": datetime(2024, 1, 15, 0, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": 45.0,
        "business_type": "B74",
        "bid_mrid": "bid-1",
        "direction": "A01",
        "original_market_product": "A01",
        "standard_market_product": "A05",
        "resolution": "1:00:00",
        "data_provider": "entsoe",
        "ingested_at": datetime(2026, 5, 8, 18, 3, tzinfo=UTC),
    },
    {
        "timestamp_utc": datetime(2024, 1, 15, 1, 0, tzinfo=UTC),
        "area_code": "10YGB----------A",
        "quantity_mw": 52.0,
        "business_type": "B74",
        "bid_mrid": "bid-1",
        "direction": "A01",
        "original_market_product": "A01",
        "standard_market_product": "A05",
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

- **GB returns EMPTY.** Live curl on 2026-05-08 returned reason 999: `No matching data found for Data item BALANCING_ENERGY_BIDS_R3 [GL EB 12.3.B&C] (10YGB----------A)...`. National Grid ESO does not publish to ENTSOE for this data item.
- **`offset` is mandatory.** Documented in ENTSOE API guide §4.1 — for endpoints with potentially many TimeSeries (>4800), pagination via `offset` is required. The connector currently always sends `offset=0` and does not iterate further pages — for high-volume areas this would silently truncate.
- **`bid_mrid` is the bidder identity.** The transformer renames `timeseries_mrid` → `bid_mrid`. Multiple Points within a bid share the same `bid_mrid`; multiple bids in the same response have distinct mRIDs.
- **Direction casing varies.** Some responses emit `<Direction>` and others `<flowDirection><direction>`; parser handles both.

### Control-area vs cross-zonal

A37 uses `connecting_Domain` (the area where the bid connects to the
reserve pool), not `area_Domain` (which is the TSO control area). This
distinction matters for cross-zonal balancing — a French BSP can submit
bids that connect via the GB control area through the IFA interconnector.
For domestic balancing only, `connecting_Domain` and `area_Domain` will
typically point to the same EIC.

---

## Implementation delta

- **Pagination not implemented in connector.** `offset=0` is hardcoded as an extra param; the client never iterates pages. For dense-bid areas this would cap results at 4800 TimeSeries. Track as a follow-up; not changed in V1.
- **Schema-vs-fixture default for `business_type`.** Schema default is `""` but `endpoints.py` always sends `B74` and the fixture carries `B74`. Empty default is harmless but misleading — the dataset will never produce a row with empty `business_type` from this query path.

---

## Modelling notes

- Bid-level features (offered MW, direction, product type) are useful for: balancing market price formation, BSP behaviour modelling, capacity-margin shadow-price modelling.
- For aggregate balancing pressure, use `aggregated_balancing_energy_bids` instead — bid-level data is high-cardinality and noisy when summed across bidders.
- GB modelling alternative: Elexon `boal` (bid-offer-acceptance) — different schema (per-acceptance, not per-bid) but equivalent semantic content.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf) — Section 17.4 / GL EB 12.3.B&C
- [Connector source](../../../../src/gridflow/connectors/entsoe/client.py)
- [Endpoint registry](../../../../src/gridflow/connectors/entsoe/endpoints.py) — `balancing_energy_bids`
- [Silver transformer](../../../../src/gridflow/silver/entsoe/h8_balancing.py) — `BalancingEnergyBidsTransformer`
- [Pydantic schema](../../../../src/gridflow/schemas/entsoe.py) — `EntsoeBalancingEnergyBid`
- [Fixture](../../../../tests/fixtures/entsoe/balancing_energy_bids_gb.xml)
- [Aggregated counterpart](./aggregated_balancing_energy_bids.md)
