---
source: entsoe
dataset_key: outages_generation
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Unavailability of generation units (A80)

## Overview

Outage notifications for generation units — one document per outage, each
declaring the affected unit (`registeredResource`), the period of
unavailability (`Available_Period`), the unavailable MW (`<quantity>`),
and the planning status (`businessType` A53=planned / A54=unplanned).
Critical input for short-term tightness models, supply-stack adjustments,
and outage-driven price spike features.

→ [Outages production](outages_production.md), [Generation units master data](generation_units_master_data.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None at the API; large windows return a **ZIP archive** of multiple XML files |
| Historical depth | ~2014 onwards |
| Publication lag  | T+~1h after TSO publication |
| Response format  | XML — root `Unavailability_MarketDocument`. Multi-document responses come as a ZIP of XML files. Code unzips transparently. |
| Document type    | A80 |
| Process type     | n/a |
| Business type    | A53 (planned) — also accepts A54 (unplanned) |
| Domain param name| `BiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A80` | `A80` |
| `BusinessType` | str | yes | `A53` (planned) or `A54` (unplanned) | `A53` |
| `BiddingZone_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm`, **30-day window recommended** | `202604010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605010000` |
| `DocStatus` | str | no | Outage status filter (A05 active, A09 cancelled, A13 withdrawn) | `A05` |
| `mRID` | str | no | Lookup specific outage notification | |
| `RegisteredResource` | EIC | no | Filter to one unit | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A80&BusinessType=A53&BiddingZone_Domain=10YGB----------A&periodStart=202604010000&periodEnd=202605010000" \
  -H "Accept: application/xml" \
  --output outages.zip
```

Live verification 2026-05-08:
- GB 30-day window: HTTP 200, **PASS** — ZIP archive (40 KB) of 17 individual `UNAVAILABILITY_OF_PRODUCTION_AND_GENERATION_UNITS_*.xml` documents covering generation outages active in the period. Connector unzips transparently and writes one bronze file per archive entry.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/outages_generation/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML — one bronze file per inner ZIP entry.
**Granularity**: One bronze XML file per outage notification (multiple inner XMLs per API call).

### Bronze sample (single outage doc, schematic)

```xml
<Unavailability_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-2:unavailibilitydocument:5:0">
  <mRID>...</mRID>
  <type>A80</type>
  <revisionNumber>2</revisionNumber>
  <docStatus><value>A05</value></docStatus>
  <TimeSeries>
    <mRID>1</mRID>
    <businessType>A53</businessType>
    <biddingZone_Domain.mRID>10YGB----------A</biddingZone_Domain.mRID>
    <production_RegisteredResource.mRID>48W000000DRAXX-1Y</production_RegisteredResource.mRID>
    <production_RegisteredResource.name>DRAXX-1</production_RegisteredResource.name>
    <production_RegisteredResource.pSRType.psrType>B02</production_RegisteredResource.pSRType.psrType>
    <Available_Period>
      <timeInterval><start>...</start><end>...</end></timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>0</quantity></Point>
    </Available_Period>
  </TimeSeries>
</Unavailability_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/outages_generation/year=YYYY/month=MM/outages_generation_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.outages_generation.OutagesGenerationTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeOutagesGeneration`
**Dedup key**: `(timestamp_utc, unit_mrid)`
**Point-in-time field**: `ingested_at` (no `published_at` surfaced)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | `Available_Period` start + position * resolution | tz-aware UTC |
| area_code | str | No | `<biddingZone_Domain.mRID>` | EIC |
| unit_mrid | str | No | `<production_RegisteredResource.mRID>` (or `RegisteredResource/mRID`) | Unit EIC |
| unit_name | str | No | `<production_RegisteredResource.name>` | Default "" in canonical. |
| outage_type | str | No | derived from `<businessType>` | "planned" (A53) / "unplanned" (A54) |
| unavailable_mw | float | No | `<Point><quantity>` | MW unavailable during interval |
| resolution | str | No | parsed | Default "" in canonical. Typically `PT60M`. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-04-15T14:00:00+00:00",
        "area_code": "10YGB----------A",
        "unit_mrid": "48W000000DRAXX-1Y",
        "unit_name": "DRAXX-1",
        "outage_type": "planned",
        "unavailable_mw": 645.0,
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

- **30-day window minimum.** A 1-day query window often returns Acknowledgement reason 999 even when outages exist. Use 30-day windows for backfill; daily incremental queries can use a rolling 30-day window with dedup.
- **ZIP archives** — the API returns a ZIP for any window with ≥1 outage. Bytes start with `PK\x03\x04`. Connector detects this in `client._is_zip_response()` and `_iter_zip_xml()` extracts inner XMLs into separate `RawResponse`s.
- **Outage status codes** (DocStatus): `A05` Active, `A09` Cancelled, `A13` Withdrawn. The default query returns Active outages only; `DocStatus=A09` retrieves cancelled notifications which can revise earlier values. NOTE: gridflow silver dedup is `df.unique(keep="last")` over the dedup key and is NOT revision-aware — `revisionNumber` is parsed but not used to order survivors, so the surviving row follows bronze parse order, not the highest revision.
- **Revision number** — same outage `mRID` may be republished with `revisionNumber > 1`. gridflow does NOT currently sort by `revisionNumber`; dedup keeps the last row in parse order (known limitation).
- **Pagination by record count** — windows with >200 outages return HTTP 400 reason 999 "exceeds the allowed maximum (200)". Splits into smaller windows are required for high-outage zones.
- `unavailable_mw` is the **unavailable** MW, not the available capacity. To compute available output, subtract from installed capacity.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §15.1.A): `(documentType=A80, processType=n/a, BusinessType=A53|A54, BiddingZone_Domain)`.
  - Code: `("A80", None, BusinessType="A53", domain_style="bidding_zone")` → `BiddingZone_Domain`.
  - **Match.** (Code defaults to A53; A54 reachable via override.)
- DocStatus values (A05/A09/A13) are **not** validated server-side beyond the codelist; passing other strings returns reason 999.

---

## Modelling notes

- Capacity-tightness models — `installed_capacity - sum(unavailable_mw)` per zone.
- Outage-driven price spike features — high `unavailable_mw` ↔ price tail risk.
- Distinguish planned (A53) vs unplanned (A54) — unplanned has higher price elasticity.
- Use unit_mrid to join with master data for production_type and capacity normalisation.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/outages_generation.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
