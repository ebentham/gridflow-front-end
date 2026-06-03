---
source: entsoe
dataset_key: outages_consumption
vendor: ENTSO-E Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSO-E — Aggregated unavailability of consumption units (A76)

## Overview

Aggregated outage notifications for consumption units. Captures planned
maintenance and forced outages of large industrial loads aggregated to
the bidding-zone level (no per-unit identification at the aggregate
level). Used to model demand-side outage shocks and tightness asymmetry —
losing 500 MW of demand and losing 500 MW of supply have opposite price
implications.

→ [Outages generation](outages_generation.md), [Actual load](actual_load.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | https://web-api.tp.entsoe.eu |
| Path             | /api |
| Method           | GET |
| Auth             | query param `securityToken=$ENTSOE_API_KEY` |
| Rate limit       | 1 req/s |
| Pagination       | None at the API; large windows may return ZIP archives |
| Historical depth | ~2014 onwards |
| Publication lag  | T+~1h |
| Response format  | XML — root `Unavailability_MarketDocument` |
| Document type    | A76 |
| Process type     | n/a |
| Business type    | A53 (planned) — also A54 (unplanned) |
| Domain param name| `BiddingZone_Domain` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `documentType` | str | yes | `A76` | `A76` |
| `BusinessType` | str | yes | `A53` or `A54` | `A53` |
| `BiddingZone_Domain` | EIC | yes | Bidding zone | `10YGB----------A` |
| `periodStart` | str | yes | UTC `yyyymmddhhmm` (30-day) | `202604010000` |
| `periodEnd` | str | yes | UTC `yyyymmddhhmm` | `202605010000` |
| `DocStatus` | str | no | A05/A09/A13 status filter | `A05` |
| `mRID` | str | no | Lookup specific notification | |
| `PeriodStartUpdate` | str | no | Filter by update timestamp | |
| `PeriodEndUpdate` | str | no | Filter by update timestamp | |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  "https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A76&BusinessType=A53&BiddingZone_Domain=10YGB----------A&periodStart=202604010000&periodEnd=202605010000" \
  -H "Accept: application/xml"
```

Live verification 2026-05-08:
- GB 30-day window: HTTP 200, **EMPTY** (Ack 999 "UNAVAILABILITY_OF_CONSUMPTION_UNITS_AGGREGATED [7.1.A, 7.1.B]"). GB does not publish post-Brexit.
- DE-LU 30-day window: HTTP 200, **PASS** — `Unavailability_MarketDocument`, 1 TimeSeries.

---

## Bronze layer

**Path pattern**: `data/bronze/entsoe/outages_consumption/<year>/<month>/<day>/raw_<uuid>.xml`
**Format**: Raw XML, immutable.
**Granularity**: One file per (zone, day).

### Bronze sample (DE-LU, schematic)

```xml
<Unavailability_MarketDocument xmlns="urn:iec62325.351:tc57wg16:451-2:unavailibilitydocument:5:0">
  <type>A76</type>
  <docStatus><value>A05</value></docStatus>
  <TimeSeries>
    <businessType>A53</businessType>
    <biddingZone_Domain.mRID>10Y1001A1001A82H</biddingZone_Domain.mRID>
    <Available_Period>
      <timeInterval>...</timeInterval>
      <resolution>PT60M</resolution>
      <Point><position>1</position><quantity>120</quantity></Point>
    </Available_Period>
  </TimeSeries>
</Unavailability_MarketDocument>
```

---

## Silver layer

**Path pattern**: `data/silver/entsoe/outages_consumption/year=YYYY/month=MM/outages_consumption_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsoe.outages_h7.OutagesConsumptionTransformer`
**Pydantic schema**: `gridflow.schemas.entsoe.EntsoeOutagesConsumption`
**Dedup key**: `(timestamp_utc, area_code, business_type, timeseries_mrid)` — aggregate-level, no unit_mrid
**Point-in-time (as-of) field**: `available_at` (the bitemporal as-of column written by `BaseSilverTransformer`, reconstructable from bronze sidecars on reingest). `ingested_at` is the transform wall-clock (`datetime.now(UTC)`), **not** a publication vintage, so do not use it as a leak-proof as-of anchor.

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| timestamp_utc | datetime[UTC] | No | Available_Period | tz-aware UTC |
| area_code | str | No | `<biddingZone_Domain.mRID>` | EIC |
| outage_type | str | No | derived from `<businessType>` | "planned" / "unplanned" |
| unavailable_mw | float | No | `<Point><quantity>` | MW |
| business_type | str | No | `<businessType>` | Default "" in canonical. Raw EIC code. |
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
        "timestamp_utc": "2026-04-10T08:00:00+00:00",
        "area_code": "10Y1001A1001A82H",
        "outage_type": "planned",
        "unavailable_mw": 120.0,
        "business_type": "A53",
        "document_mrid": "ABC123",
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
- **30-day window** required as for other outage datasets.
- **Outage status codes** (DocStatus): `A05` Active, `A09` Cancelled, `A13` Withdrawn. Cancelled and withdrawn notifications are revisions to active ones. NOTE: gridflow silver dedups on `(timestamp_utc, area_code, business_type, timeseries_mrid)` with `keep="last"` and is NOT revision-aware (it does not sort by `revisionNumber`).
- Aggregate-only — no `unit_mrid`. Use ENTSO-E's per-unit consumption datasets if available, or country aggregates.
- Sparse for many zones — most TSOs do not publish granular consumer outages.

---

## Implementation delta

- Tuple verified 2026-05-08:
  - Docs (API guide §7.1.A/B): `(documentType=A76, processType=n/a, BusinessType=A53|A54, BiddingZone_Domain)`.
  - Code: `("A76", None, BusinessType="A53", domain_style="bidding_zone")` → `BiddingZone_Domain`.
  - **Match.**

---

## Modelling notes

- Tightness asymmetry features — separate generation outage and consumption outage signals.
- Industrial-load disruption — combined with `actual_load` to extract residual load behaviour.
- Plot vs price tails — large consumption outages reduce demand and can suppress prices.

---

## Links

- [Official API docs](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.pdf)
- [Connector source](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/entsoe/client.py)
- [Silver transformer](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/silver/entsoe/outages_h7.py)
- [Pydantic schema](../../../../../../OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsoe.py)
- [Gold view/builder](none)
