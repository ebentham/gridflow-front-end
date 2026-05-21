---
source: entsoe
dataset_key: generation_units_master_data
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Production and generation units master data (A95)

## Overview

Reference catalogue of every registered production / generation unit in a
bidding zone — EIC mRID, asset name, production type, control area,
provider/operator. Updated as units are commissioned / retired.
Distinct from operational time-series datasets — this is the static
**registry** lookup. Used to populate the unit-name mapping table for
joining EIC-coded data (A73, A71/A33, outages) with vendor-named data
(Elexon BMUs, internal asset registers).

→ [Installed capacity per unit](installed_capacity_units.md), [Outages production](outages_production.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None |
| Historical depth | snapshot — current registry |
| Publication lag  | continuous; updated when registry changes |
| Response format  | XML — root `Configuration_MarketDocument` |
| Document type    | A95 |
| Process type     | n/a (response carries `process.processType=A39` "production unit registry") |
| Business type    | B11 (production unit) — required parameter |
| Domain param name| `BiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A95` | `A95` |
| `BusinessType` | str | yes | `B11` (production unit) | `B11` |
| `BiddingZone_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `Implementation_DateAndOrTime` | ISO date | yes | Single date — **not a period range** | `2026-05-06` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A95&BusinessType=B11&BiddingZone_Domain=10YGB----------A&Implementation_DateAndOrTime=2026-05-06" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB: HTTP 200, **PASS** — `Configuration_MarketDocument`, 230 TimeSeries (one per registered unit). Each has `<registeredResource.mRID>`, `<registeredResource.name>`, `<registeredResource.location.name>`, `<ControlArea_Domain>`, `<Provider_MarketParticipant>`, `<MktPSRType>` and an `<implementation_DateAndOrTime.date>`.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/generation_units_master_data/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (GB, truncated)

```xml
<Configuration_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:configurationdocument:3:0">
  <type>A95</type>
  <process.processType>A39</process.processType>
  <TimeSeries>
    <mRID>a805edf4304d4b7d</mRID>
    <businessType>B11</businessType>
    <implementation_DateAndOrTime.date>2019-01-01</implementation_DateAndOrTime.date>
    <biddingZone_Domain.mRID codingScheme="A01">10YGB----------A</biddingZone_Domain.mRID>
    <registeredResource.mRID codingScheme="A01">48WSTN0000ABRBON</registeredResource.mRID>
    <registeredResource.name>ABRBO</registeredResource.name>
    <registeredResource.location.name>GB</registeredResource.location.name>
    <ControlArea_Domain><mRID codingScheme="A01">10YGB----------A</mRID></ControlArea_Domain>
    <Provider_MarketParticipant><mRID codingScheme="A01">48X000000000228R</mRID></Provider_MarketParticipant>
    <MktPSRType><psrType>B18</psrType></MktPSRType>
  </TimeSeries>
</Configuration_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/generation_units_master_data/year=YYYY/month=MM/generation_units_master_data_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.generation_units_master_data.GenerationUnitsMasterDataTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeGenerationUnitsMasterData`
**Dedup key**: `(area_code, unit_mrid)` — registry, not time series
**Point-in-time field**: `implementation_datetime_utc`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| area_code | str | No | `<biddingZone_Domain.mRID>` | EIC |
| unit_mrid | str | No | `<registeredResource.mRID>` | Unit EIC — keep verbatim |
| unit_name | str | No | `<registeredResource.name>` | Default "" in canonical. Asset short name. |
| production_type | str | No | `<psrType>` | Default "" in canonical. EIC PSR type. |
| implementation_datetime_utc | datetime[UTC] | Yes | `<implementation_DateAndOrTime.date>` | UTC tz-aware |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "area_code": "10YGB----------A",
        "unit_mrid": "48WSTN0000ABRBON",
        "unit_name": "ABRBO",
        "production_type": "B18",
        "implementation_datetime_utc": "2019-01-01T00:00:00+00:00",
        "data_provider": "entsoe",
        "ingested_at": "2026-05-08T18:00:00+00:00",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **`Implementation_DateAndOrTime` is a single date, not `periodStart`/`periodEnd`.** The connector special-cases this via `EntsoeDocType.date_param` and replaces the period range with a single ISO date. A naive `periodStart`/`periodEnd` call **will return EMPTY or 400**.
- **`BusinessType=B11` is required** — without it the request returns an Acknowledgement.
- Response root is `Configuration_MarketDocument`, **not** `Publication_MarketDocument` or `GL_MarketDocument`. Validation logic that hard-codes a single root element will reject this dataset.
- The parser uses a separate function `parse_generation_units_master_data_xml()` because the structure differs from time-series documents.
- Multiple `psrType` per unit is theoretically possible (multi-fuel) — silver keeps only the first.
- Some legacy units have `implementation_DateAndOrTime.date` as far back as 1990; check tz handling — they round-trip as UTC midnight.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §15.1.D / Static "Production and generation units"): `(documentType=A95, processType=n/a, BusinessType=B11, BiddingZone_Domain)`.
  - Code (`endpoints.py`): `("A95", None, BusinessType="B11", domain_style="bidding_zone", date_param="Implementation_DateAndOrTime")` → `BiddingZone_Domain`.
  - **Match.**
- The `date_param` mechanism is unique to A95 in `DOC_TYPES`. Anyone adding a new dataset with a similar non-period parameter must reuse this pattern.

---

## Modelling notes

- **Cross-vendor ID mapping** — join unit_mrid ↔ Elexon BM unit IDs via name fuzzy match (e.g. `bmunits_reference`).
- Asset commissioning timeline — `implementation_datetime_utc` for new-build curves.
- Production-type registry by zone — for capacity-mix dashboards.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/generation_units_master_data.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
