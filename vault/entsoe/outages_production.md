---
source: entsoe
dataset_key: outages_production
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Unavailability of production units (A77)

## Overview

Outage notifications for **production units** — distinct from generation
units (A80) in scope at the API level (different documentType code) but
with overlapping content. A77 covers production-unit-level outages where
the registry references `production_RegisteredResource`. Used alongside
A80 for portfolio-wide outage tracking; in practice the two datasets
overlap for many TSOs and consumers ingest both then dedup by unit_mrid.

→ [Outages generation](outages_generation.md), [Generation units master data](generation_units_master_data.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None (200-record cap; large windows can return HTTP 400 reason 999) |
| Historical depth | ~2014 onwards |
| Publication lag  | T+~1h |
| Response format  | XML — root `Unavailability_MarketDocument`. ZIP for multi-document. |
| Document type    | A77 |
| Process type     | n/a |
| Business type    | A53 (planned) — also A54 (unplanned) |
| Domain param name| `BiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A77` | `A77` |
| `BusinessType` | str | yes | `A53` or `A54` | `A53` |
| `BiddingZone_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm`, 30-day | `202604010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605010000` |
| `DocStatus` | str | no | A05/A09/A13 status filter | |
| `mRID` | str | no | Specific notification | |
| `RegisteredResource` | EIC | no | Filter to one unit | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A77&BusinessType=A53&BiddingZone_Domain=10YGB----------A&periodStart=202604010000&periodEnd=202605010000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB 30-day window: HTTP 200, **EMPTY** (Ack 999 "UNAVAILABILITY_OF_PRODUCTION_AND_GENERATION_UNITS [15.1.A, 15.1.B, 15.1.C, 15.1.D]"). Brexit-GB.
- DE-LU 30-day window: HTTP 400 reason 999 "The number of instances (3209) exceeds the allowed maximum (200)" — confirms request shape valid; 30-day window over DE produces too many notifications. Use 1-day windows or split.
- DE-LU 1-day window: HTTP 200, **PASS** — ZIP archive (150 KB) containing many outage XMLs.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/outages_production/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML — one bronze file per inner ZIP entry.
**Granularity**: One bronze file per outage notification.

### Bronze sample (single outage doc, schematic)

```xml
<Unavailability_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-2:unavailibilitydocument:5:0">
  <type>A77</type>
  <docStatus><value>A05</value></docStatus>
  <TimeSeries>
    <businessType>A53</businessType>
    <biddingZone_Domain.mRID>10Y1001A1001A82H</biddingZone_Domain.mRID>
    <production_RegisteredResource.mRID>...</production_RegisteredResource.mRID>
    <production_RegisteredResource.name>UNIT-XYZ</production_RegisteredResource.name>
    <production_RegisteredResource.pSRType.psrType>B11</production_RegisteredResource.pSRType.psrType>
    <Available_Period>
      <timeInterval>...</timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>250</quantity></Point>
    </Available_Period>
  </TimeSeries>
</Unavailability_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/outages_production/year=YYYY/month=MM/outages_production_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.outages_h7.OutagesProductionTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeOutagesProduction`
**Dedup key**: `(timestamp_utc, area_code, unit_mrid, document_mrid)`
**Point-in-time field**: `ingested_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Available_Period | tz-aware UTC |
| area_code | str | No | `<biddingZone_Domain.mRID>` | EIC |
| unit_mrid | str | No | `<production_RegisteredResource.mRID>` | Production unit EIC |
| unit_name | str | No | `<production_RegisteredResource.name>` | Default "" in canonical. |
| production_type | str | No | `<production_RegisteredResource.pSRType.psrType>` | Default "" in canonical. EIC PSR. |
| outage_type | str | No | derived from `<businessType>` | "planned" / "unplanned" |
| unavailable_mw | float | No | `<Point><quantity>` | MW |
| business_type | str | No | `<businessType>` | Default "" in canonical. Raw. |
| document_mrid | str | No | root `<mRID>` | Default "" in canonical. |
| document_status | str | No | `<docStatus><value>` | Default "" in canonical. A05/A09/A13. |
| timeseries_mrid | str | No | TimeSeries `<mRID>` | Default "" in canonical. |
| resolution | str | No | parsed | Default "" in canonical. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-04-10T00:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "unit_mrid": "11WD7--AAA-VATTI",
        "unit_name": "UNIT-XYZ",
        "production_type": "B11",
        "outage_type": "planned",
        "unavailable_mw": 250.0,
        "business_type": "A53",
        "document_mrid": "DOC-001",
        "document_status": "A05",
        "timeseries_mrid": "1",
        "resolution": "1:00:00",
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

- **GB EMPTY post-Brexit.**
- **200-record cap** — DE-LU 30-day window observed to return HTTP 400 reason 999 "exceeds maximum 200". Use shorter windows (daily) or split queries by `psrType`.
- **A77 vs A80 overlap** — A77 production units and A80 generation units are distinct documentTypes but content overlaps for many TSOs. Some TSOs publish to A77 only, others to A80 only. Best practice: ingest both and dedup by `unit_mrid + document_mrid + revision`.
- **30-day window for ingestion** — gives reasonable coverage but watch for 200-cap rejection.
- **Outage status codes** (DocStatus): `A05` Active, `A09` Cancelled, `A13` Withdrawn.
- ZIP archives for multi-document responses, same as A80.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §15.1.A-D): `(documentType=A77, processType=n/a, BusinessType=A53|A54, BiddingZone_Domain)`.
  - Code: `("A77", None, BusinessType="A53", domain_style="bidding_zone")` → `BiddingZone_Domain`.
  - **Match.**
- A77 and A80 share the same XML response shape (`production_RegisteredResource` element) — silver transformers `outages_h7.OutagesProductionTransformer` and `outages_generation.OutagesGenerationTransformer` use very similar parsing. Confirm they remain in sync if either is changed.

---

## Modelling notes

- Combine with A80 for unified outage feed; dedup on `unit_mrid + document_mrid`.
- Tightness modelling — `unavailable_mw` per zone, weighted by `production_type`.
- Forecast quality benchmark — compare outage publication time vs realised generation drop.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/outages_h7.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
