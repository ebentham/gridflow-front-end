---
source: entsoe
dataset_key: installed_capacity_units
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Installed capacity per production unit (A71/A33)

## Overview

Installed capacity in MW for each named generation unit per bidding zone,
broken out by EIC PSR production type. The unit-level twin of A68/A33.
Updated yearly. Used to look up nameplate capacity per unit, attribute
generation to specific assets, and to map asset names ↔ EIC mRIDs for
cross-referencing with `actual_generation_units` (A73) or master data
(A95).

→ [Installed capacity (aggregate)](installed_capacity.md), [Generation units master data](generation_units_master_data.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None (large responses arrive in one document — 366 KB observed for GB) |
| Historical depth | yearly snapshots from ~2014 |
| Publication lag  | yearly publication |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A71 |
| Process type     | A33 (year-ahead reference) |
| Business type    | n/a (per-TimeSeries `B11` — production unit) |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A71` | `A71` |
| `processType` | str | yes | `A33` | `A33` |
| `in_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` | `202601010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202612310000` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A71&processType=A33&in_Domain=10YGB----------A&periodStart=202601010000&periodEnd=202612310000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB yearly window: HTTP 200, **PASS** — `GL_MarketDocument`, 230 TimeSeries (one per registered production unit). Each TimeSeries has `<registeredResource.mRID>` (EIC unit code) and `<registeredResource.name>` (asset short name e.g. "ABRBO" for Aberthaw).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/installed_capacity_units/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, year-window).

### Bronze sample (GB 2026, truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <type>A71</type>
  <process.processType>A33</process.processType>
  <TimeSeries>
    <mRID>4207978978a44c9a</mRID>
    <businessType>B11</businessType>
    <objectAggregation>A06</objectAggregation>
    <inBiddingZone_Domain.mRID codingScheme="A01">10YGB----------A</inBiddingZone_Domain.mRID>
    <registeredResource.mRID codingScheme="A01">48WSTN0000ABRBON</registeredResource.mRID>
    <registeredResource.name>ABRBO</registeredResource.name>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <MktPSRType><psrType>B18</psrType></MktPSRType>
    ...
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/installed_capacity_units/year=YYYY/month=MM/installed_capacity_units_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.installed_capacity_units.InstalledCapacityUnitsTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeInstalledCapacityUnits`
**Dedup key**: `(timestamp_utc, area_code, unit_mrid)`
**Point-in-time field**: `ingested_at`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Period start | Yearly P1Y resolution |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| production_type | str | No | `<MktPSRType><psrType>` | EIC PSR type |
| unit_mrid | str | No | `<registeredResource.mRID>` | Unit EIC — keep verbatim |
| unit_name | str | No | `<registeredResource.name>` | Default "" in canonical. Asset short name. |
| capacity_mw | float | No | `<Point><quantity>` | MW |
| resolution | str | No | parsed | Default "" in canonical. `P1Y`. |
| data_provider | str | No | constant | "entsoe" |
| ingested_at | datetime[UTC] | Yes | derived | optional |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-01-01T00:00:00+00:00",
        "area_code": "10YGB----------A",
        "production_type": "B18",
        "unit_mrid": "48WSTN0000ABRBON",
        "unit_name": "ABRBO",
        "capacity_mw": 100.0,
        "resolution": "365 days, 0:00:00",
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

- **GB still publishes A71/A33** — capacity per unit is part of network code obligations and survives Brexit, unlike most operational A75/A73 datasets. Use this instead of A68/A33 (aggregate) which **does** EMPTY for GB.
- **Use a yearly window** — `max_query_days: 365` in config matches.
- A71 documentType is shared with `generation_forecast` (A71/A01); disambiguate by `processType`.
- Unit names are short codes (ABRBO, DRAXX-1, etc.) — see Elexon `bmunits_reference` to map to BM unit IDs.
- `MAW` in the `quantity_Measure_Unit.name` field is ENTSO-E shorthand for MW.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §14.1.A unit-level annex): `(documentType=A71, processType=A33, businessType=n/a, in_Domain)`.
  - Code: `("A71", "A33", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- A71 collision with `generation_forecast` (A71/A01) — code disambiguates by `processType` and dataset key. No bug, just a footgun for direct API users.

---

## Modelling notes

- Asset registry — map BM unit IDs (Elexon) ↔ EIC mRIDs (ENTSO-E) via name match.
- Capacity-weighted aggregation for portfolio models.
- Closure / new-build tracking via year-on-year diffs.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/installed_capacity_units.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
