---
source: entsoe
dataset_key: installed_capacity
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Installed generation capacity aggregated (A68/A33)

## Overview

Installed generation capacity in MW per bidding zone, aggregated by EIC
production type. Published yearly. Used as the structural denominator for
capacity-factor models, scenario builds, and to track new-build / closure
trends. Process type `A33` denotes "year-ahead" reference.

→ [Installed capacity per unit](installed_capacity_units.md), [Generation units master data](generation_units_master_data.md)

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
| Historical depth | ~2014 onwards |
| Publication lag  | yearly publication, around start of year |
| Response format  | XML — root `GL_MarketDocument` |
| Document type    | A68 |
| Process type     | A33 (year-ahead reference) |
| Business type    | n/a |
| Domain param name| `in_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A68` | `A68` |
| `processType` | str | yes | `A33` | `A33` |
| `in_Domain` | EIC | yes | Bidding zone | `10Y1001A1001A82H` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm`, year boundary | `202601010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm`, year boundary | `202612310000` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A68&processType=A33&in_Domain=10Y1001A1001A82H&periodStart=202601010000&periodEnd=202612310000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB yearly window: HTTP 200, **EMPTY** (Ack 999 "INSTALLED_GENERATION_CAPACITY_AGGREGATED_R3 [14.1.A]"). Brexit-GB.
- DE-LU yearly window: HTTP 200, **PASS** — `GL_MarketDocument`, 20 TimeSeries (one per production type).

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/installed_capacity/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, year-window).

### Bronze sample (DE-LU, truncated)

```xml
<GL_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0">
  <type>A68</type>
  <process.processType>A33</process.processType>
  <TimeSeries>
    <businessType>B01</businessType>
    <inBiddingZone_Domain.mRID>10Y1001A1001A82H</inBiddingZone_Domain.mRID>
    <quantity_Measure_Unit.name>MAW</quantity_Measure_Unit.name>
    <MktPSRType><psrType>B16</psrType></MktPSRType>
    <Period>
      <resolution>P1Y</resolution>
      <Point><position>1</position><quantity>9000</quantity></Point>
    </Period>
  </TimeSeries>
</GL_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/installed_capacity/year=YYYY/month=MM/installed_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.installed_capacity.InstalledCapacityTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeInstalledCapacity`
**Dedup key**: `(timestamp_utc, area_code, production_type)`
**Point-in-time field**: none

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Period start | Year boundary, P1Y resolution |
| area_code | str | No | `<inBiddingZone_Domain.mRID>` | EIC |
| production_type | str | No | `<MktPSRType><psrType>` | EIC PSR type |
| capacity_mw | float | No | `<Point><quantity>` | MW |
| resolution | str | No | parsed | Default "" in canonical. `P1Y`. |
| data_provider | str | No | constant | "entsoe" |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-01-01T00:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "production_type": "B16",
        "capacity_mw": 9000.0,
        "resolution": "365 days, 0:00:00",
        "data_provider": "entsoe",
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Use a yearly window** — P1Y resolution means short windows return EMPTY.
- **GB EMPTY post-Brexit.** GB capacity registry is via Elexon and DUKES.
- A68 is yearly snapshot — values change at year boundaries; intra-year ingestion just rewrites the same data.
- Distinct from `installed_capacity_units` (A71/A33) which gives unit-level breakdown. Same `processType` A33 but different documentType.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §14.1.A): `(documentType=A68, processType=A33, businessType=n/a, in_Domain)`.
  - Code: `("A68", "A33", -, domain_style="in_domain")` → `in_Domain`.
  - **Match.**
- `max_query_days: 365` in `config/sources.yaml` is appropriate for yearly publication.

---

## Modelling notes

- Capacity-factor denominators per production type per zone per year.
- Capacity-mix scenario builds (closure / new-build trajectories).
- Combine with `actual_generation` (A75) for utilisation rates.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/installed_capacity.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
